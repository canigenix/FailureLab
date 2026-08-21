from failurelab.api import FailureLab
from failurelab.failure_forecast_policy import (
    FailureForecastPolicyResult,
)
from failurelab.failure_forecast_report import (
    FailureForecastReport,
)


def test_failurelab_builds_forecast_report():
    report = FailureLab.failure_forecast(
        [
            ("v1", "blur", 0.80),
            ("v2", "blur", 0.60),
            ("v3", "blur", 0.40),

            ("v1", "rotation", 0.20),
            ("v2", "rotation", 0.40),
            ("v3", "rotation", 0.60),
        ]
    )

    assert isinstance(
        report,
        FailureForecastReport,
    )

    assert report.total_failures == 2
    assert report.improving_count == 1
    assert report.worsening_count == 1


def test_failurelab_forecast_respects_tolerance():
    report = FailureLab.failure_forecast(
        [
            ("v1", "blur", 0.50),
            ("v2", "blur", 0.505),
        ],
        tolerance=0.01,
    )

    assert report.stable_count == 1
    assert report.worsening_count == 0


def test_failurelab_forecast_policy():
    report = FailureLab.failure_forecast(
        [
            ("v1", "rotation", 0.20),
            ("v2", "rotation", 0.60),
        ]
    )

    result = FailureLab.failure_forecast_policy(
        report,
        max_worsening=0,
    )

    assert isinstance(
        result,
        FailureForecastPolicyResult,
    )

    assert result.passed is False

    assert any(
        "Worsening forecasts exceeded limit"
        in violation
        for violation in result.violations
    )


def test_failurelab_save_forecast_json(
    tmp_path,
):
    report = FailureLab.failure_forecast(
        [
            ("v1", "rotation", 0.20),
            ("v2", "rotation", 0.60),
        ]
    )

    policy = FailureLab.failure_forecast_policy(
        report,
        max_worsening=1,
    )

    path = tmp_path / "forecast.json"

    result = FailureLab.save_failure_forecast_json(
        report,
        path,
        policy=policy,
    )

    assert result == path
    assert path.exists()