"""Actionable recommendations derived from discovered weaknesses."""

from __future__ import annotations

from dataclasses import dataclass

from failurelab.explanations import explain_weakness
from failurelab.vision_report import VisionWeakness


@dataclass(frozen=True)
class Recommendation:
    """Actionable guidance for one discovered robustness weakness."""

    weakness_name: str
    severity: str
    diagnosis: str
    likely_cause: str
    suggested_action: str


def build_recommendations(
    weaknesses: list[VisionWeakness],
    minimum_severity: str = "medium",
) -> list[Recommendation]:
    """
    Build actionable recommendations for meaningful weaknesses.

    Severity order:
        low < medium < high < critical
    """

    severity_rank = {
        "low": 0,
        "medium": 1,
        "high": 2,
        "critical": 3,
    }

    if minimum_severity not in severity_rank:
        raise ValueError(
            f"Unknown minimum severity: {minimum_severity}"
        )

    recommendations = []

    for weakness in weaknesses:
        if weakness.severity not in severity_rank:
            raise ValueError(
                f"Unknown weakness severity: {weakness.severity}"
            )

        if (
            severity_rank[weakness.severity]
            < severity_rank[minimum_severity]
        ):
            continue

        explanation = explain_weakness(
            weakness.name
        )

        recommendations.append(
            Recommendation(
                weakness_name=weakness.name,
                severity=weakness.severity,
                diagnosis=explanation.summary,
                likely_cause=explanation.likely_cause,
                suggested_action=explanation.suggested_action,
            )
        )

    return recommendations