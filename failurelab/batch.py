from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from failurelab.config import SuiteConfig
from failurelab.experiment import (
    ExperimentOutput,
    ExperimentRunner,
)


@dataclass(frozen=True)
class BatchExperiment:
    model_id: str
    predict_proba_fn: object
    dataset: object
    config: SuiteConfig
    result_path: str | Path
    history_path: str | Path
    run_id: str | None = None


@dataclass(frozen=True)
class BatchOutput:
    experiments: list[ExperimentOutput]

    @property
    def count(self) -> int:
        return len(self.experiments)

    @property
    def failed_count(self) -> int:
        return sum(
            output.result.status == "failed"
            for output in self.experiments
        )

    @property
    def passed_count(self) -> int:
        return sum(
            output.result.status == "passed"
            for output in self.experiments
        )

    @property
    def unevaluated_count(self) -> int:
        return sum(
            output.result.status == "not_evaluated"
            for output in self.experiments
        )

    @property
    def status(self) -> str:
        if self.failed_count > 0:
            return "failed"

        if self.unevaluated_count > 0:
            return "not_evaluated"

        return "passed"

    def to_dict(self) -> dict:
        return {
            "experiment_count": self.count,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "unevaluated_count": self.unevaluated_count,
            "status": self.status,
            "experiments": [
                {
                    "model_id": output.model_id,
                    "run_id": output.run_id,
                    "suite_name": output.result.name,
                    "status": output.result.status,
                    "worst_stress": output.result.worst_result.name,
                    "worst_drop": output.result.worst_drop,
                    "maximum_drop": output.result.maximum_drop,
                    "result_path": str(output.result_path),
                    "history_path": str(output.history_path),
                }
                for output in self.experiments
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


class BatchExperimentRunner:
    def run(
        self,
        experiments: list[BatchExperiment],
    ) -> BatchOutput:
        if not experiments:
            raise ValueError(
                "batch must contain at least one experiment."
            )

        outputs = []

        for experiment in experiments:
            runner = ExperimentRunner(
                experiment.predict_proba_fn
            )

            output = runner.run(
                dataset=experiment.dataset,
                config=experiment.config,
                result_path=experiment.result_path,
                history_path=experiment.history_path,
                model_id=experiment.model_id,
                run_id=experiment.run_id,
            )

            outputs.append(output)

        return BatchOutput(
            experiments=outputs
        )