"""Generate readable diagnostic reports from ranked model weaknesses."""

from __future__ import annotations

from failurelab.ranking import Weakness


class DiagnosticReport:
    """Format ranked weaknesses into a human-readable report."""

    def __init__(self, weaknesses: list[Weakness]):
        self.weaknesses = weaknesses

    def to_text(self) -> str:
        """Return a plain-text summary of discovered model weaknesses."""
        if not self.weaknesses:
            return "No model weaknesses were detected."

        lines = [
            "FailureLab Diagnostic Report",
            "============================",
            "",
        ]

        for position, weakness in enumerate(self.weaknesses, start=1):
            lines.extend(
                [
                    f"{position}. {weakness.name.title()}",
                    f"   Severity: {weakness.severity}",
                    f"   Accuracy drop: {weakness.accuracy_drop:.1%}",
                    f"   Worst stress level: {weakness.stress_level}",
                    "",
                ]
            )

        return "\n".join(lines).rstrip()