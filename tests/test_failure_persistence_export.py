import json

from failurelab.failure_persistence_export import (
    export_failure_persistence_json,
    failure_persistence_to_dict,
)
from failurelab.failure_persistence_policy import (
    evaluate_failure_persistence_policy,
)
from failurelab.failure_persistence_report import (
    build_failure_persistence_report,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
)


def make_report():
    return build_failure_persistence_report(
        [
            FailureOccurrence(
                "v1",
                "blur",
                0.80,
            ),
            FailureOccurrence(
                "v2",
                "blur",
                0.70,
            ),
            FailureOccurrence(
                "v3",
                "blur",
                0.60,
            ),
            FailureOccurrence(
                "v1",
                "rotation",
                0.40,
            ),
        ]
    )


def test_failure_persistence_to_dict():
    data = failure_persistence_to_dict(
        make_report()
    )

    assert data["total_failures"] == 2
    assert data["persistent_count"] == 1
    assert data["isolated_count"] == 1
    assert data["unresolved_count"] == 1

    assert (
        data["highest_persistence"]["failure_name"]
        == "blur"
    )

    assert len(data["failures"]) == 2


def test_export_failure_persistence_json(
    tmp_path,
):
    path = tmp_path / "persistence.json"

    result = export_failure_persistence_json(
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

    assert data["total_failures"] == 2
    assert data["persistent_count"] == 1
    assert data["highest_persistence"]["level"] == (
        "persistent"
    )


def test_export_failure_persistence_with_policy(
    tmp_path,
):
    report = make_report()

    policy = evaluate_failure_persistence_policy(
        report,
        max_persistent=0,
    )

    path = tmp_path / "persistence.json"

    export_failure_persistence_json(
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
        "Persistent failures exceeded limit"
        in violation
        for violation in data["policy"]["violations"]
    )


def test_export_empty_persistence_report(
    tmp_path,
):
    report = build_failure_persistence_report(
        []
    )

    path = tmp_path / "empty.json"

    export_failure_persistence_json(
        report,
        path,
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["total_failures"] == 0
    assert data["highest_persistence"] is None
    assert data["failures"] == []