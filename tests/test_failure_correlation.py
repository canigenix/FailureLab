from failurelab.failure_correlation import (
    analyze_failure_correlations,
    analyze_report_correlations,
    calculate_failure_correlation,
)

from failurelab.sample_analysis import (
    SampleFailureResult,
)
from failurelab.sample_report import (
    SampleFailureReport,
)


def test_failure_correlation_detects_overlap():
    result = calculate_failure_correlation(
        "blur",
        {0, 1, 2},
        "noise",
        {1, 2, 3},
    )

    assert result.stress_a == "blur"
    assert result.stress_b == "noise"

    assert result.shared_failures == 2
    assert result.total_failures == 4

    assert result.correlation == 0.5


def test_failure_correlation_handles_no_overlap():
    result = calculate_failure_correlation(
        "blur",
        {0, 1},
        "brightness",
        {2, 3},
    )

    assert result.shared_failures == 0
    assert result.correlation == 0.0


def test_failure_correlation_handles_empty_failures():
    result = calculate_failure_correlation(
        "blur",
        set(),
        "noise",
        set(),
    )

    assert result.shared_failures == 0
    assert result.total_failures == 0
    assert result.correlation == 0.0


def test_analyze_failure_correlations_all_pairs():
    results = analyze_failure_correlations(
        {
            "blur": {0, 1, 2},
            "noise": {1, 2, 3},
            "brightness": {4},
        }
    )

    assert len(results) == 3

    assert results[0].stress_a == "blur"
    assert results[0].stress_b == "noise"
    assert results[0].correlation == 0.5


def test_analyze_failure_correlations_sorted():
    results = analyze_failure_correlations(
        {
            "blur": {0, 1, 2},
            "noise": {0, 1, 2},
            "brightness": {3},
        }
    )

    assert results[0].correlation == 1.0

    assert (
        results[0].stress_a
        == "blur"
    )

    assert (
        results[0].stress_b
        == "noise"
    )


def test_analyze_report_correlations():
    report = SampleFailureReport(
        suite_name="correlation-test",
        samples=[
            SampleFailureResult(
                sample_index=0,
                target=0,
                stress_count=3,
                failure_stress_count=2,
                failure_frequency=2 / 3,
                flip_stress_count=0,
                flip_frequency=0.0,
                failed_stresses=[
                    "blur",
                    "noise",
                ],
                flipped_stresses=[],
                severity="localized",
            ),
            SampleFailureResult(
                sample_index=1,
                target=1,
                stress_count=3,
                failure_stress_count=2,
                failure_frequency=2 / 3,
                flip_stress_count=0,
                flip_frequency=0.0,
                failed_stresses=[
                    "blur",
                    "noise",
                ],
                flipped_stresses=[],
                severity="localized",
            ),
            SampleFailureResult(
                sample_index=2,
                target=1,
                stress_count=3,
                failure_stress_count=1,
                failure_frequency=1 / 3,
                flip_stress_count=0,
                flip_frequency=0.0,
                failed_stresses=[
                    "brightness",
                ],
                flipped_stresses=[],
                severity="localized",
            ),
        ],
    )

    results = analyze_report_correlations(
        report
    )

    assert len(results) == 3

    assert results[0].stress_a == "blur"
    assert results[0].stress_b == "noise"
    assert results[0].shared_failures == 2
    assert results[0].correlation == 1.0