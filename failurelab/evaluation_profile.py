from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class EvaluationProfile:
    """Configuration for a complete FailureLab evaluation."""

    name: str
    suite_config: str
    forecast_input: str | None = None
    triage_input: str | None = None
    progression_input: str | None = None
    signature_input: str | None = None
    run_progression: bool = False
    run_signature: bool = False
    run_triage: bool = False
    run_persistence: bool = False
    run_resolution: bool = False
    run_forecast: bool = False


def load_evaluation_profile(
    path: str | Path,
) -> EvaluationProfile:
    """Load an evaluation profile from JSON."""

    profile_path = Path(path)

    data = json.loads(
        profile_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Evaluation profile must be a JSON object."
        )

    if "name" not in data:
        raise ValueError(
            "Evaluation profile is missing 'name'."
        )

    if "suite_config" not in data:
        raise ValueError(
            "Evaluation profile is missing 'suite_config'."
        )

    return EvaluationProfile(
        name=str(data["name"]),
        suite_config=str(
            data["suite_config"]
        ),
        forecast_input=(
            str(data["forecast_input"])
            if data.get("forecast_input") is not None
            else None
        ),
        triage_input=(
            str(data["triage_input"])
            if data.get("triage_input") is not None
            else None
        ),
        progression_input=(
            str(data["progression_input"])
            if data.get("progression_input") is not None
            else None
        ),
        signature_input=(
            str(data["signature_input"])
            if data.get("signature_input") is not None
            else None
        ),
        run_progression=bool(
            data.get(
                "run_progression",
                False,
            )
        ),
        run_signature=bool(
            data.get(
                "run_signature",
                False,
            )
        ),
        run_triage=bool(
            data.get(
                "run_triage",
                False,
            )
        ),
        run_persistence=bool(
            data.get(
                "run_persistence",
                False,
            )
        ),
        run_resolution=bool(
            data.get(
                "run_resolution",
                False,
            )
        ),
        run_forecast=bool(
            data.get(
                "run_forecast",
                False,
            )
        ),
    )