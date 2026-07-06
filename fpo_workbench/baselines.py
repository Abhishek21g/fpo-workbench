"""Paper baselines from amazon-far/fpo-control isaaclab_experiments README."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class TaskBaseline:
    task_id: str
    experiment_name: str
    max_iterations: int
    target_return: float
    num_envs: int = 4096


LOCOMOTION_BASELINES: dict[str, TaskBaseline] = {
    "Isaac-Velocity-Flat-Unitree-Go2-v0": TaskBaseline(
        task_id="Isaac-Velocity-Flat-Unitree-Go2-v0",
        experiment_name="unitree_go2_flat_flow",
        max_iterations=1500,
        target_return=40.0,
    ),
    "Isaac-Velocity-Flat-Spot-v0": TaskBaseline(
        task_id="Isaac-Velocity-Flat-Spot-v0",
        experiment_name="spot_flat_flow",
        max_iterations=1500,
        target_return=315.0,
    ),
    "Isaac-Velocity-Flat-H1-v0": TaskBaseline(
        task_id="Isaac-Velocity-Flat-H1-v0",
        experiment_name="h1_flat_flow",
        max_iterations=2000,
        target_return=38.0,
    ),
    "Isaac-Velocity-Flat-G1-v0": TaskBaseline(
        task_id="Isaac-Velocity-Flat-G1-v0",
        experiment_name="g1_flat_flow",
        max_iterations=2000,
        target_return=37.0,
    ),
}

# Default runner hyperparams mirrored from fpo-control task_cfgs + rl_cfg defaults.
TASK_PLAN_TEMPLATES: dict[str, dict] = {
    "Isaac-Velocity-Flat-G1-v0": {
        "task_id": "Isaac-Velocity-Flat-G1-v0",
        "experiment_name": "g1_flat_flow",
        "max_iterations": 2000,
        "num_envs": 4096,
        "num_steps_per_env": 24,
        "policy": {
            "sampling_steps": 64,
            "actor_hidden_dims": [256, 256, 256],
            "critic_hidden_dims": [768, 768, 768],
            "cfm_loss_reduction": "sqrt",
        },
        "algorithm": {
            "learning_rate": 1e-4,
            "n_samples_per_action": 32,
            "num_learning_epochs": 32,
            "ema_decay": 0.95,
            "ema_warmup_steps": 500,
            "clip_param": 0.05,
            "trust_region_mode": "aspo",
            "normalize_advantage": True,
            "schedule": "fixed",
            "cfm_loss_clamp": 20.0,
            "cfm_diff_clamp_max": 10.0,
        },
        "flow_eval_modes": ["zero", "random"],
    },
    "Isaac-Velocity-Flat-H1-v0": {
        "task_id": "Isaac-Velocity-Flat-H1-v0",
        "experiment_name": "h1_flat_flow",
        "max_iterations": 2000,
        "num_envs": 4096,
        "algorithm": {"n_samples_per_action": 32, "num_learning_epochs": 32, "ema_decay": 0.95},
        "flow_eval_modes": ["zero", "random"],
    },
    "Isaac-Velocity-Flat-Unitree-Go2-v0": {
        "task_id": "Isaac-Velocity-Flat-Unitree-Go2-v0",
        "experiment_name": "unitree_go2_flat_flow",
        "max_iterations": 1500,
        "num_envs": 4096,
        "algorithm": {"n_samples_per_action": 16, "num_learning_epochs": 16, "ema_decay": 0.95},
        "flow_eval_modes": ["zero", "random"],
    },
    "Isaac-Velocity-Flat-Spot-v0": {
        "task_id": "Isaac-Velocity-Flat-Spot-v0",
        "experiment_name": "spot_flat_flow",
        "max_iterations": 1500,
        "num_envs": 4096,
        "algorithm": {"n_samples_per_action": 32, "num_learning_epochs": 32, "ema_decay": 0.95},
        "flow_eval_modes": ["zero", "random"],
    },
}


def baseline_for_task(task_id: str) -> TaskBaseline | None:
    return LOCOMOTION_BASELINES.get(task_id)


def baseline_for_experiment(experiment_name: str | None) -> TaskBaseline | None:
    if not experiment_name:
        return None
    for baseline in LOCOMOTION_BASELINES.values():
        if baseline.experiment_name == experiment_name:
            return baseline
    return None


def baseline_as_dict(task_id: str) -> dict | None:
    baseline = baseline_for_task(task_id)
    return asdict(baseline) if baseline else None
