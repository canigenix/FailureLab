"""FailureLab public package interface."""

from failurelab.api import (
    FailureLab,
    FailureLabReport,
)
from failurelab.failure_clusters import (
    FailureCluster,
    build_failure_clusters,
    build_report_clusters,
)
from failurelab.failure_cluster_report import (
    FailureClusterReport,
    build_failure_cluster_report,
)
from failurelab.failure_cluster_policy import (
    FailureClusterPolicy,
    FailureClusterPolicyEvaluation,
    FailureClusterPolicyViolation,
    evaluate_failure_cluster_policy,
)
from failurelab.failure_cluster_policy_config import (
    load_failure_cluster_policy,
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
from failurelab.sample_analysis import (
    SampleFailureResult,
    analyze_sample_failures,
    classify_sample_failure_severity,
)
from failurelab.sample_report import (
    SampleFailureReport,
    build_sample_failure_report,
)
from failurelab.sample_policy import (
    SampleFailurePolicy,
    SampleFailurePolicyEvaluation,
    SampleFailurePolicyViolation,
    evaluate_sample_failure_policy,
)
from failurelab.sample_policy_config import (
    load_sample_failure_policy,
)

from failurelab.failure_correlation import (
    StressCorrelationResult,
    analyze_failure_correlations,
    analyze_report_correlations,
    calculate_failure_correlation,
)
from failurelab.failure_correlation_report import (
    FailureCorrelationReport,
    build_failure_correlation_report,
)
from failurelab.failure_correlation_policy import (
    FailureCorrelationPolicy,
    FailureCorrelationPolicyEvaluation,
    FailureCorrelationPolicyViolation,
    evaluate_failure_correlation_policy,
)
from failurelab.failure_correlation_policy_config import (
    load_failure_correlation_policy,
)

from failurelab.progression_policy import (
    ProgressionPolicyResult,
    evaluate_progression_policy,
)
from failurelab.progression_risk import (
    CheckpointRisk,
    highest_risk_checkpoint,
    score_checkpoint_risk,
)
from failurelab.progression_export import (
    export_progression_json,
    progression_report_to_dict,
)

from failurelab.progression import (
    ProgressionHistoryReport,
    ProgressionPoint,
    ProgressionReport,
    ProgressionStatus,
    ProgressionTrend,
    analyze_progression,
    analyze_progression_history,
    classify_progression,
    classify_progression_trend,
    failure_rate_delta,
    summarize_progression_history,
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
        "SampleFailureResult",
    "analyze_sample_failures",
    "classify_sample_failure_severity",
    "SampleFailureReport",
    "build_sample_failure_report",
    "SampleFailurePolicy",
    "SampleFailurePolicyEvaluation",
    "SampleFailurePolicyViolation",
    "evaluate_sample_failure_policy",
    "load_sample_failure_policy",
        "StressCorrelationResult",
    "analyze_failure_correlations",
    "analyze_report_correlations",
    "calculate_failure_correlation",
    "FailureCorrelationReport",
    "build_failure_correlation_report",
    "FailureCorrelationPolicy",
    "FailureCorrelationPolicyEvaluation",
    "FailureCorrelationPolicyViolation",
    "evaluate_failure_correlation_policy",
    "load_failure_correlation_policy",
        "FailureCluster",
    "build_failure_clusters",
    "build_report_clusters",
    "FailureClusterReport",
    "build_failure_cluster_report",
    "FailureClusterPolicy",
    "FailureClusterPolicyEvaluation",
    "FailureClusterPolicyViolation",
    "evaluate_failure_cluster_policy",
    "load_failure_cluster_policy",
    "ProgressionHistoryReport",
"ProgressionPoint",
"ProgressionReport",
"ProgressionStatus",
"ProgressionTrend",
"analyze_progression",
"analyze_progression_history",
"classify_progression",
"classify_progression_trend",
"failure_rate_delta",
"summarize_progression_history",
"ProgressionPolicyResult",
"evaluate_progression_policy",
"CheckpointRisk",
"highest_risk_checkpoint",
"score_checkpoint_risk",
"export_progression_json",
"progression_report_to_dict",
]

__version__ = "0.5.0"