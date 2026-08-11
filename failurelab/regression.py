from __future__ import annotations
from dataclasses import dataclass
from .vision_runner import VisionStressResult
@dataclass(frozen=True)
class RobustnessThreshold:
    stress_name:str
    minimum_top1_accuracy:float|None=None
    minimum_top5_accuracy:float|None=None
    minimum_target_confidence:float|None=None
    maximum_top1_drop:float|None=None
    maximum_top5_drop:float|None=None
    maximum_confidence_drop:float|None=None
@dataclass(frozen=True)
class RegressionCheck:
    stress_name:str; passed:bool; failures:tuple[str,...]
def _validate(name,v):
    if v is not None and not 0<=v<=1: raise ValueError(f"{name} must be between 0.0 and 1.0.")
def evaluate_regression(result,threshold):
    if result.name!=threshold.stress_name: raise ValueError("result and threshold stress names must match.")
    for name in ("minimum_top1_accuracy","minimum_top5_accuracy","minimum_target_confidence","maximum_top1_drop","maximum_top5_drop","maximum_confidence_drop"):_validate(name,getattr(threshold,name))
    f=[]
    if threshold.minimum_top1_accuracy is not None and result.stressed.top1_accuracy<threshold.minimum_top1_accuracy:f.append(f"top-1 accuracy {result.stressed.top1_accuracy:.1%} is below required {threshold.minimum_top1_accuracy:.1%}")
    if threshold.minimum_top5_accuracy is not None and result.stressed.top5_accuracy<threshold.minimum_top5_accuracy:f.append(f"top-5 accuracy {result.stressed.top5_accuracy:.1%} is below required {threshold.minimum_top5_accuracy:.1%}")
    if threshold.minimum_target_confidence is not None and result.stressed.mean_target_confidence<threshold.minimum_target_confidence:f.append(f"target confidence {result.stressed.mean_target_confidence:.1%} is below required {threshold.minimum_target_confidence:.1%}")
    if threshold.maximum_top1_drop is not None and result.top1_drop>threshold.maximum_top1_drop:f.append(f"top-1 drop {result.top1_drop:.1%} exceeds allowed {threshold.maximum_top1_drop:.1%}")
    if threshold.maximum_top5_drop is not None and result.top5_drop>threshold.maximum_top5_drop:f.append(f"top-5 drop {result.top5_drop:.1%} exceeds allowed {threshold.maximum_top5_drop:.1%}")
    if threshold.maximum_confidence_drop is not None and result.target_confidence_drop>threshold.maximum_confidence_drop:f.append(f"confidence drop {result.target_confidence_drop:.1%} exceeds allowed {threshold.maximum_confidence_drop:.1%}")
    return RegressionCheck(result.name,not f,tuple(f))
def evaluate_regression_suite(results,thresholds):
    d={r.name:r for r in results}; out=[]
    for t in thresholds:
        out.append(evaluate_regression(d[t.stress_name],t) if t.stress_name in d else RegressionCheck(t.stress_name,False,("stress test result is missing",)))
    return out
