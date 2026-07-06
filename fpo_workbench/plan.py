"""Build hyperparam plan manifests."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from fpo_workbench.baselines import TASK_PLAN_TEMPLATES, baseline_as_dict, baseline_for_task


def build_plan(
    *,
    task_id: str,
    mock: bool = False,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if task_id not in TASK_PLAN_TEMPLATES:
        raise ValueError(f"Unknown task_id: {task_id}. Known: {sorted(TASK_PLAN_TEMPLATES)}")

    template = TASK_PLAN_TEMPLATES[task_id].copy()
    if overrides:
        template = _deep_merge(template, overrides)

    baseline = baseline_as_dict(task_id)
    paper = baseline_for_task(task_id)

    risks: list[str] = []
    algo = template.get("algorithm", {})
    max_iters = template.get("max_iterations", 2000)

    if max_iters > 2000 and algo.get("ema_decay", 0.95) == 0.95:
        risks.append(
            "max_iterations > 2000 with ema_decay=0.95 — long-run cliff risk (see fpo-control#4)"
        )
    if algo.get("num_learning_epochs", 16) >= 32 and max_iters > 2000:
        risks.append("32 learning epochs past 2000 iters may overtrain converged policies")
    if algo.get("normalize_advantage", True) and max_iters > 3000:
        risks.append("Advantage normalization can amplify noise near convergence")

    return {
        "version": "0.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mock": mock,
        "task_id": task_id,
        "baseline": baseline,
        "manifest": template,
        "paper_target": asdict(paper) if paper else None,
        "risks": risks,
        "flow_eval_modes": template.get("flow_eval_modes", ["zero", "random"]),
    }


def load_plan_file(path: Path) -> dict[str, Any]:
    with path.open() as f:
        if path.suffix == ".json":
            import json
            data = json.load(f)
        else:
            data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid plan file: {path}")
    return data


def _deep_merge(base: dict, overrides: dict) -> dict:
    out = base.copy()
    for key, value in overrides.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out
