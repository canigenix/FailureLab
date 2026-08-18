from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from failurelab.suite_runner import SuiteResult


@dataclass(frozen=True)
class SampleFailureResult:
    sample_index: int
    target: int
    stress_count: int
    failure_stress_count: int
    failure_frequency: float
    flip_stress_count: int
    flip_frequency: float
    failed_stresses: list[str]
    flipped_stresses: list[str]
    severity: str = ""


def analyze_sample_failures(
    result: SuiteResult,
) -> list[SampleFailureResult]:
    if not result.results:
        return []

    first = result.results[0]

    if not hasattr(
        first,
        "targets",
    ):
        raise ValueError(
            "sample-level analysis requires "
            "unsaved VisionStressResult data."
        )

    targets = np.asarray(
        first.targets,
        dtype=int,
    )

    sample_count = len(
        targets
    )

    failures: list[list[str]] = [
        []
        for _ in range(sample_count)
    ]

    flips: list[list[str]] = [
        []
        for _ in range(sample_count)
    ]

    for stress_result in result.results:
        if not all(
            hasattr(
                stress_result,
                attribute,
            )
            for attribute in (
                "baseline_probabilities",
                "stressed_probabilities",
                "targets",
            )
        ):
            raise ValueError(
                "sample-level analysis requires "
                "unsaved VisionStressResult data."
            )

        stress_targets = np.asarray(
            stress_result.targets,
            dtype=int,
        )

        if len(stress_targets) != sample_count:
            raise ValueError(
                "all stress results must contain "
                "the same number of samples."
            )

        if not np.array_equal(
            stress_targets,
            targets,
        ):
            raise ValueError(
                "all stress results must use "
                "the same target ordering."
            )

        baseline_predictions = np.argmax(
            stress_result.baseline_probabilities,
            axis=1,
        )

        stressed_predictions = np.argmax(
            stress_result.stressed_probabilities,
            axis=1,
        )

        for sample_index in range(
            sample_count
        ):
            if (
                stressed_predictions[sample_index]
                != targets[sample_index]
            ):
                failures[
                    sample_index
                ].append(
                    stress_result.name
                )

            if (
                baseline_predictions[sample_index]
                != stressed_predictions[sample_index]
            ):
                flips[
                    sample_index
                ].append(
                    stress_result.name
                )

    stress_count = len(
        result.results
    )

    output = []

    for sample_index in range(
        sample_count
    ):
        failure_stress_count = len(
            failures[sample_index]
        )

        flip_stress_count = len(
            flips[sample_index]
        )

        failure_frequency = (
            failure_stress_count
            / stress_count
        )

        flip_frequency = (
            flip_stress_count
            / stress_count
        )

        temporary_result = SampleFailureResult(
            sample_index=sample_index,
            target=int(
                targets[sample_index]
            ),
            stress_count=stress_count,
            failure_stress_count=(
                failure_stress_count
            ),
            failure_frequency=(
                failure_frequency
            ),
            flip_stress_count=(
                flip_stress_count
            ),
            flip_frequency=(
                flip_frequency
            ),
            failed_stresses=list(
                failures[sample_index]
            ),
            flipped_stresses=list(
                flips[sample_index]
            ),
        )

        output.append(
            SampleFailureResult(
                sample_index=temporary_result.sample_index,
                target=temporary_result.target,
                stress_count=temporary_result.stress_count,
                failure_stress_count=(
                    temporary_result.failure_stress_count
                ),
                failure_frequency=(
                    temporary_result.failure_frequency
                ),
                flip_stress_count=(
                    temporary_result.flip_stress_count
                ),
                flip_frequency=(
                    temporary_result.flip_frequency
                ),
                failed_stresses=temporary_result.failed_stresses,
                flipped_stresses=temporary_result.flipped_stresses,
                severity=classify_sample_failure_severity(
                    temporary_result
                ),
            )
        )

    return sorted(
        output,
        key=lambda row: (
            row.failure_frequency,
            row.flip_frequency,
        ),
        reverse=True,
    )

def classify_sample_failure_severity(
    result: SampleFailureResult,
) -> str:
    if result.failure_frequency == 0.0:
        return "stable"

    if result.failure_frequency >= 0.67:
        return "systemic"

    return "localized"