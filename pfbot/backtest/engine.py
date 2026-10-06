"""Bar-based trade simulator.

A strategy outputs a table of *signals* decided at the close of a bar; the
engine turns each into an order that becomes active on the next bar, so no
signal can trade on the bar that produced it.

Execution model (deliberately conservative):
- Bars hold mid prices. Buys execute on the ask (mid + spread/2), sells on the
  bid; stops and targets trigger on the side they would execute on.
- Gaps through a stop/entry fill at the bar open, not at the order price.
- When stop and target are both touched inside one bar, the stop wins.
- On a stop/limit entry bar only the stop is checked (we cannot know whether
  the target came after the fill); on a market entry the whole bar follows the
  fill, so both are checked.
- Position size is fixed at placement from the *intended* entry and the stop,
  so R = pnl / intended risk and a gap can produce a loss beyond -1R.
- One position (or pending order) at a time per call: signals arriving while
  busy are ignored.

Signal columns
    time         bar timestamp at whose close the signal is decided (index or column)
    side         +1 long / -1 short
    order        "market" | "stop" | "limit"           (default "market")
    price        trigger price for stop / limit orders
    expiry       pending order cancelled from the first bar with time >= expiry
    stop_price | stop_dist      protective stop, absolute or distance (one required)
    target_price | target_dist  optional take profit
    exit_time    flatten at the open of the first bar with time >= exit_time
"""
from __future__ import annotations

from dataclasses import dataclass

import numba
import numpy as np
import pandas as pd

from pfbot.data.schema import validate_bars

ORDER_CODES = {"market": 0, "stop": 1, "limit": 2}
EXIT_REASONS = np.array(["stop", "target", "time", "end_of_data"])


@dataclass(frozen=True)
class CostModel:
    """Trading costs. Spread comes from the bars' spread column when present."""

    default_spread: float = 0.0  # price units, used when bars have no spread column
    spread_mult: float = 1.0  # stress-test multiplier on the spread
    min_spread: float = 0.0
    slippage: float = 0.0  # price units, on market/stop entries and stop/time exits
    commission_frac: float = 0.0  # fraction of price, charged per side
    financing_annual: float = 0.0  # CFD swap: fraction of notional per year, charged per night held
    rollover_tz: str = "America/New_York"  # nights are counted at the 17:00 rollover in this zone


@numba.njit(cache=True)
def _simulate(o, h, l, c, s, i0, side, otype, trig, exp_idx, stop, target, exit_idx, slip):
    """Simulate one order. Returns (filled, entry_i, entry_px, exit_i, exit_px,
    reason, mae, mfe, cancel_i) with prices in executable terms and mae/mfe as
    per-unit pnl extremes."""
    n = len(o)
    half = s / 2.0
    j = i0
    entry_px = np.nan
    # ---- entry ----
    while j < n:
        if j >= exp_idx or j >= exit_idx:
            return False, -1, np.nan, -1, np.nan, -1, 0.0, 0.0, j
        eo = o[j] + side * half[j]  # entry-side open
        if otype == 0:
            entry_px = eo + side * slip
            break
        elif otype == 1:  # stop entry: buy when ask >= trig
            ext = (h[j] + half[j]) if side > 0 else (l[j] - half[j])
            if side * (eo - trig) >= 0:
                entry_px = eo + side * slip
                break
            if side * (ext - trig) >= 0:
                entry_px = trig + side * slip
                break
        else:  # limit entry: buy when ask < trig (strict)
            ext = (l[j] + half[j]) if side > 0 else (h[j] - half[j])
            if side * (eo - trig) <= 0:
                entry_px = eo
                break
            if side * (ext - trig) < 0:
                entry_px = trig
                break
        j += 1
    if j >= n:
        return False, -1, np.nan, -1, np.nan, -1, 0.0, 0.0, n

    entry_i = j
    has_tgt = not np.isnan(target)
    mae = 0.0
    mfe = 0.0
    k = j
    while k < n:
        xo = o[k] - side * half[k]  # exit-side prices
        xh = h[k] - side * half[k]
        xl = l[k] - side * half[k]
        adverse = xl if side > 0 else xh
        favour = xh if side > 0 else xl
        first_bar = k == entry_i
        if k >= exit_idx and not first_bar:
            px = xo - side * slip
            pnl = side * (px - entry_px)
            return True, entry_i, entry_px, k, px, 2, min(mae, pnl), max(mfe, pnl), k
        # Gaps at the open (not applicable on a stop/limit entry bar: we filled intrabar).
        if not first_bar or otype == 0:
            if side * (xo - stop) <= 0:
                px = xo - side * slip
                pnl = side * (px - entry_px)
                return True, entry_i, entry_px, k, px, 0, min(mae, pnl), max(mfe, pnl), k
            if has_tgt and side * (xo - target) >= 0 and not first_bar:
                pnl = side * (xo - entry_px)
                return True, entry_i, entry_px, k, xo, 1, min(mae, pnl), max(mfe, pnl), k
        if side * (adverse - stop) <= 0:
            px = stop - side * slip
            pnl = side * (px - entry_px)
            return True, entry_i, entry_px, k, px, 0, min(mae, pnl), max(mfe, pnl), k
        if has_tgt and side * (favour - target) > 0 and (not first_bar or otype == 0):
            pnl = side * (target - entry_px)
            mae = min(mae, side * (adverse - entry_px))
            return True, entry_i, entry_px, k, target, 1, mae, max(mfe, pnl), k
        mae = min(mae, side * (adverse - entry_px))
        mfe = max(mfe, side * (favour - entry_px))
        k += 1
    px = c[n - 1] - side * half[n - 1]
    pnl = side * (px - entry_px)
    return True, entry_i, entry_px, n - 1, px, 3, min(mae, pnl), max(mfe, pnl), n - 1


def _col(sig: pd.DataFrame, name: str, default=np.nan) -> np.ndarray:
    if name in sig.columns:
        return sig[name].to_numpy()
    return np.full(len(sig), default, dtype=object if isinstance(default, str) else float)


def _nights(entry: pd.Timestamp, exit_: pd.Timestamp, tz: str) -> int:
    """Calendar nights between entry and exit, counted at the 17:00 rollover (weekend = 3)."""
    roll = lambda t: (t.tz_convert(tz) - pd.Timedelta(hours=17)).normalize()
    return int((roll(exit_) - roll(entry)).days)


def run_backtest(
    bars: pd.DataFrame,
    signals: pd.DataFrame,
    costs: CostModel = CostModel(),
    symbol: str = "",
) -> pd.DataFrame:
    """Simulate signals on bars; return one row per filled trade."""
    validate_bars(bars)
    sig = signals.copy()
    if "time" not in sig.columns:
        sig = sig.reset_index().rename(columns={sig.index.name or "index": "time"})
    sig = sig.sort_values("time", kind="stable").reset_index(drop=True)

    idx = bars.index
    o, h, l, c = (bars[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    spr = bars["spread"].to_numpy(float) if "spread" in bars.columns else np.full(len(bars), costs.default_spread)
    spr = np.maximum(spr * costs.spread_mult, costs.min_spread)
    n = len(bars)

    def to_idx(ts) -> int:
        if pd.isna(ts):
            return n
        return int(idx.searchsorted(pd.Timestamp(ts), side="left"))

    sides = sig["side"].to_numpy(int)
    orders = _col(sig, "order", "market")
    prices = _col(sig, "price").astype(float)
    stop_p, stop_d = _col(sig, "stop_price").astype(float), _col(sig, "stop_dist").astype(float)
    tgt_p, tgt_d = _col(sig, "target_price").astype(float), _col(sig, "target_dist").astype(float)
    expiry = sig["expiry"].to_numpy() if "expiry" in sig.columns else [pd.NaT] * len(sig)
    exit_t = sig["exit_time"].to_numpy() if "exit_time" in sig.columns else [pd.NaT] * len(sig)

    rows = []
    busy_until = -1
    for r in range(len(sig)):
        i0 = int(idx.searchsorted(pd.Timestamp(sig.at[r, "time"]), side="right"))
        if i0 >= n or i0 <= busy_until:
            continue
        side = int(sides[r])
        if side not in (1, -1):
            raise ValueError(f"signal {r}: side must be +1/-1")
        otype = ORDER_CODES[orders[r] if isinstance(orders[r], str) else "market"]
        if otype == 0:
            intended = c[i0 - 1] + side * spr[i0 - 1] / 2 if i0 > 0 else o[i0] + side * spr[i0] / 2
            trig = np.nan
        else:
            trig = prices[r]
            if np.isnan(trig):
                raise ValueError(f"signal {r}: {orders[r]} order needs a price")
            intended = trig
        stop = stop_p[r] if not np.isnan(stop_p[r]) else intended - side * stop_d[r]
        if np.isnan(stop) or side * (intended - stop) <= 0:
            raise ValueError(f"signal {r}: stop missing or on the wrong side of entry")
        target = tgt_p[r] if not np.isnan(tgt_p[r]) else intended + side * tgt_d[r]
        risk = side * (intended - stop)

        res = _simulate(
            o, h, l, c, spr, i0, side, otype, trig if otype else 0.0,
            to_idx(expiry[r]), stop, target, to_idx(exit_t[r]), costs.slippage,
        )
        filled, ei, epx, xi, xpx, reason, mae, mfe, end_i = res
        busy_until = end_i
        if not filled:
            continue
        comm = costs.commission_frac * (epx + xpx)
        if costs.financing_annual:
            comm += costs.financing_annual / 360.0 * epx * _nights(idx[ei], idx[xi], costs.rollover_tz)
        pnl = side * (xpx - epx) - comm
        rows.append(
            dict(
                symbol=symbol,
                signal_time=sig.at[r, "time"],
                side=side,
                order=orders[r] if isinstance(orders[r], str) else "market",
                entry_time=idx[ei],
                entry_price=epx,
                stop_price=stop,
                target_price=target,
                exit_time=idx[xi],
                exit_price=xpx,
                exit_reason=EXIT_REASONS[reason],
                risk=risk,
                pnl=pnl,
                R=pnl / risk,
                mae_R=(mae - comm) / risk,
                mfe_R=mfe / risk,
                bars_held=xi - ei + 1,
            )
        )
    cols = ["symbol", "signal_time", "side", "order", "entry_time", "entry_price", "stop_price",
            "target_price", "exit_time", "exit_price", "exit_reason", "risk", "pnl", "R", "mae_R",
            "mfe_R", "bars_held"]
    return pd.DataFrame(rows, columns=cols)


def summarize(trades: pd.DataFrame) -> dict:
    """Per-trade statistics in R units."""
    r = trades["R"].to_numpy(float)
    if len(r) == 0:
        return {"n": 0}
    wins, losses = r[r > 0], r[r <= 0]
    sd = r.std(ddof=1) if len(r) > 1 else np.nan
    return {
        "n": len(r),
        "win_rate": len(wins) / len(r),
        "avg_R": r.mean(),
        "total_R": r.sum(),
        "avg_win_R": wins.mean() if len(wins) else 0.0,
        "avg_loss_R": losses.mean() if len(losses) else 0.0,
        "profit_factor": wins.sum() / -losses.sum() if losses.sum() < 0 else np.inf,
        "t_stat": r.mean() / sd * np.sqrt(len(r)) if sd and sd > 0 else np.nan,
        "worst_mae_R": trades["mae_R"].min(),
    }
