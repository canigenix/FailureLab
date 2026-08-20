import json

from failurelab.failure_signature import (
    StressFailureSignal,
    build_failure_signature,
)
from failurelab.signature_history import (
    SignatureCheckpoint,
    analyze_signature_history,
)
from failurelab.signature_history_export import (
    export_signature_history_json,
    signature_history_to_dict,
)
from failurelab.signature_history_policy import (
    evaluate_signature_history_policy,
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


def build_report():
    return analyze_signature_history(
        [
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
    )


def test_signature_history_to_dict():
    report = build_report()

    data = signature_history_to_dict(
        report
    )

    assert data["trend"] == "volatile"
    assert data["improved_transitions"] == 1
    assert data["regressed_transitions"] == 1
    assert len(data["checkpoints"]) == 3
    assert len(data["transitions"]) == 2


def test_export_signature_history_json(
    tmp_path,
):
    report = build_report()

    path = tmp_path / "history.json"

    result = export_signature_history_json(
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

    assert data["trend"] == "volatile"


def test_export_signature_history_json_with_policy(
    tmp_path,
):
    report = build_report()

    policy = evaluate_signature_history_policy(
        report,
        max_regressed_transitions=10,
        max_severity_regressions=10,
        allow_volatile=False,
    )

    path = tmp_path / "history.json"

    export_signature_history_json(
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
    assert "Signature history trend is volatile." in (
        data["policy"]["violations"]
    )