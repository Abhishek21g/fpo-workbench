"""Doctor: multi-signal training health diagnosis."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from fpo_workbench.baselines import baseline_for_experiment
from fpo_workbench.signals import (
    detect_cliff,
    detect_kl_spike,
    detect_obs_norm_drift,
    detect_surrogate_spike,
)
from fpo_workbench.store import read_json, receipt_dir, write_json


STATUS_ORDER = {"pass": 0, "warn": 1, "fail": 2}


def diagnose_receipt(receipt_path: Path) -> dict[str, Any]:
    receipt_path = receipt_path.expanduser().resolve()
    if receipt_path.is_dir():
        rdir = receipt_path
    else:
        rdir = receipt_path.parent

    ingested = read_json(rdir / "ingested.json")
    summary = read_json(rdir / "summary.json") if (rdir / "summary.json").exists() else {}

    series = ingested.get("series", {})
    rewards = series.get("reward", [])
    kl = series.get("kl", [])
    surrogate = series.get("surrogate", [])
    obs_max = series.get("obs_norm_max", [])

    signals = [
        detect_cliff(rewards),
        detect_kl_spike(kl),
        detect_surrogate_spike(surrogate),
        detect_obs_norm_drift(obs_max),
    ]

    baseline = baseline_for_experiment(ingested.get("experiment_name"))
    baseline_grade = _grade_baseline(rewards, baseline)

    overall = _overall_status([s.status for s in signals] + [baseline_grade["status"]])

    result = {
        "run_id": summary.get("run_id", rdir.name),
        "receipt_dir": str(rdir),
        "overall_status": overall,
        "baseline_grade": baseline_grade,
        "signals": [asdict(s) for s in signals],
    }
    write_json(rdir / "doctor.json", result)
    return result


def _grade_baseline(rewards: list[float], baseline) -> dict[str, Any]:
    if not baseline or not rewards:
        return {
            "status": "warn",
            "message": "No baseline or reward series for comparison",
        }

    peak = max(rewards) if rewards else 0.0
    target = baseline.target_return
    ratio = peak / target if target else 0.0

    if ratio >= 0.85:
        status = "pass"
        message = f"Peak {peak:.1f} within 85% of paper target {target:.1f}"
    elif ratio >= 0.60:
        status = "warn"
        message = f"Peak {peak:.1f} below paper target {target:.1f} ({ratio*100:.0f}%)"
    else:
        status = "fail"
        message = f"Peak {peak:.1f} far below paper target {target:.1f}"

    return {
        "status": status,
        "message": message,
        "peak_reward": peak,
        "target_return": target,
        "ratio": ratio,
    }


def _overall_status(statuses: list[str]) -> str:
    worst = max(statuses, key=lambda s: STATUS_ORDER.get(s, 1))
    if worst == "fail":
        return "unhealthy"
    if worst == "warn":
        return "degraded"
    return "healthy"


def resolve_receipt(path: str | Path, out_root: Path | None = None) -> Path:
    path = Path(path).expanduser()
    if path.is_dir() and (path / "ingested.json").exists():
        return path
    if path.is_dir() and out_root and (out_root / "receipts" / path.name).exists():
        return out_root / "receipts" / path.name
    if out_root:
        candidate = receipt_dir(out_root, path.name)
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No receipt at {path}")
