"""Doctor signal: advantage normalization blow-up proxy via surrogate loss spikes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class SignalResult:
    signal: str
    status: str
    message: str
    details: dict


def detect_surrogate_spike(
    surrogate_series: Sequence[float],
    *,
    median_window: int = 100,
    spike_multiplier: float = 5.0,
) -> SignalResult:
    if len(surrogate_series) < median_window + 1:
        return SignalResult(
            signal="advantage_norm_proxy",
            status="warn",
            message="Insufficient surrogate loss history",
            details={"length": len(surrogate_series)},
        )

    baseline = sorted(surrogate_series[:median_window])
    median = baseline[len(baseline) // 2]
    threshold = max(abs(median) * spike_multiplier, 0.05)

    for i, value in enumerate(surrogate_series[median_window:], start=median_window):
        if abs(value) > threshold:
            return SignalResult(
                signal="advantage_norm_proxy",
                status="fail",
                message=(
                    f"Surrogate loss spike {value:.4f} at iter {i} "
                    f"(baseline median {median:.4f})"
                ),
                details={
                    "iteration": i,
                    "value": value,
                    "baseline_median": median,
                    "threshold": threshold,
                },
            )

    return SignalResult(
        signal="advantage_norm_proxy",
        status="pass",
        message="Surrogate loss stable after warmup window",
        details={"baseline_median": median},
    )
