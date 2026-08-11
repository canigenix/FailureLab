from __future__ import annotations
from dataclasses import dataclass
from .sweeps import SweepResult

@dataclass
class Weakness:
    name: str
    severity: str
    accuracy_drop: float
    stress_level: str

class WeaknessRanker:
    def rank(self, sweeps: list[SweepResult]) -> list[Weakness]:
        out=[]
        for sweep in sweeps:
            worst=sweep.worst_result()
            out.append(Weakness(sweep.test_name,worst.severity,worst.accuracy_drop,worst.name))
        return sorted(out,key=lambda w:w.accuracy_drop,reverse=True)
