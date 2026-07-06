"""CLI integration tests."""

import json
from pathlib import Path

from fpo_workbench.cli import main

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_cli_plan_json(capsys):
    assert main(["plan", "--task", "Isaac-Velocity-Flat-G1-v0", "--mock", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["task_id"] == "Isaac-Velocity-Flat-G1-v0"


def test_cli_demo(tmp_path):
    assert main(["demo", "--out", str(tmp_path)]) == 0
    assert (tmp_path / "receipts").exists()
