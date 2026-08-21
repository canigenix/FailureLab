from failurelab.api import FailureLab
from failurelab.failure_persistence_report import (
    FailurePersistenceReport,
)
from failurelab.failure_persistence_policy import (
    FailurePersistencePolicyResult,
)


def test_failurelab_builds_persistence_report():
    report = FailureLab.failure_persistence(
        [
            ("v1", "blur", 0.80),
            ("v2", "blur", 0.70),
            ("v3", "blur", 0.60),
            ("v1", "rotation", 0.40),
        ]
    )

    assert isinstance(
        report,
        FailurePersistenceReport,
    )

    assert report.total_failures == 2
    assert report.persistent_count == 1
    assert report.isolated_count == 1
    assert report.highest_persistence is not None
    assert (
        report.highest_persistence.failure_name
        == "blur"
    )


def test_failurelab_persistence_policy():
    report = FailureLab.failure_persistence(
        [
            ("v1", "blur", 0.80),
            ("v2", "blur", 0.70),
            ("v3", "blur", 0.60),
        ]
    )

    result = FailureLab.failure_persistence_policy(
        report,
        max_persistent=0,
    )

    assert isinstance(
        result,
        FailurePersistencePolicyResult,
    )

    assert result.passed is False

    assert any(
        "Persistent failures exceeded limit"
        in violation
        for violation in result.violations
    )


def test_failurelab_persistence_policy_can_pass():
    report = FailureLab.failure_persistence(
        [
            ("v1", "blur", 0.80),
            ("v2", "blur", 0.70),
            ("v3", "blur", 0.60),
        ]
    )

    result = FailureLab.failure_persistence_policy(
        report,
        max_persistent=1,
        max_unresolved=1,
        max_recurrence_rate=1.0,
    )

    assert result.passed is True
    assert result.violations == ()


def test_failurelab_save_persistence_json(
    tmp_path,
):
    report = FailureLab.failure_persistence(
        [
            ("v1", "blur", 0.80),
            ("v2", "blur", 0.70),
            ("v3", "blur", 0.60),
            ("v1", "rotation", 0.40),
        ]
    )

    policy = FailureLab.failure_persistence_policy(
        report,
        max_persistent=1,
    )

    path = tmp_path / "persistence.json"

    result = FailureLab.save_failure_persistence_json(
        report,
        path,
        policy=policy,
    )

    assert result == path
    assert path.exists()