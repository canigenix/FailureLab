"""Export FailureLab diagnostics into portable report files."""

from __future__ import annotations

import html
import json
from pathlib import Path

from failurelab.recommendations import Recommendation
from failurelab.score import RobustnessScore
from failurelab.vision_report import VisionWeakness


def export_vision_json(
    weaknesses: list[VisionWeakness],
    path,
    robustness_score: RobustnessScore | None = None,
    recommendations: list[Recommendation] | None = None,
) -> Path:
    """Export ranked vision weaknesses as JSON."""

    path = Path(path)

    payload = {
        "failurelab_version": "0.1.0",
        "robustness_score": (
            None
            if robustness_score is None
            else {
                "score": robustness_score.score,
                "grade": robustness_score.grade,
                "status": robustness_score.status,
                "average_degradation": (
                    robustness_score.average_degradation
                ),
                "worst_degradation": (
                    robustness_score.worst_degradation
                ),
            }
        ),
        "weaknesses": [
            {
                "name": weakness.name,
                "severity": weakness.severity,
                "top1_drop": weakness.top1_drop,
                "top5_drop": weakness.top5_drop,
                "confidence_drop": weakness.confidence_drop,
            }
            for weakness in weaknesses
        ],
        "recommendations": [
            {
                "weakness_name": recommendation.weakness_name,
                "severity": recommendation.severity,
                "diagnosis": recommendation.diagnosis,
                "likely_cause": recommendation.likely_cause,
                "suggested_action": recommendation.suggested_action,
            }
            for recommendation in (
                recommendations or []
            )
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


def export_vision_html(
    weaknesses: list[VisionWeakness],
    path,
    robustness_score: RobustnessScore | None = None,
    recommendations: list[Recommendation] | None = None,
) -> Path:
    """Export ranked vision weaknesses as standalone HTML."""

    path = Path(path)

    rows = []

    for position, weakness in enumerate(
        weaknesses,
        start=1,
    ):
        severity_class = html.escape(
            weakness.severity.lower()
        )

        rows.append(
            f"""
            <tr>
                <td>{position}</td>
                <td>{html.escape(weakness.name.title())}</td>
                <td>
                    <span class="severity {severity_class}">
                        {html.escape(weakness.severity.title())}
                    </span>
                </td>
                <td>{weakness.top1_drop:.1%}</td>
                <td>{weakness.top5_drop:.1%}</td>
                <td>{weakness.confidence_drop:.1%}</td>
            </tr>
            """
        )

    table_rows = "\n".join(rows)

    if robustness_score is None:
        score_section = ""
    else:
        score_section = f"""
        <section class="score-card">
            <div class="score-number">
                {robustness_score.score:.1f}
            </div>

            <div class="score-details">
                <div class="score-label">
                    Robustness Score
                </div>

                <div class="grade">
                    Grade {html.escape(robustness_score.grade)}
                </div>

                <div class="status">
                    {html.escape(robustness_score.status)}
                </div>

                <div class="score-metrics">
                    Average degradation:
                    {robustness_score.average_degradation:.1%}
                    &nbsp; | &nbsp;
                    Worst degradation:
                    {robustness_score.worst_degradation:.1%}
                </div>
            </div>
        </section>
        """

    recommendation_cards = []

    for recommendation in (
        recommendations or []
    ):
        severity_class = html.escape(
            recommendation.severity.lower()
        )

        recommendation_cards.append(
            f"""
            <article class="recommendation-card">

                <div class="recommendation-header">
                    <h3>
                        {html.escape(
                            recommendation.weakness_name.title()
                        )}
                    </h3>

                    <span class="severity {severity_class}">
                        {html.escape(
                            recommendation.severity.title()
                        )}
                    </span>
                </div>

                <p>
                    <strong>Diagnosis:</strong>
                    {html.escape(recommendation.diagnosis)}
                </p>

                <p>
                    <strong>Likely cause:</strong>
                    {html.escape(recommendation.likely_cause)}
                </p>

                <p>
                    <strong>Recommended action:</strong>
                    {html.escape(recommendation.suggested_action)}
                </p>

            </article>
            """
        )

    if recommendation_cards:
        recommendations_section = f"""
        <section class="recommendations">

            <h2>Priority Recommendations</h2>

            <p class="section-description">
                Suggested actions for the most meaningful robustness weaknesses.
            </p>

            {"".join(recommendation_cards)}

        </section>
        """
    else:
        recommendations_section = ""

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>FailureLab Vision Report</title>

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

            max-width: 1100px;
            margin: 0 auto;
            padding: 48px 24px;
            line-height: 1.5;
            background: #f7f8fa;
            color: #1f2328;
        }}

        .container {{
            background: white;
            border: 1px solid #dfe3e8;
            border-radius: 16px;
            padding: 36px;
        }}

        h1 {{
            margin-top: 0;
            margin-bottom: 6px;
            font-size: 32px;
        }}

        h2 {{
            margin-top: 36px;
            margin-bottom: 4px;
        }}

        .subtitle,
        .section-description {{
            color: #667085;
        }}

        .subtitle {{
            margin-bottom: 30px;
        }}

        .score-card {{
            display: flex;
            align-items: center;
            gap: 26px;
            padding: 26px;
            margin-bottom: 34px;
            border: 1px solid #dfe3e8;
            border-radius: 14px;
            background: #fafafa;
        }}

        .score-number {{
            font-size: 58px;
            line-height: 1;
            font-weight: 700;
        }}

        .score-label {{
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #667085;
        }}

        .grade {{
            font-size: 24px;
            font-weight: 650;
            margin-top: 4px;
        }}

        .status,
        .score-metrics {{
            margin-top: 3px;
            color: #667085;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #667085;
            background: #f8f9fb;
        }}

        th,
        td {{
            padding: 14px 12px;
            border-bottom: 1px solid #e8eaed;
            text-align: left;
        }}

        .severity {{
            display: inline-block;
            padding: 4px 9px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 650;
        }}

        .critical {{
            background: #fdecec;
            color: #b42318;
        }}

        .high {{
            background: #fff1e7;
            color: #b54708;
        }}

        .medium {{
            background: #fff8db;
            color: #8a6100;
        }}

        .low {{
            background: #eaf7ee;
            color: #137333;
        }}

        .recommendation-card {{
            padding: 20px;
            margin-top: 16px;
            border: 1px solid #e1e4e8;
            border-radius: 12px;
            background: #fcfcfd;
        }}

        .recommendation-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }}

        .recommendation-header h3 {{
            margin: 0;
        }}

        .recommendation-card p {{
            margin-bottom: 0;
        }}
    </style>
</head>

<body>

    <main class="container">

        <h1>FailureLab Vision Robustness Report</h1>

        <div class="subtitle">
            Ranked model weaknesses discovered through controlled stress testing.
        </div>

        {score_section}

        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Stress Type</th>
                    <th>Severity</th>
                    <th>Top-1 Drop</th>
                    <th>Top-5 Drop</th>
                    <th>Confidence Drop</th>
                </tr>
            </thead>

            <tbody>
                {table_rows}
            </tbody>
        </table>

        {recommendations_section}

    </main>

</body>
</html>
"""

    path.write_text(
        document,
        encoding="utf-8",
    )

    return path