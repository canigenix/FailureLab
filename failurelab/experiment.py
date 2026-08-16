from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from uuid import uuid4

from failurelab.config import SuiteConfig
from failurelab.history import SuiteHistory
from failurelab.suite_runner import (
    ConfiguredSuiteRunner,
    SuiteResult,
)


@dataclass(frozen=True)
class ExperimentOutput:
    result: SuiteResult
    result_path: Path
    history_path: Path
    model_id: str
    run_id: str


class ExperimentRunner:
    def __init__(self, predict_proba_fn):
        self.suite_runner = ConfiguredSuiteRunner(
            predict_proba_fn
        )

    def run(
        self,
        dataset,
        config: SuiteConfig,
        result_path: str | Path,
        history_path: str | Path,
        model_id: str = "unknown",
        run_id: str | None = None,
    ) -> ExperimentOutput:
        result_path = Path(result_path)
        history_path = Path(history_path)

        if not isinstance(model_id, str) or not model_id.strip():
            raise ValueError(
                "model_id must be a non-empty string."
            )

        if run_id is None:
            run_id = uuid4().hex

        if not isinstance(run_id, str) or not run_id.strip():
            raise ValueError(
                "run_id must be a non-empty string."
            )

        model_id = model_id.strip()
        run_id = run_id.strip()

        result = self.suite_runner.run(
            dataset=dataset,
            config=config,
        )

        result_data = result.to_dict()

        result_data["model_id"] = model_id
        result_data["run_id"] = run_id

        result_path.write_text(
            json.dumps(
                result_data,
                indent=2,
            ),
            encoding="utf-8",
        )

        history = SuiteHistory.load_json(
            history_path
        )

        history.add_result(
            result,
            model_id=model_id,
            run_id=run_id,
        )

        history.save_json(
            history_path
        )

        return ExperimentOutput(
            result=result,
            result_path=result_path,
            history_path=history_path,
            model_id=model_id,
            run_id=run_id,
        )