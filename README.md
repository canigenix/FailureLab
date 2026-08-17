# FailureLab

**Find where vision models fail — before those failures reach production.**

FailureLab is an open-source Python framework for stress-testing computer vision models, measuring robustness degradation, and detecting regressions between model versions.

Instead of asking only *"How accurate is my model?"*, FailureLab asks:

> **What breaks it, how badly does it break, and did the next version get worse?**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.4.0-green)](https://github.com/canigenix/FailureLab/releases)
[![Tests](https://github.com/canigenix/FailureLab/actions/workflows/tests.yml/badge.svg)](https://github.com/canigenix/FailureLab/actions/workflows/tests.yml)

---

## FailureLab v0.4.0

Version 0.4.0 adds configuration-driven robustness workflows and experiment tracking.

Highlights:

- JSON-configured stress suites
- Suite-level degradation thresholds
- Automated PASS/FAIL evaluation
- Persistent experiment history
- Model and run identifiers
- Robustness trend detection
- Model-specific history queries
- Batch experiment execution
- Batch JSON summaries
- `suite` and `history` CLI workflows
- Expanded public Python API
  Configurable global robustness policies
  Stress-specific policy thresholds
  Warning vs failure severity levels
  Class-level robustness policies
  Class-specific warning/failure thresholds
  Minimum sample requirements
  Class coverage enforcement
  Policy evaluation CLI
  CI-friendly exit codes

These features build on the failure analysis, custom stress tests, visualization, model comparison, and CI regression gates introduced in earlier releases.

---

## Features

FailureLab currently provides:

- Six built-in image stress tests
- Top-1 and Top-5 accuracy degradation analysis
- Confidence degradation analysis
- Automatic weakness severity classification
- Robustness scoring
- Per-class failure analysis
- Prediction flip-rate analysis
- Failure-threshold detection
- Multi-severity stress sweeps
- Failure envelopes
- Custom stress tests
- PNG robustness visualizations
- HTML and JSON reports
- Reusable robustness snapshots
- Baseline-vs-candidate model comparison
- Configurable regression tolerance
- Python and CLI robustness gates
- Configured stress suites
- Experiment history and trend tracking
- Batch experiment execution

---

## Installation

From the repository:

```bash
pip install .
```

For development:

```bash
pip install -e .
```

Optional visualization support:

```bash
pip install ".[visualization]"
```

Optional vision dependencies:

```bash
pip install ".[vision]"
```

Verify the installation:

```bash
failurelab --version
```

Expected:

```text
failurelab 0.4.0
```

---

## Quick Start

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

A dataset contains image/label pairs:

```python
dataset = [
    (image_1, class_index_1),
    (image_2, class_index_2),
]
```

The prediction function returns a probability vector for one image:

```python
def predict_proba(image):
    ...
    return probabilities
```

---

## Built-In Stress Tests

FailureLab includes six common visual perturbations:

- Brightness
- Blur
- Compression
- Occlusion
- Rotation
- Center crop

These can be evaluated individually or through configured suites and severity sweeps.

---

## Configured Stress Suites

v0.4.0 introduces reusable stress-suite configurations.

Example:

```json
{
  "name": "production-vision",
  "maximum_drop": 0.20,
  "stresses": [
    {
      "type": "blur",
      "radius": 2.0
    },
    {
      "type": "rotation",
      "degrees": 15
    },
    {
      "type": "brightness",
      "factor": 0.5
    }
  ]
}
```

Load a suite from Python:

```python
from failurelab import (
    ConfiguredSuiteRunner,
    load_suite_config,
)

config = load_suite_config("suite.json")

runner = ConfiguredSuiteRunner(
    predict_proba
)

result = runner.run(
    dataset=dataset,
    config=config,
)

print(result.status)
print(result.worst_drop)
```

When `maximum_drop` is configured, the suite produces a PASS/FAIL result based on its worst observed degradation.

Inspect a configuration from the CLI:

```bash
failurelab suite --config suite.json
```

---

## Experiment Tracking

`ExperimentRunner` combines suite execution, result persistence, and history tracking.

```python
from failurelab import ExperimentRunner

runner = ExperimentRunner(
    predict_proba
)

output = runner.run(
    dataset=dataset,
    config=config,
    result_path="result.json",
    history_path="history.json",
    model_id="resnet18-v3",
)
```

Each run can record:

- suite name
- model ID
- run ID
- timestamp
- PASS/FAIL status
- worst stress
- worst degradation
- configured threshold

Run IDs can be supplied explicitly or generated automatically.

---

## Robustness History

FailureLab can retain repeated experiment results and detect whether robustness is changing over time.

```python
from failurelab import SuiteHistory

history = SuiteHistory.load_json(
    "history.json"
)

print(
    history.trend(
        "production-vision"
    )
)
```

Possible trend results include:

```text
improved
stable
regressed
insufficient_history
```

History can also be queried by model:

```python
latest = history.latest_for_model(
    "resnet18-v3"
)

trend = history.model_trend(
    "resnet18-v3"
)
```

From the CLI:

```bash
failurelab history \
  --input history.json \
  --suite production-vision
```

Or:

```bash
failurelab history \
  --input history.json \
  --model resnet18-v3
```

---

## Batch Experiments

Multiple models or experiment configurations can be executed as one batch.

```python
from failurelab import (
    BatchExperiment,
    BatchExperimentRunner,
)

experiments = [
    BatchExperiment(
        model_id="model-a",
        predict_proba_fn=model_a_predict,
        dataset=dataset,
        config=config,
        result_path="model-a.json",
        history_path="history.json",
    ),
    BatchExperiment(
        model_id="model-b",
        predict_proba_fn=model_b_predict,
        dataset=dataset,
        config=config,
        result_path="model-b.json",
        history_path="history.json",
    ),
]

runner = BatchExperimentRunner()

output = runner.run(
    experiments
)

output.save_json(
    "batch-summary.json"
)
```

The batch summary records experiment counts, overall status, individual model results, and output locations.

---

## Failure Envelopes

A single perturbation level does not show when degradation begins.

FailureLab can sweep increasingly severe conditions:

```python
blur_sweep = lab.sweep("blur")
```

Or evaluate every built-in sweep:

```python
envelope = lab.sweep_all()
```

FailureLab records the first severity level where the configured failure criterion is crossed, producing a model failure envelope across multiple stress dimensions.

---

## Custom Stress Tests

Project-specific transformations can use the same robustness pipeline as built-in stresses.

```python
from failurelab import CustomStressTest

custom_test = CustomStressTest(
    name="custom_shift",
    transform=lambda image: image,
)
```

---

## Visualization

Generate robustness degradation charts programmatically:

```python
from failurelab.visualization import plot_robustness_drops

plot_robustness_drops(
    weaknesses,
    output_path="robustness.png",
)
```

Or from the CLI:

```bash
failurelab visualize \
  --input weaknesses.json \
  --output robustness.png
```

Visualization uses a headless backend so chart generation works in CI, containers, servers, and terminal environments.

---

## Compare Model Versions

FailureLab can compare baseline and candidate model robustness.

```python
from failurelab import compare_reports

comparison = compare_reports(
    baseline_report,
    candidate_report,
)

print(comparison.summary())

comparison.require_pass()
```

FailureLab evaluates both:

- failure-threshold regressions
- worst-case degradation regressions

If a candidate violates the robustness gate, `RobustnessRegressionError` is raised.

---

## Command-Line Interface

Show available commands:

```bash
failurelab --help
```

Current workflows include:

```text
check
compare
visualize
suite
history
```

Compare saved model snapshots:

```bash
failurelab compare \
  --baseline baseline_snapshot.json \
  --candidate candidate_snapshot.json
```

Set a custom regression tolerance:

```bash
failurelab compare \
  --baseline baseline_snapshot.json \
  --candidate candidate_snapshot.json \
  --tolerance 0.05
```

CLI exit codes are suitable for automated pipelines:

```text
0 = passed
1 = robustness regression detected
2 = invalid input or configuration error
```

---

## CI/CD

FailureLab can act as a model robustness gate in CI.

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

A detected regression returns a non-zero exit code and can block the pipeline.

---

## Reports and Snapshots

Reports can be exported as HTML or JSON:

```python
report.save_html(
    "failurelab_report.html"
)

report.save_json(
    "failurelab_report.json"
)
```

A report with a failure envelope can also be saved as a reusable robustness snapshot:

```python
report.save_snapshot(
    "model_snapshot.json"
)
```

Snapshots allow model versions to be compared without rerunning the original evaluation during the comparison step.

---

## Testing

Run the complete test suite:

```bash
python -m pytest -q
```

FailureLab v0.4.0 currently passes:

```text
116 automated tests
```

The suite covers core robustness evaluation, stress tests, scoring, per-class analysis, failure envelopes, snapshots, model comparisons, visualization, configured suites, experiment history, batch execution, and CLI behavior.

---

## Building

Build the package with:

```bash
python -m pip install build
python -m build
```

Artifacts are generated under:

```text
dist/
```

For v0.4.0:

```text
failurelab-0.4.0-py3-none-any.whl
failurelab-0.4.0.tar.gz
```

---

## Current Scope

FailureLab currently focuses on image-classification robustness.

Its stress tests measure model behavior under configured image perturbations. FailureLab does not attempt to model every real-world distribution shift or establish that a model is safe for a particular deployment.

Robustness scores, thresholds, and gates should be treated as engineering diagnostics under the configured evaluation.

---

## Design Philosophy

FailureLab is built around four questions:

1. What breaks the model?
2. How severe is the weakness?
3. At what point does failure begin?
4. Did a new model version make robustness better or worse?

The goal is to make robustness testing part of model development and validation rather than something discovered only after deployment.

---

## Status

FailureLab is under active development.

Current version:

```text
0.4.0
```

v0.4.0 includes configuration-driven stress suites, experiment tracking, model/run metadata, robustness history, trend detection, batch execution, visualization, model comparison, and CI-compatible regression gates.

---

## License

FailureLab is licensed under the Apache License 2.0.

See `LICENSE` and `NOTICE` for details.