import numpy as np
import pandas as pd
import pytest

from pfbot.features.amd_maze import fit_amd, segment_direction


def _bars(path, noise=0.05, seed=0):
    rng = np.random.default_rng(seed)
    close = np.asarray(path, dtype=float) + rng.normal(0, noise, len(path))
    return pd.DataFrame({"high": close + 0.5, "low": close - 0.5, "close": close})


def _path(manip_slope, dist_slope, warm=30, a=25, m=15, d=25):
    flat = np.full(warm + a, 100.0)
    man = flat[-1] + manip_slope * np.arange(1, m + 1)
    dis = man[-1] + dist_slope * np.arange(1, d + 1)
    return np.concatenate([flat, man, dis])


@pytest.mark.parametrize("ms,ds,exp", [(-0.5, 0.5, ("D", "U")), (0.5, -0.5, ("U", "D")),
                                       (0.5, 0.0, ("U", "F"))])
def test_recovers_scenario_and_meeting_point(ms, ds, exp):
    sc = fit_amd(_bars(_path(ms, ds)), window=65)
    best = sc[0]
    assert (best.manip, best.dist) == exp
    assert best.consistent
    if exp[0] != "F":  # with a flat M phase the A/M border is not identifiable
        assert abs(best.t1 - 25) <= 4
    assert abs(best.t2 - 40) <= 4
    assert len(sc) == 9
    assert all(a.cost <= b.cost for a, b in zip(sc, sc[1:]))


def test_flat_then_move_is_ambiguous():
    # Flat then down: M(F)->D(D) and M(D)->D(D) both describe it; the model may
    # split the single down move. Only the last phase is identifiable.
    best = fit_amd(_bars(_path(0.0, -0.5)), window=65)[0]
    assert best.dist == "D"


def test_random_walk_always_ranks_all_nine():
    rng = np.random.default_rng(1)
    sc = fit_amd(_bars(100 + np.cumsum(rng.normal(0, 1, 300)), noise=0), window=60)
    assert len(sc) == 9 and all(np.isfinite(s.cost) for s in sc)


def test_direction_threshold():
    assert segment_direction(0.1, 0.05) == "U"
    assert segment_direction(-0.1, 0.05) == "D"
    assert segment_direction(0.01, 0.05) == "F"


def test_window_too_short():
    with pytest.raises(ValueError):
        fit_amd(_bars(_path(0.5, 0.5)), window=10)
