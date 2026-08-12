"""Overall robustness scoring for FailureLab."""

from __future__ import annotations

from dataclasses import dataclass

from failurelab.vision_report import VisionWeakness


@dataclass(frozen=True)
class RobustnessScore:
    """Overall summary score for model robustness."""

    score: float
    grade: str
    status: str
    average_degradation: float = 0.0
    worst_degradation: float = 0.0


def calculate_robustness_score(
    weaknesses: list[VisionWeakness],
) -> RobustnessScore:
    """
    Convert model degradation into a 0-100 robustness score.

    The score combines:
    - average degradation across stress tests
    - worst-case degradation

    This prevents one catastrophic failure mode from being hidden
    by several strong results.
    """

    if not weaknesses:
        return RobustnessScore(
            score=100.0,
            grade="A",
            status="Excellent",
            average_degradation=0.0,
            worst_degradation=0.0,
        )

    degradation_values = []

    for weakness in weaknesses:
        strongest_drop = max(
            0.0,
            weakness.top1_drop,
            weakness.top5_drop,
            weakness.confidence_drop,
        )

        degradation_values.append(
            min(strongest_drop, 1.0)
        )

    average_degradation = (
        sum(degradation_values)
        / len(degradation_values)
    )

    worst_degradation = max(
        degradation_values
    )

    # Average behavior represents 70% of the score.
    # Worst-case behavior represents 30%.
    combined_degradation = (
        0.70 * average_degradation
        + 0.30 * worst_degradation
    )

    score = 100.0 * (
        1.0 - combined_degradation
    )

    score = round(
        max(
            0.0,
            min(score, 100.0),
        ),
        1,
    )

    if score >= 90:
        grade = "A"
        status = "Excellent"

    elif score >= 80:
        grade = "B"
        status = "Strong"

    elif score >= 70:
        grade = "C"
        status = "Needs Improvement"

    elif score >= 60:
        grade = "D"
        status = "Weak"

    else:
        grade = "F"
        status = "Critical"

    return RobustnessScore(
        score=score,
        grade=grade,
        status=status,
        average_degradation=average_degradation,
        worst_degradation=worst_degradation,
    )