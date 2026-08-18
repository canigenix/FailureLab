import json

from failurelab.sample_analysis import (
    SampleFailureResult,
)
from failurelab.sample_report import (
    SampleFailureReport,
)


def test_sample_report_round_trip_json(tmp_path):
    report = SampleFailureReport(
        suite_name="sample-persistence",
        samples=[
            SampleFailureResult(
                sample_index=0,
                target=1,
                stress_count=3,
                failure_stress_count=2,
                failure_frequency=2 / 3,
                flip_stress_count=2,
                flip_frequency=2 / 3,
                failed_stresses=[
                    "blur",
                    "brightness",
                ],
                flipped_stresses=[
                    "blur",
                    "brightness",
                ],
                severity="localized",
            ),
        ],
    )

    path = tmp_path / "sample-report.json"

    report.save_json(path)

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["suite_name"] == "sample-persistence"
    assert data["sample_count"] == 1
    assert data["samples"][0]["sample_index"] == 0
    assert data["samples"][0]["severity"] == "localized"


def test_sample_report_loads_json(tmp_path):
    original = SampleFailureReport(
        suite_name="sample-persistence",
        samples=[
            SampleFailureResult(
                sample_index=4,
                target=2,
                stress_count=3,
                failure_stress_count=3,
                failure_frequency=1.0,
                flip_stress_count=2,
                flip_frequency=2 / 3,
                failed_stresses=[
                    "blur",
                    "noise",
                    "brightness",
                ],
                flipped_stresses=[
                    "blur",
                    "noise",
                ],
                severity="systemic",
            ),
        ],
    )

    path = tmp_path / "sample-report.json"

    original.save_json(path)

    loaded = SampleFailureReport.load_json(
        path
    )

    assert loaded.suite_name == "sample-persistence"
    assert loaded.sample_count == 1
    assert loaded.samples[0].sample_index == 4
    assert loaded.samples[0].severity == "systemic"