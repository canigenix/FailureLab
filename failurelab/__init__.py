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
from failurelab.class_policy import (
    ClassPolicy,
    ClassPolicyEvaluation,
    ClassPolicyViolation,
    evaluate_class_policy,
)
from failurelab.class_policy_config import (
    LoadedClassPolicy,
    load_class_policy,
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
from failurelab.policy_config import (
    load_robustness_policy,
)
from failurelab.policy_report import (
    PolicyReport,
    build_policy_report,
)
from failurelab.robustness_policy import (
    PolicyEvaluation,
    PolicyViolation,
    RobustnessPolicy,
    StressPolicy,
    evaluate_policy,
)
from failurelab.suite_runner import (
    ConfiguredSuiteRunner,
    SavedStressResult,
    SuiteResult,
)

from failurelab.cross_stress import (
    CrossStressClassResult,
    analyze_cross_stress_classes,
    classify_cross_stress_severity,
)
from failurelab.cross_stress_report import (
    CrossStressReport,
    build_cross_stress_report,
)
from failurelab.cross_stress_policy import (
    CrossStressPolicy,
    CrossStressPolicyEvaluation,
    CrossStressPolicyViolation,
    evaluate_cross_stress_policy,
)
from failurelab.cross_stress_policy_config import (
    load_cross_stress_policy,
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
    "SavedStressResult",
    "ExperimentRunner",
    "ExperimentOutput",
    "SuiteHistory",
    "HistoryEntry",
    "BatchExperiment",
    "BatchExperimentRunner",
    "BatchOutput",
    "StressPolicy",
    "RobustnessPolicy",
    "PolicyViolation",
    "PolicyEvaluation",
    "evaluate_policy",
    "load_robustness_policy",
    "ClassPolicy",
    "ClassPolicyViolation",
    "ClassPolicyEvaluation",
    "evaluate_class_policy",
    "LoadedClassPolicy",
    "load_class_policy",
    "PolicyReport",
    "build_policy_report",

        "CrossStressClassResult",
    "analyze_cross_stress_classes",
    "classify_cross_stress_severity",
    "CrossStressReport",
    "build_cross_stress_report",
    "CrossStressPolicy",
    "CrossStressPolicyEvaluation",
    "CrossStressPolicyViolation",
    "evaluate_cross_stress_policy",
    "load_cross_stress_policy",
]

__version__ = "0.4.0"