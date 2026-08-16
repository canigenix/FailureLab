from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from failurelab.class_analysis import (
    analyze_class_robustness,
)
from failurelab.class_policy import (
    ClassPolicy,
    ClassPolicyEvaluation,
    evaluate_class_policy,
)
from failurelab.robustness_policy import (
    PolicyEvaluation,
    RobustnessPolicy,
    evaluate_policy,
)
from failurelab.suite_runner import (
    SavedStressResult,
    SuiteResult,
)


@dataclass(frozen=True)
class PolicyReport:
    suite_name: str
    suite_status: str
    policy_status: str
    class_policy_status: str
    worst_stress: str
    worst_drop: float
    evaluation: PolicyEvaluation
    class_evaluation: ClassPolicyEvaluation

    @property
    def passed(self) -> bool:
        return (
            self.suite_status == "passed"
            and self.evaluation.passed
            and self.class_evaluation.passed
        )

    @property
    def status(self) -> str:
        return (
            "passed"
            if self.passed
            else "failed"
        )

    def to_dict(self) -> dict:
        return {
            "suite_name": self.suite_name,
            "status": self.status,
            "suite_status": self.suite_status,
            "policy_status": self.policy_status,
            "class_policy_status": (
                self.class_policy_status
            ),
            "worst_stress": self.worst_stress,
            "worst_drop": self.worst_drop,
            "violation_count": len(
                self.evaluation.violations
            ),
            "class_violation_count": len(
                self.class_evaluation.violations
            ),
            "violations": [
                {
                    "stress_name": violation.stress_name,
                    "metric": violation.metric,
                    "observed": violation.observed,
                    "allowed": violation.allowed,
                }
                for violation
                in self.evaluation.violations
            ],
            "class_violations": [
                {
                    "class_index": violation.class_index,
                    "metric": violation.metric,
                    "observed": violation.observed,
                    "allowed": violation.allowed,
                }
                for violation
                in self.class_evaluation.violations
            ],
        }

    def save_json(
        self,
        path: str | Path,
    ) -> None:
        path = Path(path)

        path.write_text(
            json.dumps(
                self.to_dict(),
                indent=2,
            ),
            encoding="utf-8",
        )


def build_policy_report(
    result: SuiteResult,
    policy: RobustnessPolicy,
    default_class_policy: ClassPolicy | None = None,
    class_policies: dict[int, ClassPolicy] | None = None,
) -> PolicyReport:
    evaluation = evaluate_policy(
        result,
        policy,
    )

    if default_class_policy is None:
        default_class_policy = ClassPolicy()

    if class_policies is None:
        class_policies = {}

    class_results = []

    for stress_result in result.results:
        if isinstance(
            stress_result,
            SavedStressResult,
        ):
            class_results.extend(
                stress_result.class_results
            )
            continue

        class_results.extend(
            analyze_class_robustness(
                stress_result.baseline_probabilities,
                stress_result.stressed_probabilities,
                stress_result.targets,
            )
        )

    class_evaluation = evaluate_class_policy(
        class_results,
        default_policy=default_class_policy,
        class_policies=class_policies,
    )

    return PolicyReport(
        suite_name=result.name,
        suite_status=result.status,
        policy_status=evaluation.status,
        class_policy_status=(
            class_evaluation.status
        ),
        worst_stress=result.worst_result.name,
        worst_drop=result.worst_drop,
        evaluation=evaluation,
        class_evaluation=class_evaluation,
    )