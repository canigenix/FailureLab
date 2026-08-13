from failurelab.visualization import plot_robustness_drops
from failurelab.vision_report import VisionWeakness


def test_plot_robustness_drops_returns_figure():
    weaknesses = [
        VisionWeakness(
            name="blur",
            severity="high",
            top1_drop=0.20,
            top5_drop=0.10,
            confidence_drop=0.15,
        ),
        VisionWeakness(
            name="rotation",
            severity="medium",
            top1_drop=0.08,
            top5_drop=0.03,
            confidence_drop=0.06,
        ),
    ]

    figure = plot_robustness_drops(weaknesses)

    assert figure is not None
    assert len(figure.axes) == 1


def test_plot_robustness_drops_saves_file(tmp_path):
    weaknesses = [
        VisionWeakness(
            name="blur",
            severity="high",
            top1_drop=0.20,
            top5_drop=0.10,
            confidence_drop=0.15,
        ),
    ]

    output = tmp_path / "robustness.png"

    figure = plot_robustness_drops(
        weaknesses,
        output_path=output,
    )

    assert figure is not None
    assert output.exists()
    assert output.stat().st_size > 0