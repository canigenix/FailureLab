import json

from failurelab.failure_priority import (
    FailurePrioritySignal,
)
from failurelab.failure_triage import (
    build_failure_triage_report,
)
from failurelab.failure_triage_export import (
    export_failure_triage_json,
    failure_triage_to_dict,
)
from failurelab.failure_triage_policy import (
    evaluate_failure_triage_policy,
)


def make_report():
    return build_failure_triage_report(
        [
            FailurePrioritySignal(
                "blur",
                failure_rate=0.80,
                prediction_flip_rate=0.70,
                affected_fraction=0.80,
            ),
            FailurePrioritySignal(
                "rotation",
                failure_rate=0.20,
                prediction_flip_rate=0.10,
                affected_fraction=0.20,
            ),
        ]
    )


def test_failure_triage_to_dict():
    report = make_report()

    data = failure_triage_to_dict(
        report
    )

    assert data["total_failures"] == 2
    assert data["highest_priority"]["name"] == "blur"
    assert len(data["priorities"]) == 2
    assert len(data["remediations"]) == 2

    assert (
        data["remediations"][0]["name"]
        == "blur"
    )

    assert (
        data["remediations"][0]["primary_driver"]
        == "failure_rate"
    )


def test_export_failure_triage_json(
    tmp_path,
):
    report = make_report()

    path = tmp_path / "triage.json"

    result = export_failure_triage_json(
        report,
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
    assert data["highest_priority"]["name"] == "blur"


def test_export_failure_triage_json_with_policy(
    tmp_path,
):
    report = make_report()

    policy = evaluate_failure_triage_policy(
        report,
        max_critical=0,
    )

    path = tmp_path / "triage.json"

    export_failure_triage_json(
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
    assert len(
        data["policy"]["violations"]
    ) >= 1


def test_failure_triage_to_dict_empty_report():
    report = build_failure_triage_report(
        []
    )

    data = failure_triage_to_dict(
        report
    )

    assert data["total_failures"] == 0
    assert data["highest_priority"] is None
    assert data["priorities"] == []
    assert data["remediations"] == []