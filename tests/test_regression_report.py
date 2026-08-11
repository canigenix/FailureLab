from failurelab.regression import RegressionCheck
from failurelab.regression_report import RegressionReport


def test_regression_report_passes():
    checks = [
        RegressionCheck(
            stress_name="brightness_0.45",
            passed=True,
            failures=(),
        ),
        RegressionCheck(
            stress_name="jpeg_20",
            passed=True,
            failures=(),
        ),
    ]

    report = RegressionReport(
        checks
    )

    assert report.passed is True
    assert report.failed_count == 0

    text = report.to_text()

    assert "RESULT: PASSED" in text
    assert "brightness_0.45" in text


def test_regression_report_fails():
    checks = [
        RegressionCheck(
            stress_name="blur_3.00",
            passed=False,
            failures=(
                "top-1 drop 30.4% exceeds allowed 25.0%",
            ),
        ),
        RegressionCheck(
            stress_name="jpeg_20",
            passed=True,
            failures=(),
        ),
    ]

    report = RegressionReport(
        checks
    )

    assert report.passed is False
    assert report.failed_count == 1

    text = report.to_text()

    assert "blur_3.00" in text
    assert "FAIL" in text
    assert "RESULT: FAILED" in text


def test_regression_report_counts_multiple_failures():
    checks = [
        RegressionCheck(
            stress_name="blur_3.00",
            passed=False,
            failures=("failure one",),
        ),
        RegressionCheck(
            stress_name="occlusion_0.40",
            passed=False,
            failures=("failure two",),
        ),
        RegressionCheck(
            stress_name="jpeg_20",
            passed=True,
            failures=(),
        ),
    ]

    report = RegressionReport(
        checks
    )

    assert report.failed_count == 2