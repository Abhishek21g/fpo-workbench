"""Tests for surrogate spike proxy."""

from fpo_workbench.signals.advantage_norm import detect_surrogate_spike


def test_surrogate_pass():
    r = detect_surrogate_spike([0.02] * 300, median_window=50)
    assert r.status == "pass"


def test_surrogate_fail():
    series = [0.02] * 150 + [0.5]
    r = detect_surrogate_spike(series, median_window=100)
    assert r.status == "fail"
