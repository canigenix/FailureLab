from pathlib import Path

from failurelab.evaluation_inputs import (
    EvaluationInputs,
    build_evaluation_inputs,
    resolve_input_path,
)


def test_resolve_relative_input_path(
    tmp_path,
):
    result = resolve_input_path(
        "failures.json",
        base_path=tmp_path,
    )

    assert result == (
        tmp_path / "failures.json"
    )


def test_resolve_absolute_input_path(
    tmp_path,
):
    path = (
        tmp_path
        / "failures.json"
    ).resolve()

    result = resolve_input_path(
        path,
        base_path=Path("ignored"),
    )

    assert result == path


def test_resolve_none():
    assert (
        resolve_input_path(
            None
        )
        is None
    )


def test_build_evaluation_inputs(
    tmp_path,
):
    inputs = build_evaluation_inputs(
        progression_input="progression.json",
        signature_input="signature.json",
        triage_input="triage.json",
        occurrence_input="failures.json",
        base_path=tmp_path,
    )

    assert isinstance(
        inputs,
        EvaluationInputs,
    )

    assert inputs.progression == (
        tmp_path / "progression.json"
    )

    assert inputs.signature == (
        tmp_path / "signature.json"
    )

    assert inputs.triage == (
        tmp_path / "triage.json"
    )

    assert inputs.occurrences == (
        tmp_path / "failures.json"
    )


def test_build_partial_inputs(
    tmp_path,
):
    inputs = build_evaluation_inputs(
        occurrence_input="failures.json",
        base_path=tmp_path,
    )

    assert inputs.progression is None
    assert inputs.signature is None
    assert inputs.triage is None

    assert inputs.occurrences == (
        tmp_path / "failures.json"
    )