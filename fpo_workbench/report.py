"""Markdown report generation."""

from __future__ import annotations

from pathlib import Path

from fpo_workbench.store import read_json


def write_report(receipt_path: Path, output: Path | None = None) -> Path:
    receipt_path = receipt_path.expanduser().resolve()
    rdir = receipt_path if receipt_path.is_dir() else receipt_path.parent

    doctor = read_json(rdir / "doctor.json")
    summary = read_json(rdir / "summary.json")
    plan = read_json(rdir / "plan.json")

    lines = [
        f"# FPO++ Training Report — `{doctor['run_id']}`",
        "",
        f"**Overall:** `{doctor['overall_status']}`",
        "",
        "## Baseline grade",
        f"- {doctor['baseline_grade']['message']}",
        "",
        "## Doctor signals",
    ]

    for sig in doctor.get("signals", []):
        icon = {"pass": "✓", "warn": "!", "fail": "✗"}.get(sig["status"], "?")
        lines.append(f"- [{icon}] **{sig['signal']}** ({sig['status']}): {sig['message']}")

    lines.extend(
        [
            "",
            "## Plan manifest",
            f"- Task: `{plan.get('task_id', '—')}`",
            f"- Experiment: `{summary.get('experiment_name', '—')}`",
            f"- Flow eval modes: `{plan.get('flow_eval_modes', [])}`",
            "",
            "## Artifacts",
            f"- Receipt dir: `{rdir}`",
            f"- Checkpoints: {len(summary.get('checkpoints', []))}",
            f"- Reward series length: {summary.get('reward_series_length', 0)}",
            "",
        ]
    )

    if plan.get("risks"):
        lines.append("## Pre-run risks (from plan)")
        for risk in plan["risks"]:
            lines.append(f"- {risk}")
        lines.append("")

    out = output or (rdir / "report.md")
    out.write_text("\n".join(lines))
    return out
