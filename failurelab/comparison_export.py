"""Export FailureLab model-comparison reports."""

from __future__ import annotations

import html
import json
from pathlib import Path

from failurelab.comparison import ModelComparison


def _reason_label(reason: str) -> str:
    labels = {
        "threshold": "Threshold Regression",
        "worst_drop": "Worst-Drop Regression",
        "both": "Threshold + Worst-Drop Regression",
        "none": "No Regression",
    }

    return labels.get(
        reason,
        reason.replace("_", " ").title(),
    )


def export_comparison_json(
    comparison: ModelComparison,
    path,
) -> Path:
    """Export model comparison as JSON."""

    path = Path(path)

    payload = {
        "baseline_score": comparison.baseline_score,
        "candidate_score": comparison.candidate_score,
        "score_delta": comparison.score_delta,
        "passed": comparison.passed,
        "regression_count": len(comparison.regressions),
        "boundaries": [
            {
                "stress_name": boundary.stress_name,
                "baseline_threshold": boundary.baseline_threshold,
                "candidate_threshold": boundary.candidate_threshold,
                "baseline_worst_drop": boundary.baseline_worst_drop,
                "candidate_worst_drop": boundary.candidate_worst_drop,
                "worst_drop_delta": boundary.worst_drop_delta,
                "threshold_status": boundary.threshold_status,
                "regression": boundary.regression,
                "regression_reason": boundary.regression_reason,
            }
            for boundary in comparison.boundaries
        ],
    }

    path.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    return path


def export_comparison_html(
    comparison: ModelComparison,
    path,
) -> Path:
    """Export model comparison as standalone HTML."""

    path = Path(path)

    result_text = (
        "PASS"
        if comparison.passed
        else "REGRESSION DETECTED"
    )

    result_class = (
        "pass"
        if comparison.passed
        else "fail"
    )

    rows = []

    for boundary in comparison.boundaries:
        baseline_threshold = (
            "Not reached"
            if boundary.baseline_threshold is None
            else str(boundary.baseline_threshold)
        )

        candidate_threshold = (
            "Not reached"
            if boundary.candidate_threshold is None
            else str(boundary.candidate_threshold)
        )

        row_class = (
            "regression-row"
            if boundary.regression
            else ""
        )

        reason = _reason_label(
            boundary.regression_reason
        )

        rows.append(
            f"""
            <tr class="{row_class}">
                <td>{html.escape(boundary.stress_name.title())}</td>
                <td>{html.escape(baseline_threshold)}</td>
                <td>{html.escape(candidate_threshold)}</td>
                <td>{boundary.baseline_worst_drop:.1%}</td>
                <td>{boundary.candidate_worst_drop:.1%}</td>
                <td>{boundary.worst_drop_delta:+.1%}</td>
                <td>{html.escape(boundary.threshold_status.title())}</td>
                <td>{html.escape(reason)}</td>
            </tr>
            """
        )

    regression_cards = []

    for boundary in comparison.regressions:
        reason = _reason_label(
            boundary.regression_reason
        )

        details = []

        if boundary.regression_reason in {
            "threshold",
            "both",
        }:
            baseline_threshold = (
                "Not reached"
                if boundary.baseline_threshold is None
                else str(boundary.baseline_threshold)
            )

            candidate_threshold = (
                "Not reached"
                if boundary.candidate_threshold is None
                else str(boundary.candidate_threshold)
            )

            details.append(
                f"""
                <p>
                    <strong>Failure threshold:</strong>
                    {html.escape(baseline_threshold)}
                    →
                    {html.escape(candidate_threshold)}
                </p>
                """
            )

        if boundary.regression_reason in {
            "worst_drop",
            "both",
        }:
            details.append(
                f"""
                <p>
                    <strong>Worst degradation:</strong>
                    {boundary.baseline_worst_drop:.1%}
                    →
                    {boundary.candidate_worst_drop:.1%}
                    ({boundary.worst_drop_delta:+.1%})
                </p>
                """
            )

        regression_cards.append(
            f"""
            <article class="regression-card">
                <div class="regression-title">
                    {html.escape(boundary.stress_name.title())}
                </div>

                <div class="reason">
                    {html.escape(reason)}
                </div>

                {"".join(details)}
            </article>
            """
        )

    if regression_cards:
        regression_section = f"""
        <section>
            <h2>Regression Details</h2>

            <p class="muted">
                Stress families where the candidate model became less robust.
            </p>

            {"".join(regression_cards)}
        </section>
        """
    else:
        regression_section = """
        <section>
            <h2>Regression Details</h2>
            <p class="pass-message">
                No robustness regressions detected.
            </p>
        </section>
        """

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>FailureLab Model Comparison</title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Arial,
                sans-serif;

            max-width: 1180px;
            margin: 0 auto;
            padding: 48px 24px;
            background: #f7f8fa;
            color: #1f2328;
            line-height: 1.5;
        }}

        .container {{
            background: white;
            border: 1px solid #dfe3e8;
            border-radius: 16px;
            padding: 36px;
        }}

        h1 {{
            margin-top: 0;
        }}

        h2 {{
            margin-top: 36px;
        }}

        .muted {{
            color: #667085;
        }}

        .result {{
            display: inline-block;
            padding: 8px 14px;
            border-radius: 999px;
            font-weight: 700;
            margin-bottom: 24px;
        }}

        .pass {{
            background: #eaf7ee;
            color: #137333;
        }}

        .fail {{
            background: #fdecec;
            color: #b42318;
        }}

        .score-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }}

        .score-card {{
            border: 1px solid #dfe3e8;
            border-radius: 12px;
            padding: 18px;
            background: #fafafa;
        }}

        .label {{
            color: #667085;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .value {{
            font-size: 28px;
            font-weight: 700;
            margin-top: 4px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th,
        td {{
            padding: 13px 10px;
            border-bottom: 1px solid #e8eaed;
            text-align: left;
        }}

        th {{
            background: #f8f9fb;
            color: #667085;
            font-size: 12px;
            text-transform: uppercase;
        }}

        .regression-row {{
            background: #fff6f6;
        }}

        .regression-card {{
            margin-top: 14px;
            padding: 18px;
            border: 1px solid #f2c6c6;
            border-radius: 12px;
            background: #fff8f8;
        }}

        .regression-title {{
            font-size: 18px;
            font-weight: 700;
        }}

        .reason {{
            color: #b42318;
            font-weight: 650;
            margin-top: 2px;
        }}

        .regression-card p {{
            margin-bottom: 0;
        }}

        .pass-message {{
            padding: 14px;
            border-radius: 10px;
            background: #eaf7ee;
            color: #137333;
            font-weight: 650;
        }}
    </style>
</head>

<body>

    <main class="container">

        <h1>FailureLab Model Comparison</h1>

        <div class="result {result_class}">
            {result_text}
        </div>

        <div class="score-grid">

            <div class="score-card">
                <div class="label">Baseline Score</div>
                <div class="value">
                    {comparison.baseline_score:.1f}
                </div>
            </div>

            <div class="score-card">
                <div class="label">Candidate Score</div>
                <div class="value">
                    {comparison.candidate_score:.1f}
                </div>
            </div>

            <div class="score-card">
                <div class="label">Score Delta</div>
                <div class="value">
                    {comparison.score_delta:+.1f}
                </div>
            </div>

        </div>

        <h2>Stress-by-Stress Comparison</h2>

        <table>
            <thead>
                <tr>
                    <th>Stress</th>
                    <th>Baseline Threshold</th>
                    <th>Candidate Threshold</th>
                    <th>Baseline Worst Drop</th>
                    <th>Candidate Worst Drop</th>
                    <th>Drop Delta</th>
                    <th>Threshold Status</th>
                    <th>Regression Type</th>
                </tr>
            </thead>

            <tbody>
                {"".join(rows)}
            </tbody>
        </table>

        {regression_section}

    </main>

</body>
</html>
"""

    path.write_text(
        document,
        encoding="utf-8",
    )

    return path