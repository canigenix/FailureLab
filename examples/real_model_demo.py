"""Evaluate FailureLab on a balanced real-image dataset."""

from collections import Counter
from pathlib import Path

import torch
from torchvision.datasets import OxfordIIITPet
from torchvision.models import (
    ResNet18_Weights,
    resnet18,
)

from failurelab import FailureLab


# ---------------------------------------------------------
# Model
# ---------------------------------------------------------

weights = ResNet18_Weights.DEFAULT

model = resnet18(
    weights=weights
)

model.eval()

preprocess = weights.transforms()
categories = weights.meta["categories"]

category_to_index = {
    name.lower(): index
    for index, name in enumerate(categories)
}


def predict_proba_fn(image):
    """Return the complete ImageNet probability vector for one image."""

    tensor = preprocess(
        image
    ).unsqueeze(0)

    with torch.no_grad():
        logits = model(
            tensor
        )

        probabilities = torch.softmax(
            logits,
            dim=1,
        )[0]

    return probabilities.cpu().numpy()


# ---------------------------------------------------------
# Dataset
# ---------------------------------------------------------

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


def load_real_dataset(
    samples_per_class: int = 20,
):
    """Build a balanced Oxford-IIIT Pet subset."""

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

        imagenet_key = imagenet_name.lower()

        if imagenet_key not in category_to_index:
            continue

        imagenet_target = category_to_index[
            imagenet_key
        ]

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

    if not dataset:
        raise RuntimeError(
            "No compatible real images were found."
        )

    return dataset


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

dataset = load_real_dataset(
    samples_per_class=20
)

target_counts = Counter(
    target
    for _, target in dataset
)

print(
    f"Loaded {len(dataset)} images "
    f"across {len(target_counts)} ImageNet classes."
)

print()


# ---------------------------------------------------------
# Run FailureLab core evaluation
# ---------------------------------------------------------

lab = FailureLab(
    predict_proba_fn=predict_proba_fn,
    dataset=dataset,
)

report = lab.run()

print(
    report.to_text()
)

print()
print(
    report.summary()
)


# ---------------------------------------------------------
# Build complete failure envelope
# ---------------------------------------------------------

print()
print()
print("Running FailureLab severity sweeps...")
print()

envelope = lab.sweep_all()

report.with_failure_envelope(
    envelope
)


# ---------------------------------------------------------
# Print failure envelope
# ---------------------------------------------------------

print(
    "Failure Envelope"
)

print(
    "================"
)

for boundary in envelope.boundaries:
    print()
    print(
        boundary.stress_name.title()
    )

    print(
        f"  Worst top-1 drop: "
        f"{boundary.worst_top1_drop:.1%}"
    )

    if boundary.failure_threshold is None:
        print(
            "  Failure threshold: "
            "not reached"
        )

    else:
        print(
            f"  Failure threshold: "
            f"{boundary.failure_threshold}"
        )


# ---------------------------------------------------------
# Export complete reports
# ---------------------------------------------------------

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

json_path = report.save_json(
    REPORT_DIR
    / "failurelab_report.json"
)

html_path = report.save_html(
    REPORT_DIR
    / "failurelab_report.html"
)


print()
print()
print("Reports saved")
print("=============")

print(
    f"JSON: {json_path}"
)

print(
    f"HTML: {html_path}"
)