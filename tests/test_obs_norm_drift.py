"""Tests for obs norm drift."""

from fpo_workbench.signals.obs_norm_drift import detect_obs_norm_drift


def test_obs_norm_pass():
    r = detect_obs_norm_drift([1.0 + i * 0.001 for i in range(200)], window=50)
    assert r.status == "pass"


def test_obs_norm_fail():
    series = [1.0] * 60 + [5.0] * 40
    r = detect_obs_norm_drift(series, window=50, drift_ratio=3.0)
    assert r.status == "fail"
