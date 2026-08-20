import pytest

from failurelab.failure_signature import (
    StressFailureSignal,
    build_failure_signature,
)
from failurelab.signature_history import (
    SignatureCheckpoint,
    SignatureHistoryReport,
    analyze_signature_history,
)


def make_signature(*rows):
    return build_failure_signature(
        [
            StressFailureSignal(
                stress_name=name,
                failure_rate=failure_rate,
                prediction_flip_rate=flip_rate,
            )
            for name, failure_rate, flip_rate in rows
        ]
    )


def test_analyze_signature_history():
    checkpoints = [
        SignatureCheckpoint(
            "v1",
            make_signature(
                ("blur", 0.25, 0.05),
                ("rotation", 0.03, 0.01),
            ),
        ),
        SignatureCheckpoint(
            "v2",
            make_signature(
                ("blur", 0.15, 0.03),
                ("rotation", 0.04, 0.01),
            ),
        ),
        SignatureCheckpoint(
            "v3",
            make_signature(
                ("blur", 0.10, 0.03),
                ("rotation", 0.30, 0.08),
            ),
        ),
    ]

    report = analyze_signature_history(
        checkpoints
    )

    assert isinstance(
        report,
        SignatureHistoryReport,
    )

    assert len(report.transitions) == 2
    assert report.dominant_stress_changes == 1


def test_signature_history_counts_regressions():
    checkpoints = [
        SignatureCheckpoint(
            "v1",
            make_signature(
                ("blur", 0.03, 0.01),
                ("rotation", 0.02, 0.01),
            ),
        ),
        SignatureCheckpoint(
            "v2",
            make_signature(
                ("blur", 0.20, 0.05),
                ("rotation", 0.18, 0.04),
            ),
        ),
    ]

    report = analyze_signature_history(
        checkpoints
    )

    assert report.regressed_transitions == 1
    assert report.severity_regressions == 1


def test_signature_history_counts_improvements():
    checkpoints = [
        SignatureCheckpoint(
            "v1",
            make_signature(
                ("blur", 0.30, 0.10),
                ("rotation", 0.20, 0.08),
            ),
        ),
        SignatureCheckpoint(
            "v2",
            make_signature(
                ("blur", 0.10, 0.03),
                ("rotation", 0.05, 0.02),
            ),
        ),
    ]

    report = analyze_signature_history(
        checkpoints
    )

    assert report.improved_transitions == 1
    assert report.regressed_transitions == 0


def test_signature_history_respects_tolerance():
    checkpoints = [
        SignatureCheckpoint(
            "v1",
            make_signature(
                ("blur", 0.10, 0.03),
                ("rotation", 0.05, 0.02),
            ),
        ),
        SignatureCheckpoint(
            "v2",
            make_signature(
                ("blur", 0.105, 0.032),
                ("rotation", 0.05, 0.02),
            ),
        ),
    ]

    report = analyze_signature_history(
        checkpoints,
        tolerance=0.01,
    )

    assert report.stable_transitions == 1


def test_signature_history_requires_two_checkpoints():
    checkpoint = SignatureCheckpoint(
        "v1",
        make_signature(
            ("blur", 0.10, 0.03),
        ),
    )

    with pytest.raises(
        ValueError,
        match="At least two signature checkpoints",
    ):
        analyze_signature_history(
            [checkpoint]
        )


def test_signature_history_trend_improving():
    checkpoints = [
        SignatureCheckpoint(
            "v1",
            make_signature(
                ("blur", 0.30, 0.10),
                ("rotation", 0.20, 0.08),
            ),
        ),
        SignatureCheckpoint(
            "v2",
            make_signature(
                ("blur", 0.20, 0.06),
                ("rotation", 0.10, 0.04),
            ),
        ),
        SignatureCheckpoint(
            "v3",
            make_signature(
                ("blur", 0.10, 0.03),
                ("rotation", 0.05, 0.02),
            ),
        ),
    ]

    report = analyze_signature_history(
        checkpoints
    )

    assert report.trend == "improving"


def test_signature_history_trend_degrading():
    checkpoints = [
        SignatureCheckpoint(
            "v1",
            make_signature(
                ("blur", 0.05, 0.02),
                ("rotation", 0.03, 0.01),
            ),
        ),
        SignatureCheckpoint(
            "v2",
            make_signature(
                ("blur", 0.15, 0.05),
                ("rotation", 0.10, 0.03),
            ),
        ),
        SignatureCheckpoint(
            "v3",
            make_signature(
                ("blur", 0.30, 0.10),
                ("rotation", 0.20, 0.08),
            ),
        ),
    ]

    report = analyze_signature_history(
        checkpoints
    )

    assert report.trend == "degrading"


def test_signature_history_trend_volatile():
    checkpoints = [
        SignatureCheckpoint(
            "v1",
            make_signature(
                ("blur", 0.20, 0.05),
                ("rotation", 0.10, 0.03),
            ),
        ),
        SignatureCheckpoint(
            "v2",
            make_signature(
                ("blur", 0.10, 0.03),
                ("rotation", 0.05, 0.02),
            ),
        ),
        SignatureCheckpoint(
            "v3",
            make_signature(
                ("blur", 0.25, 0.08),
                ("rotation", 0.15, 0.05),
            ),
        ),
    ]

    report = analyze_signature_history(
        checkpoints
    )

    assert report.trend == "volatile"


def test_signature_history_trend_stable():
    checkpoints = [
        SignatureCheckpoint(
            "v1",
            make_signature(
                ("blur", 0.10, 0.03),
                ("rotation", 0.05, 0.02),
            ),
        ),
        SignatureCheckpoint(
            "v2",
            make_signature(
                ("blur", 0.10, 0.03),
                ("rotation", 0.05, 0.02),
            ),
        ),
    ]

    report = analyze_signature_history(
        checkpoints
    )

    assert report.trend == "stable"