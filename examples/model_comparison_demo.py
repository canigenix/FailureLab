"""Compare the robustness of two real pretrained vision models."""

from collections import Counter
from pathlib import Path

import torch
from torchvision.datasets import OxfordIIITPet
from torchvision.models import (
    MobileNet_V3_Small_Weights,
    ResNet18_Weights,
    mobilenet_v3_small,
    resnet18,
)

from failurelab import FailureLab, compare_reports


DATA_ROOT = (
    Path(__file__).resolve().parent
    / "downloaded_data"
)

REPORT_DIR = (
    Path(__file__).resolve().parent
    / "reports"
)


BREED_MAPPING = {
    "Abyssinian": "Egyptian cat",
    "Bengal": "Egyptian cat",
    "Egyptian Mau": "Egyptian cat",
    "Maine Coon": "tabby",
    "American Bulldog": "American Staffordshire terrier",
    "American Pit Bull Terrier": "American Staffordshire terrier",
    "Basset Hound": "basset",
    "Beagle": "beagle",
    "Boxer": "boxer",
    "Chihuahua": "Chihuahua",
    "English Cocker Spaniel": "cocker spaniel",
    "English Setter": "English setter",
    "German Shorthaired": "German short-haired pointer",
    "Great Pyrenees": "Great Pyrenees",
    "Japanese Chin": "Japanese spaniel",
    "Keeshond": "keeshond",
    "Leonberger": "Leonberg",
    "Miniature Pinscher": "miniature pinscher",
    "Newfoundland": "Newfoundland",
    "Pomeranian": "Pomeranian",
    "Pug": "pug",
    "Saint Bernard": "Saint Bernard",
    "Samoyed": "Samoyed",
    "Scottish Terrier": "Scotch terrier",
    "Staffordshire Bull Terrier": "Staffordshire bullterrier",
    "Wheaten Terrier": "soft-coated wheaten terrier",
    "Yorkshire Terrier": "Yorkshire terrier",
}


# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

resnet_weights = ResNet18_Weights.DEFAULT

resnet = resnet18(
    weights=resnet_weights
)

resnet.eval()

resnet_preprocess = resnet_weights.transforms()


mobilenet_weights = MobileNet_V3_Small_Weights.DEFAULT

mobilenet = mobilenet_v3_small(
    weights=mobilenet_weights
)

mobilenet.eval()

mobilenet_preprocess = mobilenet_weights.transforms()


categories = resnet_weights.meta[
    "categories"
]

category_to_index = {
    name.lower(): index
    for index, name in enumerate(categories)
}


def resnet_predict(image):
    tensor = resnet_preprocess(
        image
    ).unsqueeze(0)

    with torch.no_grad():
        logits = resnet(
            tensor
        )

    return torch.softmax(
        logits,
        dim=1,
    )[0].cpu().numpy()


def mobilenet_predict(image):
    tensor = mobilenet_preprocess(
        image
    ).unsqueeze(0)

    with torch.no_grad():
        logits = mobilenet(
            tensor
        )

    return torch.softmax(
        logits,
        dim=1,
    )[0].cpu().numpy()


# ---------------------------------------------------------
# Dataset
# ---------------------------------------------------------

def load_dataset(
    samples_per_class=10,
):
    source_dataset = OxfordIIITPet(
        root=DATA_ROOT,
        split="test",
        target_types="category",
        download=True,
    )

    buckets = {}

    for image, target in source_dataset:
        pet_class = source_dataset.classes[
            target
        ]

        imagenet_name = BREED_MAPPING.get(
            pet_class
        )

        if imagenet_name is None:
            continue

        key = imagenet_name.lower()

        if key not in category_to_index:
            continue

        imagenet_target = (
            category_to_index[key]
        )

        bucket = buckets.setdefault(
            imagenet_target,
            []
        )

        if len(bucket) >= samples_per_class:
            continue

        bucket.append(
            (
                image.convert("RGB"),
                imagenet_target,
            )
        )

    dataset = []

    for samples in buckets.values():
        dataset.extend(
            samples
        )

    return dataset


dataset = load_dataset()

counts = Counter(
    target
    for _, target in dataset
)

print(
    f"Loaded {len(dataset)} images "
    f"across {len(counts)} classes."
)


# ---------------------------------------------------------
# Baseline — ResNet18
# ---------------------------------------------------------

print()
print("Evaluating baseline: ResNet18")
print("=============================")

baseline_lab = FailureLab(
    predict_proba_fn=resnet_predict,
    dataset=dataset,
)

baseline_report = baseline_lab.run()

baseline_envelope = baseline_lab.sweep_all()

baseline_report.with_failure_envelope(
    baseline_envelope
)

print(
    baseline_report.summary()
)


# ---------------------------------------------------------
# Candidate — MobileNet V3 Small
# ---------------------------------------------------------

print()
print(
    "Evaluating candidate: MobileNet V3 Small"
)
print(
    "========================================"
)

candidate_lab = FailureLab(
    predict_proba_fn=mobilenet_predict,
    dataset=dataset,
)

candidate_report = candidate_lab.run()

candidate_envelope = candidate_lab.sweep_all()

candidate_report.with_failure_envelope(
    candidate_envelope
)

print(
    candidate_report.summary()
)


# ---------------------------------------------------------
# Compare
# ---------------------------------------------------------

comparison = compare_reports(
    baseline_report,
    candidate_report,
)

print()
print("Model Comparison")
print("================")

print(
    comparison.summary()
)

for boundary in comparison.boundaries:
    if boundary.regression_reason == "threshold":
        status = "THRESHOLD REGRESSION"

    elif boundary.regression_reason == "worst_drop":
        status = "WORST-DROP REGRESSION"

    elif boundary.regression_reason == "both":
        status = "BOTH REGRESSED"

    else:
        status = boundary.threshold_status.upper()

    baseline_threshold = (
        "not reached"
        if boundary.baseline_threshold is None
        else str(boundary.baseline_threshold)
    )

    candidate_threshold = (
        "not reached"
        if boundary.candidate_threshold is None
        else str(boundary.candidate_threshold)
    )

    print()
    print(
        f"{boundary.stress_name.title()} — {status}"
    )

    print(
        f"  Threshold: "
        f"{baseline_threshold} → "
        f"{candidate_threshold}"
    )

    print(
        f"  Worst drop: "
        f"{boundary.baseline_worst_drop:.1%} → "
        f"{boundary.candidate_worst_drop:.1%} "
        f"({boundary.worst_drop_delta:+.1%})"
    )


# ---------------------------------------------------------
# Export reports and CI snapshots
# ---------------------------------------------------------

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

comparison_html = comparison.save_html(
    REPORT_DIR
    / "model_comparison.html"
)

comparison_json = comparison.save_json(
    REPORT_DIR
    / "model_comparison.json"
)

baseline_snapshot = baseline_report.save_snapshot(
    REPORT_DIR
    / "resnet18_snapshot.json"
)

candidate_snapshot = candidate_report.save_snapshot(
    REPORT_DIR
    / "mobilenet_v3_small_snapshot.json"
)


print()
print("Comparison reports saved")
print("========================")

print(
    f"HTML: {comparison_html}"
)

print(
    f"JSON: {comparison_json}"
)

print(
    f"Baseline snapshot: {baseline_snapshot}"
)

print(
    f"Candidate snapshot: {candidate_snapshot}"
)