"""Tests for doctor."""

from pathlib import Path

from fpo_workbench.doctor import diagnose_receipt
from fpo_workbench.run_module import execute_run

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_doctor_cliff_unhealthy(tmp_path):
    run = execute_run(EXAMPLES / "g1-cliff-synthetic", tmp_path, label="cliff")
    doc = diagnose_receipt(Path(run["receipt_dir"]))
    assert doc["overall_status"] == "unhealthy"
    assert any(s["signal"] == "reward_cliff" and s["status"] == "fail" for s in doc["signals"])


def test_doctor_healthy(tmp_path):
    run = execute_run(EXAMPLES / "g1-healthy-synthetic", tmp_path, label="healthy")
    doc = diagnose_receipt(Path(run["receipt_dir"]))
    assert doc["overall_status"] == "healthy"
