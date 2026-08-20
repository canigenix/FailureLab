from dataclasses import dataclass
from typing import Literal, Sequence


ProgressionStatus = Literal["improved", "stable", "regressed"]
ProgressionTrend = Literal["improving", "stable", "degrading", "volatile"]


@dataclass(frozen=True)
class ProgressionPoint:
    """A model checkpoint or version with its observed failure rate."""

    label: str
    failure_rate: float


@dataclass(frozen=True)
class ProgressionReport:
    """Summary of failure-rate change between two progression points."""

    start: ProgressionPoint
    end: ProgressionPoint
    delta: float
    status: ProgressionStatus


@dataclass(frozen=True)
class ProgressionHistoryReport:
    """Summary of failure progression across multiple checkpoints."""

    points: tuple[ProgressionPoint, ...]
    transitions: tuple[ProgressionReport, ...]
    overall_delta: float
    overall_status: ProgressionStatus
    trend: ProgressionTrend
    improved_count: int
    stable_count: int
    regressed_count: int


def failure_rate_delta(
    start: ProgressionPoint,
    end: ProgressionPoint,
) -> float:
    return end.failure_rate - start.failure_rate


def classify_progression(
    start: ProgressionPoint,
    end: ProgressionPoint,
    tolerance: float = 0.0,
) -> ProgressionStatus:
    delta = failure_rate_delta(start, end)

    if delta > tolerance:
        return "regressed"

    if delta < -tolerance:
        return "improved"

    return "stable"


def analyze_progression(
    start: ProgressionPoint,
    end: ProgressionPoint,
    tolerance: float = 0.0,
) -> ProgressionReport:
    return ProgressionReport(
        start=start,
        end=end,
        delta=failure_rate_delta(start, end),
        status=classify_progression(
            start,
            end,
            tolerance=tolerance,
        ),
    )


def analyze_progression_history(
    points: Sequence[ProgressionPoint],
    tolerance: float = 0.0,
) -> list[ProgressionReport]:
    if len(points) < 2:
        return []

    return [
        analyze_progression(
            points[index],
            points[index + 1],
            tolerance=tolerance,
        )
        for index in range(len(points) - 1)
    ]


def classify_progression_trend(
    transitions: Sequence[ProgressionReport],
) -> ProgressionTrend:
    if not transitions:
        return "stable"

    improved = sum(
        transition.status == "improved"
        for transition in transitions
    )
    regressed = sum(
        transition.status == "regressed"
        for transition in transitions
    )

    if improved and regressed:
        return "volatile"

    if improved:
        return "improving"

    if regressed:
        return "degrading"

    return "stable"


def summarize_progression_history(
    points: Sequence[ProgressionPoint],
    tolerance: float = 0.0,
) -> ProgressionHistoryReport:
    if len(points) < 2:
        raise ValueError(
            "At least two progression points are required."
        )

    transitions = analyze_progression_history(
        points,
        tolerance=tolerance,
    )

    overall_delta = failure_rate_delta(
        points[0],
        points[-1],
    )

    overall_status = classify_progression(
        points[0],
        points[-1],
        tolerance=tolerance,
    )

    improved_count = sum(
        report.status == "improved"
        for report in transitions
    )
    stable_count = sum(
        report.status == "stable"
        for report in transitions
    )
    regressed_count = sum(
        report.status == "regressed"
        for report in transitions
    )

    return ProgressionHistoryReport(
        points=tuple(points),
        transitions=tuple(transitions),
        overall_delta=overall_delta,
        overall_status=overall_status,
        trend=classify_progression_trend(transitions),
        improved_count=improved_count,
        stable_count=stable_count,
        regressed_count=regressed_count,
    )