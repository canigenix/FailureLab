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
from failurelab.vision_report import (
    VisionDiagnosticReport,
    VisionWeakness,
    rank_vision_results,
)
from failurelab.vision_runner import (
    VisionStressResult,
    VisionStressRunner,
)


@dataclass
class FailureLabReport:
    """Result of a complete FailureLab vision evaluation."""

    weaknesses: list[VisionWeakness]
    raw_results: list[VisionStressResult]
    robustness_score: RobustnessScore
    recommendations: list[Recommendation]

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
                        f"   Diagnosis: {recommendation.diagnosis}",
                        f"   Likely cause: {recommendation.likely_cause}",
                        f"   Next action: {recommendation.suggested_action}",
                        "",
                    ]
                )

            sections.append(
                "\n".join(lines).rstrip()
            )

        return "\n\n".join(sections)

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
            BrightnessTest(factor=0.45),
            BlurTest(radius=3.0),
            CompressionTest(quality=20),
            OcclusionTest(fraction=0.40),
            RotationTest(degrees=30),
            CenterCropTest(fraction=0.60),
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