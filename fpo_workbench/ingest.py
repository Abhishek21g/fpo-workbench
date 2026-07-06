"""Ingest training logs from metrics.jsonl, agent.yaml, or tensorboard."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml


METRIC_KEYS = {
    "reward": "Train/mean_reward",
    "kl": "Metrics/kl",
    "surrogate": "Loss/surrogate_loss",
    "obs_norm_max": "Metrics/obs_norm_max_std",
}


def load_agent_yaml(log_dir: Path) -> dict[str, Any]:
    path = log_dir / "params" / "agent.yaml"
    if not path.exists():
        return {}
    with path.open() as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def load_metrics_jsonl(log_dir: Path) -> list[dict[str, Any]]:
    path = log_dir / "metrics.jsonl"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _series_from_jsonl(rows: list[dict], key: str) -> list[float]:
    if not rows:
        return []
    max_iter = max(int(r.get("iteration", 0)) for r in rows)
    series = [0.0] * (max_iter + 1)
    for row in rows:
        it = int(row.get("iteration", 0))
        if key in row and 0 <= it < len(series):
            series[it] = float(row[key])
    return series


def _series_from_tensorboard(log_dir: Path, tag: str) -> list[float]:
    try:
        from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    except ImportError:
        return []

    if not list(log_dir.glob("events.out.tfevents.*")):
        return []

    acc = EventAccumulator(str(log_dir), size_guidance={"scalars": 0})
    acc.Reload()
    if tag not in acc.Tags().get("scalars", []):
        return []

    events = acc.Scalars(tag)
    if not events:
        return []
    max_step = max(e.step for e in events)
    series = [0.0] * (max_step + 1)
    for e in events:
        if 0 <= e.step < len(series):
            series[e.step] = e.value
    return series


def ingest_log_dir(log_dir: Path) -> dict[str, Any]:
    log_dir = log_dir.expanduser().resolve()
    agent = load_agent_yaml(log_dir)
    rows = load_metrics_jsonl(log_dir)

    def get_series(short: str, tag: str) -> list[float]:
        if rows:
            return _series_from_jsonl(rows, tag)
        return _series_from_tensorboard(log_dir, tag)

    checkpoints = sorted(
        int(m.group(1))
        for p in log_dir.glob("model_*.pt")
        if (m := re.match(r"model_(\d+)\.pt", p.name))
    )

    reward_series = get_series("reward", METRIC_KEYS["reward"])
    return {
        "log_dir": str(log_dir),
        "source": "metrics.jsonl" if rows else ("tensorboard" if reward_series else "agent_only"),
        "agent": agent,
        "experiment_name": agent.get("experiment_name"),
        "task_id": agent.get("task_id"),
        "max_iterations": agent.get("max_iterations"),
        "checkpoints": checkpoints,
        "series": {
            "reward": reward_series,
            "kl": get_series("kl", METRIC_KEYS["kl"]),
            "surrogate": get_series("surrogate", METRIC_KEYS["surrogate"]),
            "obs_norm_max": get_series("obs_norm_max", METRIC_KEYS["obs_norm_max"]),
        },
        "metrics_rows": len(rows),
    }
