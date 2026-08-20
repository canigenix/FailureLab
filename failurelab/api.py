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