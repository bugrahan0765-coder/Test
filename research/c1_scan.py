"""C1 - systematic scan of conditional intraday return patterns.

Spec: research/hypotheses/C1_intraday_scan.md (pre-registered; implemented exactly).
Run:  python -m research.c1_scan [--no-log]
Output: research/reports/C1_scan.md and research/reports/C1_scan.csv

Design
------
Per instrument the M1 IS bars are resampled once to a 5-minute grid and the ex-ante per-bar
expected std (``expected_bar_vol``, day d uses only trading days < d) is computed once. Both are put
on a dense integer grid (one cell per 5 minutes, NaN where a bar is missing) with cumulative sums
of the variances, so every window sum / completeness test is O(1) and vectorised across dates.

For each (slot t, holding H) all weekday NY dates are processed at once (``scan_instrument``);
``config_values`` then turns the stored arrays into per-trade values for a (signal, rule)
configuration.

Interpretation choices where the spec is silent (all documented in the report):
* "latest close known at t" = close of the last 5-min bar *starting* before t, and that bar must
  start no earlier than t - 10 min (same start-based convention as harness.price_at).
* Trade window [t, t+H) must have all H/5 expected-vol bins present and non-NaN. This implies
  there is no gap > 5 minutes in the window, so the "gap > 15 min" rule is subsumed.
* ``recent`` additionally needs the whole window [t-H, t) to have all its bins (complete window)
  and a price at t-H; ``day`` sums the bins that exist between the previous 16:00 and t.
* Previous close for ``day`` = the 16:00 ET price of the nearest earlier weekday that has one
  (holidays are skipped), at most 4 calendar days back.
* Period split is by NY calendar date of the entry.
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

from pfbot.data.histdata import SPREAD
from pfbot.data.schema import resample_bars
from pfbot.features.volatility import expected_bar_vol
from pfbot.research.harness import SLIPPAGE, cost_frac, load_period, local_times
from pfbot.stats.performance import TrialRegistry, deflated_sharpe_ratio

NY = "America/New_York"
HYP_ID = "C1"
COST_VERSION = "v1"  # "v2": relative costs from harness.COST_BPS
SYMBOLS = ["US100", "US500", "XAUUSD"]
SISTER = {"US100": "US500", "US500": "US100"}
HS = (60, 120, 240)
SLOT_MINUTES = tuple(range(2 * 60, 15 * 60 + 31, 30))  # 02:00 .. 15:30 ET, 28 slots
CLOSE_MIN = 16 * 60
KINDS = ("none", "day", "recent")
RULES = ("follow", "fade")
THRESHOLD = 0.5
MAX_PREV_CLOSE_DAYS = 4
MAX_STALE_BARS = 1  # last bar start >= t - 10 min, i.e. at most one missing 5-min bar just before t
DISCOVERY = ("2015-01-01", "2018-12-31")
CONFIRMATION = ("2019-01-01", "2020-12-31")
MIN_DISC_TRADES = 300
T_DISC = 3.0
T_DISC_XAU = 3.4
T_CONF = 2.0
N_CONFIGS_PER_SYMBOL = len(SLOT_MINUTES) * len(HS) * len(KINDS) * len(RULES)  # 504

STEP_NS = 5 * 60 * 10**9
PAD = 3000  # empty grid cells either side so windows near the data edges are simply invalid

REPORTS = Path(__file__).parent / "reports"


def hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _ns(idx: pd.DatetimeIndex) -> np.ndarray:
    return idx.as_unit("ns").asi8


# ---------------------------------------------------------------------------
# dense 5-minute grid
# ---------------------------------------------------------------------------
class Grid:
    """Dense 5-minute grid of closes and expected variances with cumulative sums."""

    def __init__(self, bars5: pd.DataFrame, ev: pd.Series):
        ns = _ns(bars5.index)
        if len(ns) == 0:
            raise ValueError("no bars")
        self.t0 = int(ns[0]) - PAD * STEP_NS
        self.n = int((ns[-1] - ns[0]) // STEP_NS) + 1 + 2 * PAD
        p = (ns - self.t0) // STEP_NS
        self.close = np.full(self.n, np.nan)
        self.close[p] = bars5["close"].to_numpy(float)
        var = np.full(self.n, np.nan)
        pe = (_ns(ev.index) - self.t0) // STEP_NS
        var[pe] = ev.to_numpy(float) ** 2
        self.var = var
        present = ~np.isnan(self.close)
        self.last_idx = np.maximum.accumulate(np.where(present, np.arange(self.n), -1))
        ok = ~np.isnan(var)
        self.cumvar = np.concatenate([[0.0], np.cumsum(np.where(ok, var, 0.0))])
        self.cumcnt = np.concatenate([[0], np.cumsum(ok)]).astype(np.int64)

    def pos(self, t: pd.DatetimeIndex) -> tuple[np.ndarray, np.ndarray]:
        """Grid cell index of instants ``t`` (UTC) and a validity mask (not NaT, on-grid, in range)."""
        ok = ~np.asarray(pd.isna(t))
        ns = np.where(ok, _ns(t), self.t0)
        rel = ns - self.t0
        ok &= (rel % STEP_NS == 0) & (rel >= 0) & (rel // STEP_NS <= self.n)
        return np.clip(rel // STEP_NS, 0, self.n).astype(np.int64), ok

    def price_known(self, pos: np.ndarray, ok: np.ndarray) -> np.ndarray:
        """Close of the last 5-min bar starting strictly before cell ``pos`` (so already closed),
        if it starts no earlier than 10 minutes before; NaN otherwise."""
        j = pos - 1
        good = ok & (j >= 0)
        jj = np.clip(j, 0, self.n - 1)
        k = self.last_idx[jj]
        good &= (k >= 0) & (jj - k <= MAX_STALE_BARS)
        return np.where(good, self.close[np.clip(k, 0, self.n - 1)], np.nan)

    def window(self, a: np.ndarray, b: np.ndarray, ok: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(summed variance, number of bins with a forecast, number of cells) of cells [a, b)."""
        ok = ok & (b >= a)
        a = np.clip(a, 0, self.n)
        b = np.clip(b, 0, self.n)
        var = self.cumvar[b] - self.cumvar[a]
        cnt = self.cumcnt[b] - self.cumcnt[a]
        return np.where(ok, var, np.nan), np.where(ok, cnt, 0), np.where(ok, b - a, 0)


# ---------------------------------------------------------------------------
# per (slot, H) vectorised computation across dates
# ---------------------------------------------------------------------------
@dataclass
class SlotData:
    """Everything per weekday date for one (slot, H). ``ok`` marks dates with a valid trade window."""
    symbol: str
    slot: str
    H: int
    dates: pd.DatetimeIndex  # naive NY dates
    ok: np.ndarray
    entry: np.ndarray        # price known at t
    exit: np.ndarray         # price known at t+H
    sigma: np.ndarray        # expected std of the window [t, t+H) (log-return units)
    cost: float              # price units: SPREAD + 2 * SLIPPAGE
    x_day: np.ndarray
    x_recent: np.ndarray
    cost_frac: float | None = None  # cost model v2: round-trip cost as a fraction of price

    @property
    def logret(self) -> np.ndarray:
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.log(self.exit / self.entry)

    @property
    def cost_log(self) -> np.ndarray:
        with np.errstate(invalid="ignore", divide="ignore"):
            if self.cost_frac is not None:
                return np.full(self.entry.shape, self.cost_frac)
            return self.cost / self.entry


def weekday_dates(bars5: pd.DataFrame) -> pd.DatetimeIndex:
    local = bars5.index.tz_convert(NY)
    first, last = local[0].tz_localize(None).normalize(), local[-1].tz_localize(None).normalize()
    return pd.bdate_range(first, last)


def scan_instrument(grid: Grid, dates: pd.DatetimeIndex, symbol: str,
                    slots=SLOT_MINUTES, hs=HS) -> dict[tuple[str, int], SlotData]:
    """Per (slot label, H): SlotData for all ``dates``. Pure function of data known by each instant."""
    cost = float(SPREAD[symbol] + 2.0 * SLIPPAGE[symbol])
    cfrac = cost_frac(symbol) if COST_VERSION == "v2" else None
    N = len(dates)

    # previous 16:00 close per date (nearest earlier weekday with a price, <= 4 calendar days back)
    p16_pos, p16_ok = grid.pos(local_times(dates, hhmm(CLOSE_MIN), NY))
    p16 = grid.price_known(p16_pos, p16_ok)
    have = np.isfinite(p16)
    la = np.maximum.accumulate(np.where(have, np.arange(N), -1))
    prev = np.concatenate([[-1], la[:-1]])
    prev_c = np.clip(prev, 0, None)
    gap_days = np.asarray((dates - dates[prev_c]).days)
    prev_ok = (prev >= 0) & (gap_days <= MAX_PREV_CLOSE_DAYS)
    prev_pos, prev_px = p16_pos[prev_c], p16[prev_c]

    out: dict[tuple[str, int], SlotData] = {}
    for sm in slots:
        label = hhmm(sm)
        pos_t, v_t = grid.pos(local_times(dates, label, NY))
        entry = grid.price_known(pos_t, v_t)
        # day signal (independent of H)
        var_d, cnt_d, _ = grid.window(prev_pos, pos_t, v_t & prev_ok)
        with np.errstate(invalid="ignore", divide="ignore"):
            x_day = np.log(entry / prev_px) / np.sqrt(np.where(cnt_d > 0, var_d, np.nan))
        x_day = np.where(np.isfinite(x_day), x_day, np.nan)
        for H in hs:
            nb = H // 5
            nan = np.full(N, np.nan)
            if sm + H > CLOSE_MIN:
                out[(label, H)] = SlotData(symbol, label, H, dates, np.zeros(N, bool), nan, nan, nan, cost, nan, nan, cfrac)
                continue
            pos_e, v_e = grid.pos(local_times(dates, hhmm(sm + H), NY))
            v = v_t & v_e & (pos_e - pos_t == nb)
            exit_ = grid.price_known(pos_e, v)
            var_w, cnt_w, len_w = grid.window(pos_t, pos_e, v)
            ok = v & np.isfinite(entry) & np.isfinite(exit_) & (cnt_w == nb) & (len_w == nb) & (var_w > 0)
            sigma = np.where(ok, np.sqrt(np.where(var_w > 0, var_w, np.nan)), np.nan)
            # recent signal: [t-H, t)
            pos_h = pos_t - nb
            v_h = v_t & (pos_h >= 0)
            p_h = grid.price_known(pos_h, v_h)
            var_r, cnt_r, len_r = grid.window(pos_h, pos_t, v_h)
            good_r = np.isfinite(p_h) & np.isfinite(entry) & (cnt_r == nb) & (len_r == nb) & (var_r > 0)
            with np.errstate(invalid="ignore", divide="ignore"):
                x_rec = np.where(good_r, np.log(entry / p_h) / np.sqrt(np.where(var_r > 0, var_r, np.nan)), np.nan)
            out[(label, H)] = SlotData(symbol, label, H, dates, ok, entry, exit_, sigma, cost,
                                       x_day, np.where(np.isfinite(x_rec), x_rec, np.nan), cfrac)
    return out


def config_values(sd: SlotData, kind: str, rule: str, threshold: float = THRESHOLD) -> np.ndarray:
    """Trade value in sigma units per date (NaN = no trade) for one (signal, rule) configuration:
    (side * log(exit/entry) - cost/entry) / window_std."""
    if kind == "none":
        x = np.ones(len(sd.dates))
    elif kind == "day":
        x = sd.x_day
    elif kind == "recent":
        x = sd.x_recent
    else:
        raise ValueError(kind)
    with np.errstate(invalid="ignore"):
        trade = sd.ok & np.isfinite(x)
        if kind != "none":
            trade &= np.abs(x) >= threshold
        side = np.sign(x) * (1.0 if rule == "follow" else -1.0)
        val = (side * sd.logret - sd.cost_log) / sd.sigma
    return np.where(trade & np.isfinite(val), val, np.nan)


def period_mask(dates: pd.DatetimeIndex, period: tuple[str, str]) -> np.ndarray:
    return np.asarray((dates >= pd.Timestamp(period[0])) & (dates <= pd.Timestamp(period[1])))


def trade_stats(v: np.ndarray) -> dict:
    v = v[~np.isnan(v)]
    n = len(v)
    if n < 2:
        return dict(n=n, mean=np.nan, std=np.nan, t=np.nan, sr=np.nan, skew=np.nan, kurt=np.nan)
    m, s = float(v.mean()), float(v.std(ddof=1))
    if s > 0:
        t, sr = m / s * np.sqrt(n), m / s
    else:
        t = sr = np.nan
    skew = float(sps.skew(v)) if n > 2 and s > 0 else np.nan
    kurt = float(sps.kurtosis(v, fisher=False)) if n > 3 and s > 0 else np.nan
    return dict(n=n, mean=m, std=s, t=float(t), sr=float(sr), skew=skew, kurt=kurt)


def build_table(slotdata: dict[str, dict[tuple[str, int], SlotData]]) -> pd.DataFrame:
    """One row per (symbol, slot, H, signal, rule): discovery (d_*) and confirmation (c_*) stats."""
    rows = []
    for sym, sdict in slotdata.items():
        for (slot, H), sd in sdict.items():
            md, mc = period_mask(sd.dates, DISCOVERY), period_mask(sd.dates, CONFIRMATION)
            for kind in KINDS:
                for rule in RULES:
                    v = config_values(sd, kind, rule)
                    row = dict(symbol=sym, slot=slot, H=H, x=kind, rule=rule)
                    for pre, m in (("d_", md), ("c_", mc)):
                        st = trade_stats(v[m])
                        row.update({pre + k: val for k, val in st.items()})
                    rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# selection and deflated Sharpe
# ---------------------------------------------------------------------------
def select_candidates(tab: pd.DataFrame) -> pd.DataFrame:
    """Add sister-instrument discovery mean and the boolean ``candidate`` column (rule fixed in advance)."""
    tab = tab.copy()
    key = ["slot", "H", "x", "rule"]
    mean_by = tab.set_index(["symbol"] + key)["d_mean"]
    sister_mean = []
    for sym, slot, H, x, rule in zip(tab["symbol"], tab["slot"], tab["H"], tab["x"], tab["rule"]):
        sis = SISTER.get(sym)
        sister_mean.append(mean_by.get((sis, slot, H, x, rule), np.nan) if sis else np.nan)
    tab["sister_d_mean"] = sister_mean
    xau = tab["symbol"] == "XAUUSD"
    disc_t_ok = np.where(xau, tab["d_t"] > T_DISC_XAU, tab["d_t"] > T_DISC)
    sister_ok = np.where(xau, True, tab["sister_d_mean"] > 0)
    tab["candidate"] = (
        (tab["d_mean"] > 0) & disc_t_ok & (tab["d_n"] >= MIN_DISC_TRADES)
        & (tab["c_mean"] > 0) & (tab["c_t"] > T_CONF) & sister_ok
    ).astype(bool)
    return tab


def add_dsr(tab: pd.DataFrame) -> pd.DataFrame:
    """Deflated Sharpe of every config (discovery sample), trial set = discovery SRs of all configs.
    ``dsr`` uses N = total configs (1,512); ``dsr_eff`` uses N = configs with a defined SR."""
    tab = tab.copy()
    trials = tab["d_sr"].to_numpy(float)
    n_all = len(tab)
    n_eff = int(np.isfinite(trials).sum())
    dsr, dsr_eff = [], []
    for sr, n, sk, ku in zip(tab["d_sr"], tab["d_n"], tab["d_skew"], tab["d_kurt"]):
        if not (np.isfinite(sr) and np.isfinite(sk) and np.isfinite(ku)) or n < 3:
            dsr.append(np.nan)
            dsr_eff.append(np.nan)
            continue
        dsr.append(deflated_sharpe_ratio(sr, sr_trials=trials, n_trials=n_all, n_obs=int(n), skew=sk, kurt=ku))
        dsr_eff.append(deflated_sharpe_ratio(sr, sr_trials=trials, n_trials=n_eff, n_obs=int(n), skew=sk, kurt=ku))
    tab["dsr"], tab["dsr_eff"] = dsr, dsr_eff
    return tab


def log_trials(tab: pd.DataFrame, registry: TrialRegistry) -> int:
    """Log every config (discovery stats) to the trial registry. Idempotent: skips if C1 is already logged."""
    if registry.n_trials(HYP_ID) > 0:
        print(f"registry already holds {registry.n_trials(HYP_ID)} {HYP_ID} trials; not logging again")
        return 0
    for r in tab.itertuples(index=False):
        sr = float(r.d_sr) if np.isfinite(r.d_sr) else float("nan")
        registry.log(HYP_ID, dict(symbol=r.symbol, period="discovery", slot=r.slot, H=int(r.H),
                                  x=r.x, rule=r.rule, start=DISCOVERY[0], end=DISCOVERY[1]),
                     n_obs=int(r.d_n), sharpe=sr)
    return len(tab)


# ---------------------------------------------------------------------------
# loading / orchestration
# ---------------------------------------------------------------------------
def prepare_bars(bars_m1: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """5-min bars and ex-ante per-bar expected std (computed once; it resamples internally, which is
    idempotent on an already 5-minute frame)."""
    bars5 = resample_bars(bars_m1, "5min")
    return bars5, expected_bar_vol(bars5, tz=NY)


def scan_bars(bars_m1: pd.DataFrame, symbol: str, slots=SLOT_MINUTES, hs=HS) -> dict[tuple[str, int], SlotData]:
    """Convenience wrapper for tests / small data: M1 bars -> SlotData per (slot, H)."""
    bars5, ev = prepare_bars(bars_m1)
    return scan_instrument(Grid(bars5, ev), weekday_dates(bars5), symbol, slots, hs)


def run_scan(symbols=SYMBOLS) -> tuple[dict, dict]:
    slotdata, info = {}, {}
    for sym in symbols:
        t0 = time.time()
        bars = load_period(sym, "IS")
        bars5, ev = prepare_bars(bars)
        info[sym] = dict(m1_bars=len(bars), bars5=len(bars5), ev_nan=int(ev.isna().sum()),
                         first=str(bars.index[0]), last=str(bars.index[-1]))
        slotdata[sym] = scan_instrument(Grid(bars5, ev), weekday_dates(bars5), sym)
        print(f"{sym}: {len(bars):,} M1 bars, {len(bars5):,} M5 bars, scanned in {time.time() - t0:.1f}s", flush=True)
    return slotdata, info


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
def _fmt(x, nd=3):
    return "" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}f}"


def _md_table(df: pd.DataFrame, cols: list[tuple[str, str, int]]) -> str:
    head = "| " + " | ".join(c[1] for c in cols) + " |\n|" + "|".join("---" for _ in cols) + "|\n"
    body = []
    for _, r in df.iterrows():
        cells = []
        for key, _, nd in cols:
            v = r[key]
            if nd < 0:
                cells.append(str(v))
            elif nd == 0:
                cells.append("" if pd.isna(v) else f"{int(v)}")
            else:
                cells.append(_fmt(float(v), nd))
        body.append("| " + " | ".join(cells) + " |")
    return head + "\n".join(body) + "\n"


TOP_COLS = [("symbol", "symbol", -1), ("slot", "slot ET", -1), ("H", "H", 0), ("x", "x", -1), ("rule", "rule", -1),
            ("d_n", "d n", 0), ("d_mean", "d mean", 3), ("d_t", "d t", 2), ("d_sr", "d SR", 3),
            ("c_n", "c n", 0), ("c_mean", "c mean", 3), ("c_t", "c t", 2), ("c_sr", "c SR", 3),
            ("candidate", "cand", -1)]
CAND_COLS = [("symbol", "symbol", -1), ("slot", "slot ET", -1), ("H", "H", 0), ("x", "x", -1), ("rule", "rule", -1),
             ("d_n", "d n", 0), ("d_mean", "d mean", 3), ("d_t", "d t", 2), ("d_sr", "d SR", 3),
             ("d_skew", "d skew", 2), ("d_kurt", "d kurt", 1), ("sister_d_mean", "sister d mean", 3),
             ("c_n", "c n", 0), ("c_mean", "c mean", 3), ("c_t", "c t", 2), ("c_sr", "c SR", 3),
             ("dsr", "DSR (N=1512)", 3), ("dsr_eff", "DSR (N eff)", 3)]


def write_report(tab: pd.DataFrame, info: dict, runtime: float, logged: int, path: Path) -> str:
    n_all = len(tab)
    defined = tab[tab["d_t"].notna()]
    n_eff = len(defined)
    cand = tab[tab["candidate"]].sort_values("d_t", ascending=False)
    top = tab[tab["d_t"].notna()].sort_values("d_t", ascending=False).head(30)

    def exp_cnt(thr, n):
        return n * float(sps.norm.sf(thr))

    dist_rows = []
    for label, sub in [("all", defined)] + [(s, defined[defined["symbol"] == s]) for s in SYMBOLS]:
        n = len(sub)
        dist_rows.append(
            f"| {label} | {n} | {(sub['d_t'] > 2).sum()} | {exp_cnt(2, n):.1f} | {(sub['d_t'] > 3).sum()} | "
            f"{exp_cnt(3, n):.1f} | {(sub['d_t'] < -2).sum()} | {(sub['d_t'] < -3).sum()} | "
            f"{sub['d_t'].median():.2f} | {sub['d_mean'].median():.3f} |")
    n_pos = int((defined["d_mean"] > 0).sum())
    follow_fade = defined.groupby(["x", "rule"]).agg(n=("d_t", "size"), gt2=("d_t", lambda s: int((s > 2).sum())),
                                                       gt3=("d_t", lambda s: int((s > 3).sum())),
                                                       med_mean=("d_mean", "median")).reset_index()
    ff = "| x | rule | configs | t>2 | t>3 | median d mean |\n|---|---|---|---|---|---|\n" + "\n".join(
        f"| {r.x} | {r.rule} | {r.n} | {r.gt2} | {r.gt3} | {r.med_mean:.3f} |" for r in follow_fade.itertuples())

    steps = [
        ("configs total (3 instruments x 504)", n_all),
        ("configs with a defined discovery t (>= 2 trades)", n_eff),
        ("structurally empty (exit after 16:00 ET)", n_all - n_eff),
        ("discovery n >= 300", int((tab["d_n"] >= MIN_DISC_TRADES).sum())),
        ("discovery mean > 0", int((tab["d_mean"] > 0).sum())),
        ("... and discovery t > 3.0 (XAUUSD: > 3.4)", int(((tab["d_mean"] > 0) & np.where(tab["symbol"] == "XAUUSD", tab["d_t"] > T_DISC_XAU, tab["d_t"] > T_DISC)).sum())),
        ("... and n >= 300", int(((tab["d_mean"] > 0) & np.where(tab["symbol"] == "XAUUSD", tab["d_t"] > T_DISC_XAU, tab["d_t"] > T_DISC) & (tab["d_n"] >= MIN_DISC_TRADES)).sum())),
        ("... and confirmation mean > 0 and t > 2.0", int(((tab["d_mean"] > 0) & np.where(tab["symbol"] == "XAUUSD", tab["d_t"] > T_DISC_XAU, tab["d_t"] > T_DISC) & (tab["d_n"] >= MIN_DISC_TRADES) & (tab["c_mean"] > 0) & (tab["c_t"] > T_CONF)).sum())),
        ("... and sister-instrument discovery mean > 0 (XAUUSD: n/a) = candidates", len(cand)),
    ]
    steps_md = "| step | count |\n|---|---|\n" + "\n".join(f"| {a} | {b} |" for a, b in steps)

    inst = "\n".join(
        f"- {s}: {i['m1_bars']:,} M1 bars ({i['first'][:10]} .. {i['last'][:10]}) after month exclusions, "
        f"{i['bars5']:,} 5-min bars, {i['ev_nan']:,} bars without a vol forecast (warm-up / gaps)"
        for s, i in info.items())

    md = f"""# C1 - systematic intraday scan (in-sample)

Generated by `python -m research.c1_scan` (runtime {runtime:.0f} s). Spec: `research/hypotheses/C1_intraday_scan.md`.
Full table: `research/reports/C1_scan.csv`. All {logged if logged else 0} configurations logged to
`research/trials.jsonl` with hypothesis id `C1` in this run (logging is skipped if C1 trials already exist).

## Method
- Data: `load_period(sym, "IS")` M1 bars (HistData months excluded as in the harness), resampled to a 5-minute grid;
  per-bar ex-ante std from `expected_bar_vol(bars5, tz=America/New_York)` (HAR-RV x intraday profile, no look-ahead).
{inst}
- Grid: instruments US100, US500, XAUUSD x 28 entry slots (02:00..15:30 ET every 30 min, DST aware) x H in {{60,120,240}} min
  x signal {{none, day, recent}} x rule {{follow, fade}} = {N_CONFIGS_PER_SYMBOL} per instrument, {n_all} total.
- Entry price: close of the last 5-min bar starting before t (must start >= t-10 min). Exit price: same rule at t+H.
  A trade is skipped if t+H > 16:00 ET, if any of the H/5 expected-vol bins in [t, t+H) is missing/NaN
  (this also rules out any gap > 15 min), or if the entry/exit price is stale.
- Window std = sqrt(sum of the bins' expected variances). `day`: log(P_t / P_prev16:00) / sqrt(sum of existing bins' variances
  from previous 16:00 to t), previous close = nearest earlier weekday with a 16:00 price, at most 4 calendar days back.
  `recent`: log(P_t / P_(t-H)) / std of [t-H, t) (all bins required). Threshold |x| >= {THRESHOLD}; `none`: x = +1 (follow = long, fade = short).
- Trade value (sigma units) = (side * log(exit/entry) - cost) / window std, cost = (SPREAD + 2 x SLIPPAGE) / entry price
  (US100 {SPREAD['US100']}+2x{SLIPPAGE['US100']}, US500 {SPREAD['US500']}+2x{SLIPPAGE['US500']}, XAUUSD {SPREAD['XAUUSD']}+2x{SLIPPAGE['XAUUSD']} index points / USD).
- Per config and period: n, mean, t = mean/std x sqrt(n), per-trade Sharpe = mean/std. Discovery 2015-01-01..2018-12-31, confirmation 2019-01-01..2020-12-31 (by NY entry date).
  OOS 2021-2023 is not loaded.
- Selection: discovery mean > 0, t > 3.0 (XAUUSD t > 3.4), n >= 300; confirmation mean > 0, t > 2.0; sister instrument (US100 <-> US500)
  positive discovery mean for the same slot/H/x/rule.
- DSR: `deflated_sharpe_ratio` with the discovery per-trade Sharpes of all configs as the trial set (variance of the {n_eff} defined SRs),
  candidate's own discovery SR, skew, Pearson kurtosis and n. `DSR (N=1512)` uses N = 1,512 trials (the pre-registered count; the
  {n_all - n_eff} structurally empty configs have no SR and contribute only to N), `DSR (N eff)` uses N = {n_eff}.

## Counts
{steps_md}

## Distribution of discovery t-statistics versus the null
Null expectation = N x P(Z > c) with N the number of configs with a defined t (normal approximation, one-sided). Costs shift every mean
below zero, so under a true null fewer positives than this are expected; but configs are heavily dependent (overlapping windows, shared
signals, follow/fade are mirror images up to cost, US100/US500 highly correlated), so the effective number of independent tests is much
smaller than N and the count of large |t| is more dispersed than the independent-tests figure suggests.

| group | N | t>2 | expected | t>3 | expected | t<-2 | t<-3 | median d t | median d mean |
|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(dist_rows)}

Share of configs with a positive discovery mean: {n_pos}/{n_eff}.

{ff}

## Top 30 configs by discovery t (all instruments) with confirmation stats
{_md_table(top, TOP_COLS)}
## Candidates ({len(cand)})
{_md_table(cand, CAND_COLS) if len(cand) else "No configuration passes the pre-registered selection rule."}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding="utf-8")
    return md


def main(argv=None) -> pd.DataFrame:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-log", action="store_true", help="do not append to research/trials.jsonl (development)")
    ap.add_argument("--cost", choices=["v1", "v2"], default="v1", help="cost model (v2 = relative, see harness)")
    args = ap.parse_args(argv)
    global COST_VERSION, HYP_ID
    COST_VERSION = args.cost
    suffix = "" if args.cost == "v1" else "_v3"
    if args.cost == "v2":
        HYP_ID = "C1v3"
    t0 = time.time()
    slotdata, info = run_scan()
    tab = add_dsr(select_candidates(build_table(slotdata)))
    assert len(tab) == 3 * N_CONFIGS_PER_SYMBOL, len(tab)
    logged = 0
    if not args.no_log:
        logged = log_trials(tab, TrialRegistry())
    REPORTS.mkdir(parents=True, exist_ok=True)
    tab.to_csv(REPORTS / f"C1_scan{suffix}.csv", index=False)
    runtime = time.time() - t0
    write_report(tab, info, runtime, logged, REPORTS / f"C1_scan{suffix}.md")
    if args.cost == "v2":
        with open(REPORTS / f"C1_scan{suffix}.md", "a") as f:
            f.write("\n\n**Cost model v3**: round-trip cost = (spread + 2 x slippage) bps of price from "
                    "`harness.COST_BPS`; the per-point SPREAD/SLIPPAGE figures quoted above do not apply.\n")
    print(f"done in {runtime:.0f}s; candidates: {int(tab['candidate'].sum())}")
    return tab


if __name__ == "__main__":
    sys.exit(0 if main() is not None else 1)
