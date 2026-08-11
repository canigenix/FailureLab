from __future__ import annotations
from dataclasses import dataclass
from .explanations import explain_weakness
from .vision_runner import VisionStressResult
@dataclass
class VisionWeakness:
    name:str; severity:str; top1_drop:float; top5_drop:float; confidence_drop:float

def classify_vision_severity(top1_drop,top5_drop,confidence_drop):
    strongest=max(top1_drop,top5_drop,confidence_drop)
    if strongest>=0.25:return "critical"
    if strongest>=0.15:return "high"
    if strongest>=0.05:return "medium"
    return "low"

def _normalize_test_name(name):
    base=name.split("_")[0]
    return {"jpeg":"compression"}.get(base,base)

def rank_vision_results(results:list[VisionStressResult])->list[VisionWeakness]:
    out=[]
    for r in results:
        out.append(VisionWeakness(_normalize_test_name(r.name),classify_vision_severity(r.top1_drop,r.top5_drop,r.target_confidence_drop),r.top1_drop,r.top5_drop,r.target_confidence_drop))
    return sorted(out,key=lambda x:max(x.top1_drop,x.top5_drop,x.confidence_drop),reverse=True)

class VisionDiagnosticReport:
    def __init__(self,weaknesses,minimum_meaningful_drop:float=0.05): self.weaknesses=weaknesses; self.minimum_meaningful_drop=minimum_meaningful_drop
    def to_text(self):
        lines=["FailureLab Vision Robustness Report","===================================",""]
        for i,w in enumerate(self.weaknesses,1):
            lines += [f"{i}. {w.name.title()}",f"   Severity: {w.severity}",f"   Top-1 drop: {w.top1_drop:.1%}",f"   Top-5 drop: {w.top5_drop:.1%}",f"   Confidence drop: {w.confidence_drop:.1%}"]
            strongest=max(w.top1_drop,w.top5_drop,w.confidence_drop)
            if strongest<self.minimum_meaningful_drop:
                lines += ["   Status: No meaningful robustness issue detected.",""]; continue
            e=explain_weakness(w.name)
            lines += [f"   Diagnosis: {e.summary}",f"   Likely cause: {e.likely_cause}",f"   Suggested action: {e.suggested_action}",""]
        return "\n".join(lines).rstrip()
