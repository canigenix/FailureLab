import json
from pathlib import Path

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.failure_signature import (
    StressFailureSignal,
    build_failure_signature,
)


def run_profile_signature(
    profile: EvaluationProfile,
    *,
    input_path: str | Path | None = None,
    base_path: Path | None = None,
    affected_threshold: float = 0.10,
    systemic_fraction: float = 0.50,
    instability_threshold: float = 0.20,
) -> EvaluationStepResult:
    """Execute the signature step for an evaluation profile."""

    if not profile.run_signature:
        raise ValueError(
            "Signature analysis is not enabled."
        )

    source = (
        Path(input_path)
        if input_path is not None
        else None
    )

    if source is None:
        raise ValueError(
            "A signature input is required to execute signature analysis."
        )

    if (
        base_path is not None
        and not source.is_absolute()
    ):
        source = base_path / source

    data = json.loads(
        source.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Signature input must be a JSON list."
        )

    signals = [
        StressFailureSignal(
            stress_name=row["stress_name"],
            failure_rate=float(
                row["failure_rate"]
            ),
            prediction_flip_rate=float(
                row["prediction_flip_rate"]
            ),
        )
        for row in data
    ]

    signature = build_failure_signature(
        signals,
        affected_threshold=affected_threshold,
        systemic_fraction=systemic_fraction,
        instability_threshold=instability_threshold,
    )

    message = (
        f"signature {signature.signature_type}; "
        f"dominant stress {signature.dominant_stress}; "
        f"{len(signature.affected_stresses)} affected stresses."
    )

    return EvaluationStepResult(
        analysis="signature",
        passed=True,
        message=message,
    )