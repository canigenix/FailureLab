from dataclasses import dataclass

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_profile_validation import (
    validate_evaluation_profile,
)


@dataclass(frozen=True)
class EvaluationPlan:
    """Ordered execution plan for an evaluation profile."""

    profile_name: str
    suite_config: str
    analyses: tuple[str, ...]

    @property
    def analysis_count(self) -> int:
        return len(self.analyses)


def build_evaluation_plan(
    profile: EvaluationProfile,
) -> EvaluationPlan:
    """Build an ordered evaluation plan."""

    validation = validate_evaluation_profile(
        profile
    )

    if not validation.passed:
        raise ValueError(
            "; ".join(validation.errors)
        )

    analyses = []

    if profile.run_progression:
        analyses.append("progression")

    if profile.run_signature:
        analyses.append("signature")

    if profile.run_triage:
        analyses.append("triage")

    if profile.run_persistence:
        analyses.append("persistence")

    if profile.run_resolution:
        analyses.append("resolution")

    if profile.run_forecast:
        analyses.append("forecast")

    return EvaluationPlan(
        profile_name=profile.name,
        suite_config=profile.suite_config,
        analyses=tuple(analyses),
    )