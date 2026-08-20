from dataclasses import dataclass

from failurelab.failure_signature import FailureSignature


@dataclass(frozen=True)
class FailureDiagnosis:
    """Structured diagnosis derived from a failure signature."""

    diagnosis: str
    likely_cause: str
    recommended_action: str


def diagnose_failure_signature(
    signature: FailureSignature,
) -> FailureDiagnosis:
    """Translate a failure signature into an actionable diagnosis."""

    if signature.signature_type == "low-risk":
        return FailureDiagnosis(
            diagnosis=(
                "No broad failure pattern was detected across the "
                "evaluated stresses."
            ),
            likely_cause=(
                "Observed failures appear limited and below the "
                "configured affected-stress threshold."
            ),
            recommended_action=(
                "Continue monitoring robustness across future model "
                "versions and stress configurations."
            ),
        )

    if signature.signature_type == "localized":
        return FailureDiagnosis(
            diagnosis=(
                "The model shows a localized robustness weakness "
                f"centered on {signature.dominant_stress}."
            ),
            likely_cause=(
                "The model appears sensitive to a limited subset of "
                "perturbations rather than broadly fragile."
            ),
            recommended_action=(
                f"Prioritize targeted evaluation and augmentation for "
                f"{signature.dominant_stress} and related stresses."
            ),
        )

    if signature.signature_type == "systemic":
        return FailureDiagnosis(
            diagnosis=(
                "The model shows systemic robustness degradation "
                "across multiple stress conditions."
            ),
            likely_cause=(
                "The learned representation may be overly dependent "
                "on brittle visual features that do not remain stable "
                "under perturbation."
            ),
            recommended_action=(
                "Review training diversity, augmentation coverage, "
                "and representation robustness across the affected "
                "stress families."
            ),
        )

    if signature.signature_type == "unstable":
        return FailureDiagnosis(
            diagnosis=(
                "The model shows prediction instability across the "
                "evaluated stress conditions."
            ),
            likely_cause=(
                "Predictions are changing frequently under perturbation, "
                "suggesting weak decision boundaries or unstable "
                "confidence behavior."
            ),
            recommended_action=(
                "Inspect prediction flips, confidence margins, and "
                "borderline samples before deployment."
            ),
        )

    raise ValueError(
        f"Unknown failure signature type: {signature.signature_type}"
    )