from __future__ import annotations
import html,json
from pathlib import Path
from .vision_report import VisionWeakness

def export_vision_json(weaknesses:list[VisionWeakness],path)->Path:
    path=Path(path); payload={"failurelab_version":"0.1.0","weaknesses":[{"name":w.name,"severity":w.severity,"top1_drop":w.top1_drop,"top5_drop":w.top5_drop,"confidence_drop":w.confidence_drop} for w in weaknesses]}
    path.write_text(json.dumps(payload,indent=2),encoding="utf-8"); return path

def export_vision_html(weaknesses:list[VisionWeakness],path)->Path:
    path=Path(path)
    rows="\n".join(f"<tr><td>{i}</td><td>{html.escape(w.name.title())}</td><td>{html.escape(w.severity.title())}</td><td>{w.top1_drop:.1%}</td><td>{w.top5_drop:.1%}</td><td>{w.confidence_drop:.1%}</td></tr>" for i,w in enumerate(weaknesses,1))
    doc=f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>FailureLab Vision Report</title></head><body><h1>FailureLab Vision Robustness Report</h1><table><thead><tr><th>Rank</th><th>Stress Type</th><th>Severity</th><th>Top-1 Drop</th><th>Top-5 Drop</th><th>Confidence Drop</th></tr></thead><tbody>{rows}</tbody></table></body></html>'''
    path.write_text(doc,encoding="utf-8"); return path
