from __future__ import annotations
from dataclasses import dataclass
import numpy as np
@dataclass
class ClassRobustnessResult:
    class_index:int; sample_count:int; baseline_accuracy:float; stressed_accuracy:float; accuracy_drop:float; baseline_confidence:float; stressed_confidence:float; confidence_drop:float

def analyze_class_robustness(baseline_probabilities,stressed_probabilities,targets):
    bp=np.asarray(baseline_probabilities,float); sp=np.asarray(stressed_probabilities,float); t=np.asarray(targets,int)
    if bp.shape!=sp.shape: raise ValueError("baseline and stressed probabilities must have the same shape.")
    if len(t)!=len(bp): raise ValueError("targets must match the number of probability rows.")
    results=[]
    for c in np.unique(t):
        mask=t==c; b=bp[mask]; s=sp[mask]; ct=t[mask]
        ba=float(np.mean(np.argmax(b,axis=1)==ct)); sa=float(np.mean(np.argmax(s,axis=1)==ct))
        bc=float(np.mean(b[np.arange(len(ct)),ct])); sc=float(np.mean(s[np.arange(len(ct)),ct]))
        results.append(ClassRobustnessResult(int(c),len(ct),ba,sa,ba-sa,bc,sc,bc-sc))
    return sorted(results,key=lambda x:max(x.accuracy_drop,x.confidence_drop),reverse=True)
