from __future__ import annotations
from dataclasses import dataclass
import numpy as np
@dataclass
class VisionMetrics:
    top1_accuracy: float
    top5_accuracy: float
    mean_target_confidence: float

def calculate_vision_metrics(probabilities, targets)->VisionMetrics:
    p=np.asarray(probabilities,dtype=float); t=np.asarray(targets,dtype=int)
    if p.ndim != 2: raise ValueError("probabilities must be a 2D array.")
    if len(p)!=len(t): raise ValueError("probabilities and targets must contain the same number of samples.")
    if len(t)==0: raise ValueError("at least one sample is required.")
    top1=np.argmax(p,axis=1); top1_acc=float(np.mean(top1==t))
    k=min(5,p.shape[1]); topk=np.argsort(p,axis=1)[:,-k:]
    top5=float(np.mean([target in preds for target,preds in zip(t,topk)]))
    conf=float(np.mean(p[np.arange(len(t)),t]))
    return VisionMetrics(top1_acc,top5,conf)
