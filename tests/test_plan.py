"""Tests for plan command."""

from fpo_workbench.plan import build_plan


def test_plan_g1_mock():
    plan = build_plan(task_id="Isaac-Velocity-Flat-G1-v0", mock=True)
    assert plan["task_id"] == "Isaac-Velocity-Flat-G1-v0"
    assert plan["mock"] is True
    assert plan["paper_target"]["target_return"] == 37.0


def test_plan_long_run_risk():
    plan = build_plan(
        task_id="Isaac-Velocity-Flat-G1-v0",
        overrides={"max_iterations": 5000},
    )
    assert any("cliff" in r.lower() for r in plan["risks"])
