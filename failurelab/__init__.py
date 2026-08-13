"""FailureLab public package interface."""

from failurelab.api import (
    
    FailureLab,
    FailureLabReport,
)
from failurelab.comparison import (
    BoundaryComparison,
    ModelComparison,
    RobustnessRegressionError,
    compare_reports,
)

from failurelab.custom_stress import CustomStressTest
from failurelab.failure_envelope import (
    FailureBoundary,
    FailureEnvelope,
)

__all__ = [
    "FailureLab",
    "FailureLabReport",
    "FailureBoundary",
    "FailureEnvelope",
    "BoundaryComparison",
    "ModelComparison",
    "RobustnessRegressionError",
    "compare_reports",
    "CustomStressTest",
    
]



__version__ = "0.2.0"