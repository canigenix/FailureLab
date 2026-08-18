import pytest

from failurelab.failure_clusters import (
    build_failure_clusters,
    build_report_clusters,
)

from failurelab.failure_correlation import (
    StressCorrelationResult,
)
from failurelab.failure_correlation_report import (
    FailureCorrelationReport,
)


def correlation(
    stress_a,
    stress_b,
    value,
):
    return StressCorrelationResult(
        stress_a=stress_a,
        stress_b=stress_b,
        shared_failures=1,
        total_failures=1,
        correlation=value,
    )


def test_build_failure_clusters_groups_connected_stresses():
    clusters = build_failure_clusters(
        [
            correlation(
                "blur",
                "noise",
                0.90,
            ),
            correlation(
                "noise",
                "compression",
                0.80,
            ),
            correlation(
                "brightness",
                "rotation",
                0.20,
            ),
        ],
        minimum_correlation=0.75,
    )

    assert len(clusters) == 1

    assert clusters[0].stresses == [
        "blur",
        "compression",
        "noise",
    ]

    assert clusters[0].pair_count == 2
    assert clusters[0].mean_correlation == pytest.approx(0.85)


def test_build_failure_clusters_separates_components():
    clusters = build_failure_clusters(
        [
            correlation(
                "blur",
                "noise",
                0.90,
            ),
            correlation(
                "brightness",
                "rotation",
                0.80,
            ),
        ],
        minimum_correlation=0.75,
    )

    assert len(clusters) == 2

    stress_groups = [
        cluster.stresses
        for cluster in clusters
    ]

    assert [
        "blur",
        "noise",
    ] in stress_groups

    assert [
        "brightness",
        "rotation",
    ] in stress_groups


def test_build_failure_clusters_rejects_invalid_threshold():
    with pytest.raises(
        ValueError,
        match="between 0.0 and 1.0",
    ):
        build_failure_clusters(
            [],
            minimum_correlation=1.5,
        )


def test_build_report_clusters():
    report = FailureCorrelationReport(
        suite_name="cluster-test",
        correlations=[
            correlation(
                "blur",
                "noise",
                0.90,
            ),
            correlation(
                "noise",
                "compression",
                0.80,
            ),
            correlation(
                "brightness",
                "rotation",
                0.20,
            ),
        ],
    )

    clusters = build_report_clusters(
        report,
        minimum_correlation=0.75,
    )

    assert len(clusters) == 1

    assert clusters[0].stresses == [
        "blur",
        "compression",
        "noise",
    ]

    assert clusters[0].mean_correlation == pytest.approx(
        0.85
    )