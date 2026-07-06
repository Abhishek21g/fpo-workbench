# FPO++ Training Workbench

[![CI](https://github.com/Abhishek21g/fpo-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/Abhishek21g/fpo-workbench/actions/workflows/ci.yml)

**Plan → run → doctor → report** for [Amazon FAR FPO++](https://github.com/amazon-far/fpo-control) flow-policy RL training.

Validates training health vs paper baselines, detects cliffs/KL spikes/obs-norm drift, and exports checkpoint receipts — **without Isaac Sim or a GPU** for mock mode.

**Live demo:** [enaguthi.com/fpo-workbench/site/](https://enaguthi.com/fpo-workbench/site/)

## 60-second demo

```bash
pip install -e .
fpo-workbench demo --out out/demo
fpo-workbench doctor out/demo/receipts/<cliff-run-id> --json
```

## CLI

```bash
# Hyperparam manifest + pre-run risks
fpo-workbench plan --task Isaac-Velocity-Flat-G1-v0 --mock --json

# Ingest log directory (metrics.jsonl, agent.yaml, or tensorboard)
fpo-workbench run --input examples/g1-cliff-synthetic --out out/

# Multi-signal doctor
fpo-workbench doctor out/receipts/<run-id> --json

# Markdown report
fpo-workbench report out/receipts/<run-id>
```

## Doctor signals

| Signal | Detects |
|--------|---------|
| `reward_cliff` | Post-plateau reward collapse (fpo-control#4 shape) |
| `kl_spike` | Adaptive KL blow-up |
| `advantage_norm_proxy` | Surrogate loss spikes near convergence |
| `obs_norm_drift` | Empirical normalizer std drift |

Plus **paper baseline grade** (Go2, G1, H1, Spot targets from upstream README).

## Artifact trail

```
out/receipts/<run-id>/
  manifest.json
  plan.json
  ingested.json
  summary.json
  doctor.json
  report.md
```

## Bundled examples

- `examples/g1-cliff-synthetic/` — mimics #4 cliff at ~4k iters
- `examples/g1-healthy-synthetic/` — healthy G1 run to ~37 return

## Development

```bash
pip install -e ".[dev]"
pytest -q
```

## Relationship to upstream PRs

This workbench is **independent** of specific fpo-control bugfixes. It solves training observability for any FPO++ run. See `agent/COMPANY_PROBLEM_CANVAS.md` in the amazon-far research workspace.

## License

MIT
