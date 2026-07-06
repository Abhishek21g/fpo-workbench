"""Doctor signal: reward cliff detection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence


@dataclass(frozen=True)
class SignalResult:
    signal: str
    status: str  # pass | warn | fail
    message: str
    details: dict


def detect_cliff(
    rewards: Sequence[float],
    *,
    min_peak_reward: float = 10.0,
    min_plateau_iters: int = 100,
    drop_threshold: float = 0.30,
    window: int = 50,
) -> SignalResult:
    if len(rewards) < min_plateau_iters + window:
        return SignalResult(
            signal="reward_cliff",
            status="warn",
            message=f"Insufficient reward history ({len(rewards)} iterations)",
            details={"length": len(rewards)},
        )

    peak_reward = max(rewards)
    peak_iteration = rewards.index(peak_reward)

    if peak_reward < min_peak_reward:
        return SignalResult(
            signal="reward_cliff",
            status="warn",
            message=f"Peak reward {peak_reward:.2f} below threshold",
            details={"peak_reward": peak_reward, "peak_iteration": peak_iteration},
        )

    search_start = peak_iteration + min_plateau_iters
    for start in range(search_start, len(rewards) - window + 1):
        window_mean = sum(rewards[start : start + window]) / window
        drop = (peak_reward - window_mean) / max(peak_reward, 1e-8)
        if drop >= drop_threshold:
            return SignalResult(
                signal="reward_cliff",
                status="fail",
                message=(
                    f"Cliff: reward dropped {drop * 100:.1f}% from peak {peak_reward:.2f} "
                    f"(iter {peak_iteration}) to {window_mean:.2f} (iter {start})"
                ),
                details={
                    "peak_reward": peak_reward,
                    "peak_iteration": peak_iteration,
                    "cliff_iteration": start,
                    "drop_fraction": drop,
                },
            )

    return SignalResult(
        signal="reward_cliff",
        status="pass",
        message=f"No cliff; peak {peak_reward:.2f} at iter {peak_iteration}",
        details={"peak_reward": peak_reward, "peak_iteration": peak_iteration},
    )


def signal_to_dict(result: SignalResult) -> dict:
    return asdict(result)
