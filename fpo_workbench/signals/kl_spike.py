"""Doctor signal: KL divergence spikes (adaptive schedule runs)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class SignalResult:
    signal: str
    status: str
    message: str
    details: dict


def detect_kl_spike(
    kl_series: Sequence[float],
    *,
    desired_kl: float = 1e-4,
    spike_multiplier: float = 50.0,
    window: int = 10,
) -> SignalResult:
    if not kl_series:
        return SignalResult(
            signal="kl_spike",
            status="warn",
            message="No KL metrics in log (schedule=fixed runs omit this)",
            details={},
        )

    threshold = desired_kl * spike_multiplier
    max_kl = max(kl_series)
    max_iter = kl_series.index(max_kl)

    # Sustained spike: window mean exceeds threshold
    for start in range(0, len(kl_series) - window + 1):
        mean_kl = sum(kl_series[start : start + window]) / window
        if mean_kl > threshold:
            return SignalResult(
                signal="kl_spike",
                status="fail",
                message=(
                    f"KL spike: window mean {mean_kl:.2e} > {threshold:.2e} at iter {start}"
                ),
                details={
                    "max_kl": max_kl,
                    "max_iteration": max_iter,
                    "spike_iteration": start,
                    "threshold": threshold,
                },
            )

    if max_kl > threshold:
        return SignalResult(
            signal="kl_spike",
            status="warn",
            message=f"Transient KL peak {max_kl:.2e} at iter {max_iter}",
            details={"max_kl": max_kl, "max_iteration": max_iter},
        )

    return SignalResult(
        signal="kl_spike",
        status="pass",
        message=f"KL stable (max {max_kl:.2e})",
        details={"max_kl": max_kl},
    )
