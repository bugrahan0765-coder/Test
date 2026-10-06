"""Shared helpers for the daily / multi-day hypotheses B1 (turn of month), B2 (overnight drift)
and B3 (weekly time-series momentum). Specs: research/hypotheses/B{1,2,3}_*.md.

Conventions
* Trading days are New York cash-session dates present in the data: ``session_dates(bars,
  SESSIONS["US100"])`` = local dates with a bar at 09:30 ET. This also works for XAUUSD bars (gold
  trades through NY hours); its own ``SESSIONS`` entry (COMEX pit hours) is deliberately not used.
* "Price at T" is ``price_at(bars, T)``: close of the last M1 bar starting strictly before T. The
  decision bar for an instant T is that last bar; the engine then fills at the open of the next bar,
  i.e. the first bar starting at/after T (``decision_bar``).
* Daily closes are the prices known at 15:55 ET (``DECISION_TIME``), DST aware via ``local_times``.

Ex-ante daily variance forecast: exact alignment (``daily_variance_forecast``)
  * ``daily_realized_vol`` labels a *trading day* by the NY calendar date on which it ENDS: it runs
    from 17:00 NY of the previous calendar day to 17:00 NY of that date (Sunday 17:00 -> Monday 17:00
    is Monday). The 15:55 ET decision on session date d therefore lies inside trading day d, which is
    still open: RV_d is NOT known. Only RV_s for s < d is (trading day s ended at 17:00 NY on s < d).
  * ``har_rv_next_day(rv)`` stamps at origin day t the forecast of RV_{t+1} made from RVs through t
    (coefficients fit on targets <= t). The forecast used on date d is the one stamped at the LAST
    origin t strictly before d (``searchsorted(origin_dates, d, "left") - 1``). It equals
    ``har_rv_forecast(rv).loc[d]`` whenever d is itself in the RV index; the explicit lookup is used
    because d can be absent from the RV index (stub sessions are dropped by ``min_returns``) and
    ``har_rv_forecast`` shifts positionally. The forecast is stale (NaN) if that origin is more than
    ``MAX_FORECAST_AGE_DAYS`` calendar days before d. Days with RV <= 0 are dropped (log-HAR needs > 0).
  * It is a forecast of the 5-minute-grid RV of the full 24h trading day (the close-to-open gap and
    the maintenance break are excluded from RV by construction), in squared log-return units.
    Variances over a holding period of n trading days = n x forecast (spec); multiply the sqrt by
    the entry price for a stop distance in price terms.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfbot.features.volatility import daily_realized_vol, har_rv_next_day
from pfbot.research.harness import SESSIONS, local_times, price_at, session_dates

NY = "America/New_York"
DECISION_TIME = "15:55"
BAR = pd.Timedelta(minutes=1)
MAX_BAR_GAP = pd.Timedelta(minutes=5)
MAX_FORECAST_AGE_DAYS = 5
EARLIEST_EARLY_CLOSE = "12:00"  # earliest US early close is 13:00 ET; guard for the half-day fallback
_EPOCH = pd.Timestamp("1970-01-01", tz="UTC")


def ny_trading_dates(bars: pd.DataFrame) -> pd.DatetimeIndex:
    """NY cash-session dates (tz-naive, sorted) with a bar at 09:30 ET."""
    return session_dates(bars, SESSIONS["US100"]).sort_values()


def daily_closes(bars: pd.DataFrame, dates, hhmm: str = DECISION_TIME) -> np.ndarray:
    """Price known at ``hhmm`` ET on each date (NaN if the latest bar is >30 min stale)."""
    return price_at(bars, local_times(dates, hhmm, NY))


def decision_bar(bars: pd.DataFrame, instants: pd.DatetimeIndex):
    """Decision / fill bars for entry instants T (UTC).

    Returns ``(dec_time, fill_time, ok)``: ``dec_time`` = start of the last M1 bar beginning before T
    (the signal's ``time``; the bar has closed by T), ``fill_time`` = start of the first bar at/after T
    (where an order placed on ``dec_time`` fills). ``ok`` requires a decision bar starting in
    [T-5min, T) that closes by T and a fill bar starting in [T, T+5min). Where not ok the times are
    NaT.
    """
    idx = bars.index
    valid = ~pd.isna(instants)
    te = instants.where(valid, _EPOCH)
    pos = idx.searchsorted(te, side="left") - 1
    has = (pos >= 0) & ((pos + 1) < len(idx)) & valid
    dec = idx[np.clip(pos, 0, None)]
    fill = idx[np.clip(pos + 1, None, len(idx) - 1)]
    ok = has & ((te - dec) <= MAX_BAR_GAP) & ((fill - te) < MAX_BAR_GAP) & ((dec + BAR) <= te)
    return dec.where(ok), fill.where(ok), np.asarray(ok)


def exit_instants(bars: pd.DataFrame, dates, hhmm: str, early_close_fallback: bool = True):
    """Time-exit instants for exits at ``hhmm`` ET on each date; returns ``(exit_time, ok)``.

    ``exit_time`` is the instant itself when a bar starts in [T, T+5min) (the engine exits at the open
    of the first bar >= exit_time). Otherwise, with ``early_close_fallback`` (use for late-afternoon
    exits only), it is the start of the last bar of that date's cash session (last bar starting before
    16:00 ET on that date, and not before 12:00 ET): the half-day rule, which uses only the public
    trading calendar. Otherwise NaT / not ok.
    """
    idx = bars.index
    t = local_times(dates, hhmm, NY)
    valid = ~pd.isna(t)
    tx = t.where(valid, _EPOCH)
    ex = idx.searchsorted(tx, side="left")
    in_range = ex < len(idx)
    bar = idx[np.clip(ex, None, len(idx) - 1)]
    ok = valid & in_range & ((bar - tx) < MAX_BAR_GAP)
    out = t.where(ok)
    if early_close_fallback:
        close = local_times(dates, SESSIONS["US100"].close, NY)
        floor = local_times(dates, EARLIEST_EARLY_CLOSE, NY)
        cvalid = ~pd.isna(close) & ~pd.isna(floor)
        pos = idx.searchsorted(close.where(cvalid, _EPOCH), side="left") - 1
        last = idx[np.clip(pos, 0, None)]
        fb_ok = ~ok & cvalid & (pos >= 0) & (last >= floor.where(cvalid, _EPOCH))
        out = out.where(ok, last.where(fb_ok))
        ok = ok | fb_ok
    return out, np.asarray(ok)


def daily_variance_forecast(bars: pd.DataFrame, dates, rv: pd.Series | None = None) -> np.ndarray:
    """Ex-ante HAR-RV forecast of the daily variance for each session date d, usable at 15:55 ET of d.

    Uses only RVs of trading days strictly before d; see the module docstring for the exact
    alignment. NaN during the HAR warm-up (22 + 100 trading days) or when stale.
    """
    if rv is None:
        rv = daily_realized_vol(bars)
    rv = rv[rv > 0]
    nxt = har_rv_next_day(rv)
    dates = pd.DatetimeIndex(dates)
    origins = nxt.index
    pos = origins.searchsorted(dates, side="left") - 1  # last origin strictly before d
    ok = pos >= 0
    p = np.clip(pos, 0, None)
    vals = nxt.to_numpy()[p]
    age = np.asarray((dates - origins[p]).days)
    return np.where(ok & (age <= MAX_FORECAST_AGE_DAYS), vals, np.nan)
