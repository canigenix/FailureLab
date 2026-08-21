from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvaluationInputs:
    """Resolved input paths for an evaluation profile."""

    progression: Path | None = None
    signature: Path | None = None
    triage: Path | None = None
    occurrences: Path | None = None


def resolve_input_path(
    value: str | Path | None,
    *,
    base_path: Path | None = None,
) -> Path | None:
    """Resolve one optional evaluation input path."""

    if value is None:
        return None

    path = Path(value)

    if (
        base_path is not None
        and not path.is_absolute()
    ):
        path = base_path / path

    return path


def build_evaluation_inputs(
    *,
    progression_input: str | Path | None = None,
    signature_input: str | Path | None = None,
    triage_input: str | Path | None = None,
    occurrence_input: str | Path | None = None,
    base_path: Path | None = None,
) -> EvaluationInputs:
    """Build resolved input paths for an evaluation."""

    return EvaluationInputs(
        progression=resolve_input_path(
            progression_input,
            base_path=base_path,
        ),
        signature=resolve_input_path(
            signature_input,
            base_path=base_path,
        ),
        triage=resolve_input_path(
            triage_input,
            base_path=base_path,
        ),
        occurrences=resolve_input_path(
            occurrence_input,
            base_path=base_path,
        ),
    )