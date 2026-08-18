from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StressCorrelationResult:
    stress_a: str
    stress_b: str
    shared_failures: int
    total_failures: int
    correlation: float


def calculate_failure_correlation(
    stress_a: str,
    failures_a: set[int],
    stress_b: str,
    failures_b: set[int],
) -> StressCorrelationResult:
    shared = failures_a & failures_b
    combined = failures_a | failures_b

    correlation = (
        len(shared) / len(combined)
        if combined
        else 0.0
    )

    return StressCorrelationResult(
        stress_a=stress_a,
        stress_b=stress_b,
        shared_failures=len(shared),
        total_failures=len(combined),
        correlation=correlation,
    )

def analyze_failure_correlations(
    stress_failures: dict[str, set[int]],
) -> list[StressCorrelationResult]:
    stress_names = list(
        stress_failures
    )

    results = []

    for index, stress_a in enumerate(
        stress_names
    ):
        for stress_b in stress_names[
            index + 1:
        ]:
            results.append(
                calculate_failure_correlation(
                    stress_a,
                    stress_failures[stress_a],
                    stress_b,
                    stress_failures[stress_b],
                )
            )

    return sorted(
        results,
        key=lambda row: row.correlation,
        reverse=True,
    )
def analyze_report_correlations(
    report,
) -> list[StressCorrelationResult]:
    stress_failures: dict[str, set[int]] = {}

    for sample in report.samples:
        for stress_name in sample.failed_stresses:
            stress_failures.setdefault(
                stress_name,
                set(),
            ).add(
                sample.sample_index
            )

    return analyze_failure_correlations(
        stress_failures
    )