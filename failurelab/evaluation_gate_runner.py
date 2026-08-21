from failurelab.evaluation_gate import (
    EvaluationGateResult,
    evaluate_intelligence_gate,
)
from failurelab.evaluation_gate_config import (
    EvaluationGateConfig,
)
from failurelab.evaluation_intelligence import (
    EvaluationIntelligence,
)


def run_evaluation_gate(
    intelligence: EvaluationIntelligence,
    config: EvaluationGateConfig,
) -> EvaluationGateResult:
    """Apply evaluation gate configuration to evaluation intelligence."""

    return evaluate_intelligence_gate(
        intelligence,
        maximum_failed_analyses=(
            config.maximum_failed_analyses
        ),
        allowed_health_statuses=(
            config.allowed_health_statuses
        ),
    )