import json

from failurelab.failure_recurrence import (
    FailureOccurrence,
)
from failurelab.failure_resolution_export import (
    export_failure_resolution_json,
    failure_resolution_to_dict,
)
from failurelab.failure_resolution_policy import (
    evaluate_failure_resolution_policy,
)
from failurelab.failure_resolution_report import (
    build_failure_resolution_report,
)


def make_report():
    return build_failure_resolution_report(
        [
            FailureOccurrence(
                "v1",
                "blur",
                0.80,
            ),
            FailureOccurrence(
                "v2",
                "blur",
                0.50,
            ),
            FailureOccurrence(
                "v1",
                "rotation",
                0.30,
            ),
            FailureOccurrence(
                "v2",
                "rotation",
                0.60,
            ),
            FailureOccurrence(
                "v1",
                "crop",
                0.40,
            ),
            FailureOccurrence(
                "v2",
                "crop",
                0.40,
            ),
        ]
    )


def test_failure_resolution_to_dict():
    data = failure_resolution_to_dict(
        make_report()
    )

    assert data["total_failures"] == 3
    assert data["improving_count"] == 1
    assert data["worsening_count"] == 1
    assert data["unchanged_count"] == 1
    assert data["unresolved_count"] == 2

    assert (
        data["worst_resolution"]["failure_name"]
        == "rotation"
    )


def test_export_failure_resolution_json(
    tmp_path,
):
    path = tmp_path / "resolution.json"

    result = export_failure_resolution_json(
        make_report(),
        path,
    )

    assert result == path
    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["total_failures"] == 3
    assert data["worsening_count"] == 1
    assert (
        data["worst_resolution"]["status"]
        == "worsening"
    )


def test_export_failure_resolution_with_policy(
    tmp_path,
):
    report = make_report()

    policy = evaluate_failure_resolution_policy(
        report,
        max_worsening=0,
    )

    path = tmp_path / "resolution.json"

    export_failure_resolution_json(
        report,
        path,
        policy=policy,
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["policy"]["passed"] is False

    assert any(
        "Worsening failures exceeded limit"
        in violation
        for violation in data["policy"]["violations"]
    )


def test_export_empty_resolution_report(
    tmp_path,
):
    report = build_failure_resolution_report(
        []
    )

    path = tmp_path / "empty.json"

    export_failure_resolution_json(
        report,
        path,
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["total_failures"] == 0
    assert data["worst_resolution"] is None
    assert data["failures"] == []