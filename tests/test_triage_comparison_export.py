import json

from failurelab.failure_priority import (
    FailurePrioritySignal,
)
from failurelab.failure_triage import (
    build_failure_triage_report,
)
from failurelab.triage_comparison import (
    compare_failure_triage,
)
from failurelab.triage_comparison_export import (
    export_triage_comparison_json,
    triage_comparison_to_dict,
)
from failurelab.triage_comparison_policy import (
    evaluate_triage_comparison_policy,
)


def make_report(*rows):
    return build_failure_triage_report(
        [
            FailurePrioritySignal(
                name=name,
                failure_rate=failure_rate,
                prediction_flip_rate=flip_rate,
                affected_fraction=affected_fraction,
            )
            for (
                name,
                failure_rate,
                flip_rate,
                affected_fraction,
            ) in rows
        ]
    )


def make_comparison():
    baseline = make_report(
        ("blur", 0.20, 0.10, 0.20),
    )

    candidate = make_report(
        ("blur", 1.0, 1.0, 1.0),
    )

    return compare_failure_triage(
        baseline,
        candidate,
    )


def test_triage_comparison_to_dict():
    comparison = make_comparison()

    data = triage_comparison_to_dict(
        comparison
    )

    assert data["status"] == "regressed"
    assert data["actionable_delta"] > 0
    assert data["critical_delta"] > 0
    assert data["highest_score_delta"] > 0


def test_export_triage_comparison_json(
    tmp_path,
):
    comparison = make_comparison()

    path = tmp_path / "comparison.json"

    result = export_triage_comparison_json(
        comparison,
        path,
    )

    assert result == path
    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["status"] == "regressed"
    assert data["candidate_critical"] == 1


def test_export_triage_comparison_with_policy(
    tmp_path,
):
    comparison = make_comparison()

    policy = evaluate_triage_comparison_policy(
        comparison
    )

    path = tmp_path / "comparison.json"

    export_triage_comparison_json(
        comparison,
        path,
        policy=policy,
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["policy"]["passed"] is False
    assert "Failure triage regressed." in (
        data["policy"]["violations"]
    )


def test_export_stable_triage_comparison(
    tmp_path,
):
    report = make_report(
        ("blur", 0.20, 0.10, 0.20),
    )

    comparison = compare_failure_triage(
        report,
        report,
    )

    path = tmp_path / "stable.json"

    export_triage_comparison_json(
        comparison,
        path,
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["status"] == "stable"
    assert data["actionable_delta"] == 0
    assert data["critical_delta"] == 0