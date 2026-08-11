from .ranking import WeaknessRanker
from .report import DiagnosticReport
from .runner import StressTestRunner
from .sweeps import BlurSweep,BrightnessSweep,CompressionSweep,OcclusionSweep,RotationSweep,CropSweep
def diagnose_model(predict_fn,dataset)->str:
    runner=StressTestRunner(predict_fn)
    sweeps=[BrightnessSweep().run(runner,dataset),BlurSweep().run(runner,dataset),CompressionSweep().run(runner,dataset),OcclusionSweep().run(runner,dataset),RotationSweep().run(runner,dataset),CropSweep().run(runner,dataset)]
    return DiagnosticReport(WeaknessRanker().rank(sweeps)).to_text()
