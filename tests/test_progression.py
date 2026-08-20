import pytest

from failurelab.progression import (
    ProgressionHistoryReport,
    ProgressionPoint,
    ProgressionReport,
    analyze_progression,
    analyze_progression_history,
    classify_progression,
    classify_progression_trend,
    failure_rate_delta,
    summarize_progression_history,
)


def test_failure_rate_delta_detects_regression():
    start = ProgressionPoint("v1", 0.10)
    end = ProgressionPoint("v2", 0.18)

    assert failure_rate_delta(start, end) == pytest.approx(0.08)


def test_failure_rate_delta_detects_improvement():
    start = ProgressionPoint("v1", 0.20)
    end = ProgressionPoint("v2", 0.12)

    assert failure_rate_delta(start, end) == pytest.approx(-0.08)


def test_failure_rate_delta_detects_no_change():
    start = ProgressionPoint("v1", 0.15)
    end = ProgressionPoint("v2", 0.15)

    assert failure_rate_delta(start, end) == pytest.approx(0.0)


def test_classify_progression_regressed():
    start = ProgressionPoint("v1", 0.10)
    end = ProgressionPoint("v2", 0.18)

    assert classify_progression(start, end) == "regressed"


def test_classify_progression_improved():
    start = ProgressionPoint("v1", 0.20)
    end = ProgressionPoint("v2", 0.12)

    assert classify_progression(start, end) == "improved"


def test_classify_progression_stable():
    start = ProgressionPoint("v1", 0.15)
    end = ProgressionPoint("v2", 0.15)

    assert classify_progression(start, end) == "stable"


def test_classify_progression_respects_tolerance():
    start = ProgressionPoint("v1", 0.10)
    end = ProgressionPoint("v2", 0.105)

    assert classify_progression(
        start,
        end,
        tolerance=0.01,
    ) == "stable"


def test_analyze_progression_returns_report():
    start = ProgressionPoint("v1", 0.10)
    end = ProgressionPoint("v2", 0.18)

    report = analyze_progression(start, end)

    assert isinstance(report, ProgressionReport)
    assert report.start == start
    assert report.end == end
    assert report.delta == pytest.approx(0.08)
    assert report.status == "regressed"


def test_analyze_progression_respects_tolerance():
    start = ProgressionPoint("v1", 0.10)
    end = ProgressionPoint("v2", 0.105)

    report = analyze_progression(
        start,
        end,
        tolerance=0.01,
    )

    assert report.status == "stable"
    assert report.delta == pytest.approx(0.005)


def test_analyze_progression_history():
    points = [
        ProgressionPoint("v1", 0.20),
        ProgressionPoint("v2", 0.15),
        ProgressionPoint("v3", 0.15),
        ProgressionPoint("v4", 0.22),
    ]

    reports = analyze_progression_history(points)

    assert len(reports) == 3
    assert reports[0].status == "improved"
    assert reports[1].status == "stable"
    assert reports[2].status == "regressed"


def test_analyze_progression_history_respects_tolerance():
    points = [
        ProgressionPoint("v1", 0.10),
        ProgressionPoint("v2", 0.105),
        ProgressionPoint("v3", 0.13),
    ]

    reports = analyze_progression_history(
        points,
        tolerance=0.01,
    )

    assert reports[0].status == "stable"
    assert reports[1].status == "regressed"


def test_analyze_progression_history_with_single_point():
    assert analyze_progression_history(
        [ProgressionPoint("v1", 0.10)]
    ) == []


def test_analyze_progression_history_with_no_points():
    assert analyze_progression_history([]) == []


def test_classify_progression_trend_improving():
    points = [
        ProgressionPoint("v1", 0.30),
        ProgressionPoint("v2", 0.20),
        ProgressionPoint("v3", 0.10),
    ]

    transitions = analyze_progression_history(points)

    assert classify_progression_trend(transitions) == "improving"


def test_classify_progression_trend_degrading():
    points = [
        ProgressionPoint("v1", 0.10),
        ProgressionPoint("v2", 0.20),
        ProgressionPoint("v3", 0.30),
    ]

    transitions = analyze_progression_history(points)

    assert classify_progression_trend(transitions) == "degrading"


def test_classify_progression_trend_stable():
    points = [
        ProgressionPoint("v1", 0.10),
        ProgressionPoint("v2", 0.10),
        ProgressionPoint("v3", 0.10),
    ]

    transitions = analyze_progression_history(points)

    assert classify_progression_trend(transitions) == "stable"


def test_classify_progression_trend_volatile():
    points = [
        ProgressionPoint("v1", 0.20),
        ProgressionPoint("v2", 0.10),
        ProgressionPoint("v3", 0.25),
    ]

    transitions = analyze_progression_history(points)

    assert classify_progression_trend(transitions) == "volatile"


def test_summarize_progression_history():
    points = [
        ProgressionPoint("v1", 0.20),
        ProgressionPoint("v2", 0.15),
        ProgressionPoint("v3", 0.15),
        ProgressionPoint("v4", 0.22),
        ProgressionPoint("v5", 0.12),
    ]

    report = summarize_progression_history(points)

    assert isinstance(report, ProgressionHistoryReport)
    assert report.overall_delta == pytest.approx(-0.08)
    assert report.overall_status == "improved"
    assert report.trend == "volatile"

    assert report.improved_count == 2
    assert report.stable_count == 1
    assert report.regressed_count == 1

    assert len(report.transitions) == 4


def test_summarize_progression_history_respects_tolerance():
    points = [
        ProgressionPoint("v1", 0.10),
        ProgressionPoint("v2", 0.105),
    ]

    report = summarize_progression_history(
        points,
        tolerance=0.01,
    )

    assert report.overall_status == "stable"
    assert report.trend == "stable"
    assert report.stable_count == 1


def test_summarize_progression_history_requires_two_points():
    with pytest.raises(
        ValueError,
        match="At least two progression points",
    ):
        summarize_progression_history(
            [ProgressionPoint("v1", 0.10)]
        )