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
from failurelab.failure_signature import (
    FailureSignature,
    FailureSignatureType,
    StressFailureSignal,
    build_failure_signature,
    classify_failure_signature,
)
from failurelab.failure_diagnosis import (
    FailureDiagnosis,
    diagnose_failure_signature,
)
from failurelab.failure_diagnostic_report import (
    FailureDiagnosticReport,
    build_failure_diagnostic_report,
)
from failurelab.signature_comparison import (
    FailureSignatureComparison,
    SignatureComparisonStatus,
    classify_signature_comparison,
    compare_failure_signatures,
)
from failurelab.signature_policy import (
    SignaturePolicyResult,
    evaluate_signature_policy,
)
from failurelab.signature_export import (
    diagnostic_report_to_dict,
    export_signature_json,
    failure_signature_to_dict,
    signature_comparison_to_dict,
)
from failurelab.signature_history import (
    SignatureCheckpoint,
    SignatureHistoryReport,
    SignatureHistoryTrend,
    analyze_signature_history,
    classify_signature_history_trend,
)
from failurelab.signature_history_policy import (
    SignatureHistoryPolicyResult,
    evaluate_signature_history_policy,
)
from failurelab.signature_history_export import (
    export_signature_history_json,
    signature_history_to_dict,
)
from failurelab.failure_priority import (
    FailurePriority,
    FailurePrioritySignal,
    PriorityLevel,
    calculate_priority_score,
    classify_priority_level,
    rank_failure_priorities,
)
from failurelab.failure_triage import (
    FailureTriageReport,
    build_failure_triage_report,
)
from failurelab.failure_remediation import (
    FailureRemediation,
    build_failure_remediations,
    identify_primary_driver,
    remediation_for_driver,
)
from failurelab.failure_triage_policy import (
    FailureTriagePolicyResult,
    evaluate_failure_triage_policy,
)
from failurelab.failure_triage_export import (
    export_failure_triage_json,
    failure_triage_to_dict,
)
from failurelab.triage_comparison import (
    FailureTriageComparison,
    TriageComparisonStatus,
    compare_failure_triage,
)
from failurelab.triage_comparison_policy import (
    TriageComparisonPolicyResult,
    evaluate_triage_comparison_policy,
)
from failurelab.triage_comparison_export import (
    export_triage_comparison_json,
    triage_comparison_to_dict,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
    FailureRecurrence,
    analyze_failure_recurrence,
)
from failurelab.failure_persistence import (
    FailurePersistence,
    PersistenceLevel,
    analyze_failure_persistence,
    classify_persistence,
)
from failurelab.failure_persistence_report import (
    FailurePersistenceReport,
    build_failure_persistence_report,
)
from failurelab.failure_persistence_policy import (
    FailurePersistencePolicyResult,
    evaluate_failure_persistence_policy,
)
from failurelab.failure_persistence_export import (
    export_failure_persistence_json,
    failure_persistence_to_dict,
)
from failurelab.failure_resolution import (
    FailureResolution,
    ResolutionStatus,
    analyze_failure_resolution,
    classify_resolution_status,
)
from failurelab.failure_resolution_report import (
    FailureResolutionReport,
    build_failure_resolution_report,
)
from failurelab.failure_resolution_policy import (
    FailureResolutionPolicyResult,
    evaluate_failure_resolution_policy,
)
from failurelab.failure_resolution_export import (
    export_failure_resolution_json,
    failure_resolution_to_dict,
)
from failurelab.failure_forecast import (
    FailureForecast,
    ForecastStatus,
    classify_forecast_status,
    forecast_failure_trajectory,
)
from failurelab.failure_forecast_report import (
    FailureForecastReport,
    build_failure_forecast_report,
)
from failurelab.failure_forecast_policy import (
    FailureForecastPolicyResult,
    evaluate_failure_forecast_policy,
)
from failurelab.failure_forecast_export import (
    export_failure_forecast_json,
    failure_forecast_to_dict,
)
from failurelab.evaluation_profile import (
    EvaluationProfile,
    load_evaluation_profile,
)
from failurelab.evaluation_profile_validation import (
    EvaluationProfileValidation,
    validate_evaluation_profile,
)
from failurelab.evaluation_plan import (
    EvaluationPlan,
    build_evaluation_plan,
)
from failurelab.evaluation_report import (
    EvaluationReport,
    EvaluationStepResult,
    build_evaluation_report,
)
from failurelab.evaluator import (
    EvaluationHandler,
    run_evaluation,
)
from failurelab.evaluation_export import (
    evaluation_report_to_dict,
    export_evaluation_json,
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
"FailureSignature",
"FailureSignatureType",
"StressFailureSignal",
"build_failure_signature",
"classify_failure_signature",
"FailureDiagnosis",
"diagnose_failure_signature",
"FailureDiagnosticReport",
"build_failure_diagnostic_report",
"FailureSignatureComparison",
"SignatureComparisonStatus",
"classify_signature_comparison",
"compare_failure_signatures",
"SignaturePolicyResult",
"evaluate_signature_policy",
"diagnostic_report_to_dict",
"export_signature_json",
"failure_signature_to_dict",
"signature_comparison_to_dict",
"SignatureCheckpoint",
"SignatureHistoryReport",
"SignatureHistoryTrend",
"analyze_signature_history",
"classify_signature_history_trend",
"SignatureHistoryPolicyResult",
"evaluate_signature_history_policy",
"export_signature_history_json",
"signature_history_to_dict",
"FailurePriority",
"FailurePrioritySignal",
"PriorityLevel",
"calculate_priority_score",
"classify_priority_level",
"rank_failure_priorities",
"FailureTriageReport",
"build_failure_triage_report",
"FailureRemediation",
"build_failure_remediations",
"identify_primary_driver",
"remediation_for_driver",
"FailureTriagePolicyResult",
"evaluate_failure_triage_policy",
"export_failure_triage_json",
"failure_triage_to_dict",
"FailureTriageComparison",
"TriageComparisonStatus",
"compare_failure_triage",
"TriageComparisonPolicyResult",
"evaluate_triage_comparison_policy",
"export_triage_comparison_json",
"triage_comparison_to_dict",
"FailureOccurrence",
"FailureRecurrence",
"analyze_failure_recurrence",
"FailurePersistence",
"PersistenceLevel",
"analyze_failure_persistence",
"classify_persistence",
"FailurePersistenceReport",
"build_failure_persistence_report",
"FailurePersistencePolicyResult",
"evaluate_failure_persistence_policy",
"export_failure_persistence_json",
"failure_persistence_to_dict",
"EvaluationProfile",
"load_evaluation_profile",
"EvaluationProfileValidation",
"validate_evaluation_profile",
"EvaluationPlan",
"build_evaluation_plan",
"EvaluationReport",
"EvaluationStepResult",
"build_evaluation_report",
"EvaluationHandler",
"run_evaluation",
"evaluation_report_to_dict",
"export_evaluation_json",
]

__version__ = "0.12.0"