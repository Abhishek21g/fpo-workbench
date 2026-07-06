"""Run ingestion: log dir → receipt bundle."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fpo_workbench.baselines import baseline_for_experiment
from fpo_workbench.ingest import ingest_log_dir
from fpo_workbench.plan import build_plan
from fpo_workbench.store import make_run_id, receipt_dir, write_json


def execute_run(
    input_path: Path,
    out_root: Path,
    *,
    plan: dict[str, Any] | None = None,
    label: str | None = None,
) -> dict[str, Any]:
    input_path = input_path.expanduser().resolve()
    ingested = ingest_log_dir(input_path)

    experiment = ingested.get("experiment_name")
    baseline = baseline_for_experiment(experiment)

    if plan is None:
        task_id = ingested.get("task_id") or (
            baseline.task_id if baseline else "Isaac-Velocity-Flat-G1-v0"
        )
        plan = build_plan(task_id=task_id, mock=input_path.name.endswith("-synthetic"))

    run_id = make_run_id(label or input_path.name)
    rdir = receipt_dir(out_root, run_id)

    summary = {
        "run_id": run_id,
        "input_log_dir": str(input_path),
        "experiment_name": experiment,
        "baseline": {
            "task_id": baseline.task_id,
            "target_return": baseline.target_return,
            "max_iterations": baseline.max_iterations,
        }
        if baseline
        else None,
        "checkpoints": ingested.get("checkpoints", []),
        "metrics_source": ingested.get("source"),
        "reward_series_length": len(ingested.get("series", {}).get("reward", [])),
    }

    manifest = {
        "run_id": run_id,
        "workbench_version": "0.1.0",
        "plan": plan,
        "ingested": {
            "log_dir": ingested["log_dir"],
            "experiment_name": experiment,
            "max_iterations": ingested.get("max_iterations"),
            "checkpoints": ingested.get("checkpoints", []),
        },
    }

    write_json(rdir / "plan.json", plan)
    write_json(rdir / "ingested.json", ingested)
    write_json(rdir / "summary.json", summary)
    write_json(rdir / "manifest.json", manifest)

    return {
        "run_id": run_id,
        "receipt_dir": str(rdir),
        "summary": summary,
        "manifest": manifest,
    }
