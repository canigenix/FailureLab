import failurelab


def test_public_api_has_no_duplicate_names():
    assert len(
        failurelab.__all__
    ) == len(
        set(
            failurelab.__all__
        )
    )


def test_every_public_api_name_exists():
    missing = [
        name
        for name in failurelab.__all__
        if not hasattr(
            failurelab,
            name,
        )
    ]

    assert missing == []


def test_core_public_api_is_stable():
    expected = {
        "FailureLab",
        "FailureLabReport",
        "ConfiguredSuiteRunner",
        "ExperimentRunner",
        "compare_reports",
        "EvaluationProfile",
        "EvaluationPlan",
        "EvaluationReport",
        "EvaluationStepResult",
        "run_evaluation",
        "EvaluationSummary",
        "EvaluationHealth",
        "EvaluationIntelligence",
        "EvaluationGateConfig",
        "EvaluationGateResult",
        "evaluate_intelligence_gate",
        "run_evaluation_gate",
        "evaluate_report_gate",
    }

    assert expected.issubset(
        set(
            failurelab.__all__
        )
    )


def test_resolution_and_forecast_are_public():
    expected = {
        "FailureResolution",
        "ResolutionStatus",
        "analyze_failure_resolution",
        "FailureResolutionReport",
        "FailureForecast",
        "ForecastStatus",
        "forecast_failure_trajectory",
        "FailureForecastReport",
    }

    assert expected.issubset(
        set(
            failurelab.__all__
        )
    )


def test_evaluation_v014_api_is_public():
    expected = {
        "EvaluationInputs",
        "build_evaluation_inputs",
        "EvaluationSummary",
        "build_evaluation_summary",
        "EvaluationHealth",
        "classify_evaluation_health",
        "EvaluationIntelligence",
        "build_evaluation_intelligence",
        "EvaluationGateConfig",
        "EvaluationGateResult",
        "evaluate_intelligence_gate",
        "run_evaluation_gate",
        "evaluate_report_gate",
    }

    assert expected.issubset(
        set(
            failurelab.__all__
        )
    )


def test_package_version_exists():
    assert isinstance(
        failurelab.__version__,
        str,
    )

    assert failurelab.__version__