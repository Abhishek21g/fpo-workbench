"""Tests for report generation."""

from pathlib import Path

from fpo_workbench.doctor import diagnose_receipt
from fpo_workbench.report import write_report
from fpo_workbench.run_module import execute_run

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_report_md(tmp_path):
    run = execute_run(EXAMPLES / "g1-healthy-synthetic", tmp_path, label="r")
    rdir = Path(run["receipt_dir"])
    diagnose_receipt(rdir)
    path = write_report(rdir)
    text = path.read_text()
    assert "FPO++ Training Report" in text
    assert "healthy" in text.lower() or "Overall" in text
