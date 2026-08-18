from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from failurelab.cross_stress import (
    CrossStressClassResult,
    analyze_cross_stress_classes,
)
from failurelab.suite_runner import SuiteResult


@dataclass(frozen=True)
class CrossStressReport:
    suite_name: str
    classes: list[CrossStressClassResult]

    @property
    def class_count(self) -> int:
        return len(self.classes)

    @property
    def systemic_count(self) -> int:
        return sum(
            row.severity == "systemic"
            for row in self.classes
        )

    @property
    def localized_count(self) -> int:
        return sum(
            row.severity == "localized"
            for row in self.classes
        )

    @property
    def stable_count(self) -> int:
        return sum(
            row.severity == "stable"
            for row in self.classes
        )

    def to_dict(self) -> dict:
        return {
            "suite_name": self.suite_name,
            "class_count": self.class_count,
            "systemic_count": self.systemic_count,
            "localized_count": self.localized_count,
            "stable_count": self.stable_count,
            "classes": [
                {
                    "class_index": row.class_index,
                    "severity": row.severity,
                    "stress_count": row.stress_count,
                    "failure_stress_count": (
                        row.failure_stress_count
                    ),
                    "failure_frequency": (
                        row.failure_frequency
                    ),
                    "mean_accuracy_drop": (
                        row.mean_accuracy_drop
                    ),
                    "mean_confidence_drop": (
                        row.mean_confidence_drop
                    ),
                    "mean_failure_rate": (
                        row.mean_failure_rate
                    ),
                    "mean_flip_rate": (
                        row.mean_flip_rate
                    ),
                    "worst_stress": row.worst_stress,
                    "worst_accuracy_drop": (
                        row.worst_accuracy_drop
                    ),
                }
                for row in self.classes
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


def build_cross_stress_report(
    result: SuiteResult,
) -> CrossStressReport:
    return CrossStressReport(
        suite_name=result.name,
        classes=analyze_cross_stress_classes(
            result
        ),
    )