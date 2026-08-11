from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .vision_metrics import VisionMetrics, calculate_vision_metrics
@dataclass
class VisionStressResult:
    name:str
    baseline:VisionMetrics
    stressed:VisionMetrics
    baseline_probabilities:np.ndarray
    stressed_probabilities:np.ndarray
    targets:np.ndarray
    @property
    def top1_drop(self): return self.baseline.top1_accuracy-self.stressed.top1_accuracy
    @property
    def top5_drop(self): return self.baseline.top5_accuracy-self.stressed.top5_accuracy
    @property
    def target_confidence_drop(self): return self.baseline.mean_target_confidence-self.stressed.mean_target_confidence
class VisionStressRunner:
    def __init__(self,predict_proba_fn): self.predict_proba_fn=predict_proba_fn
    def run(self,dataset,stress_test):
        bp=[]; sp=[]; targets=[]
        for image,target in dataset:
            bp.append(self.predict_proba_fn(image)); sp.append(self.predict_proba_fn(stress_test.apply(image))); targets.append(target)
        if not targets: raise ValueError("dataset must contain at least one sample.")
        bp=np.asarray(bp); sp=np.asarray(sp); targets=np.asarray(targets,dtype=int)
        return VisionStressResult(stress_test.name,calculate_vision_metrics(bp,targets),calculate_vision_metrics(sp,targets),bp,sp,targets)
