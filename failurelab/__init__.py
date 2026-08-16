"""FailureLab public package interface."""

from failurelab.api import (
    FailureLab,
    FailureLabReport,
)
from failurelab.batch import (
    BatchExperiment,
    BatchExperimentRunner,
    BatchOutput,
)
from failurelab.comparison import (
    BoundaryComparison,
    ModelComparison,
    RobustnessRegressionError,
    compare_reports,
)
from failurelab.config import (
    StressSpec,
    SuiteConfig,
    build_stress_tests,
    load_suite_config,
)
from failurelab.custom_stress import CustomStressTest
from failurelab.experiment import (
    ExperimentOutput,
    ExperimentRunner,
)
from failurelab.failure_envelope import (
    FailureBoundary,
    FailureEnvelope,
)
from failurelab.history import (
    HistoryEntry,
    SuiteHistory,
)
from failurelab.suite_runner import (
    ConfiguredSuiteRunner,
    SuiteResult,
)

__all__ = [
    "FailureLab",
    "FailureLabReport",
    "FailureBoundary",
    "FailureEnvelope",
    "BoundaryComparison",
    "ModelComparison",
    "RobustnessRegressionError",
    "compare_reports",
    "CustomStressTest",
    "StressSpec",
    "SuiteConfig",
    "build_stress_tests",
    "load_suite_config",
    "ConfiguredSuiteRunner",
    "SuiteResult",
    "ExperimentRunner",
    "ExperimentOutput",
    "SuiteHistory",
    "HistoryEntry",
    "BatchExperiment",
    "BatchExperimentRunner",
    "BatchOutput",
]

__version__ = "0.3.0"