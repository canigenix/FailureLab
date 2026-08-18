import json

import pytest

from failurelab.failure_cluster_report import (
    build_failure_cluster_report,
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


def build_report():
    return FailureCorrelationReport(
        suite_name="cluster-report-test",
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


def test_cluster_report_summarizes_clusters():
    report = build_failure_cluster_report(
        build_report(),
        minimum_correlation=0.75,
    )

    assert report.suite_name == "cluster-report-test"
    assert report.cluster_count == 1

    assert report.largest_cluster is not None

    assert report.largest_cluster.stresses == [
        "blur",
        "compression",
        "noise",
    ]

    assert (
        report.largest_cluster.mean_correlation
        == pytest.approx(0.85)
    )


def test_cluster_report_saves_json(
    tmp_path,
):
    report = build_failure_cluster_report(
        build_report(),
        minimum_correlation=0.75,
    )

    path = tmp_path / "clusters.json"

    report.save_json(path)

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["suite_name"] == "cluster-report-test"
    assert data["cluster_count"] == 1
    assert data["largest_cluster_size"] == 3

    assert data["clusters"][0]["stresses"] == [
        "blur",
        "compression",
        "noise",
    ]