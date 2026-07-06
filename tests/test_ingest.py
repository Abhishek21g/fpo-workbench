"""Tests for ingest."""

from pathlib import Path

from fpo_workbench.ingest import ingest_log_dir

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_ingest_jsonl():
    data = ingest_log_dir(EXAMPLES / "g1-cliff-synthetic")
    assert data["source"] == "metrics.jsonl"
    assert len(data["series"]["reward"]) == 5000
    assert data["experiment_name"] == "g1_flat_flow"


def test_ingest_checkpoints():
    data = ingest_log_dir(EXAMPLES / "g1-healthy-synthetic")
    assert 2000 in data["checkpoints"]
