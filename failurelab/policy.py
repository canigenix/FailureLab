from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
from .regression import RobustnessThreshold
def save_policy(thresholds,path)->Path:
    path=Path(path); path.write_text(json.dumps({"version":1,"thresholds":[asdict(t) for t in thresholds]},indent=2),encoding="utf-8"); return path
def load_policy(path):
    path=Path(path)
    if not path.exists(): raise FileNotFoundError(f"FailureLab policy file not found: {path}")
    p=json.loads(path.read_text(encoding="utf-8"))
    if p.get("version")!=1: raise ValueError("Unsupported FailureLab policy version.")
    raw=p.get("thresholds")
    if not isinstance(raw,list): raise ValueError("Policy file must contain a thresholds list.")
    return [RobustnessThreshold(**x) for x in raw]
