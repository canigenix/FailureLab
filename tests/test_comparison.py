import pytest

from failurelab import (
    RobustnessRegressionError,
)
from failurelab.comparison import (
    BoundaryComparison,
    ModelComparison,
)


def make_passing_comparison():
    return ModelComparison(
        baseline_score=75.0,
        candidate_score=80.0,
        score_delta=5.0,
        boundaries=[
            BoundaryComparison(
                stress_name="blur",
                baseline_threshold=3.0,
                candidate_threshold=5.0,
                baseline_worst_drop=0.50,
                candidate_worst_drop=0.40,
                worst_drop_delta=-0.10,
                threshold_status="improved",
                regression=False,
                regression_reason="none",
            )
        ],
    )


def make_failing_comparison():
    return ModelComparison(
        baseline_score=75.0,
        candidate_score=74.0,
        score_delta=-1.0,
        boundaries=[
            BoundaryComparison(
                stress_name="occlusion",
                baseline_threshold=0.40,
                candidate_threshold=0.30,
                baseline_worst_drop=0.58,
                candidate_worst_drop=0.50,
                worst_drop_delta=-0.08,
                threshold_status="regressed",
                regression=True,
                regression_reason="threshold",
            )
        ],
    )


def test_require_pass_allows_clean_candidate():
    comparison = make_passing_comparison()

    comparison.require_pass()

    assert comparison.passed is True


def test_require_pass_raises_on_regression():
    comparison = make_failing_comparison()

    with pytest.raises(
        RobustnessRegressionError
    ):
        comparison.require_pass()


def test_gate_error_identifies_regression():
    comparison = make_failing_comparison()

    with pytest.raises(
        RobustnessRegressionError
    ) as exc_info:
        comparison.require_pass()

    message = str(
        exc_info.value
    )

    assert "robustness gate failed" in message.lower()
    assert "occlusion" in message.lower()
    assert "1 regression" in message.lower()