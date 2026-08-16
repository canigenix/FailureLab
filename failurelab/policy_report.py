from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from failurelab.robustness_policy import (
    PolicyEvaluation,
    RobustnessPolicy,
    evaluate_policy,
)
from failurelab.suite_runner import SuiteResult


@dataclass(frozen=True)
class PolicyReport:
    suite_name: str
    suite_status: str
    policy_status: str
    worst_stress: str
    worst_drop: float
    evaluation: PolicyEvaluation

    @property
    def passed(self) -> bool:
        return (
            self.suite_status == "passed"
            and self.evaluation.passed
        )

    @property
    def status(self) -> str:
        return "passed" if self.passed else "failed"

    def to_dict(self) -> dict:
        return {
            "suite_name": self.suite_name,
            "status": self.status,
            "suite_status": self.suite_status,
            "policy_status": self.policy_status,
            "worst_stress": self.worst_stress,
            "worst_drop": self.worst_drop,
            "violation_count": len(
                self.evaluation.violations
            ),
            "violations": [
                {
                    "stress_name": violation.stress_name,
                    "metric": violation.metric,
                    "observed": violation.observed,
                    "allowed": violation.allowed,
                }
                for violation in self.evaluation.violations
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
) -> PolicyReport:
    evaluation = evaluate_policy(
        result,
        policy,
    )

    return PolicyReport(
        suite_name=result.name,
        suite_status=result.status,
        policy_status=evaluation.status,
        worst_stress=result.worst_result.name,
        worst_drop=result.worst_drop,
        evaluation=evaluation,
    )