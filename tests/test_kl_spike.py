"""Tests for KL spike signal."""

from fpo_workbench.signals.kl_spike import detect_kl_spike


def test_kl_pass():
    r = detect_kl_spike([1e-5] * 200)
    assert r.status == "pass"


def test_kl_fail():
    series = [1e-5] * 100 + [1e-2] * 20
    r = detect_kl_spike(series, spike_multiplier=50.0, window=5)
    assert r.status == "fail"


def test_kl_missing():
    r = detect_kl_spike([])
    assert r.status == "warn"
