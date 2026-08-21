# FailureLab
**Find where vision models fail --- before those failures reach
production.**
FailureLab is an open-source Python framework for stress-testing
computer vision models, measuring robustness degradation, discovering
failure patterns, prioritizing weaknesses, tracking persistent failures,
and detecting regressions between model versions.
Instead of asking only *"How accurate is my model?"*, FailureLab
asks:
> **What breaks it, how badly does it break, what should I fix
first, and did the next version actually fix it?**
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.10.0-green)](https://github.com/canigenix/FailureLab/releases)
[![Tests](https://github.com/canigenix/FailureLab/actions/workflows/tests.yml/badge.svg)](https://github.com/canigenix/FailureLab/actions/workflows/tests.yml)
---
## FailureLab v0.10.0
Version 0.10.0 adds failure trajectory forecasting across model
checkpoints.
FailureLab can now use recent failure-score history to project which
weaknesses are likely to improve, remain stable, or worsen at the next
checkpoint.
Highlights:
- Failure recurrence analysis
- Isolated, recurring, and persistent failure classification
- Failure persistence reports
- Recurrence-rate tracking
- Unresolved-failure tracking
- Persistence policy gates
- Failure resolution analysis
- Improving, unchanged, worsening, and insufficient-history
classification
- Configurable resolution tolerance
- Worst-regression detection
- Resolution policy gates
- JSON persistence and resolution reports
- `failurelab persistence` CLI workflow
- `failurelab resolution` CLI workflow
- Expanded public Python API
These capabilities build on FailureLab's persistence and resolution
tracking, stress suites, failure signatures, experiment history,
progression analysis, failure triage, robustness policies, model
comparison, and CI regression gates.
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
- Cross-stress class vulnerability analysis
- Sample-level repeated failure analysis
- Stress failure correlation analysis
- Failure clustering
- Global and stress-specific robustness policies
- Class-level robustness policies
- Sample-level failure policies
- Correlation and cluster policies
- Minimum sample and class-coverage enforcement
- PNG robustness visualizations
- HTML and JSON reports
- Reusable robustness snapshots
- Baseline-vs-candidate model comparison
- Configurable regression tolerance
- Python and CLI robustness gates
- Configured stress suites
- Experiment history and trend tracking
- Batch experiment execution
- Model checkpoint progression analysis
- Progression trend classification and policy gates
- Checkpoint risk scoring
- Failure signature analysis and diagnostics
- Failure signature comparison and policy gates
- Multi-version signature history and trend analysis
- Signature-history policy gates
- Failure priority scoring
- Ranked failure triage
- Remediation recommendations
- Failure triage policy gates
- Triage comparison across model versions
- Triage regression detection and policy gates
- Failure recurrence and persistence analysis
- Persistent and unresolved failure tracking
- Failure resolution analysis across checkpoints
- Improving, unchanged, and worsening failure classification
- Persistence and resolution policy gates
- JSON export across analysis workflows
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
failurelab 0.10.0
```
---
## Quick Start
FailureLab works with a prediction function that accepts an image and
returns class probabilities.
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
These can be evaluated individually or through configured suites and
severity sweeps.
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
When `maximum_drop` is configured, the suite produces a PASS/FAIL
result based on its worst observed degradation.
CLI:
```bash
failurelab suite --config suite.json
```
---
## Cross-Stress Vulnerability Analysis
FailureLab can identify classes that repeatedly fail across multiple
stress conditions.
This helps distinguish weaknesses isolated to one perturbation from
classes that are systematically fragile across several stresses.
Cross-stress results can also be evaluated against configurable
policies.
```bash
failurelab cross-stress --help
```
---
## Sample-Level Failure Analysis
FailureLab can identify individual samples that repeatedly fail across
different stress conditions.
Sample analysis tracks:
- Failure frequency
- Prediction-flip frequency
- Associated failure stresses
- Associated prediction-flip stresses
- Stable, localized, and systemic severity
Reports can be persisted to JSON and evaluated against sample-level
policy gates.
```bash
failurelab sample-report --help
```
---
## Failure Correlation and Clustering
FailureLab can measure whether different stresses tend to fail on the
same samples.
Pairwise correlations help reveal perturbations that expose related
weaknesses. These relationships can then be grouped into larger failure
clusters.
Correlation policies can limit:
- Maximum observed failure correlation
- Number of highly correlated stress pairs
- Configurable high-correlation thresholds
Cluster policies can limit:
- Number of vulnerability clusters
- Maximum cluster size
```bash
failurelab correlation --help
failurelab clusters --help
```
---
## Robustness Policies
FailureLab supports configurable policies that turn analysis results
into automated PASS/FAIL gates.
Policies can enforce:
- Global robustness thresholds
- Stress-specific thresholds
- Warning and failure severity levels
- Class-level thresholds
- Minimum sample requirements
- Minimum class coverage
- Sample-level systemic-failure limits
- Correlation limits
- Failure-cluster limits
```bash
failurelab policy-evaluate --help
```
---
## Experiment Tracking
`ExperimentRunner` combines suite execution, result persistence, and
history tracking.
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
Each run can record its suite, model ID, run ID, timestamp, status,
worst stress, worst degradation, and configured threshold.
---
## Robustness History
FailureLab can retain repeated experiment results and detect whether
robustness changes over time.
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
CLI:
```bash
failurelab history --input history.json --suite production-vision
```
---
## Model Progression Analysis
FailureLab can track failure-rate changes across model checkpoints and
classify transitions as improved, stable, or regressed.
Across a checkpoint history, the overall trend can be classified as:
- Improving
- Stable
- Degrading
- Volatile
Progression analysis supports configurable tolerance, policy gates,
checkpoint risk scoring, and JSON export.
```bash
failurelab progression --input progression.json
```
---
## Failure Signatures
FailureLab can summarize failure behavior across stress types as a
reusable failure signature.
Signatures classify weaknesses as:
- Low-risk
- Localized
- Systemic
- Unstable
Signatures can be compared between model versions to detect regressions,
severity changes, and changes in the dominant failure mode.
Signature history extends the analysis across multiple checkpoints and
classifies the trajectory as improving, stable, degrading, or volatile.
```bash
failurelab signature --input signature.json
failurelab signature-history --input history.json
```
Signature workflows support diagnostics, policy gates, JSON export, and
Python API access.
---
## Failure Triage
FailureLab can rank detected weaknesses according to their remediation
priority.
Priority scoring considers:
- Failure rate
- Prediction instability
- Affected fraction
- Optional severity weighting
Failures are classified into:
```text
low
medium
high
critical
```
A triage report ranks failures from highest to lowest priority and
summarizes critical, high, medium, low, and actionable failures.
FailureLab also identifies the primary driver behind each priority and
generates a structured remediation recommendation.
CLI:
```bash
failurelab triage --input triage.json
```
Optional policy controls can enforce limits on critical failures,
high-priority failures, actionable failures, and maximum priority score.
```bash
failurelab triage \
  --input triage.json \
  --max-critical 0 \
  --max-high 1 \
  --output triage-report.json
```
---
## Triage Comparison
FailureLab can compare the remediation burden of a baseline model
against a candidate model.
Comparison tracks changes in:
- Actionable failures
- Critical failures
- Highest failure-priority score
The result is classified as:
```text
improved
stable
regressed
```
CLI:
```bash
failurelab triage-compare \
  --baseline baseline.json \
  --candidate candidate.json
```
Regression policies can limit actionable-failure increases,
critical-failure increases, and priority-score increases.
A configurable score tolerance can also prevent insignificant score
movement from being classified as a regression.
```bash
failurelab triage-compare \
  --baseline baseline.json \
  --candidate candidate.json \
  --score-tolerance 0.01 \
  --max-actionable-increase 0 \
  --max-critical-increase 0 \
  --max-score-increase 0.05 \
  --output triage-comparison.json
```
This makes failure prioritization usable as a CI gate between model
releases.
---
## Failure Persistence
FailureLab can track the same failure across multiple model checkpoints
to determine whether a weakness is isolated or repeatedly survives new
model versions.
Failures can be classified as:
```text
isolated
recurring
persistent
```
Persistence reports track recurrence behavior, persistent and recurring
failure counts, unresolved failures, and the failure with the highest
persistence.
CLI:
```bash
failurelab persistence \
  --input persistence.json
```
Optional policy gates can limit persistent, recurring, and unresolved
failures or enforce a maximum recurrence rate.
```bash
failurelab persistence \
  --input persistence.json \
  --max-persistent 0 \
  --max-unresolved 1 \
  --max-recurrence-rate 0.75 \
  --output persistence-report.json
```
This makes it possible to detect weaknesses that repeatedly survive
model updates instead of treating every evaluation as an isolated run.
---
## Failure Resolution
FailureLab can analyze whether recurring failures are actually being
resolved across checkpoints.
Resolution status is classified as:
```text
improving
unchanged
worsening
insufficient_history
```
Resolution reports track first and latest failure scores, score changes,
occurrence counts, unresolved failures, and the worst observed
regression.
A configurable tolerance can prevent insignificant score movement from
being treated as improvement or regression.
CLI:
```bash
failurelab resolution \
  --input resolution.json \
  --tolerance 0.01
```
Resolution policy gates can limit worsening, unchanged, and unresolved
failures or enforce a maximum allowed failure-score regression.
```bash
failurelab resolution \
  --input resolution.json \
  --max-worsening 0 \
  --max-unresolved 1 \
  --max-score-regression 0.05 \
  --output resolution-report.json
```
Together, persistence and resolution analysis show both **which
failures keep returning** and **whether later model versions are
actually fixing them**.
---
## Batch Experiments
Multiple models or experiment configurations can be executed as one
batch.
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
The first severity level where the configured failure criterion is
crossed becomes part of the model's failure envelope.
---
## Custom Stress Tests
Project-specific transformations can use the same robustness pipeline as
built-in stresses.
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
Visualization uses a headless backend for CI, containers, servers, and
terminal environments.
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
FailureLab evaluates failure-threshold regressions and worst-case
degradation regressions.
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
```
Inspect any command with:
```bash
failurelab <command> --help
```
CLI exit codes are suitable for automated pipelines:
```text
0 = passed
1 = robustness or policy failure detected
2 = invalid input or configuration error
```
---
## CI/CD
FailureLab can act as a model robustness and failure-regression gate in
CI.
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
      - name: Compare robustness snapshots
        run: |
          failurelab compare \
            --baseline reports/baseline_snapshot.json \
            --candidate reports/candidate_snapshot.json
```
A detected regression or policy violation returns a non-zero exit code
and can block the pipeline.
---
## Reports and JSON Export
FailureLab supports structured output across its robustness and
failure-analysis workflows.
Core reports can be exported as HTML or JSON:
```python
report.save_html(
    "failurelab_report.html"
)
report.save_json(
    "failurelab_report.json"
)
```
A report with a failure envelope can also be saved as a reusable
robustness snapshot:
```python
report.save_snapshot(
    "model_snapshot.json"
)
```
Structured JSON output is available for workflows including:
- Cross-stress analysis
- Sample-level failure analysis
- Failure correlation
- Failure clustering
- Model progression
- Failure signatures
- Signature history
- Failure triage
- Triage policy evaluation
- Triage comparison
- Triage comparison policy evaluation
- Failure persistence
- Persistence policy evaluation
- Failure resolution
- Resolution policy evaluation
---
## Public Python API
FailureLab exposes its major workflows through the package-level Python
API.
Public interfaces cover:
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
- Signature comparison
- Signature history
- Failure priority scoring
- Failure triage
- Remediation recommendations
- Triage policy evaluation
- Triage comparison
- Triage regression policy evaluation
- Failure persistence analysis
- Persistence policy evaluation
- Failure resolution analysis
- Resolution policy evaluation
- JSON export
This allows the same capabilities used by the CLI to be integrated
directly into Python evaluation pipelines.
---
## Testing
Run the complete test suite:
```bash
python -m pytest -q
```
The automated suite covers FailureLab's core evaluation, stress tests,
policies, reports, experiment tracking, model comparison, progression,
failure signatures, triage, persistence, resolution analysis, failure
forecasting, CLI workflows, and public Python API.
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
For v0.10.0:
```text
failurelab-0.10.0-py3-none-any.whl
failurelab-0.10.0.tar.gz
```
---
## Current Scope
FailureLab currently focuses on image-classification robustness.
Its stress tests measure model behavior under configured image
perturbations. FailureLab does not attempt to model every real-world
distribution shift or establish that a model is safe for a particular
deployment.
Robustness scores, thresholds, correlations, clusters, priority scores,
persistence metrics, resolution trends, forecasts, and policy gates
should be treated as engineering diagnostics under the configured
evaluation.
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
8. Are those persistent failures actually improving?
9. Did a new model version make robustness better or worse?
The goal is to make robustness testing, failure-pattern discovery,
failure-resolution tracking, and projected-risk analysis part of model
development and validation rather than something discovered only after
deployment.
---
## Status
FailureLab is under active development.
Current version:
```text
0.9.0
```
v0.9.0 adds failure recurrence and persistence analysis,
unresolved-failure tracking, resolution trends across checkpoints,
persistence and resolution policy gates, JSON export, expanded Python
APIs, and new `persistence` and `resolution` CLI workflows.
---
## License
FailureLab is licensed under the Apache License 2.0.
See `LICENSE` and `NOTICE` for details.