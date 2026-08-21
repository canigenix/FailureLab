# FailureLab

**Find where vision models fail — before those failures reach production.**

FailureLab is an open-source Python framework for stress-testing computer vision models, measuring robustness degradation, discovering failure patterns, prioritizing weaknesses, tracking failures across model versions, and evaluating whether those weaknesses are improving or getting worse.

Instead of asking only *"How accurate is my model?"*, FailureLab asks:

> **What breaks it, how badly does it break, what should I fix first, and is this model ready to pass a production gate?**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.14.0-green)](https://github.com/canigenix/FailureLab/releases)
[![Tests](https://github.com/canigenix/FailureLab/actions/workflows/tests.yml/badge.svg)](https://github.com/canigenix/FailureLab/actions/workflows/tests.yml)

---

## FailureLab v0.14.0

Version 0.14.0 adds **configurable evaluation release gates** to FailureLab.

Unified evaluations can now be checked against explicit model-health requirements and used as automated CI or release gates.

Gate policies can control:

- Maximum number of failed analyses
- Allowed evaluation health states
- Gate PASS/FAIL status
- Human-readable policy violations
- CLI exit behavior for CI pipelines

A gate configuration can be supplied directly to `failurelab evaluate`:

```bash
failurelab evaluate \
  --config failurelab.json \
  --gate-config gate.json
```

This extends the evaluation intelligence introduced in v0.13.0 into an automated decision layer suitable for CI and release workflows.

---

## Features

FailureLab currently provides:

- Built-in image stress tests
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
- Cross-stress class vulnerability analysis
- Sample-level repeated failure analysis
- Stress failure correlation analysis
- Failure clustering
- Configurable robustness and failure policies
- PNG robustness visualizations
- HTML and JSON reports
- Reusable robustness snapshots
- Baseline-vs-candidate model comparison
- Experiment history and trend tracking
- Batch experiment execution
- Model checkpoint progression analysis
- Failure signature analysis and history
- Ranked failure triage
- Remediation recommendations
- Failure recurrence and persistence analysis
- Failure resolution analysis
- Failure trajectory forecasting
- Unified profile-driven evaluation
- Shared evaluation input resolution
- Evaluation intelligence
- Overall model-health classification
- Configurable evaluation release gates
- CI-compatible gate exit codes
- Python and CLI integration

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
failurelab 0.14.0
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

FailureLab supports reusable stress-suite configurations.

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

CLI:

```bash
failurelab suite --config suite.json
```

---

## Unified Evaluation Profiles

FailureLab can orchestrate multiple analyses through a single evaluation profile.

Example:

```json
{
  "name": "production",
  "suite_config": "suite.json",

  "progression_input": "progression.json",
  "signature_input": "signature.json",
  "triage_input": "triage.json",
  "occurrence_input": "failures.json",

  "run_progression": true,
  "run_signature": true,
  "run_triage": true,
  "run_persistence": true,
  "run_resolution": true,
  "run_forecast": true
}
```

`occurrence_input` provides shared failure-occurrence history for persistence, resolution, and forecasting.

Profiles created for earlier releases that use:

```json
{
  "forecast_input": "failures.json"
}
```

remain supported.

When both `occurrence_input` and `forecast_input` are supplied, `occurrence_input` takes precedence.

Run the complete evaluation:

```bash
failurelab evaluate --config failurelab.json
```

Analyses execute in a deterministic order:

```text
progression
signature
triage
persistence
resolution
forecast
```

Export the combined report:

```bash
failurelab evaluate \
  --config failurelab.json \
  --output evaluation-report.json
```

---

## Evaluation Intelligence

FailureLab summarizes the complete outcome of unified evaluations.

Evaluation intelligence includes:

- Total analyses
- Passed analyses
- Failed analyses
- Failed analysis names
- Failure ratio
- Overall evaluation health
- Human-readable health summary

Possible health states:

```text
healthy
watch
at-risk
critical
```

A healthy evaluation may produce:

```text
Health: healthy
Failed analyses: 0/6
Failure ratio: 0.00%
All enabled analyses passed.
```

The same information is available programmatically:

```python
intelligence = report.intelligence

print(intelligence.health.status)
print(intelligence.health.failure_ratio)
print(intelligence.summary.failed_analysis_names)
```

The evaluation report also exposes:

```python
print(report.health_status)
```

---

## Evaluation Release Gates

FailureLab v0.14.0 can apply a configurable release gate to completed evaluation intelligence.

Create a gate configuration:

```json
{
  "maximum_failed_analyses": 0,
  "allowed_health_statuses": [
    "healthy"
  ]
}
```

Run the evaluation with the gate:

```bash
failurelab evaluate \
  --config failurelab.json \
  --gate-config gate.json
```

A passing gate reports:

```text
Gate: PASSED
RESULT: PASSED
```

A failing gate reports:

```text
Gate: FAILED
- Failed analyses 2 exceed maximum 1.
- Health status 'at-risk' is not allowed.

RESULT: FAILED
```

Gate failure returns a non-zero CLI exit code, allowing the evaluation to block CI or release workflows.

### Controlled degradation

Gate policies do not have to require perfect health.

For example:

```json
{
  "maximum_failed_analyses": 1,
  "allowed_health_statuses": [
    "healthy",
    "watch"
  ]
}
```

This allows a limited degradation state while still rejecting more serious `at-risk` or `critical` evaluations.

### Gate configuration

Supported fields:

```text
maximum_failed_analyses
allowed_health_statuses
```

`maximum_failed_analyses` must be zero or greater.

Valid health states are:

```text
healthy
watch
at-risk
critical
```

An invalid gate configuration is rejected before a gate decision is made.

---

## Evaluation JSON Reports

Unified evaluation JSON reports include evaluation intelligence.

Example:

```json
{
  "profile_name": "production",
  "suite_config": "suite.json",
  "passed": false,
  "passed_count": 4,
  "failed_count": 2,
  "health_status": "at-risk",
  "failure_ratio": 0.3333333333333333,
  "failed_analyses": [
    "triage",
    "forecast"
  ],
  "health_message": "Multiple evaluation areas require attention.",
  "steps": []
}
```

Structured evaluation output can be consumed by CI systems, reporting tools, or downstream automation.

---

## Evaluation Input Resolution

FailureLab centralizes evaluation input-path resolution.

Evaluation profiles can provide:

- `progression_input`
- `signature_input`
- `triage_input`
- `occurrence_input`

The shared `occurrence_input` is used by:

```text
persistence
resolution
forecast
```

For compatibility, `forecast_input` remains supported as a fallback for existing profiles.

---

## Model Progression Analysis

FailureLab can track failure-rate changes across model checkpoints and classify transitions as improved, stable, or regressed.

Possible overall trends include:

- Improving
- Stable
- Degrading
- Volatile

```bash
failurelab progression --input progression.json
```

Progression analysis supports configurable tolerance, policy gates, checkpoint risk scoring, and JSON export.

---

## Failure Signatures

FailureLab can summarize failure behavior across stress types as a reusable failure signature.

Signatures classify weaknesses as:

- Low-risk
- Localized
- Systemic
- Unstable

```bash
failurelab signature --input signature.json
```

Signature history:

```bash
failurelab signature-history --input history.json
```

---

## Failure Triage

FailureLab can rank detected weaknesses according to remediation priority.

Priority scoring considers:

- Failure rate
- Prediction instability
- Affected fraction
- Optional severity weighting

Failures can be classified as:

```text
low
medium
high
critical
```

Run triage:

```bash
failurelab triage --input triage.json
```

Compare triage between model versions:

```bash
failurelab triage-compare \
  --baseline baseline.json \
  --candidate candidate.json
```

---

## Failure Persistence

FailureLab can track the same failure across multiple model checkpoints.

Failures can be classified as:

```text
isolated
recurring
persistent
```

```bash
failurelab persistence \
  --input persistence.json
```

Persistence reports track recurrence behavior and unresolved weaknesses across model versions.

---

## Failure Resolution

FailureLab can analyze whether recurring failures are actually being resolved.

Resolution status can be:

```text
improving
unchanged
worsening
insufficient_history
```

```bash
failurelab resolution \
  --input resolution.json \
  --tolerance 0.01
```

Together, persistence and resolution show both which failures keep returning and whether later model versions are fixing them.

---

## Failure Forecasting

FailureLab can use failure-score history to estimate the likely direction of a weakness at the next checkpoint.

```bash
failurelab forecast \
  --input failures.json
```

Forecast results can be exported to JSON and can participate in unified evaluations.

---

## Cross-Stress Vulnerability Analysis

FailureLab can identify classes that repeatedly fail across multiple stress conditions.

```bash
failurelab cross-stress --help
```

---

## Sample-Level Failure Analysis

FailureLab can identify individual samples that repeatedly fail across stress conditions.

Sample analysis tracks:

- Failure frequency
- Prediction-flip frequency
- Associated failure stresses
- Associated prediction-flip stresses
- Stable, localized, and systemic severity

```bash
failurelab sample-report --help
```

---

## Failure Correlation and Clustering

FailureLab can measure whether different stresses tend to fail on the same samples and group related failure patterns into clusters.

```bash
failurelab correlation --help
failurelab clusters --help
```

---

## Robustness Policies

FailureLab supports configurable policies that turn analysis results into automated PASS/FAIL gates.

Policies can cover:

- Global robustness thresholds
- Stress-specific thresholds
- Class-level thresholds
- Sample-level limits
- Correlation limits
- Cluster limits
- Progression requirements
- Signature requirements
- Triage limits
- Persistence limits
- Resolution limits
- Forecast limits

The v0.14 evaluation gate operates above these individual analyses, allowing the combined model-health result to drive an additional release decision.

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

---

## Robustness History

FailureLab can retain repeated experiment results and detect whether robustness changes over time.

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

Possible trends include:

```text
improved
stable
regressed
insufficient_history
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
]

runner = BatchExperimentRunner()

output = runner.run(
    experiments
)
```

---

## Failure Envelopes

FailureLab can sweep increasingly severe perturbations to identify where failure begins.

```python
blur_sweep = lab.sweep("blur")
```

Or:

```python
envelope = lab.sweep_all()
```

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

Generate robustness degradation charts:

```python
from failurelab.visualization import plot_robustness_drops

plot_robustness_drops(
    weaknesses,
    output_path="robustness.png",
)
```

CLI:

```bash
failurelab visualize \
  --input weaknesses.json \
  --output robustness.png
```

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
policy-evaluate
cross-stress
sample-report
correlation
clusters
progression
signature
signature-history
triage
triage-compare
persistence
resolution
forecast
evaluate
```

Inspect any command with:

```bash
failurelab <command> --help
```

The unified evaluation command supports:

```text
--config
--output
--gate-config
```

CLI exit codes:

```text
0 = passed
1 = robustness, evaluation, or gate failure detected
2 = invalid input or configuration error
```

---

## CI/CD

FailureLab can act as a model robustness and release gate in CI.

Example evaluation profile:

```json
{
  "name": "production",
  "suite_config": "suite.json",
  "occurrence_input": "failures.json",
  "run_forecast": true
}
```

Example gate:

```json
{
  "maximum_failed_analyses": 0,
  "allowed_health_statuses": [
    "healthy"
  ]
}
```

GitHub Actions example:

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

      - name: Run tests
        run: python -m pytest -q

      - name: Run FailureLab release gate
        run: |
          failurelab evaluate \
            --config failurelab.json \
            --gate-config gate.json \
            --output evaluation-report.json
```

If the evaluation or configured release gate fails, FailureLab returns a non-zero exit code and the CI job can fail.

---

## Reports and JSON Export

FailureLab supports structured output across its robustness and failure-analysis workflows.

Unified evaluation reports include:

- Overall PASS/FAIL result
- Per-analysis results
- Health status
- Failure ratio
- Failed analysis names
- Health summary message

Gate results provide:

- Gate status
- PASS/FAIL result
- Policy violations

---

## Public Python API

FailureLab exposes its major workflows through Python modules and package interfaces.

Major capabilities include:

- Core robustness evaluation
- Configured stress suites
- Experiment history
- Model comparison
- Robustness policies
- Cross-stress analysis
- Sample-level failure analysis
- Failure correlation
- Failure clustering
- Model progression
- Checkpoint risk scoring
- Failure signatures and diagnostics
- Signature comparison and history
- Failure priority scoring
- Failure triage
- Remediation recommendations
- Failure persistence
- Failure resolution
- Failure forecasting
- Evaluation profiles
- Evaluation input resolution
- Evaluation summaries
- Evaluation health classification
- Evaluation intelligence
- Evaluation release gates
- Gate configuration
- Gate execution
- JSON export

---

## Testing

Run the complete test suite:

```bash
python -m pytest -q
```

The automated suite covers FailureLab's core evaluation, stress tests, policies, reports, experiment tracking, model comparison, progression, failure signatures, triage, persistence, resolution, forecasting, evaluation orchestration, evaluation intelligence, release gates, CLI workflows, backward compatibility, and public Python interfaces.

The complete suite should pass before a release is built.

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

For v0.14.0:

```text
failurelab-0.14.0-py3-none-any.whl
failurelab-0.14.0.tar.gz
```

---

## Current Scope

FailureLab currently focuses on image-classification robustness.

Its stress tests measure model behavior under configured image perturbations. FailureLab does not attempt to model every real-world distribution shift or establish that a model is safe for a particular deployment.

Robustness scores, thresholds, correlations, priority scores, health classifications, forecasts, policies, and release gates should be treated as engineering diagnostics under the configured evaluation.

---

## Design Philosophy

FailureLab is built around a few practical questions:

1. What breaks the model?
2. How severe is the weakness?
3. At what point does failure begin?
4. Which classes and samples repeatedly fail?
5. Which stresses expose the same underlying weaknesses?
6. Which failures should be fixed first?
7. Which failures keep surviving across model versions?
8. Are persistent failures improving?
9. Which failures are likely to remain risky?
10. What does the complete evaluation say about the model overall?
11. Does that evaluation meet the requirements to move forward?

The goal is to make robustness testing, failure-pattern discovery, failure-resolution tracking, projected-risk analysis, model-health evaluation, and automated release gating part of normal model development.

---

## Status

FailureLab is under active development.

Current version:

```text
0.14.0
```

v0.14.0 adds configurable evaluation release gates, allowing model-health intelligence to drive automated CI and release decisions through explicit failure limits and allowed health states.

---

## License

FailureLab is licensed under the Apache License 2.0.

See `LICENSE` and `NOTICE` for details.