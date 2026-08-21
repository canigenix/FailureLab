import pytest

from failurelab.failure_forecast_policy import (
    FailureForecastPolicyResult,
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


def test_forecast_policy_result_type():
    result = evaluate_failure_forecast_policy(
        make_report()
    )

    assert isinstance(
        result,
        FailureForecastPolicyResult,
    )
    assert result.passed is True
    assert result.violations == ()


def test_forecast_policy_limits_worsening():
    result = evaluate_failure_forecast_policy(
        make_report(),
        max_worsening=0,
    )

    assert result.passed is False

    assert any(
        "Worsening forecasts exceeded limit"
        in violation
        for violation in result.violations
    )


def test_forecast_policy_limits_projected_risk():
    result = evaluate_failure_forecast_policy(
        make_report(),
        max_projected_risk=1,
    )

    assert result.passed is False

    assert any(
        "Projected-risk failures exceeded limit"
        in violation
        for violation in result.violations
    )


def test_forecast_policy_limits_projected_score():
    result = evaluate_failure_forecast_policy(
        make_report(),
        max_projected_score=0.90,
    )

    assert result.passed is False

    assert any(
        "Projected failure score exceeded limit"
        in violation
        for violation in result.violations
    )


def test_forecast_policy_can_pass():
    result = evaluate_failure_forecast_policy(
        make_report(),
        max_worsening=1,
        max_projected_risk=2,
        max_projected_score=1.0,
    )

    assert result.passed is True
    assert result.violations == ()


def test_forecast_policy_rejects_negative_limits():
    report = make_report()

    with pytest.raises(
        ValueError,
        match="max_worsening",
    ):
        evaluate_failure_forecast_policy(
            report,
            max_worsening=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_projected_risk",
    ):
        evaluate_failure_forecast_policy(
            report,
            max_projected_risk=-1,
        )


def test_forecast_policy_rejects_invalid_score():
    report = make_report()

    with pytest.raises(
        ValueError,
        match="max_projected_score",
    ):
        evaluate_failure_forecast_policy(
            report,
            max_projected_score=1.01,
        )

    with pytest.raises(
        ValueError,
        match="max_projected_score",
    ):
        evaluate_failure_forecast_policy(
            report,
            max_projected_score=-0.01,
        )