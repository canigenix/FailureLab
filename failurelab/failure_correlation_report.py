from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from failurelab.failure_correlation import (
    StressCorrelationResult,
    analyze_report_correlations,
)
from failurelab.sample_report import (
    SampleFailureReport,
)


@dataclass(frozen=True)
class FailureCorrelationReport:
    suite_name: str
    correlations: list[StressCorrelationResult]

    @property
    def pair_count(self) -> int:
        return len(self.correlations)

    @property
    def strongest_pair(
        self,
    ) -> StressCorrelationResult | None:
        if not self.correlations:
            return None

        return self.correlations[0]

    def to_dict(self) -> dict:
        strongest = self.strongest_pair

        return {
            "suite_name": self.suite_name,
            "pair_count": self.pair_count,
            "strongest_pair": (
                None
                if strongest is None
                else {
                    "stress_a": strongest.stress_a,
                    "stress_b": strongest.stress_b,
                    "correlation": strongest.correlation,
                }
            ),
            "correlations": [
                {
                    "stress_a": row.stress_a,
                    "stress_b": row.stress_b,
                    "shared_failures": (
                        row.shared_failures
                    ),
                    "total_failures": (
                        row.total_failures
                    ),
                    "correlation": row.correlation,
                }
                for row in self.correlations
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


def build_failure_correlation_report(
    report: SampleFailureReport,
) -> FailureCorrelationReport:
    return FailureCorrelationReport(
        suite_name=report.suite_name,
        correlations=(
            analyze_report_correlations(
                report
            )
        ),
    )