"""A1 - Market intraday momentum (last half hour). Spec: research/hypotheses/A1_intraday_momentum.md

Signal table for ``pfbot.backtest.engine.run_backtest``. One row per session at most:

* ``r_open``: log return from the previous session close (price known at the previous
  16:00 ET / 17:30 Berlin) to the price known at open + 30 min (10:00 ET / 09:30 Berlin),
  divided by the ex-ante expected std of that window (sum of ``expected_bar_vol`` variances
  over the window's 5-minute bars, which only use days strictly before the current one).
* optional confirmation ``r_late``: log return over [close - 60 min, close - 30 min].
* entry at close - 30 min (15:30 ET / 17:00 Berlin) at market in the direction of
  ``sign(r_open)`` when ``|r_open| >= z`` (and, with ``confirm``, ``sign(r_late) == sign(r_open)``);
* protective stop ``k`` x expected std of the 30-minute holding window (log-return units) x
  entry price; no target; exit at the session close.

"Price at T" is ``price_at(bars, T)``: the close of the last M1 bar starting before T, so it is
the latest price known at instant T. The signal's ``time`` is the start of that last bar before
the entry instant, hence the engine fills at the open of the first bar at/after the entry instant
and the decision uses only bars that closed at or before it.

Interpretation notes (where the spec is silent)
* ``r_open == 0`` gives no trade (the side is undefined); ``r_late == 0`` fails the confirmation.
* Prices needed for ``r_late`` are only required when ``confirm`` is True, so the confirm variant
  is by construction a subset of the plain variant.
* The previous session is the previous local date returned by ``session_dates`` (dates with a bar
  at the session-open minute); a previous close more than 4 calendar days back is skipped.
* "No bar within 5 minutes": the entry needs a decision bar starting in [T-5min, T) and a fill bar
  starting in [T, T+5min); the exit needs a bar starting in [T_exit, T_exit+5min) (the engine
  exits at the first bar >= exit_time, so this bounds how late a time exit can be).
* The vol model's trading day rolls at 17:00 New York (also for GER40); profile buckets are in
  the session's local time zone. A day is skipped if any 5-minute bar in either window has no
  vol forecast (warm-up / missing profile bucket).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfbot.features.volatility import expected_bar_vol
from pfbot.research import harness
from pfbot.research.harness import SESSIONS, local_times, price_at, session_dates

CONFIGS = harness.grid(z=[0.0, 0.5, 1.0], k=[1.5, 2.5], confirm=[False, True])

HOLD_MINUTES = 30
OPEN_MINUTES = 30
MAX_PREV_CLOSE_DAYS = 4
MAX_BAR_GAP = pd.Timedelta(minutes=5)
BAR = pd.Timedelta(minutes=1)
COLUMNS = ["time", "side", "order", "stop_dist", "exit_time", "r_open", "r_late"]


def _shift(hhmm: str, minutes: int) -> str:
    t = int(hhmm[:2]) * 60 + int(hhmm[3:]) + minutes
    return f"{t // 60:02d}:{t % 60:02d}"


def _window_var(exp_vol: pd.Series, starts: pd.DatetimeIndex, ends: pd.DatetimeIndex) -> np.ndarray:
    """Sum of expected variances of the 5-min bars opening in [start, end); NaN if the window is
    empty or any bar in it has no forecast."""
    v = exp_vol.to_numpy(float) ** 2
    bad = np.isnan(v)
    cs = np.concatenate([[0.0], np.cumsum(np.where(bad, 0.0, v))])
    cb = np.concatenate([[0], np.cumsum(bad)])
    ok = ~(pd.isna(starts) | pd.isna(ends))
    epoch = pd.Timestamp("1970-01-01", tz="UTC")
    a = exp_vol.index.searchsorted(starts.where(ok, epoch), side="left")
    b = exp_vol.index.searchsorted(ends.where(ok, epoch), side="left")
    out = cs[b] - cs[a]
    good = ok & (b > a) & ((cb[b] - cb[a]) == 0)
    return np.where(good, out, np.nan)


def signals(bars: pd.DataFrame, symbol: str, z: float, k: float, confirm: bool) -> pd.DataFrame:
    """A1 signal table (columns time, side, order, stop_dist, exit_time + diagnostics
    r_open / r_late) for M1 ``bars`` of ``symbol``."""
    sess = SESSIONS[symbol]
    empty = pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})

    dates = session_dates(bars, sess)
    if len(dates) < 2:
        return empty
    cur, prev = dates[1:], dates[:-1]
    gap_days = np.asarray((cur - prev).days)

    t_prev_close = local_times(prev, sess.close, sess.tz)
    t_open_end = local_times(cur, _shift(sess.open, OPEN_MINUTES), sess.tz)
    t_late0 = local_times(cur, _shift(sess.close, -2 * HOLD_MINUTES), sess.tz)
    t_entry = local_times(cur, _shift(sess.close, -HOLD_MINUTES), sess.tz)
    t_exit = local_times(cur, sess.close, sess.tz)

    # ---- prices known at each instant (latest closed M1 bar) ----
    p_prev = price_at(bars, t_prev_close)
    p_open = price_at(bars, t_open_end)
    p_entry = price_at(bars, t_entry)
    p_late0 = price_at(bars, t_late0) if confirm else np.full(len(cur), np.nan)

    # ---- bar availability at entry / exit ----
    idx = bars.index
    valid_t = ~(pd.isna(t_entry) | pd.isna(t_exit))
    epoch = pd.Timestamp("1970-01-01", tz="UTC")
    te = t_entry.where(valid_t, epoch)
    tx = t_exit.where(valid_t, epoch)
    pos = idx.searchsorted(te, side="left") - 1  # last bar starting strictly before entry
    has_dec = pos >= 0
    dec_time = idx[np.clip(pos, 0, None)]
    has_fill = (pos + 1) < len(idx)
    fill_time = idx[np.clip(pos + 1, None, len(idx) - 1)]
    ex = idx.searchsorted(tx, side="left")  # first bar at/after the exit instant
    has_exit = ex < len(idx)
    exit_bar = idx[np.clip(ex, None, len(idx) - 1)]
    entry_ok = (
        valid_t & has_dec & has_fill & has_exit
        & ((te - dec_time) <= MAX_BAR_GAP)
        & ((fill_time - te) < MAX_BAR_GAP)
        & ((exit_bar - tx) < MAX_BAR_GAP)
        & ((dec_time + BAR) <= te)  # decision bar is closed by the entry instant
    )

    # ---- ex-ante expected vol of the opening window and of the holding window ----
    ev = expected_bar_vol(bars, tz=sess.tz)
    var_open = _window_var(ev, t_prev_close, t_open_end)
    var_hold = _window_var(ev, t_entry, t_exit)

    with np.errstate(invalid="ignore", divide="ignore"):
        r_open_raw = np.log(p_open / p_prev)
        r_open = r_open_raw / np.sqrt(var_open)
        r_late = np.log(p_entry / p_late0)
        stop_dist = k * np.sqrt(var_hold) * p_entry

    keep = (
        entry_ok
        & (gap_days <= MAX_PREV_CLOSE_DAYS)
        & np.isfinite(r_open) & (r_open != 0)
        & np.isfinite(stop_dist) & (stop_dist > 0)
        & (np.abs(r_open) >= z)
    )
    side = np.sign(r_open)
    if confirm:
        keep &= np.isfinite(r_late) & (np.sign(r_late) == side)

    if not keep.any():
        return empty
    sig = pd.DataFrame(
        {
            "time": dec_time[keep],
            "side": side[keep].astype(int),
            "order": "market",
            "stop_dist": stop_dist[keep],
            "exit_time": t_exit[keep],
            "r_open": r_open[keep],
            "r_late": r_late[keep] if confirm else np.nan,
        }
    ).reset_index(drop=True)
    # no look-ahead guarantee: the deciding bar closed at or before the entry instant
    assert (sig["time"] + BAR <= t_entry[keep]).all()
    return sig
