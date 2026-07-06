"""Doctor signal: observation normalizer drift."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class SignalResult:
    signal: str
    status: str
    message: str
    details: dict


def detect_obs_norm_drift(
    max_std_series: Sequence[float],
    *,
    drift_ratio: float = 3.0,
    window: int = 50,
) -> SignalResult:
    if len(max_std_series) < window + 1:
        return SignalResult(
            signal="obs_norm_drift",
            status="warn",
            message="Insufficient obs norm metrics",
            details={"length": len(max_std_series)},
        )

    early = max_std_series[:window]
    early_mean = sum(early) / len(early)
    if early_mean <= 0:
        return SignalResult(
            signal="obs_norm_drift",
            status="warn",
            message="Early obs norm std near zero",
            details={},
        )

    for i, value in enumerate(max_std_series[window:], start=window):
        if value > early_mean * drift_ratio or value < early_mean / drift_ratio:
            return SignalResult(
                signal="obs_norm_drift",
                status="fail",
                message=(
                    f"Obs norm drift at iter {i}: max_std {value:.4f} vs early mean {early_mean:.4f}"
                ),
                details={
                    "iteration": i,
                    "max_std": value,
                    "early_mean": early_mean,
                    "drift_ratio": value / early_mean,
                },
            )

    return SignalResult(
        signal="obs_norm_drift",
        status="pass",
        message="Observation normalizer std stable",
        details={"early_mean": early_mean},
    )
