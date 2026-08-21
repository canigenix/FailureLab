from dataclasses import dataclass

from failurelab.evaluation_profile import (
    EvaluationProfile,
)


@dataclass(frozen=True)
class EvaluationProfileValidation:
    """Validation result for an evaluation profile."""

    passed: bool
    errors: tuple[str, ...]


def validate_evaluation_profile(
    profile: EvaluationProfile,
) -> EvaluationProfileValidation:
    """Validate an evaluation profile."""

    errors = []

    if not profile.name.strip():
        errors.append(
            "Evaluation profile name cannot be empty."
        )

    if not profile.suite_config.strip():
        errors.append(
            "suite_config cannot be empty."
        )

    enabled_analyses = (
        profile.run_progression,
        profile.run_signature,
        profile.run_triage,
        profile.run_persistence,
        profile.run_resolution,
        profile.run_forecast,
    )

    if not any(enabled_analyses):
        errors.append(
            "Evaluation profile must enable at least one analysis."
        )

    return EvaluationProfileValidation(
        passed=not errors,
        errors=tuple(errors),
    )