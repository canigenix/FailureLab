from .class_analysis import analyze_class_robustness


def top_vulnerable_classes(
    result,
    categories,
    limit: int = 5,
    minimum_reliable_samples: int = 10,
):
    rows = analyze_class_robustness(
        result.baseline_probabilities,
        result.stressed_probabilities,
        result.targets,
    )

    return [
        {
            "class_name": categories[r.class_index],
            "sample_count": r.sample_count,
            "accuracy_drop": r.accuracy_drop,
            "confidence_drop": r.confidence_drop,
            "stressed_failure_rate": r.stressed_failure_rate,
            "prediction_flip_rate": r.prediction_flip_rate,
            "top_confusion_class": (
    categories[r.top_confusion_class]
    if r.top_confusion_class is not None
    else None
),
            "top_confusion_rate": r.top_confusion_rate,
            "reliable": r.sample_count >= minimum_reliable_samples,
        }
        for r in rows[:limit]
    ]