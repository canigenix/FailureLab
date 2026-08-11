from __future__ import annotations
from .explanations import explain_weakness
from .ranking import Weakness
class DiagnosticReport:
    def __init__(self, weaknesses:list[Weakness], minimum_meaningful_drop:float=0.05):
        self.weaknesses=weaknesses; self.minimum_meaningful_drop=minimum_meaningful_drop
    def to_text(self)->str:
        if not self.weaknesses: return "No model weaknesses were detected."
        lines=["FailureLab Diagnostic Report","============================",""]
        for i,w in enumerate(self.weaknesses,1):
            lines += [f"{i}. {w.name.title()}",f"   Severity: {w.severity}",f"   Accuracy drop: {w.accuracy_drop:.1%}",f"   Worst stress level: {w.stress_level}"]
            if w.accuracy_drop < self.minimum_meaningful_drop:
                lines += ["   Status: No meaningful robustness issue detected.",""]; continue
            e=explain_weakness(w.name)
            lines += [f"   Diagnosis: {e.summary}",f"   Likely cause: {e.likely_cause}",f"   Suggested action: {e.suggested_action}",""]
        return "\n".join(lines).rstrip()
