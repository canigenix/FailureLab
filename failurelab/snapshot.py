"""Save FailureLab reports as reusable model robustness snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from failurelab.api import FailureLabReport


def export_snapshot(
    report: FailureLabReport,
    path,
) -> Path:
    """Export a report as a reusable robustness snapshot."""

    if report.failure_envelope is None:
        raise ValueError(
            "Cannot export snapshot without a failure envelope."
        )

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "format": "failurelab_snapshot",
        "version": 1,
        "score": report.robustness_score.score,
        "grade": report.robustness_score.grade,
        "status": report.robustness_score.status,
        "boundaries": [
            {
                "stress_name": boundary.stress_name,
                "failure_threshold": boundary.failure_threshold,
                "worst_top1_drop": boundary.worst_top1_drop,
            }
            for boundary
            in report.failure_envelope.boundaries
        ],
    }

    path.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    return path