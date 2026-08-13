FailureLab

Find where vision models fail — before those failures reach production.

FailureLab is an open-source Python framework for stress-testing computer vision models, measuring robustness degradation, and detecting regressions between model versions.

Instead of asking only "How accurate is my model?", FailureLab asks:

What breaks it, how badly does it break, and did the next version get worse?






FailureLab v0.2.0

Version 0.2.0 expands FailureLab beyond aggregate robustness metrics with deeper failure analysis and developer tooling:

Per-class vulnerability analysis

Stressed failure-rate and prediction-flip analysis

Top confusion-target discovery

Custom user-defined stress tests

Robustness degradation visualizations

failurelab visualize command-line workflow

Headless PNG generation for CI and server environments

Optional visualization dependencies to keep the core installation lightweight

What FailureLab Does

FailureLab deliberately degrades images using realistic perturbations and measures how model behavior changes.

```text
                     FailureLab
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   Stress Model     Diagnose Failure   Compare Versions
        │                │                │
   Brightness        Weaknesses        Baseline
   Blur              Severity             vs
   Compression       Score             Candidate
   Occlusion         Thresholds           │
   Rotation          Recommendations      ▼
   Crop                              Regression Gate
                                          │
                                     PASS / FAIL
```

A typical evaluation can produce:

```text
FailureLab score: 72.9/100 (C) — Needs Improvement.
Primary weakness: Occlusion.

Occlusion   CRITICAL   Top-1 drop: 50.2%
Blur        CRITICAL   Top-1 drop: 30.4%
Rotation    MEDIUM     Top-1 drop:  7.3%
```

FailureLab can then sweep perturbation severity to determine when failure begins, save the result as a robustness snapshot, and compare it against future model versions.

Why FailureLab?

Clean validation accuracy does not tell you how a model behaves when production inputs are imperfect.

A model that performs well on clean images may become unreliable when an image is:

partially occluded

out of focus

compressed

rotated

tightly cropped

poorly illuminated

FailureLab turns these conditions into repeatable robustness tests.

That enables a workflow like:

```text
Train Model
    │
    ▼
Run FailureLab
    │
    ▼
Measure Failure Envelope
    │
    ▼
Save Robustness Snapshot
    │
    ▼
Train Candidate Model
    │
    ▼
Compare Against Baseline
    │
    ├──── PASS ────► Continue
    │
    └──── FAIL ────► Block Regression
```

The goal is to move robustness testing into the development and CI/CD process, rather than discovering model weaknesses after deployment.

Features

FailureLab currently provides:

Six built-in vision stress tests

Top-1 accuracy degradation analysis

Top-5 accuracy degradation analysis

Confidence degradation analysis

Automatic severity classification

Ranked model weaknesses

Robustness score from 0–100

Human-readable robustness grades

Actionable recommendations

Multi-severity stress sweeps

Failure-threshold detection

Model failure envelopes

HTML reports

JSON reports

Reusable robustness snapshots

Baseline-vs-candidate model comparison

Threshold regression detection

Worst-case degradation regression detection

Configurable regression tolerance

Python CI robustness gates

Command-line CI enforcement

Per-class robustness analysis

Per-class stressed failure rates

Prediction flip-rate analysis

Top confusion-class detection

Custom user-defined stress tests

Robustness degradation PNG visualization

Headless visualization for CI/server environments

failurelab visualize CLI command

Installation

From the repository:

```bash
pip install .
```

For development:

```bash
pip install -e .
```

To install the optional PyTorch dependencies used by the vision examples:

```bash
pip install ".[vision]"
```

Verify the installation:

```bash
failurelab --version
```

Example:

```text
failurelab 0.2.0
```

Quick Start

FailureLab works with a prediction function that accepts an image and returns class probabilities.

```python
from failurelab import FailureLab

lab = FailureLab(
    predict_proba_fn=predict_proba,
    dataset=dataset,
)

report = lab.run()

print(report.summary())
```

Example output:

```text
FailureLab score: 72.9/100 (C) — Needs Improvement. Primary weakness: Occlusion.
```

Dataset Format

The dataset supplied to FailureLab should contain image/label pairs:

```python
dataset = [
    (image_1, class_index_1),
    (image_2, class_index_2),
    (image_3, class_index_3),
]
```

The prediction function should return a probability vector for one image:

```python
def predict_proba(image):
    ...
    return probabilities
```

Built-In Stress Tests

FailureLab currently evaluates six common forms of visual degradation.

Brightness

Tests sensitivity to reduced image brightness.

```python
BrightnessTest(factor=0.45)
```

Blur

Tests sensitivity to lost detail and out-of-focus images.

```python
BlurTest(radius=3.0)
```

Compression

Tests sensitivity to JPEG artifacts and information loss.

```python
CompressionTest(quality=20)
```

Occlusion

Tests what happens when part of the object is hidden.

```python
OcclusionTest(fraction=0.40)
```

Rotation

Tests orientation sensitivity.

```python
RotationTest(degrees=30)
```

Crop

Tests dependence on image boundaries and surrounding context.

```python
CenterCropTest(fraction=0.60)
```

Per-Class Failure Analysis

Aggregate accuracy can hide classes that fail much earlier than the model as a whole. FailureLab v0.2.0 can analyze robustness separately for each target class.

Per-class results include:

sample count

baseline and stressed accuracy

accuracy drop

baseline and stressed target confidence

confidence drop

stressed failure rate

prediction flip rate

most common stressed confusion target

This makes it possible to identify cases where a stress condition disproportionately harms one class even when aggregate model metrics still look acceptable.

Custom Stress Tests

FailureLab v0.2.0 supports user-defined image transformations through CustomStressTest, allowing project-specific perturbations to run through the same robustness pipeline as built-in tests.

from failurelab import CustomStressTest

custom_test = CustomStressTest(
    name="custom_shift",
    transform=lambda image: image,
)

Custom tests make the framework extensible without requiring changes to FailureLab's built-in corruption modules.

Robustness Visualization

Install visualization support with:

pip install ".[visualization]"

Generate robustness-drop charts programmatically:

from failurelab.visualization import plot_robustness_drops

plot_robustness_drops(
    weaknesses,
    output_path="robustness.png",
)

The visualization compares Top-1 accuracy drop, Top-5 accuracy drop, and confidence drop across detected weaknesses. Chart generation uses a headless backend so it can run in terminals, CI systems, containers, and servers without a desktop GUI.

Diagnostic Reports

A FailureLab report ranks detected weaknesses.

Example:

```text

Occlusion
   Severity: critical
   Top-1 drop: 50.2%
   Top-5 drop: 40.0%
   Confidence drop: 48.1%

Blur
   Severity: critical
   Top-1 drop: 30.4%
   Top-5 drop: 18.1%
   Confidence drop: 29.1%

Rotation
   Severity: medium
   Top-1 drop: 7.3%
```

This makes it possible to identify which environmental changes cause the largest performance degradation.

Robustness Score

FailureLab summarizes model robustness with a score from:

```text
0 → 100
```

The score is accompanied by a grade and status.

Example:

```text
FailureLab score: 72.9/100 (C) — Needs Improvement.
```

The score provides a compact model-level robustness signal while the detailed report explains the underlying weaknesses.

Recommendations

FailureLab converts detected weaknesses into actionable recommendations.

Example:

```text

Occlusion [CRITICAL]

Diagnosis:
Model performance degrades when part of the image is hidden.

Likely cause:
The model may rely heavily on a limited visual region rather than
distributed evidence across the object.

Next action:
Add partial-occlusion augmentation and partially visible examples
to the training set.
```

Recommendations are generated for meaningful robustness weaknesses.

Severity Sweeps

A single perturbation level does not reveal when a model begins to fail.

FailureLab can sweep through increasingly severe conditions.

```python
blur_sweep = lab.sweep("blur")
```

Example blur levels:

```text
0.5
1.0
2.0
3.0
5.0
```

The same concept is available for:

```text
brightness
blur
compression
occlusion
rotation
crop
```

Run every built-in sweep with:

```python
envelope = lab.sweep_all()
```

Failure Thresholds

FailureLab identifies the first severity level where degradation crosses its configured failure criterion.

Example:

```text
Blur
Worst top-1 drop: 53.8%
Failure threshold: 3.0

Occlusion
Worst top-1 drop: 70.2%
Failure threshold: 0.3
```

A threshold that is not reached is reported as:

```text
Failure threshold: not reached
```

This helps distinguish between:

"The model eventually performs badly."

and:

"The model starts becoming unreliable at this specific severity."

Failure Envelopes

Running all severity sweeps creates a failure envelope describing robustness across multiple stress dimensions.

```python
envelope = lab.sweep_all()

report.with_failure_envelope(
    envelope
)
```

The resulting report can then be saved as a reusable robustness snapshot.

HTML and JSON Reports

Reports can be exported programmatically:

```python
report.save_html(
    "failurelab_report.html"
)

report.save_json(
    "failurelab_report.json"
)
```

HTML reports provide a human-readable diagnostic view.

JSON reports are suitable for automation and downstream tooling.

Robustness Snapshots

FailureLab reports with a failure envelope can be stored as lightweight model robustness snapshots.

```python
report.save_snapshot(
    "model_snapshot.json"
)
```

A snapshot stores information such as:

```json
{
  "format": "failurelab_snapshot",
  "version": 1,
  "score": 75.0,
  "grade": "C",
  "status": "Needs Improvement",
  "boundaries": [
    {
      "stress_name": "occlusion",
      "failure_threshold": 0.3,
      "worst_top1_drop": 0.58
    }
  ]
}
```

Snapshots allow model versions to be compared without rerunning the original evaluation during the comparison step.

Compare Model Versions

FailureLab can compare a baseline model with a candidate model.

```python
from failurelab import compare_reports

comparison = compare_reports(
    baseline_report,
    candidate_report,
)

print(comparison.summary())
```

Example:

```text
Robustness score declined: 75.0 → 74.1 (-0.9).
Regressions detected: 1.
```

FailureLab evaluates changes in both:

failure thresholds

worst-case degradation

This catches cases where a model may improve in one robustness metric while becoming worse in another.

Regression Types

FailureLab distinguishes between several regression conditions.

Threshold Regression

The candidate begins failing at a less favorable stress level.

Example:

```text
Occlusion

Baseline threshold: 0.40
Candidate threshold: 0.30
```

The candidate now begins failing with less occlusion.

Worst-Drop Regression

The candidate's worst degradation increased beyond the allowed tolerance.

Both

Both the failure threshold and worst degradation became worse.

No Regression

Neither condition violated the robustness gate.

Python Robustness Gate

A comparison can be enforced directly from Python:

```python
comparison = compare_reports(
    baseline_report,
    candidate_report,
)

comparison.require_pass()
```

If the candidate passes, execution continues normally.

If a robustness regression is detected, FailureLab raises:

```python
RobustnessRegressionError
```

This allows robustness requirements to become part of automated model validation.

Command-Line Interface

Show available commands:

```bash
failurelab --help
```

Check the installed version:

```bash
failurelab --version
```

Validate a saved robustness policy:

```bash
failurelab check --policy robustness.json
```

Compare two model robustness snapshots:

```bash
failurelab compare \
    --baseline baseline_snapshot.json \
    --candidate candidate_snapshot.json
```

Configurable Regression Tolerance

The comparison gate uses a default worst-drop tolerance of:

```text
0.02
```

This can be changed from the CLI:

```bash
failurelab compare \
    --baseline baseline_snapshot.json \
    --candidate candidate_snapshot.json \
    --tolerance 0.05
```

This allows teams to define how much worst-case degradation change is acceptable for their use case.

CI/CD Integration

FailureLab's comparison command is designed for automated pipelines.

Exit codes:

```text
0 = robustness gate passed
1 = robustness regression detected
2 = invalid input or configuration error
```

This means a CI system can automatically block a candidate model that introduces a robustness regression.

Example:

```bash
failurelab compare \
    --baseline baseline_snapshot.json \
    --candidate candidate_snapshot.json
```

A regression produces:

```text
RESULT: FAILED
```

and exits with code:

```text
1
```

GitHub Actions Example

A model robustness gate can be added to a workflow:

```yaml
name: Model Robustness Gate

on:
  push:
  pull_request:

jobs:
  robustness:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install FailureLab
        run: pip install .

      - name: Compare robustness snapshots
        run: |
          failurelab compare \
            --baseline reports/baseline_snapshot.json \
            --candidate reports/candidate_snapshot.json
```

If FailureLab detects a regression, the CI job fails automatically.

Real Model Demonstration

FailureLab includes a real-model comparison example using pretrained vision models and the Oxford-IIIT Pet dataset.

Run:

```bash
python examples/model_comparison_demo.py
```

In one real evaluation during development, FailureLab produced:

```text
Evaluating baseline: ResNet18

FailureLab score: 75.0/100 (C) — Needs Improvement.
Primary weakness: Occlusion.

Evaluating candidate: MobileNet V3 Small

FailureLab score: 74.1/100 (C) — Needs Improvement.
Primary weakness: Occlusion.
```

The comparison detected:

```text
Robustness score declined: 75.0 → 74.1 (-0.9).
Regressions detected: 1.
```

The important finding was an occlusion threshold regression.

Although MobileNet V3 Small showed a lower worst-case occlusion degradation in that run, it crossed the failure threshold at a less favorable occlusion level.

This demonstrates why FailureLab evaluates both failure thresholds and worst-case degradation rather than relying on one metric.

Exact results may vary with dataset selection, environment, library versions, and evaluation configuration.

Example End-to-End Workflow

```python
from failurelab import (
    FailureLab,
    compare_reports,
)

Evaluate baseline model

baseline_lab = FailureLab(
    predict_proba_fn=baseline_predict,
    dataset=dataset,
)

baseline_report = baseline_lab.run()

baseline_report.with_failure_envelope(
    baseline_lab.sweep_all()
)

baseline_report.save_snapshot(
    "baseline_snapshot.json"
)

Evaluate candidate model

candidate_lab = FailureLab(
    predict_proba_fn=candidate_predict,
    dataset=dataset,
)

candidate_report = candidate_lab.run()

candidate_report.with_failure_envelope(
    candidate_lab.sweep_all()
)

candidate_report.save_snapshot(
    "candidate_snapshot.json"
)

Compare models

comparison = compare_reports(
    baseline_report,
    candidate_report,
)

print(comparison.summary())

Enforce deployment gate

comparison.require_pass()
```

This creates a workflow of:

```text
Train candidate model
        |
        v
Run FailureLab
        |
        v
Generate failure envelope
        |
        v
Compare against baseline
        |
        v
Detect regressions
        |
        +---- PASS ----> Continue deployment
        |
        +---- FAIL ----> Block deployment
```

Testing

Run the complete test suite:

```bash
python -m pytest -v
```

FailureLab v0.2.0 passes 89 automated tests covering core robustness evaluation, scoring, sweeps, failure envelopes, exports, per-class analysis, custom stress tests, visualization, model comparisons, snapshots, regression gates, and CLI behavior.

Building the Package

Install the Python build tooling:

```bash
python -m pip install build
```

Build FailureLab:

```bash
python -m build
```

Artifacts are generated under:

```text
dist/
```

The wheel can then be installed directly:

```bash
pip install dist/failurelab-0.2.0-py3-none-any.whl
```

Verify:

```bash
failurelab --version
```

Project Structure

```text
FailureLab/
|
├── failurelab/
|   ├── api.py
|   ├── blur.py
|   ├── cli.py
|   ├── comparison.py
|   ├── comparison_export.py
|   ├── compression.py
|   ├── crop.py
|   ├── export.py
|   ├── failure_envelope.py
|   ├── occlusion.py
|   ├── policy.py
|   ├── recommendations.py
|   ├── rotation.py
|   ├── score.py
|   ├── snapshot.py
|   ├── stress_tests.py
|   ├── sweeps.py
|   ├── vision_report.py
|   └── vision_runner.py
|
├── examples/
|   ├── real_model_demo.py
|   └── model_comparison_demo.py
|
├── tests/
├── LICENSE
├── NOTICE
├── pyproject.toml
└── README.md
```

Design Philosophy

FailureLab is built around a simple idea:

Model evaluation should identify not only whether a model works, but how it fails.

The project focuses on four questions:

What breaks the model?

How severe is the weakness?

At what point does failure begin?

Did a new model version make robustness better or worse?

The goal is to make robustness testing useful during development rather than something discovered only after deployment.

Current Scope

FailureLab currently focuses on image-classification robustness.

The built-in stress suite evaluates common image perturbations, but it does not attempt to model every possible real-world distribution shift or establish that a model is safe for a particular deployment.

Robustness scores and thresholds should therefore be interpreted as engineering diagnostics under the configured FailureLab evaluation — not as guarantees of model safety or real-world performance.

Roadmap

Potential future directions include:

Additional image corruption families

Custom stress-test plugins

Dataset-level robustness analytics

Per-class failure analysis

Configurable scoring profiles

Richer CI policies

Report trend history

Additional model/task support

Expanded visualization

Integration with model-training pipelines

Status

FailureLab is under active development.

Current package version:

```text
0.2.0
```

The project has verified v0.2.0 package builds, 89 passing automated tests, command-line tooling, per-class failure analysis, custom stress tests, visualization, model comparison, and CI-compatible robustness regression gates.

License

FailureLab is licensed under the Apache License 2.0.

See `LICENSE` and `NOTICE` for details.