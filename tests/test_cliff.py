"""Tests for cliff signal."""

from fpo_workbench.signals.cliff import detect_cliff


def test_cliff_pass():
    rewards = [30.0] * 500 + [35.0] * 500
    r = detect_cliff(rewards, min_plateau_iters=50, window=25)
    assert r.status == "pass"


def test_cliff_fail():
    rewards = [30.0] * 2000 + [35.0] * 2000 + [10.0] * 1000
    r = detect_cliff(rewards, min_plateau_iters=100, window=50)
    assert r.status == "fail"


def test_cliff_insufficient():
    r = detect_cliff([1.0, 2.0])
    assert r.status == "warn"
