from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from .blur import BlurTest
from .compression import CompressionTest
from .crop import CenterCropTest
from .export import export_vision_html, export_vision_json
from .occlusion import OcclusionTest
from .rotation import RotationTest
from .stress_tests import BrightnessTest
from .vision_report import VisionDiagnosticReport, VisionWeakness, rank_vision_results
from .vision_runner import VisionStressResult, VisionStressRunner
@dataclass
class FailureLabReport:
    weaknesses:list[VisionWeakness]
    raw_results:list[VisionStressResult]
    def to_text(self): return VisionDiagnosticReport(self.weaknesses).to_text()
    def save_json(self,path)->Path: return export_vision_json(self.weaknesses,path)
    def save_html(self,path)->Path: return export_vision_html(self.weaknesses,path)
class FailureLab:
    def __init__(self,predict_proba_fn,dataset): self.predict_proba_fn=predict_proba_fn; self.dataset=dataset
    def default_stress_tests(self): return [BrightnessTest(0.45),BlurTest(3.0),CompressionTest(20),OcclusionTest(0.40),RotationTest(30),CenterCropTest(0.60)]
    def run(self,stress_tests=None):
        if stress_tests is None: stress_tests=self.default_stress_tests()
        runner=VisionStressRunner(self.predict_proba_fn)
        results=[runner.run(self.dataset,s) for s in stress_tests]
        return FailureLabReport(rank_vision_results(results),results)
