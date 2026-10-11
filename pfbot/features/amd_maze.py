"""AMD "maze" model: accumulation -> manipulation -> distribution on a 5-SMA.

Idea (maze solving with a bidirectional search front): the explorer leaves the
maze entrance (first bar of the window) and the exit (the CURRENT bar) at the
same time and spreads in every direction; where the two fronts meet, the paths
are joined.

- The path is the 5-period SMA of the close over the last ``window`` bars.
- Three phases: accumulation (A, always sideways), manipulation (M) and
  distribution (D). Each transition A->M and M->D branches three ways:
  up (U), down (D) or sideways (F), giving 3 x 3 = 9 scenarios.
- Forward front: for every possible meeting bar t2, the best split t1 of
  A (flat) + M (direction m) ending at t2 - 1.
- Backward front: from the exit (current bar) back to t2, the D segment with
  direction d.
- Meeting: total = forward[m][t2] + backward[d][t2], minimised over t2.

Each segment is fitted with a least-squares line on the SMA; its direction is
the sign of the slope measured in ATR per bar (|slope| <= ``flat_thr`` is
sideways). The fit is constrained to the required direction: if the free slope
is outside the allowed region it is clamped to the boundary, and the exact
constrained least-squares cost is SSE_free + (slope - clamped)^2 * Var_x.
Cost = sum of squared residuals in ATR units (always finite). A scenario is
``consistent`` when every phase's free slope already has its required
direction.

Identification: when two neighbouring phases share a direction (A flat + M
flat, or M and D both up/down) the split between them is arbitrary and the
model may pick either labelling; the 5-SMA lag rounds corners, so a single
move is often split into M + D of the same direction.

This is a DESCRIPTIVE decomposition: the distribution phase ends at the current
bar, so it labels what already happened. It is not a forecast and has not been
tested (PLAN.md section 3 protocol would apply before any use in trading).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

__all__ = ["DIRS", "Scenario", "fit_amd", "segment_direction"]

DIRS = ("U", "D", "F")  # up, down, flat (sideways)


@dataclass(frozen=True)
class Scenario:
    manip: str          # direction of manipulation phase: U / D / F
    dist: str           # direction of distribution phase: U / D / F
    cost: float         # total constrained SSE in ATR^2
    t1: int             # first bar of manipulation (window-relative index)
    t2: int             # first bar of distribution = meeting point
    slopes: tuple       # (A, M, D) free (unconstrained) slopes in ATR per bar
    consistent: bool    # every free slope has the direction the scenario requires

    @property
    def name(self) -> str:
        return f"A(F)->M({self.manip})->D({self.dist})"


def segment_direction(slope_atr: float, flat_thr: float) -> str:
    if slope_atr > flat_thr:
        return "U"
    if slope_atr < -flat_thr:
        return "D"
    return "F"


class _Prefix:
    """O(1) least-squares line fit on y[i:j] via prefix sums."""

    def __init__(self, y: np.ndarray):
        x = np.arange(len(y), dtype=float)
        z = np.zeros(1)
        self.sx = np.concatenate([z, np.cumsum(x)])
        self.sy = np.concatenate([z, np.cumsum(y)])
        self.sxx = np.concatenate([z, np.cumsum(x * x)])
        self.sxy = np.concatenate([z, np.cumsum(x * y)])
        self.syy = np.concatenate([z, np.cumsum(y * y)])

    def fit(self, i: int, j: int) -> tuple[float, float, float]:
        """Slope, SSE and Var_x (sum of squared x deviations) of y[i:j], j exclusive."""
        n = j - i
        sx = self.sx[j] - self.sx[i]
        sy = self.sy[j] - self.sy[i]
        sxx = self.sxx[j] - self.sxx[i]
        sxy = self.sxy[j] - self.sxy[i]
        syy = self.syy[j] - self.syy[i]
        vx = sxx - sx * sx / n
        cxy = sxy - sx * sy / n
        vy = syy - sy * sy / n
        slope = cxy / vx if vx > 0 else 0.0
        sse = max(vy - slope * cxy, 0.0)
        return slope, sse, vx


def fit_amd(
    bars: pd.DataFrame,
    window: int = 60,
    sma_len: int = 5,
    min_seg: int = 5,
    flat_thr: float = 0.05,
    atr_len: int = 14,
) -> list[Scenario]:
    """Fit the 9 AMD scenarios to the last ``window`` bars (exit = last bar).

    ``bars`` needs high/low/close columns. Returns all 9 scenarios
    sorted by cost (best first).
    """
    if window < 3 * min_seg:
        raise ValueError("window must be >= 3 * min_seg")
    close = bars["close"].astype(float)
    sma = close.rolling(sma_len).mean()
    prev = close.shift(1)
    tr = pd.concat(
        [bars["high"] - bars["low"], (bars["high"] - prev).abs(), (bars["low"] - prev).abs()],
        axis=1,
    ).max(axis=1)
    atr = tr.rolling(atr_len).mean()
    if len(bars) < window + max(sma_len, atr_len):
        raise ValueError("not enough bars for window + warm-up")

    a = float(atr.iloc[-1])
    if not a > 0:
        raise ValueError("ATR is zero")
    y = sma.iloc[-window:].to_numpy() / a  # path in ATR units
    p = _Prefix(y)
    n = window
    inf = np.inf

    lo = {"U": flat_thr, "D": -inf, "F": -flat_thr}
    hi = {"U": inf, "D": -flat_thr, "F": flat_thr}

    def seg(i: int, j: int, want: str) -> float:
        slope, sse, vx = p.fit(i, j)
        clamped = min(max(slope, lo[want]), hi[want])
        return sse + (slope - clamped) ** 2 * vx

    # Forward front: A (flat) from the entrance, then M; best t1 for each t2.
    fwd = {m: np.full(n + 1, inf) for m in DIRS}
    fwd_t1 = {m: np.zeros(n + 1, dtype=int) for m in DIRS}
    costA = np.full(n + 1, inf)
    for t1 in range(min_seg, n - 2 * min_seg + 1):
        costA[t1] = seg(0, t1, "F")
    for t2 in range(2 * min_seg, n - min_seg + 1):
        for m in DIRS:
            best, arg = inf, 0
            for t1 in range(min_seg, t2 - min_seg + 1):
                c = costA[t1] + seg(t1, t2, m)
                if c < best:
                    best, arg = c, t1
            fwd[m][t2], fwd_t1[m][t2] = best, arg

    # Backward front from the exit (current bar), then join where fronts meet.
    out = []
    for m in DIRS:
        for d in DIRS:
            best, bt2 = inf, 0
            for t2 in range(2 * min_seg, n - min_seg + 1):
                c = fwd[m][t2] + seg(t2, n, d)
                if c < best:
                    best, bt2 = c, t2
            t1 = int(fwd_t1[m][bt2])
            slopes = (p.fit(0, t1)[0], p.fit(t1, bt2)[0], p.fit(bt2, n)[0])
            consistent = all(segment_direction(s, flat_thr) == w
                             for s, w in zip(slopes, ("F", m, d)))
            out.append(Scenario(m, d, float(best), t1, int(bt2), slopes, consistent))
    out.sort(key=lambda s: s.cost)
    return out
