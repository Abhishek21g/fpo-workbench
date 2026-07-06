"""Tests for baselines."""

from fpo_workbench.baselines import baseline_for_task, TASK_PLAN_TEMPLATES


def test_g1_baseline():
    b = baseline_for_task("Isaac-Velocity-Flat-G1-v0")
    assert b.target_return == 37.0
    assert b.max_iterations == 2000


def test_plan_templates_cover_baselines():
    for task_id in (
        "Isaac-Velocity-Flat-G1-v0",
        "Isaac-Velocity-Flat-H1-v0",
        "Isaac-Velocity-Flat-Unitree-Go2-v0",
    ):
        assert task_id in TASK_PLAN_TEMPLATES
