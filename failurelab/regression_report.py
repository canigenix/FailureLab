from dataclasses import dataclass
from .regression import RegressionCheck
@dataclass
class RegressionReport:
    checks:list[RegressionCheck]
    @property
    def passed(self): return all(c.passed for c in self.checks)
    @property
    def failed_count(self): return sum(not c.passed for c in self.checks)
    def to_text(self):
        lines=["FailureLab Regression Gate","==========================",""]
        for c in self.checks:
            lines.append(f"{c.stress_name:<24} {'PASS' if c.passed else 'FAIL'}")
            if not c.passed:
                lines += [f"  - {x}" for x in c.failures]
        lines.append("")
        lines.append("RESULT: PASSED" if self.passed else f"RESULT: FAILED ({self.failed_count} robustness requirement(s) violated)")
        return "\n".join(lines)
