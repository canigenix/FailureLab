import json

from failurelab.failure_forecast_export import (
    export_failure_forecast_json,
    failure_forecast_to_dict,
)
from failurelab.failure_forecast_policy import (
    evaluate_failure_forecast_policy,
)
from failurelab.failure_forecast_report import (
    build_failure_forecast_report,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
)


def make_report():
    return build_failure_forecast_report(
        [
            FailureOccurrence(
                "v1", "blur", 0.80
            ),
            FailureOccurrence(
                "v2", "blur", 0.60
            ),
            FailureOccurrence(
                "v1", "rotation", 0.20
            ),
            FailureOccurrence(
                "v2", "rotation", 0.60
            ),
            FailureOccurrence(
                "v1", "crop", 0.50
            ),
            FailureOccurrence(
                "v2", "crop", 0.50
            ),
        ]
    )


def test_failure_forecast_to_dict():
    data = failure_forecast_to_dict(
        make_report()
    )

    assert data["total_failures"] == 3
    assert data["improving_count"] == 1
    assert data["stable_count"] == 1
    assert data["worsening_count"] == 1
    assert data["projected_risk_count"] == 2

    assert (
        data["highest_projected_risk"]["failure_name"]
        == "rotation"
    )


def test_export_failure_forecast_json(
    tmp_path,
):
    path = tmp_path / "forecast.json"

    result = export_failure_forecast_json(
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
    assert len(data["forecasts"]) == 3


def test_export_failure_forecast_with_policy(
    tmp_path,
):
    report = make_report()

    policy = evaluate_failure_forecast_policy(
        report,
        max_worsening=0,
    )

    path = tmp_path / "forecast.json"

    export_failure_forecast_json(
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
        "Worsening forecasts exceeded limit"
        in violation
        for violation in data["policy"]["violations"]
    )


def test_export_empty_forecast_report(
    tmp_path,
):
    report = build_failure_forecast_report(
        []
    )

    path = tmp_path / "empty.json"

    export_failure_forecast_json(
        report,
        path,
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["total_failures"] == 0
    assert data["projected_risk_count"] == 0
    assert data["highest_projected_risk"] is None
    assert data["forecasts"] == []