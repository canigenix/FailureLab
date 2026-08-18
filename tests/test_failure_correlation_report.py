import json

from failurelab.failure_correlation_report import (
    build_failure_correlation_report,
)
from failurelab.sample_analysis import (
    SampleFailureResult,
)
from failurelab.sample_report import (
    SampleFailureReport,
)


def sample(
    sample_index,
    failed_stresses,
):
    return SampleFailureResult(
        sample_index=sample_index,
        target=0,
        stress_count=3,
        failure_stress_count=len(
            failed_stresses
        ),
        failure_frequency=(
            len(failed_stresses) / 3
        ),
        flip_stress_count=0,
        flip_frequency=0.0,
        failed_stresses=failed_stresses,
        flipped_stresses=[],
        severity="localized",
    )


def build_report():
    return SampleFailureReport(
        suite_name="correlation-report-test",
        samples=[
            sample(
                0,
                ["blur", "noise"],
            ),
            sample(
                1,
                ["blur", "noise"],
            ),
            sample(
                2,
                ["brightness"],
            ),
        ],
    )


def test_correlation_report_summarizes_pairs():
    report = build_failure_correlation_report(
        build_report()
    )

    assert (
        report.suite_name
        == "correlation-report-test"
    )

    assert report.pair_count == 3

    strongest = report.strongest_pair

    assert strongest is not None
    assert strongest.stress_a == "blur"
    assert strongest.stress_b == "noise"
    assert strongest.correlation == 1.0


def test_correlation_report_saves_json(
    tmp_path,
):
    report = build_failure_correlation_report(
        build_report()
    )

    path = tmp_path / "correlations.json"

    report.save_json(
        path
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        data["suite_name"]
        == "correlation-report-test"
    )

    assert data["pair_count"] == 3

    assert (
        data["strongest_pair"]["stress_a"]
        == "blur"
    )

    assert (
        data["strongest_pair"]["stress_b"]
        == "noise"
    )

    assert (
        data["strongest_pair"]["correlation"]
        == 1.0
    )