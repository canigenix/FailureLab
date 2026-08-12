import json

import pytest

from failurelab.api import FailureLabReport
from failurelab.failure_envelope import (
    FailureBoundary,
    FailureEnvelope,
)
from failurelab.score import RobustnessScore
from failurelab.snapshot import export_snapshot


def make_report(
    *,
    with_envelope=True,
):
    envelope = None

    if with_envelope:
        envelope = FailureEnvelope(
            boundaries=[
                FailureBoundary(
                    stress_name="blur",
                    failure_threshold=3.0,
                    worst_top1_drop=0.42,
                ),
                FailureBoundary(
                    stress_name="occlusion",
                    failure_threshold=0.30,
                    worst_top1_drop=0.58,
                ),
            ]
        )

    return FailureLabReport(
        weaknesses=[],
        raw_results=[],
        robustness_score=RobustnessScore(
            score=75.0,
            grade="C",
            status="Needs Improvement",
        ),
        recommendations=[],
        failure_envelope=envelope,
    )


def test_export_snapshot(tmp_path):
    report = make_report()

    path = export_snapshot(
        report,
        tmp_path / "snapshot.json",
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["format"] == "failurelab_snapshot"
    assert data["version"] == 1

    assert data["score"] == 75.0
    assert data["grade"] == "C"

    assert len(
        data["boundaries"]
    ) == 2

    assert (
        data["boundaries"][0]["stress_name"]
        == "blur"
    )

    assert (
        data["boundaries"][1]["failure_threshold"]
        == 0.30
    )


def test_snapshot_creates_parent_directory(
    tmp_path,
):
    report = make_report()

    path = export_snapshot(
        report,
        tmp_path
        / "nested"
        / "reports"
        / "snapshot.json",
    )

    assert path.exists()


def test_snapshot_requires_failure_envelope(
    tmp_path,
):
    report = make_report(
        with_envelope=False
    )

    with pytest.raises(
        ValueError,
        match="failure envelope",
    ):
        export_snapshot(
            report,
            tmp_path / "snapshot.json",
        )


def test_report_save_snapshot(
    tmp_path,
):
    report = make_report()

    path = report.save_snapshot(
        tmp_path / "report_snapshot.json"
    )

    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["format"] == "failurelab_snapshot"
    assert data["score"] == 75.0
    assert len(
        data["boundaries"]
    ) == 2