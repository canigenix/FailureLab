from dataclasses import dataclass
from typing import Literal, Sequence


FailureSignatureType = Literal[
    "localized",
    "systemic",
    "unstable",
    "low-risk",
]


@dataclass(frozen=True)
class StressFailureSignal:
    """Observed failure behavior for one stress."""

    stress_name: str
    failure_rate: float
    prediction_flip_rate: float


@dataclass(frozen=True)
class FailureSignature:
    """Compact fingerprint describing how a model fails."""

    dominant_stress: str
    dominant_failure_rate: float
    mean_failure_rate: float
    mean_flip_rate: float
    affected_stresses: tuple[str, ...]
    signature_type: FailureSignatureType


def classify_failure_signature(
    signals: Sequence[StressFailureSignal],
    *,
    affected_threshold: float = 0.10,
    systemic_fraction: float = 0.50,
    instability_threshold: float = 0.20,
) -> FailureSignatureType:
    """Classify the overall failure pattern across stresses."""

    if not signals:
        raise ValueError(
            "At least one stress failure signal is required."
        )

    affected_count = sum(
        signal.failure_rate >= affected_threshold
        for signal in signals
    )

    affected_fraction = affected_count / len(signals)

    mean_failure_rate = sum(
        signal.failure_rate
        for signal in signals
    ) / len(signals)

    mean_flip_rate = sum(
        signal.prediction_flip_rate
        for signal in signals
    ) / len(signals)

    if mean_flip_rate >= instability_threshold:
        return "unstable"

    if affected_fraction >= systemic_fraction:
        return "systemic"

    if affected_count > 0:
        return "localized"

    if mean_failure_rate < affected_threshold:
        return "low-risk"

    return "localized"


def build_failure_signature(
    signals: Sequence[StressFailureSignal],
    *,
    affected_threshold: float = 0.10,
    systemic_fraction: float = 0.50,
    instability_threshold: float = 0.20,
) -> FailureSignature:
    """Build a compact failure fingerprint from stress-level signals."""

    if not signals:
        raise ValueError(
            "At least one stress failure signal is required."
        )

    if affected_threshold < 0:
        raise ValueError(
            "affected_threshold must be greater than or equal to 0."
        )

    if not 0 <= systemic_fraction <= 1:
        raise ValueError(
            "systemic_fraction must be between 0 and 1."
        )

    if instability_threshold < 0:
        raise ValueError(
            "instability_threshold must be greater than or equal to 0."
        )

    dominant = max(
        signals,
        key=lambda signal: signal.failure_rate,
    )

    mean_failure_rate = sum(
        signal.failure_rate
        for signal in signals
    ) / len(signals)

    mean_flip_rate = sum(
        signal.prediction_flip_rate
        for signal in signals
    ) / len(signals)

    affected_stresses = tuple(
        signal.stress_name
        for signal in signals
        if signal.failure_rate >= affected_threshold
    )

    return FailureSignature(
        dominant_stress=dominant.stress_name,
        dominant_failure_rate=dominant.failure_rate,
        mean_failure_rate=mean_failure_rate,
        mean_flip_rate=mean_flip_rate,
        affected_stresses=affected_stresses,
        signature_type=classify_failure_signature(
            signals,
            affected_threshold=affected_threshold,
            systemic_fraction=systemic_fraction,
            instability_threshold=instability_threshold,
        ),
    )