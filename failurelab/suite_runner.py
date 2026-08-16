from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from failurelab.config import SuiteConfig, build_stress_tests
from failurelab.vision_runner import (
    VisionStressResult,
    VisionStressRunner,
)


@dataclass(frozen=True)
class SavedStressResult:
    name: str
    top1_drop: float
    top5_drop: float
    target_confidence_drop: float


@dataclass
class SuiteResult:
    results: list[VisionStressResult | SavedStressResult]
    name: str = "default"
    maximum_drop: float | None = None

    @property
    def count(self) -> int:
        return len(self.results)

    @property
    def worst_result(
        self,
    ) -> VisionStressResult | SavedStressResult:
        if not self.results:
            raise ValueError(
                "suite result contains no stress results."
            )

        return max(
            self.results,
            key=lambda result: max(
                result.top1_drop,
                result.top5_drop,
                result.target_confidence_drop,
            ),
        )

    @property
    def worst_drop(self) -> float:
        result = self.worst_result

        return max(
            result.top1_drop,
            result.top5_drop,
            result.target_confidence_drop,
        )

    def passes(
        self,
        maximum_drop: float,
    ) -> bool:
        if maximum_drop < 0:
            raise ValueError(
                "maximum_drop cannot be negative."
            )

        return self.worst_drop <= maximum_drop

    @property
    def passed(self) -> bool | None:
        if self.maximum_drop is None:
            return None

        return self.passes(
            self.maximum_drop
        )

    @property
    def status(self) -> str:
        if self.passed is None:
            return "not_evaluated"

        if self.passed:
            return "passed"

        return "failed"

    def to_dict(self) -> dict:
        return {
            "suite_name": self.name,
            "stress_count": self.count,
            "maximum_drop": self.maximum_drop,
            "status": self.status,
            "worst_stress": self.worst_result.name,
            "worst_drop": self.worst_drop,
            "results": [
                {
                    "name": result.name,
                    "top1_drop": result.top1_drop,
                    "top5_drop": result.top5_drop,
                    "confidence_drop": result.target_confidence_drop,
                }
                for result in self.results
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
    ) -> "SuiteResult":
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"suite result file not found: {path}"
            )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(data, dict):
            raise ValueError(
                "suite result must be a JSON object."
            )

        raw_results = data.get(
            "results"
        )

        if not isinstance(
            raw_results,
            list,
        ) or not raw_results:
            raise ValueError(
                "suite result must contain "
                "a non-empty 'results' list."
            )

        results = []

        for row in raw_results:
            if not isinstance(row, dict):
                raise ValueError(
                    "each saved stress result "
                    "must be an object."
                )

            results.append(
                SavedStressResult(
                    name=str(
                        row["name"]
                    ),
                    top1_drop=float(
                        row["top1_drop"]
                    ),
                    top5_drop=float(
                        row["top5_drop"]
                    ),
                    target_confidence_drop=float(
                        row["confidence_drop"]
                    ),
                )
            )

        maximum_drop = data.get(
            "maximum_drop"
        )

        if maximum_drop is not None:
            maximum_drop = float(
                maximum_drop
            )

        return cls(
            results=results,
            name=str(
                data.get(
                    "suite_name",
                    "default",
                )
            ),
            maximum_drop=maximum_drop,
        )


class ConfiguredSuiteRunner:
    def __init__(self, predict_proba_fn):
        self.runner = VisionStressRunner(
            predict_proba_fn
        )

    def run(
        self,
        dataset,
        config: SuiteConfig,
    ) -> SuiteResult:
        stress_tests = build_stress_tests(
            config
        )

        results = []

        for stress_test in stress_tests:
            result = self.runner.run(
                dataset=dataset,
                stress_test=stress_test,
            )

            results.append(
                result
            )

        return SuiteResult(
            results=results,
            name=config.name,
            maximum_drop=config.maximum_drop,
        )