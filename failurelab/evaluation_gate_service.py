from pathlib import Path

from failurelab.evaluation_gate import (
    EvaluationGateResult,
)
from failurelab.evaluation_gate_config import (
    load_evaluation_gate_config,
)
from failurelab.evaluation_gate_runner import (
    run_evaluation_gate,
)
from failurelab.evaluation_report import (
    EvaluationReport,
)


def evaluate_report_gate(
    report: EvaluationReport,
    gate_config_path: str | Path,
) -> EvaluationGateResult:
    """Evaluate a completed evaluation report against a gate config."""

    config = load_evaluation_gate_config(
        gate_config_path
    )

    return run_evaluation_gate(
        report.intelligence,
        config,
    )