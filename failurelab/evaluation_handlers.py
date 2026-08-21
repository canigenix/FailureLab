from pathlib import Path

from failurelab.evaluation_forecast import (
    run_profile_forecast,
)
from failurelab.evaluation_inputs import (
    build_evaluation_inputs,
)
from failurelab.evaluation_persistence import (
    run_profile_persistence,
)
from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_progression import (
    run_profile_progression,
)
from failurelab.evaluation_resolution import (
    run_profile_resolution,
)
from failurelab.evaluation_signature import (
    run_profile_signature,
)
from failurelab.evaluation_triage import (
    run_profile_triage,
)


def build_profile_handlers(
    profile: EvaluationProfile,
    *,
    base_path: Path | None = None,
):
    """Build real evaluation handlers for an evaluation profile."""

    occurrence_input = getattr(
        profile,
        "occurrence_input",
        None,
    )

    if occurrence_input is None:
        occurrence_input = getattr(
            profile,
            "forecast_input",
            None,
        )

    inputs = build_evaluation_inputs(
        progression_input=getattr(
            profile,
            "progression_input",
            None,
        ),
        signature_input=getattr(
            profile,
            "signature_input",
            None,
        ),
        triage_input=getattr(
            profile,
            "triage_input",
            None,
        ),
        occurrence_input=occurrence_input,
        base_path=base_path,
    )

    handlers = {}

    if profile.run_progression:
        handlers["progression"] = lambda: run_profile_progression(
            profile,
            input_path=inputs.progression,
        )

    if profile.run_signature:
        handlers["signature"] = lambda: run_profile_signature(
            profile,
            input_path=inputs.signature,
        )

    if profile.run_triage:
        handlers["triage"] = lambda: run_profile_triage(
            profile,
            input_path=inputs.triage,
        )

    if profile.run_persistence:
        handlers["persistence"] = lambda: run_profile_persistence(
            profile,
            input_path=inputs.occurrences,
        )

    if profile.run_resolution:
        handlers["resolution"] = lambda: run_profile_resolution(
            profile,
            input_path=inputs.occurrences,
        )

    if profile.run_forecast:
        handlers["forecast"] = lambda: run_profile_forecast(
            profile,
            base_path=base_path,
        )

    return handlers