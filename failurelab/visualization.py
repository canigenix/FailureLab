from __future__ import annotations

from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from .vision_report import VisionWeakness


def plot_robustness_drops(
    weaknesses: list[VisionWeakness],
    output_path: str | Path | None = None,
):
    if not weaknesses:
        raise ValueError("weaknesses must contain at least one result.")

    names = [w.name for w in weaknesses]
    top1 = [w.top1_drop for w in weaknesses]
    top5 = [w.top5_drop for w in weaknesses]
    confidence = [w.confidence_drop for w in weaknesses]

    x = list(range(len(names)))
    width = 0.25

    fig = Figure(figsize=(10, 6))
    FigureCanvasAgg(fig)

    ax = fig.subplots()

    ax.bar(
        [i - width for i in x],
        top1,
        width,
        label="Top-1 drop",
    )
    ax.bar(
        x,
        top5,
        width,
        label="Top-5 drop",
    )
    ax.bar(
        [i + width for i in x],
        confidence,
        width,
        label="Confidence drop",
    )

    ax.set_title("FailureLab Robustness Degradation")
    ax.set_ylabel("Performance drop")
    ax.set_xticks(x)
    ax.set_xticklabels(
        names,
        rotation=30,
        ha="right",
    )
    ax.legend()

    fig.tight_layout()

    if output_path is not None:
        fig.savefig(Path(output_path))

    return fig