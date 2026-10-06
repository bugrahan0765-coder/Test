"""Volatility features: daily realized variance, HAR-RV forecast, intraday profile.

PLAN.md section 2.2-B. All functions take canonical bar frames (see
``pfbot.data.schema``) and are strictly free of lookahead: every value stamped at
time t (or trading day d) is computable from data up to and including t (or, for
ex-ante forecasts of day d, from data strictly before day d). Each docstring states
the exact information set.

Conventions
-----------
* Returns are log returns of mid ``close`` prices sampled on a regular grid
  (``freq`` / ``rv_freq``, default 5 minutes). The first return of each trading day
  is measured from that day's first ``open`` to the first sampled close, so the
  inter-session gap (close-to-open jump, weekend gap) is *excluded* from RV.
  A missing grid bin inside a day simply makes the next return span the gap.
* Trading day: for FX/CFDs a day runs from ``day_start_hour`` (17:00) New York to
  17:00 New York the next calendar day and is labelled by the calendar date on which
  it *ends* (e.g. Sunday 17:00 -> Monday 17:00 NY is trading date Monday). Wall-clock
  local time is used, so DST is handled automatically. ``day_start_hour=0`` gives
  plain calendar days in ``session_tz``.
* Trading dates are returned as a tz-naive ``DatetimeIndex`` named ``"date"``.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pfbot.data.schema import PRICE_COLS, resample_bars

__all__ = [
    "trading_date",
    "intraday_returns",
    "daily_realized_vol",
    "har_rv_forecast",
    "har_rv_next_day",
    "intraday_vol_profile",
    "expected_bar_vol",
]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def trading_date(index: pd.DatetimeIndex, session_tz: str = "America/New_York",
                 day_start_hour: int = 17) -> pd.DatetimeIndex:
    """Map UTC timestamps (bar open times) to trading dates (tz-naive, named "date").

    A bar opening at or after ``day_start_hour`` local time belongs to the next
    calendar date's trading day. Pure per-timestamp mapping, no lookahead.
    """
    local = index.tz_convert(session_tz)
    day = local.tz_localize(None).normalize()
    roll = (local.hour >= day_start_hour) if day_start_hour > 0 else np.zeros(len(local), bool)
    out = day + pd.to_timedelta(np.asarray(roll, dtype=np.int64), unit="D")
    return pd.DatetimeIndex(out, name="date")


def intraday_returns(bars: pd.DataFrame, freq: str | None = "5min",
                     session_tz: str = "America/New_York", day_start_hour: int = 17,
                     profile_tz: str | None = None) -> pd.DataFrame:
    """Intraday log returns on a ``freq`` grid with trading date and time-of-day bucket.

    Returns a DataFrame indexed by the (resampled) bar open time with columns
    ``r`` (log return of that bar, close vs previous close of the same trading day, or
    vs the bar's own open for the first bar of the day), ``date`` (trading date) and
    ``bucket`` (minutes since local midnight in ``profile_tz``, default
    ``session_tz``). ``r`` at bar t uses only bars <= t (it is known at t's close).
    ``freq=None`` uses the bars as given.
    """
    b = resample_bars(bars[PRICE_COLS], freq) if freq else bars[PRICE_COLS]
    date = trading_date(b.index, session_tz, day_start_hour)
    logc = np.log(b["close"].to_numpy(dtype=float))
    logo = np.log(b["open"].to_numpy(dtype=float))
    prev = pd.Series(logc).groupby(date.to_numpy()).shift(1).to_numpy()
    prev = np.where(np.isnan(prev), logo, prev)  # first bar of the day: open -> close
    local = b.index.tz_convert(profile_tz or session_tz)
    return pd.DataFrame(
        {"r": logc - prev, "date": date.to_numpy(), "bucket": local.hour * 60 + local.minute},
        index=b.index,
    )


# ---------------------------------------------------------------------------
# daily realized variance
# ---------------------------------------------------------------------------
def daily_realized_vol(bars: pd.DataFrame, session_tz: str = "America/New_York",
                       day_start_hour: int = 17, rv_freq: str | None = "5min",
                       min_returns: int = 10) -> pd.Series:
    """Daily realized *variance*: sum of squared ``rv_freq`` log returns per trading day.

    Indexed by trading date (see module docstring), named ``"rv"``. Days with fewer
    than ``min_returns`` intraday returns (stub/holiday sessions) are dropped.
    Variance (not volatility) units are returned because HAR is specified on RV;
    take ``np.sqrt`` for a daily vol.

    No lookahead: RV of day d uses only bars of day d, so it is known only once day d
    has closed. Anything acting *during* day d must use forecasts (``har_rv_forecast``).
    The value for the last, possibly still-open day is a partial sum.
    """
    ir = intraday_returns(bars, rv_freq, session_tz, day_start_hour)
    g = (ir["r"] ** 2).groupby(ir["date"])
    rv = g.sum()[g.count() >= min_returns]
    rv.index = pd.DatetimeIndex(rv.index, name="date")
    return rv.rename("rv")


# ---------------------------------------------------------------------------
# HAR-RV
# ---------------------------------------------------------------------------
def _har_design(rv: np.ndarray, use_log: bool) -> np.ndarray:
    """HAR regressors at day t: [1, f(RV_t), f(mean RV_{t-4..t}), f(mean RV_{t-21..t})].

    Rows t < 21 are NaN. f = log (log-HAR) or identity. Uses data through t only.
    """
    s = pd.Series(rv)
    comps = [s, s.rolling(5).mean(), s.rolling(22).mean()]
    X = np.column_stack([np.ones(len(rv))] + [c.to_numpy() for c in comps])
    if use_log:
        X[:, 1:] = np.log(X[:, 1:])
    return X


def har_rv_next_day(rv_daily: pd.Series, window: int | None = None, refit_every: int = 20,
                    min_train: int = 100, use_log: bool = True) -> pd.Series:
    """HAR-RV forecast of the *next* trading day's RV, stamped at the origin day t.

    The value at day t is the forecast of RV_{t+1} made after day t closes: it uses
    RVs through t and coefficients fit on pairs (X_s, RV_{s+1}) with s + 1 <= t
    (expanding, or the last ``window`` targets). Coefficients are refit every
    ``refit_every`` days (refit dates are anchored to the start of the series, so
    truncating the series never changes earlier values). The last element is the
    forecast for the next, not-yet-observed day. See ``har_rv_forecast`` for details.
    """
    rv = rv_daily.to_numpy(dtype=float)
    if np.any(rv <= 0) and use_log:
        raise ValueError("log-HAR needs strictly positive RV")
    T = len(rv)
    X = _har_design(rv, use_log)
    y_next = np.full(T, np.nan)  # y_next[s] = f(RV_{s+1})
    y_next[:-1] = np.log(rv[1:]) if use_log else rv[1:]
    out = np.full(T, np.nan)

    first_t = 21 + min_train  # first origin with >= min_train training pairs (s = 21..t-1)
    beta, s2 = None, 0.0
    for t in range(first_t, T):
        if beta is None or (t - first_t) % refit_every == 0:
            lo = 21 if window is None else max(21, t - window)
            Xa, ya = X[lo:t], y_next[lo:t]  # pairs with target index s+1 <= t
            beta, *_ = np.linalg.lstsq(Xa, ya, rcond=None)
            resid = ya - Xa @ beta
            s2 = float(resid @ resid) / max(len(ya) - Xa.shape[1], 1)
        pred = float(X[t] @ beta)
        # log model -> level with lognormal bias correction exp(mu + s^2/2)
        out[t] = np.exp(pred + 0.5 * s2) if use_log else max(pred, 0.0)
    return pd.Series(out, index=rv_daily.index, name="rv_forecast_next")


def har_rv_forecast(rv_daily: pd.Series, window: int | None = None, refit_every: int = 20,
                    min_train: int = 100, use_log: bool = True) -> pd.Series:
    """Walk-forward HAR-RV (Corsi 2009) one-step-ahead forecast of daily RV.

    Model (default ``use_log=True``, log-HAR):
        log RV_{d} = b0 + bD log RV_{d-1} + bW log RV^W_{d-1} + bM log RV^M_{d-1} + e
    with RV^W / RV^M the 5-day / 22-day means of RV ending at d-1 (log of the means,
    as in Corsi's specification applied to logs). Fit by OLS. The level forecast is
    ``exp(fitted + s^2/2)`` (lognormal bias correction, s^2 = in-sample residual
    variance). Logs are used because RV is heavily right-skewed: OLS on levels is
    dominated by a few spikes and can forecast negative variance.
    ``use_log=False`` fits the original level HAR (forecast floored at 0).

    Returns a Series aligned to day d: value = forecast of RV_d, available *before*
    day d opens. It uses RVs through d-1 only, and coefficients estimated only on
    targets strictly before d (expanding window, or the last ``window`` days if
    given), refit every ``refit_every`` days. NaN until 22 + ``min_train`` days of
    history exist. Lags are positional (previous available trading day).
    """
    return har_rv_next_day(rv_daily, window, refit_every, min_train, use_log).shift(1).rename("rv_forecast")


# ---------------------------------------------------------------------------
# intraday profile
# ---------------------------------------------------------------------------
def _profile_from_returns(ir: pd.DataFrame, lookback_days: int, min_count: int) -> pd.DataFrame:
    """Per (trading date, bucket) RMS return over the previous ``lookback_days`` dates."""
    r2 = ir["r"] ** 2
    keys = [ir["date"], ir["bucket"]]
    ssq = r2.groupby(keys).sum().unstack(fill_value=0.0)
    cnt = r2.groupby(keys).count().unstack(fill_value=0)
    # rolling over trading-date rows, then shift so day d sees only days < d
    ssq = ssq.rolling(lookback_days, min_periods=1).sum().shift(1)
    cnt = cnt.rolling(lookback_days, min_periods=1).sum().shift(1)
    prof = np.sqrt(ssq / cnt).where(cnt >= min_count)
    prof.index = pd.DatetimeIndex(prof.index, name="date")
    prof.columns.name = "bucket"
    return prof


def intraday_vol_profile(bars: pd.DataFrame, freq: str = "5min", tz: str = "America/New_York",
                         lookback_days: int = 60, session_tz: str = "America/New_York",
                         day_start_hour: int = 17, min_count: int = 10) -> pd.DataFrame:
    """Rolling time-of-day volatility profile.

    Returns a DataFrame indexed by trading date, one column per time-of-day bucket
    (minutes since midnight local ``tz``, bucket width ``freq``). Entry (d, b) is the
    root-mean-square ``freq`` log return of bucket b over the previous
    ``lookback_days`` trading days, i.e. an estimate of the per-bar std (mean-zero
    returns assumed). NaN where fewer than ``min_count`` observations exist.

    No lookahead: row d uses only trading days strictly before d, so it is known
    before day d opens. Note the RMS pools days with different vol levels (high-vol
    days get more weight); ``expected_bar_vol`` only uses its *shape*.
    """
    ir = intraday_returns(bars, freq, session_tz, day_start_hour, profile_tz=tz)
    return _profile_from_returns(ir, lookback_days, min_count)


def expected_bar_vol(bars: pd.DataFrame, freq: str = "5min", tz: str = "America/New_York",
                     lookback_days: int = 60, session_tz: str = "America/New_York",
                     day_start_hour: int = 17, min_count: int = 10, min_returns: int = 10,
                     har_kwargs: dict | None = None) -> pd.Series:
    """Ex-ante expected std of each ``freq`` bar's log return.

        E[r_{d,b}^2] = RVhat_d * w_{d,b},   w_{d,b} = prof_{d,b}^2 / sum_b' prof_{d,b'}^2

    RVhat_d is the HAR forecast for trading day d (made after the last completed
    trading day before d; RV computed at the same ``freq``); w is the normalized
    intraday variance profile from ``intraday_vol_profile``. Returns a Series indexed
    by the ``freq``-resampled bar open times, named ``"exp_vol"`` (log-return units).

    No lookahead: both factors use only trading days strictly before d, so every value
    for day d is known before day d opens (it does not even use earlier bars of day d).
    """
    ir = intraday_returns(bars, freq, session_tz, day_start_hour, profile_tz=tz)

    # daily RV and HAR next-day forecasts stamped at their origin day
    g = (ir["r"] ** 2).groupby(ir["date"])
    rv = g.sum()[g.count() >= min_returns]
    nxt = har_rv_next_day(rv, **(har_kwargs or {}))
    # forecast for date D = forecast issued at the last RV date strictly before D
    dates = pd.DatetimeIndex(ir["date"].unique())
    pos = np.searchsorted(nxt.index.to_numpy(), dates.to_numpy(), side="left") - 1
    fc_vals = np.where(pos >= 0, nxt.to_numpy()[np.clip(pos, 0, None)], np.nan)
    fc = pd.Series(fc_vals, index=dates)

    prof = _profile_from_returns(ir, lookback_days, min_count)
    var = prof ** 2
    share = var.div(var.sum(axis=1, min_count=1), axis=0)
    share_long = share.stack()  # MultiIndex (date, bucket)
    key = pd.MultiIndex.from_arrays([ir["date"].to_numpy(), ir["bucket"].to_numpy()])
    w = share_long.reindex(key).to_numpy()

    exp_var = fc.reindex(ir["date"]).to_numpy() * w
    return pd.Series(np.sqrt(exp_var), index=ir.index, name="exp_vol")
