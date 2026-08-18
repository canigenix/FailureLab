from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from failurelab.sample_analysis import (
    SampleFailureResult,
    analyze_sample_failures,
)
from failurelab.suite_runner import SuiteResult


@dataclass(frozen=True)
class SampleFailureReport:
    suite_name: str
    samples: list[SampleFailureResult]

    @property
    def sample_count(self) -> int:
        return len(self.samples)

    @property
    def systemic_count(self) -> int:
        return sum(
            row.severity == "systemic"
            for row in self.samples
        )

    @property
    def localized_count(self) -> int:
        return sum(
            row.severity == "localized"
            for row in self.samples
        )

    @property
    def stable_count(self) -> int:
        return sum(
            row.severity == "stable"
            for row in self.samples
        )

    def to_dict(self) -> dict:
        return {
            "suite_name": self.suite_name,
            "sample_count": self.sample_count,
            "systemic_count": self.systemic_count,
            "localized_count": self.localized_count,
            "stable_count": self.stable_count,
            "samples": [
                {
                    "sample_index": row.sample_index,
                    "target": row.target,
                    "severity": row.severity,
                    "stress_count": row.stress_count,
                    "failure_stress_count": (
                        row.failure_stress_count
                    ),
                    "failure_frequency": (
                        row.failure_frequency
                    ),
                    "flip_stress_count": (
                        row.flip_stress_count
                    ),
                    "flip_frequency": (
                        row.flip_frequency
                    ),
                    "failed_stresses": (
                        row.failed_stresses
                    ),
                    "flipped_stresses": (
                        row.flipped_stresses
                    ),
                }
                for row in self.samples
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

    @classmethod
    def load_json(
        cls,
        path: str | Path,
    ) -> "SampleFailureReport":
        path = Path(path)

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(data, dict):
            raise ValueError(
                "sample failure report must be a JSON object."
            )

        raw_samples = data.get(
            "samples",
            [],
        )

        if not isinstance(
            raw_samples,
            list,
        ):
            raise ValueError(
                "sample failure report 'samples' must be a list."
            )

        samples = []

        for row in raw_samples:
            samples.append(
                SampleFailureResult(
                    sample_index=int(
                        row["sample_index"]
                    ),
                    target=int(
                        row["target"]
                    ),
                    stress_count=int(
                        row["stress_count"]
                    ),
                    failure_stress_count=int(
                        row["failure_stress_count"]
                    ),
                    failure_frequency=float(
                        row["failure_frequency"]
                    ),
                    flip_stress_count=int(
                        row["flip_stress_count"]
                    ),
                    flip_frequency=float(
                        row["flip_frequency"]
                    ),
                    failed_stresses=list(
                        row["failed_stresses"]
                    ),
                    flipped_stresses=list(
                        row["flipped_stresses"]
                    ),
                    severity=str(
                        row["severity"]
                    ),
                )
            )

        return cls(
            suite_name=str(
                data.get(
                    "suite_name",
                    "default",
                )
            ),
            samples=samples,
        )


def build_sample_failure_report(
    result: SuiteResult,
) -> SampleFailureReport:
    return SampleFailureReport(
        suite_name=result.name,
        samples=analyze_sample_failures(
            result
        ),
    )