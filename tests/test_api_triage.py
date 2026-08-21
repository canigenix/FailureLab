from failurelab.api import FailureLab
from failurelab.failure_triage import (
    FailureTriageReport,
)
from failurelab.failure_triage_policy import (
    FailureTriagePolicyResult,
)


def test_failurelab_builds_triage_report():
    report = FailureLab.failure_triage(
        [
            ("blur", 0.80, 0.70, 0.80),
            ("rotation", 0.20, 0.10, 0.20),
        ]
    )

    assert isinstance(
        report,
        FailureTriageReport,
    )

    assert report.total_failures == 2
    assert report.highest_priority is not None
    assert report.highest_priority.name == "blur"


def test_failurelab_triage_accepts_severity_weight():
    report = FailureLab.failure_triage(
        [
            (
                "blur",
                0.40,
                0.20,
                0.30,
                1.5,
            ),
        ]
    )

    assert report.highest_priority is not None
    assert report.highest_priority.score > 0.30


def test_failurelab_triage_policy():
    report = FailureLab.failure_triage(
        [
            ("blur", 1.0, 1.0, 1.0),
            ("rotation", 0.10, 0.05, 0.10),
        ]
    )

    result = FailureLab.failure_triage_policy(
        report,
        max_critical=0,
    )

    assert isinstance(
        result,
        FailureTriagePolicyResult,
    )

    assert result.passed is False
    assert len(result.violations) >= 1


def test_failurelab_save_triage_json(
    tmp_path,
):
    report = FailureLab.failure_triage(
        [
            ("blur", 0.80, 0.70, 0.80),
            ("rotation", 0.20, 0.10, 0.20),
        ]
    )

    policy = FailureLab.failure_triage_policy(
        report,
        max_critical=10,
    )

    path = tmp_path / "triage.json"

    result = FailureLab.save_failure_triage_json(
        report,
        path,
        policy=policy,
    )

    assert result == path
    assert path.exists()

def test_failurelab_compares_triage():
    baseline = FailureLab.failure_triage(
        [
            ("blur", 0.20, 0.10, 0.20),
        ]
    )

    candidate = FailureLab.failure_triage(
        [
            ("blur", 1.0, 1.0, 1.0),
        ]
    )

    comparison = FailureLab.compare_failure_triage(
        baseline,
        candidate,
    )

    assert comparison.status == "regressed"
    assert comparison.actionable_delta > 0
    assert comparison.critical_delta > 0
    assert comparison.highest_score_delta > 0


def test_failurelab_triage_comparison_policy():
    baseline = FailureLab.failure_triage(
        [
            ("blur", 0.20, 0.10, 0.20),
        ]
    )

    candidate = FailureLab.failure_triage(
        [
            ("blur", 1.0, 1.0, 1.0),
        ]
    )

    comparison = FailureLab.compare_failure_triage(
        baseline,
        candidate,
    )

    result = FailureLab.triage_comparison_policy(
        comparison
    )

    assert result.passed is False
    assert "Failure triage regressed." in result.violations


def test_failurelab_save_triage_comparison_json(
    tmp_path,
):
    baseline = FailureLab.failure_triage(
        [
            ("blur", 0.20, 0.10, 0.20),
        ]
    )

    candidate = FailureLab.failure_triage(
        [
            ("blur", 1.0, 1.0, 1.0),
        ]
    )

    comparison = FailureLab.compare_failure_triage(
        baseline,
        candidate,
    )

    policy = FailureLab.triage_comparison_policy(
        comparison
    )

    path = tmp_path / "triage-comparison.json"

    result = FailureLab.save_triage_comparison_json(
        comparison,
        path,
        policy=policy,
    )

    assert result == path
    assert path.exists()