from __future__ import annotations

from dataclasses import dataclass

from failurelab.class_analysis import (
    ClassRobustnessResult,
)
from failurelab.suite_runner import SuiteResult


@dataclass(frozen=True)
class CrossStressClassResult:
    class_index: int
    stress_count: int
    failure_stress_count: int
    failure_frequency: float
    mean_accuracy_drop: float
    mean_confidence_drop: float
    mean_failure_rate: float
    mean_flip_rate: float
    worst_stress: str
    worst_accuracy_drop: float
    severity: str = ""


def analyze_cross_stress_classes(
    result: SuiteResult,
) -> list[CrossStressClassResult]:
    grouped: dict[
        int,
        list[tuple[str, ClassRobustnessResult]],
    ] = {}

    for stress_result in result.results:
        class_results = result._class_results_for(
            stress_result
        )

        for class_result in class_results:
            grouped.setdefault(
                class_result.class_index,
                [],
            ).append(
                (
                    stress_result.name,
                    class_result,
                )
            )

    output = []

    for class_index, rows in grouped.items():
        stress_count = len(rows)

        failure_stress_count = sum(
            row.stressed_failure_rate > 0.0
            for _, row in rows
        )

        worst_stress, worst_result = max(
            rows,
            key=lambda item: item[1].accuracy_drop,
        )

        temporary_result = CrossStressClassResult(
    class_index=class_index,
    stress_count=stress_count,
    failure_stress_count=failure_stress_count,
    failure_frequency=(
        failure_stress_count
        / stress_count
    ),
    mean_accuracy_drop=sum(
        row.accuracy_drop
        for _, row in rows
    )
    / stress_count,
    mean_confidence_drop=sum(
        row.confidence_drop
        for _, row in rows
    )
    / stress_count,
    mean_failure_rate=sum(
        row.stressed_failure_rate
        for _, row in rows
    )
    / stress_count,
    mean_flip_rate=sum(
        row.prediction_flip_rate
        for _, row in rows
    )
    / stress_count,
    worst_stress=worst_stress,
    worst_accuracy_drop=(
        worst_result.accuracy_drop
    ),
    severity="",
)

        output.append(
    CrossStressClassResult(
        class_index=temporary_result.class_index,
        stress_count=temporary_result.stress_count,
        failure_stress_count=(
            temporary_result.failure_stress_count
        ),
        failure_frequency=(
            temporary_result.failure_frequency
        ),
        mean_accuracy_drop=(
            temporary_result.mean_accuracy_drop
        ),
        mean_confidence_drop=(
            temporary_result.mean_confidence_drop
        ),
        mean_failure_rate=(
            temporary_result.mean_failure_rate
        ),
        mean_flip_rate=(
            temporary_result.mean_flip_rate
        ),
        worst_stress=temporary_result.worst_stress,
        worst_accuracy_drop=(
            temporary_result.worst_accuracy_drop
        ),
        severity=classify_cross_stress_severity(
            temporary_result
        ),
    )
)

    return sorted(
        output,
        key=lambda row: (
            row.failure_frequency,
            row.mean_accuracy_drop,
            row.mean_failure_rate,
        ),
        reverse=True,
    )

def classify_cross_stress_severity(
    result: CrossStressClassResult,
) -> str:
    if result.failure_frequency == 0.0:
        return "stable"

    if result.failure_frequency >= 0.67:
        return "systemic"

    return "localized"