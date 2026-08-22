# FailureLab

**Find where vision models fail — before those failures reach production.**

FailureLab is an open-source Python framework for stress-testing computer vision models, measuring robustness degradation, discovering failure patterns, prioritizing weaknesses, tracking failures across model versions, and enforcing model-quality gates before release.

Instead of asking only *"How accurate is my model?"*, FailureLab asks:

> **What breaks it, how badly does it break, what should I fix first, and is this model ready to move forward?**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://github.com/canigenix/FailureLab/releases)
[![Tests](https://github.com/canigenix/FailureLab/actions/workflows/tests.yml/badge.svg)](https://github.com/canigenix/FailureLab/actions/workflows/tests.yml)

---

## FailureLab 1.0

FailureLab 1.0 is the first stable release of the framework.

The v1.0 release establishes a stable public Python API, stable command-line interface, explicit CLI exit-code behavior, package metadata guarantees, and regression coverage designed to protect compatibility in future releases.

FailureLab 1.0 includes:

- Computer-vision robustness stress testing
- Configurable stress suites
- Multi-severity stress analysis
- Failure envelopes
- Class-level and sample-level failure analysis
- Cross-stress vulnerability analysis
- Failure correlation and clustering
- Model comparison and regression detection
- Experiment history
- Model checkpoint progression analysis
- Failure signatures and signature history
- Failure triage and remediation prioritization
- Failure recurrence and persistence analysis
- Failure resolution tracking
- Failure trajectory forecasting
- Unified profile-driven evaluation
- Evaluation intelligence and model-health classification
- Configurable CI and release gates
- Structured JSON reporting
- Stable Python and CLI interfaces

---

## Stable v1.0 Contract

FailureLab 1.0 freezes the first stable public interface of the project.

The v1.0 compatibility baseline includes:

```text
211 public Python exports
19 CLI commands
```

The stable contract also covers:

- Package-level imports
- CLI command availability
- Evaluation behavior
- Evaluation intelligence
- Release-gate behavior
- CLI exit-code semantics
- Package metadata
- Console entry point
- Backward-compatible evaluation profiles

Future minor and patch releases should preserve these interfaces unless a change is explicitly documented as backward compatible.

Breaking API or CLI changes should be reserved for a future major release.

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
failurelab 1.0.0
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

These can be evaluated individually or through configured stress suites and severity sweeps.

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

Run from the CLI:

```bash
failurelab suite --config suite.json
```

Suites can also be loaded and executed through the Python API.

---

## Failure Envelopes

A single perturbation level does not show when model degradation begins.

FailureLab can sweep increasingly severe stress conditions:

```python
blur_sweep = lab.sweep("blur")
```

Or evaluate every built-in sweep:

```python
envelope = lab.sweep_all()
```

The first severity level where the configured failure criterion is crossed becomes part of the model's failure envelope.

---

## Cross-Stress Vulnerability Analysis

FailureLab can identify classes that repeatedly fail across several stress conditions.

This helps distinguish isolated weaknesses from classes that are systematically fragile.

```bash
failurelab cross-stress --help
```

---

## Sample-Level Failure Analysis

FailureLab can identify individual samples that repeatedly fail across different stress conditions.

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

FailureLab can measure whether different stresses tend to fail on the same samples.

Pairwise failure correlations can reveal related vulnerabilities, while clustering groups related stresses into larger failure patterns.

```bash
failurelab correlation --help
failurelab clusters --help
```

---

## Robustness Policies

FailureLab supports configurable policies that turn robustness results into automated PASS/FAIL gates.

Policies can cover:

- Global robustness thresholds
- Stress-specific thresholds
- Class-level thresholds
- Sample-level failure limits
- Correlation limits
- Failure-cluster limits
- Progression requirements
- Signature requirements
- Triage limits
- Persistence limits
- Resolution limits
- Forecast limits

```bash
failurelab policy-evaluate --help
```

---

## Model Comparison

FailureLab can compare a baseline model against a candidate model and detect robustness regressions.

```python
from failurelab import compare_reports

comparison = compare_reports(
    baseline_report,
    candidate_report,
)

print(comparison.summary())

comparison.require_pass()
```

CLI:

```bash
failurelab compare \
  --baseline baseline.json \
  --candidate candidate.json
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

Repeated runs can be retained for later comparison and trend analysis.

---

## Robustness History

FailureLab can track robustness over repeated experiments.

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

Multiple model or experiment configurations can be executed as one batch.

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

## Model Progression Analysis

FailureLab can track failure-rate changes across model checkpoints.

Progression analysis classifies checkpoint transitions and overall trends.

Possible overall trends include:

```text
improving
stable
degrading
volatile
```

Run:

```bash
failurelab progression --input progression.json
```

Progression analysis also supports tolerance, policy gates, checkpoint risk scoring, and JSON export.

---

## Failure Signatures

FailureLab can summarize how a model fails across multiple stress conditions.

Failure signatures classify model weaknesses as:

```text
low-risk
localized
systemic
unstable
```

Run:

```bash
failurelab signature --input signature.json
```

FailureLab can also track signature evolution across checkpoints:

```bash
failurelab signature-history --input history.json
```

Signature workflows support diagnostics, comparison, policy evaluation, and structured reporting.

---

## Failure Triage

FailureLab can rank detected weaknesses according to remediation priority.

Priority scoring considers:

- Failure rate
- Prediction instability
- Affected fraction
- Optional severity weighting

Priority levels include:

```text
low
medium
high
critical
```

Run:

```bash
failurelab triage --input triage.json
```

Compare triage burden between model versions:

```bash
failurelab triage-compare \
  --baseline baseline.json \
  --candidate candidate.json
```

FailureLab can also generate structured remediation recommendations for detected failure patterns.

---

## Failure Persistence

FailureLab can track whether the same weakness repeatedly appears across model checkpoints.

Persistence levels include:

```text
isolated
recurring
persistent
```

Run:

```bash
failurelab persistence \
  --input persistence.json
```

Persistence reports identify recurring and unresolved weaknesses that continue to survive model updates.

---

## Failure Resolution

FailureLab can determine whether recurring weaknesses are improving, staying unchanged, or getting worse.

Resolution status includes:

```text
improving
unchanged
worsening
insufficient_history
```

Run:

```bash
failurelab resolution \
  --input resolution.json \
  --tolerance 0.01
```

Persistence and resolution together answer two separate questions:

> Which failures keep returning?

and:

> Are later model versions actually fixing them?

---

## Failure Forecasting

FailureLab can project the likely next-step direction of a failure using checkpoint history.

```bash
failurelab forecast \
  --input failures.json
```

Forecasting can identify weaknesses that are likely to:

- Improve
- Remain stable
- Worsen
- Remain at projected risk

Forecast results can be exported to JSON and included in unified evaluation workflows.

---

## Unified Evaluation Profiles

FailureLab can execute multiple analysis workflows through a single evaluation profile.

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

Run:

```bash
failurelab evaluate --config failurelab.json
```

Enabled analyses execute in a deterministic order:

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

## Shared Occurrence Input

Persistence, resolution, and forecasting operate on related failure-history data.

The preferred v1.0 profile field is:

```json
{
  "occurrence_input": "failures.json"
}
```

For backward compatibility, older profiles using:

```json
{
  "forecast_input": "failures.json"
}
```

remain supported.

When both are supplied, `occurrence_input` takes precedence.

---

## Evaluation Intelligence

FailureLab provides a high-level interpretation of a complete evaluation.

Evaluation intelligence tracks:

- Total analyses
- Passed analyses
- Failed analyses
- Failed analysis names
- Failure ratio
- Overall health status
- Human-readable health message

Health states include:

```text
healthy
watch
at-risk
critical
```

Example output:

```text
Health: healthy
Failed analyses: 0/6
Failure ratio: 0.00%
All enabled analyses passed.
```

Programmatically:

```python
intelligence = report.intelligence

print(intelligence.health.status)
print(intelligence.health.failure_ratio)
print(intelligence.summary.failed_analysis_names)
```

The report also exposes:

```python
print(report.health_status)
```

---

## Evaluation Release Gates

FailureLab can apply a release gate to unified evaluation intelligence.

Example gate configuration:

```json
{
  "maximum_failed_analyses": 0,
  "allowed_health_statuses": [
    "healthy"
  ]
}
```

Run:

```bash
failurelab evaluate \
  --config failurelab.json \
  --gate-config gate.json
```

Passing gate:

```text
Gate: PASSED
RESULT: PASSED
```

Failing gate:

```text
Gate: FAILED
- Failed analyses 2 exceed maximum 1.
- Health status 'at-risk' is not allowed.

RESULT: FAILED
```

Gate failures return a non-zero exit code and can block CI or release workflows.

---

## Controlled Degradation

A release gate does not have to require a perfectly healthy evaluation.

Example:

```json
{
  "maximum_failed_analyses": 1,
  "allowed_health_statuses": [
    "healthy",
    "watch"
  ]
}
```

This can allow limited degradation while rejecting `at-risk` or `critical` results.

---

## Gate Configuration Validation

FailureLab validates release-gate configuration strictly.

`maximum_failed_analyses`:

- Must be an integer
- Cannot be negative
- Cannot be a boolean

`allowed_health_statuses`:

- Must be a JSON list
- Cannot be empty
- Must contain strings only
- Cannot contain duplicate values
- Must contain only supported health states

Supported health states:

```text
healthy
watch
at-risk
critical
```

Malformed gate configuration is treated as a configuration error.

---

## Evaluation JSON Reports

Unified evaluation reports can be exported as structured JSON.

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

These reports can be consumed by CI systems, dashboards, or downstream automation.

---

## Visualization

FailureLab can generate robustness degradation charts.

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

Visualization uses a headless backend suitable for CI, containers, servers, and terminal environments.

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

## Public Python API

FailureLab 1.0 freezes the package-level public Python API at:

```text
211 exported symbols
```

Major public interfaces include:

- Core FailureLab evaluation
- Configured stress suites
- Model comparison
- Experiment tracking
- Robustness history
- Batch execution
- Robustness policies
- Cross-stress analysis
- Sample analysis
- Correlation and clustering
- Progression analysis
- Failure signatures
- Triage and remediation
- Persistence
- Resolution
- Forecasting
- Evaluation profiles
- Evaluation inputs
- Evaluation reports
- Evaluation summaries
- Evaluation health classification
- Evaluation intelligence
- Evaluation release gates

Example:

```python
from failurelab import (
    FailureLab,
    EvaluationProfile,
    EvaluationReport,
    EvaluationSummary,
    EvaluationHealth,
    EvaluationIntelligence,
    EvaluationGateConfig,
    EvaluationGateResult,
)
```

The v1.0 regression suite verifies that the frozen package-level API remains available.

---

## Command-Line Interface

Show available commands:

```bash
failurelab --help
```

FailureLab 1.0 exposes 19 commands:

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

Inspect any command:

```bash
failurelab <command> --help
```

The unified evaluation command supports:

```text
--config
--output
--gate-config
```

The v1.0 CLI surface is protected by compatibility tests.

---

## CLI Exit-Code Contract

FailureLab 1.0 defines the following CLI exit-code contract:

```text
0 = successful execution
1 = robustness, evaluation, policy, or release-gate failure
2 = invalid input, malformed configuration, or operational error
```

Configuration and operational errors are written to `stderr`.

Examples of exit-code `2` conditions include:

- Missing configuration files
- Malformed JSON
- Invalid evaluation profile structure
- Invalid release-gate configuration

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

A failed evaluation or release gate returns a non-zero exit code and can block the workflow.

---

## Package Metadata

FailureLab 1.0 package metadata includes:

```text
Package: failurelab
Python: >=3.10
License: Apache-2.0
Build backend: setuptools.build_meta
CLI entry point: failurelab.cli:main
```

Core runtime dependencies:

```text
numpy>=1.24
pillow>=9.0
```

Optional dependency groups include:

```text
vision
visualization
dev
```

---

## Testing

Run the complete test suite:

```bash
python -m pytest -q
```

The v1.0 release candidate is validated by **685 automated tests** covering:

- Core robustness evaluation
- Stress tests
- Policies
- Reports
- Experiment tracking
- Model comparison
- Progression
- Failure signatures
- Triage
- Persistence
- Resolution
- Forecasting
- Evaluation orchestration
- Evaluation intelligence
- Release gates
- Configuration validation
- Public API stability
- CLI compatibility
- CLI error contracts
- Package metadata
- Backward compatibility
- v1.0 behavioral contracts

The suite should pass completely before a release is built.

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

For v1.0.0:

```text
failurelab-1.0.0-py3-none-any.whl
failurelab-1.0.0.tar.gz
```

---

## Current Scope

FailureLab 1.0 focuses on **image-classification robustness and failure analysis**.

Its stress tests measure model behavior under configured image perturbations.

FailureLab does not attempt to model every possible real-world distribution shift or independently establish that a model is safe for a particular deployment.

Robustness scores, thresholds, correlations, priority scores, health classifications, forecasts, policies, and release gates should be treated as engineering diagnostics under the configured evaluation.

---

## Design Philosophy

FailureLab is built around a practical sequence of questions:

1. What breaks the model?
2. How severe is the weakness?
3. At what point does failure begin?
4. Which classes and samples repeatedly fail?
5. Which stresses expose the same underlying weaknesses?
6. Which failures should be fixed first?
7. Which failures keep surviving across model versions?
8. Are persistent failures improving?
9. Which failures are likely to remain risky?
10. What does the complete evaluation say about the model?
11. Does that evaluation meet the requirements to move forward?

The goal is to make robustness testing, failure-pattern discovery, remediation prioritization, failure-resolution tracking, projected-risk analysis, model-health evaluation, and automated release gating part of normal model development.

---

## Status

FailureLab 1.0 is the first stable release of the project.

Current version:

```text
1.0.0
```

The v1.0 release establishes a stable public API and CLI compatibility baseline backed by automated regression tests.

Future minor releases can add backward-compatible functionality while preserving the v1.0 contract.

---

## License

FailureLab is licensed under the Apache License 2.0.

See `LICENSE` and `NOTICE` for details.