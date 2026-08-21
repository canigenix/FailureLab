"""Public API for FailureLab."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from failurelab.blur import BlurTest
from failurelab.compression import CompressionTest
from failurelab.crop import CenterCropTest
from failurelab.export import (
    export_vision_html,
    export_vision_json,
)
from failurelab.failure_envelope import (
    FailureEnvelope,
    build_failure_envelope,
)

from failurelab.progression import (
    ProgressionHistoryReport,
    ProgressionPoint,
    summarize_progression_history,
)
from failurelab.occlusion import OcclusionTest
from failurelab.recommendations import (
    Recommendation,
    build_recommendations,
)
from failurelab.rotation import RotationTest
from failurelab.score import (
    RobustnessScore,
    calculate_robustness_score,
)
from failurelab.stress_tests import BrightnessTest
from failurelab.sweeps import (
    StressSweepResult,
    run_stress_sweep,
)
from failurelab.vision_report import (
    VisionDiagnosticReport,
    VisionWeakness,
    rank_vision_results,
)
from failurelab.vision_runner import (
    VisionStressResult,
    VisionStressRunner,
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
)
from failurelab.failure_signature import (
    FailureSignature,
    StressFailureSignal,
    build_failure_signature,
)
from failurelab.failure_diagnostic_report import (
    FailureDiagnosticReport,
    build_failure_diagnostic_report,
)
from failurelab.signature_comparison import (
    FailureSignatureComparison,
    compare_failure_signatures,
)
from failurelab.signature_policy import (
    SignaturePolicyResult,
    evaluate_signature_policy,
)
from failurelab.signature_export import (
    export_signature_json,
)
from failurelab.signature_history import (
    SignatureCheckpoint,
    SignatureHistoryReport,
    analyze_signature_history,
)
from failurelab.signature_history_policy import (
    SignatureHistoryPolicyResult,
    evaluate_signature_history_policy,
)
from failurelab.signature_history_export import (
    export_signature_history_json,
)
from failurelab.failure_priority import (
    FailurePrioritySignal,
)
from failurelab.failure_triage import (
    FailureTriageReport,
    build_failure_triage_report,
)
from failurelab.failure_triage_export import (
    export_failure_triage_json,
)
from failurelab.failure_triage_policy import (
    FailureTriagePolicyResult,
    evaluate_failure_triage_policy,
)
from failurelab.triage_comparison import (
    FailureTriageComparison,
    compare_failure_triage,
)
from failurelab.triage_comparison_policy import (
    TriageComparisonPolicyResult,
    evaluate_triage_comparison_policy,
)
from failurelab.triage_comparison_export import (
    export_triage_comparison_json,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
    FailureRecurrence,
    analyze_failure_recurrence,
)
from failurelab.failure_persistence import (
    FailurePersistence,
    analyze_failure_persistence,
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
)
from failurelab.failure_resolution import (
    FailureResolution,
    analyze_failure_resolution,
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
)
from failurelab.evaluator import (
    EvaluationHandler,
    run_evaluation,
)
from failurelab.evaluation_export import (
    export_evaluation_json,
)

@dataclass
class FailureLabReport:
    """Result of a complete FailureLab vision evaluation."""

    weaknesses: list[VisionWeakness]
    raw_results: list[VisionStressResult]
    robustness_score: RobustnessScore
    recommendations: list[Recommendation]
    failure_envelope: FailureEnvelope | None = None

    def summary(self) -> str:
        """Return a compact one-line robustness verdict."""

        if self.weaknesses:
            worst = self.weaknesses[0].name.title()

            return (
                f"FailureLab score: "
                f"{self.robustness_score.score:.1f}/100 "
                f"({self.robustness_score.grade}) — "
                f"{self.robustness_score.status}. "
                f"Primary weakness: {worst}."
            )

        return (
            f"FailureLab score: "
            f"{self.robustness_score.score:.1f}/100 "
            f"({self.robustness_score.grade}) — "
            f"{self.robustness_score.status}."
        )

    def with_failure_envelope(
        self,
        envelope: FailureEnvelope,
    ):
        """Attach sweep-derived failure boundaries to this report."""

        self.failure_envelope = envelope
        return self

    def to_text(self) -> str:
        """Return the human-readable diagnostic report."""

        diagnostic_text = VisionDiagnosticReport(
            self.weaknesses
        ).to_text()

        score_text = (
            "FailureLab Robustness Score\n"
            "===========================\n"
            f"Score: {self.robustness_score.score:.1f}/100\n"
            f"Grade: {self.robustness_score.grade}\n"
            f"Status: {self.robustness_score.status}\n"
            f"Average degradation: "
            f"{self.robustness_score.average_degradation:.1%}\n"
            f"Worst degradation: "
            f"{self.robustness_score.worst_degradation:.1%}"
        )

        sections = [
            score_text,
            diagnostic_text,
        ]

        if self.recommendations:
            lines = [
                "Priority Recommendations",
                "========================",
                "",
            ]

            for position, recommendation in enumerate(
                self.recommendations,
                start=1,
            ):
                lines.extend(
                    [
                        (
                            f"{position}. "
                            f"{recommendation.weakness_name.title()} "
                            f"[{recommendation.severity.upper()}]"
                        ),
                        (
                            f"   Diagnosis: "
                            f"{recommendation.diagnosis}"
                        ),
                        (
                            f"   Likely cause: "
                            f"{recommendation.likely_cause}"
                        ),
                        (
                            f"   Next action: "
                            f"{recommendation.suggested_action}"
                        ),
                        "",
                    ]
                )

            sections.append(
                "\n".join(lines).rstrip()
            )

        if self.failure_envelope is not None:
            lines = [
                "Failure Envelope",
                "================",
                "",
            ]

            for boundary in self.failure_envelope.boundaries:
                lines.append(
                    boundary.stress_name.title()
                )

                lines.append(
                    f"   Worst top-1 drop: "
                    f"{boundary.worst_top1_drop:.1%}"
                )

                if boundary.failure_threshold is None:
                    lines.append(
                        "   Failure threshold: not reached"
                    )
                else:
                    lines.append(
                        f"   Failure threshold: "
                        f"{boundary.failure_threshold}"
                    )

                lines.append("")

            sections.append(
                "\n".join(lines).rstrip()
            )

        return "\n\n".join(
            sections
        )

    def save_json(
        self,
        path,
    ) -> Path:
        """Export the report as JSON."""

        return export_vision_json(
            weaknesses=self.weaknesses,
            path=path,
            robustness_score=self.robustness_score,
            recommendations=self.recommendations,
            failure_envelope=self.failure_envelope,
        )

    def save_html(
        self,
        path,
    ) -> Path:
        """Export the report as standalone HTML."""

        return export_vision_html(
            weaknesses=self.weaknesses,
            path=path,
            robustness_score=self.robustness_score,
            recommendations=self.recommendations,
            failure_envelope=self.failure_envelope,
        )

    def save_snapshot(
        self,
        path,
    ) -> Path:
        """Export this report as a reusable robustness snapshot."""

        from failurelab.snapshot import export_snapshot

        return export_snapshot(
            self,
            path,
        )


class FailureLab:
    """High-level interface for vision-model robustness testing."""

    def __init__(
        self,
        predict_proba_fn,
        dataset,
    ):
        self.predict_proba_fn = predict_proba_fn
        self.dataset = dataset

    def default_stress_tests(self):
        """Return FailureLab's default vision robustness suite."""

        return [
            BrightnessTest(
                factor=0.45
            ),
            BlurTest(
                radius=3.0
            ),
            CompressionTest(
                quality=20
            ),
            OcclusionTest(
                fraction=0.40
            ),
            RotationTest(
                degrees=30
            ),
            CenterCropTest(
                fraction=0.60
            ),
        ]

    def run(
        self,
        stress_tests=None,
    ) -> FailureLabReport:
        """Run robustness tests and return a reusable report."""

        if stress_tests is None:
            stress_tests = self.default_stress_tests()

        runner = VisionStressRunner(
            self.predict_proba_fn
        )

        results = []

        for stress_test in stress_tests:
            results.append(
                runner.run(
                    dataset=self.dataset,
                    stress_test=stress_test,
                )
            )

        weaknesses = rank_vision_results(
            results
        )

        robustness_score = calculate_robustness_score(
            weaknesses
        )

        recommendations = build_recommendations(
            weaknesses
        )

        return FailureLabReport(
            weaknesses=weaknesses,
            raw_results=results,
            robustness_score=robustness_score,
            recommendations=recommendations,
        )

    def sweep(
        self,
        stress_name: str,
    ) -> StressSweepResult:
        """Run one built-in severity sweep."""

        presets = {
            "brightness": {
                "values": [
                    0.90,
                    0.75,
                    0.60,
                    0.45,
                    0.30,
                ],
                "factory": lambda value: BrightnessTest(
                    factor=value
                ),
            },
            "blur": {
                "values": [
                    0.5,
                    1.0,
                    2.0,
                    3.0,
                    5.0,
                ],
                "factory": lambda value: BlurTest(
                    radius=value
                ),
            },
            "compression": {
                "values": [
                    90,
                    70,
                    50,
                    30,
                    10,
                ],
                "factory": lambda value: CompressionTest(
                    quality=int(value)
                ),
            },
            "occlusion": {
                "values": [
                    0.10,
                    0.20,
                    0.30,
                    0.40,
                    0.50,
                ],
                "factory": lambda value: OcclusionTest(
                    fraction=value
                ),
            },
            "rotation": {
                "values": [
                    5,
                    10,
                    20,
                    30,
                    45,
                ],
                "factory": lambda value: RotationTest(
                    degrees=value
                ),
            },
            "crop": {
                "values": [
                    0.90,
                    0.80,
                    0.70,
                    0.60,
                    0.50,
                ],
                "factory": lambda value: CenterCropTest(
                    fraction=value
                ),
            },
        }

        normalized_name = (
            stress_name
            .strip()
            .lower()
        )

        if normalized_name not in presets:
            supported = ", ".join(
                presets.keys()
            )

            raise ValueError(
                f"Unknown stress sweep: {stress_name}. "
                f"Supported sweeps: {supported}."
            )

        preset = presets[
            normalized_name
        ]

        return run_stress_sweep(
            name=normalized_name,
            severity_values=preset["values"],
            stress_factory=preset["factory"],
            predict_proba_fn=self.predict_proba_fn,
            dataset=self.dataset,
        )

    def sweep_all(
        self,
    ) -> FailureEnvelope:
        """Run all built-in sweeps and return the model failure envelope."""

        sweep_names = [
            "brightness",
            "blur",
            "compression",
            "occlusion",
            "rotation",
            "crop",
        ]

        sweeps = [
            self.sweep(
                sweep_name
            )
            for sweep_name in sweep_names
        ]

        return build_failure_envelope(
            sweeps
        )

    @staticmethod
    def progression(
        points,
        tolerance: float = 0.0,
    ) -> ProgressionHistoryReport:
        """Analyze failure-rate progression across model checkpoints."""

        progression_points = [
            point
            if isinstance(point, ProgressionPoint)
            else ProgressionPoint(
                label=point[0],
                failure_rate=point[1],
            )
            for point in points
        ]

        return summarize_progression_history(
            progression_points,
            tolerance=tolerance,
        )

    @staticmethod
    def progression_policy(
        report: ProgressionHistoryReport,
        *,
        max_overall_regression: float = 0.0,
        max_regressed_transitions: int = 0,
        allow_volatile: bool = True,
    ) -> ProgressionPolicyResult:
        """Evaluate progression history against policy rules."""

        return evaluate_progression_policy(
            report,
            max_overall_regression=max_overall_regression,
            max_regressed_transitions=max_regressed_transitions,
            allow_volatile=allow_volatile,
        )

    @staticmethod
    def progression_risk(
        points,
    ) -> list[CheckpointRisk]:
        """Score risk across model checkpoints."""

        progression_points = [
            point
            if isinstance(point, ProgressionPoint)
            else ProgressionPoint(
                label=point[0],
                failure_rate=point[1],
            )
            for point in points
        ]

        return score_checkpoint_risk(progression_points)

    @staticmethod
    def highest_progression_risk(
        points,
    ) -> CheckpointRisk:
        """Return the highest-risk model checkpoint."""

        progression_points = [
            point
            if isinstance(point, ProgressionPoint)
            else ProgressionPoint(
                label=point[0],
                failure_rate=point[1],
            )
            for point in points
        ]

        return highest_risk_checkpoint(progression_points)

    @staticmethod
    def save_progression_json(
        report: ProgressionHistoryReport,
        path,
        *,
        policy: ProgressionPolicyResult | None = None,
        risks: list[CheckpointRisk] | None = None,
    ) -> Path:
        """Export progression analysis as JSON."""

        return export_progression_json(
            report,
            path,
            policy=policy,
            risks=risks,
        )

    @staticmethod
    def failure_signature(
        signals,
        *,
        affected_threshold: float = 0.10,
        systemic_fraction: float = 0.50,
        instability_threshold: float = 0.20,
    ) -> FailureSignature:
        """Build a failure signature from stress-level signals."""

        stress_signals = [
            signal
            if isinstance(signal, StressFailureSignal)
            else StressFailureSignal(
                stress_name=signal[0],
                failure_rate=signal[1],
                prediction_flip_rate=signal[2],
            )
            for signal in signals
        ]

        return build_failure_signature(
            stress_signals,
            affected_threshold=affected_threshold,
            systemic_fraction=systemic_fraction,
            instability_threshold=instability_threshold,
        )

    @staticmethod
    def diagnose_failure_signature(
        signature: FailureSignature,
    ) -> FailureDiagnosticReport:
        """Build a diagnostic report for a failure signature."""

        return build_failure_diagnostic_report(
            signature
        )

    @staticmethod
    def compare_failure_signatures(
        baseline: FailureSignature,
        candidate: FailureSignature,
        *,
        tolerance: float = 0.0,
    ) -> FailureSignatureComparison:
        """Compare two failure signatures."""

        return compare_failure_signatures(
            baseline,
            candidate,
            tolerance=tolerance,
        )

    @staticmethod
    def signature_policy(
        comparison: FailureSignatureComparison,
        *,
        max_failure_rate_increase: float = 0.0,
        max_flip_rate_increase: float = 0.0,
        max_affected_stress_increase: int = 0,
        allow_dominant_stress_change: bool = True,
        allow_severity_regression: bool = False,
    ) -> SignaturePolicyResult:
        """Evaluate a failure-signature comparison against policy rules."""

        return evaluate_signature_policy(
            comparison,
            max_failure_rate_increase=max_failure_rate_increase,
            max_flip_rate_increase=max_flip_rate_increase,
            max_affected_stress_increase=max_affected_stress_increase,
            allow_dominant_stress_change=allow_dominant_stress_change,
            allow_severity_regression=allow_severity_regression,
        )

    @staticmethod
    def save_signature_json(
        signature: FailureSignature,
        path,
        *,
        diagnostic_report: FailureDiagnosticReport | None = None,
        comparison: FailureSignatureComparison | None = None,
        policy: SignaturePolicyResult | None = None,
    ) -> Path:
        """Export failure-signature analysis as JSON."""

        return export_signature_json(
            signature,
            path,
            diagnostic_report=diagnostic_report,
            comparison=comparison,
            policy=policy,
        )
    @staticmethod
    def signature_history(
        checkpoints,
        *,
        tolerance: float = 0.0,
    ) -> SignatureHistoryReport:
        """Analyze failure-signature evolution across model versions."""

        history_checkpoints = [
            checkpoint
            if isinstance(checkpoint, SignatureCheckpoint)
            else SignatureCheckpoint(
                label=checkpoint[0],
                signature=checkpoint[1],
            )
            for checkpoint in checkpoints
        ]

        return analyze_signature_history(
            history_checkpoints,
            tolerance=tolerance,
        )

    @staticmethod
    def signature_history_policy(
        report: SignatureHistoryReport,
        *,
        max_regressed_transitions: int = 0,
        max_severity_regressions: int = 0,
        max_dominant_stress_changes: int | None = None,
        allow_volatile: bool = False,
    ) -> SignatureHistoryPolicyResult:
        """Evaluate signature-history evolution against policy rules."""

        return evaluate_signature_history_policy(
            report,
            max_regressed_transitions=max_regressed_transitions,
            max_severity_regressions=max_severity_regressions,
            max_dominant_stress_changes=max_dominant_stress_changes,
            allow_volatile=allow_volatile,
        )

    @staticmethod
    def save_signature_history_json(
        report: SignatureHistoryReport,
        path,
        *,
        policy: SignatureHistoryPolicyResult | None = None,
    ) -> Path:
        """Export signature-history analysis as JSON."""

        return export_signature_history_json(
            report,
            path,
            policy=policy,
        )

    @staticmethod
    def failure_triage(
        signals,
    ) -> FailureTriageReport:
        """Build a prioritized failure triage report."""

        priority_signals = [
            signal
            if isinstance(signal, FailurePrioritySignal)
            else FailurePrioritySignal(
                name=signal[0],
                failure_rate=signal[1],
                prediction_flip_rate=signal[2],
                affected_fraction=signal[3],
                severity_weight=(
                    signal[4]
                    if len(signal) > 4
                    else 1.0
                ),
            )
            for signal in signals
        ]

        return build_failure_triage_report(
            priority_signals
        )

    @staticmethod
    def failure_triage_policy(
        report: FailureTriageReport,
        *,
        max_critical: int = 0,
        max_high: int | None = None,
        max_actionable: int | None = None,
        max_priority_score: float | None = None,
    ) -> FailureTriagePolicyResult:
        """Evaluate a failure triage report against policy rules."""

        return evaluate_failure_triage_policy(
            report,
            max_critical=max_critical,
            max_high=max_high,
            max_actionable=max_actionable,
            max_priority_score=max_priority_score,
        )

    @staticmethod
    def save_failure_triage_json(
        report: FailureTriageReport,
        path,
        *,
        policy: FailureTriagePolicyResult | None = None,
    ) -> Path:
        """Export failure triage analysis as JSON."""

        return export_failure_triage_json(
            report,
            path,
            policy=policy,
        )

    @staticmethod
    def compare_failure_triage(
        baseline: FailureTriageReport,
        candidate: FailureTriageReport,
        *,
        score_tolerance: float = 0.0,
    ) -> FailureTriageComparison:
        """Compare failure triage between model versions."""

        return compare_failure_triage(
            baseline,
            candidate,
            score_tolerance=score_tolerance,
        )

    @staticmethod
    def triage_comparison_policy(
        comparison: FailureTriageComparison,
        *,
        allow_regression: bool = False,
        max_actionable_increase: int | None = None,
        max_critical_increase: int | None = None,
        max_score_increase: float | None = None,
    ) -> TriageComparisonPolicyResult:
        """Evaluate triage comparison against regression policy."""

        return evaluate_triage_comparison_policy(
            comparison,
            allow_regression=allow_regression,
            max_actionable_increase=max_actionable_increase,
            max_critical_increase=max_critical_increase,
            max_score_increase=max_score_increase,
        )

    @staticmethod
    def save_triage_comparison_json(
        comparison: FailureTriageComparison,
        path,
        *,
        policy: TriageComparisonPolicyResult | None = None,
    ) -> Path:
        """Export triage comparison analysis as JSON."""

        return export_triage_comparison_json(
            comparison,
            path,
            policy=policy,
        )

    @staticmethod
    def failure_persistence(
        occurrences,
    ) -> FailurePersistenceReport:
        """Analyze recurring failures across model checkpoints."""

        failure_occurrences = [
            occurrence
            if isinstance(
                occurrence,
                FailureOccurrence,
            )
            else FailureOccurrence(
                checkpoint=occurrence[0],
                failure_name=occurrence[1],
                priority_score=occurrence[2],
            )
            for occurrence in occurrences
        ]

        return build_failure_persistence_report(
            failure_occurrences
        )

    @staticmethod
    def failure_persistence_policy(
        report: FailurePersistenceReport,
        *,
        max_persistent: int | None = None,
        max_recurring: int | None = None,
        max_unresolved: int | None = None,
        max_recurrence_rate: float | None = None,
    ) -> FailurePersistencePolicyResult:
        """Evaluate failure persistence against policy limits."""

        return evaluate_failure_persistence_policy(
            report,
            max_persistent=max_persistent,
            max_recurring=max_recurring,
            max_unresolved=max_unresolved,
            max_recurrence_rate=max_recurrence_rate,
        )

    @staticmethod
    def save_failure_persistence_json(
        report: FailurePersistenceReport,
        path,
        *,
        policy: FailurePersistencePolicyResult | None = None,
    ) -> Path:
        """Export failure persistence analysis as JSON."""

        return export_failure_persistence_json(
            report,
            path,
            policy=policy,
        )

    @staticmethod
    def failure_resolution(
        occurrences,
        *,
        tolerance: float = 0.0,
    ) -> FailureResolutionReport:
        """Analyze whether recurring failures are improving or worsening."""

        failure_occurrences = [
            occurrence
            if isinstance(
                occurrence,
                FailureOccurrence,
            )
            else FailureOccurrence(
                checkpoint=occurrence[0],
                failure_name=occurrence[1],
                priority_score=occurrence[2],
            )
            for occurrence in occurrences
        ]

        return build_failure_resolution_report(
            failure_occurrences,
            tolerance=tolerance,
        )

    @staticmethod
    def failure_resolution_policy(
        report: FailureResolutionReport,
        *,
        max_worsening: int | None = None,
        max_unchanged: int | None = None,
        max_unresolved: int | None = None,
        max_score_regression: float | None = None,
    ) -> FailureResolutionPolicyResult:
        """Evaluate failure resolution against policy limits."""

        return evaluate_failure_resolution_policy(
            report,
            max_worsening=max_worsening,
            max_unchanged=max_unchanged,
            max_unresolved=max_unresolved,
            max_score_regression=max_score_regression,
        )

    @staticmethod
    def save_failure_resolution_json(
        report: FailureResolutionReport,
        path,
        *,
        policy: FailureResolutionPolicyResult | None = None,
    ) -> Path:
        """Export failure resolution analysis as JSON."""

        return export_failure_resolution_json(
            report,
            path,
            policy=policy,
        )

    @staticmethod
    def failure_forecast(
        occurrences,
        *,
        tolerance: float = 0.0,
    ) -> FailureForecastReport:
        """Forecast failure trajectories across model checkpoints."""

        failure_occurrences = [
            occurrence
            if isinstance(
                occurrence,
                FailureOccurrence,
            )
            else FailureOccurrence(
                checkpoint=occurrence[0],
                failure_name=occurrence[1],
                priority_score=occurrence[2],
            )
            for occurrence in occurrences
        ]

        return build_failure_forecast_report(
            failure_occurrences,
            tolerance=tolerance,
        )

    @staticmethod
    def failure_forecast_policy(
        report: FailureForecastReport,
        *,
        max_worsening: int | None = None,
        max_projected_risk: int | None = None,
        max_projected_score: float | None = None,
    ) -> FailureForecastPolicyResult:
        """Evaluate failure forecasts against policy limits."""

        return evaluate_failure_forecast_policy(
            report,
            max_worsening=max_worsening,
            max_projected_risk=max_projected_risk,
            max_projected_score=max_projected_score,
        )

    @staticmethod
    def save_failure_forecast_json(
        report: FailureForecastReport,
        path,
        *,
        policy: FailureForecastPolicyResult | None = None,
    ) -> Path:
        """Export failure forecast analysis as JSON."""

        return export_failure_forecast_json(
            report,
            path,
            policy=policy,
        )

    @staticmethod
    def load_evaluation_profile(
        path,
    ) -> EvaluationProfile:
        """Load an evaluation profile from JSON."""

        return load_evaluation_profile(path)

    @staticmethod
    def validate_evaluation_profile(
        profile: EvaluationProfile,
    ) -> EvaluationProfileValidation:
        """Validate an evaluation profile."""

        return validate_evaluation_profile(profile)

    @staticmethod
    def evaluation_plan(
        profile: EvaluationProfile,
    ) -> EvaluationPlan:
        """Build an ordered evaluation plan."""

        return build_evaluation_plan(profile)

    @staticmethod
    def evaluate_profile(
        profile: EvaluationProfile,
        handlers: dict[str, EvaluationHandler],
    ) -> EvaluationReport:
        """Execute an evaluation profile using registered handlers."""

        return run_evaluation(
            profile,
            handlers,
        )

    @staticmethod
    def save_evaluation_json(
        report: EvaluationReport,
        path,
    ) -> Path:
        """Export a complete evaluation report as JSON."""

        return export_evaluation_json(
            report,
            path,
        )

