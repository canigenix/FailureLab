from pathlib import Path

from failurelab.evaluation_forecast import (
    run_profile_forecast,
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

    handlers = {}

    if profile.run_progression:
        handlers["progression"] = lambda: run_profile_progression(
            profile,
            input_path=profile.progression_input,
            base_path=base_path,
        )

    if profile.run_signature:
        handlers["signature"] = lambda: run_profile_signature(
            profile,
            input_path=profile.signature_input,
            base_path=base_path,
        )

    if profile.run_triage:
        handlers["triage"] = lambda: run_profile_triage(
            profile,
            input_path=profile.triage_input,
            base_path=base_path,
        )

    if profile.run_persistence:
        handlers["persistence"] = lambda: run_profile_persistence(
            profile,
            base_path=base_path,
        )

    if profile.run_resolution:
        handlers["resolution"] = lambda: run_profile_resolution(
            profile,
            base_path=base_path,
        )

    if profile.run_forecast:
        handlers["forecast"] = lambda: run_profile_forecast(
            profile,
            base_path=base_path,
        )

    return handlers