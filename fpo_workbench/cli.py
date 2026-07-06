"""fpo-workbench CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fpo_workbench.doctor import diagnose_receipt, resolve_receipt
from fpo_workbench.plan import build_plan, load_plan_file
from fpo_workbench.report import write_report
from fpo_workbench.run_module import execute_run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fpo-workbench",
        description="Plan, ingest, doctor, and report on FPO++ training runs.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    plan_p = sub.add_parser("plan", help="Build hyperparam manifest for a task")
    plan_p.add_argument("--task", required=True, help="Gym task id e.g. Isaac-Velocity-Flat-G1-v0")
    plan_p.add_argument("--mock", action="store_true", help="Mark plan as mock/demo")
    plan_p.add_argument("--json", action="store_true", dest="as_json")
    plan_p.set_defaults(handler=_cmd_plan)

    run_p = sub.add_parser("run", help="Ingest a log directory into receipt bundle")
    run_p.add_argument("--input", type=Path, required=True, help="Training log dir")
    run_p.add_argument("--out", type=Path, default=Path("out"), help="Output root")
    run_p.add_argument("--plan", type=Path, default=None, help="Optional plan JSON/YAML")
    run_p.add_argument("--json", action="store_true", dest="as_json")
    run_p.set_defaults(handler=_cmd_run)

    doc_p = sub.add_parser("doctor", help="Diagnose a receipt bundle")
    doc_p.add_argument("receipt", help="Receipt dir or run id under --out")
    doc_p.add_argument("--out", type=Path, default=Path("out"))
    doc_p.add_argument("--json", action="store_true", dest="as_json")
    doc_p.set_defaults(handler=_cmd_doctor)

    rep_p = sub.add_parser("report", help="Write Markdown report from doctor output")
    rep_p.add_argument("receipt", help="Receipt dir or run id")
    rep_p.add_argument("--out", type=Path, default=Path("out"))
    rep_p.add_argument("--format", choices=["md"], default="md")
    rep_p.add_argument("--output", type=Path, default=None)
    rep_p.set_defaults(handler=_cmd_report)

    demo_p = sub.add_parser("demo", help="Run bundled 60s mock demo (cliff + healthy)")
    demo_p.add_argument("--out", type=Path, default=Path("out/demo"))
    demo_p.set_defaults(handler=_cmd_demo)

    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _cmd_plan(args: argparse.Namespace) -> int:
    plan = build_plan(task_id=args.task, mock=args.mock)
    if args.as_json:
        print(json.dumps(plan, indent=2))
    else:
        print(f"Task: {plan['task_id']}")
        print(f"Baseline target: {plan['paper_target']}")
        if plan["risks"]:
            print("Risks:")
            for r in plan["risks"]:
                print(f"  - {r}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    plan = load_plan_file(args.plan) if args.plan else None
    result = execute_run(args.input, args.out, plan=plan)
    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"run_id: {result['run_id']}")
        print(f"receipt: {result['receipt_dir']}")
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    rdir = resolve_receipt(args.receipt, args.out)
    result = diagnose_receipt(rdir)
    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"overall: {result['overall_status']}")
        print(f"baseline: {result['baseline_grade']['message']}")
        for sig in result["signals"]:
            print(f"  [{sig['status']}] {sig['signal']}: {sig['message']}")
    return 2 if result["overall_status"] == "unhealthy" else 0


def _cmd_report(args: argparse.Namespace) -> int:
    rdir = resolve_receipt(args.receipt, args.out)
    if not (rdir / "doctor.json").exists():
        diagnose_receipt(rdir)
    path = write_report(rdir, args.output)
    print(path)
    return 0


def _cmd_demo(args: argparse.Namespace) -> int:
    examples = Path(__file__).resolve().parent.parent / "examples"
    for name in ("g1-cliff-synthetic", "g1-healthy-synthetic"):
        inp = examples / name
        run_result = execute_run(inp, args.out, label=name)
        rdir = Path(run_result["receipt_dir"])
        doc = diagnose_receipt(rdir)
        write_report(rdir)
        print(f"{name}: {doc['overall_status']} → {rdir}")
    print(f"\nDemo complete. Open site/data/ or run: fpo-workbench report <run_id> --out {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
