"""Tests for run ingestion."""

from pathlib import Path

from fpo_workbench.run_module import execute_run

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_run_cliff_synthetic(tmp_path):
    result = execute_run(EXAMPLES / "g1-cliff-synthetic", tmp_path, label="cliff-test")
    rdir = Path(result["receipt_dir"])
    assert (rdir / "manifest.json").exists()
    assert (rdir / "ingested.json").exists()
    assert result["summary"]["reward_series_length"] == 5000


def test_run_healthy_synthetic(tmp_path):
    result = execute_run(EXAMPLES / "g1-healthy-synthetic", tmp_path, label="healthy-test")
    assert result["summary"]["experiment_name"] == "g1_flat_flow"
