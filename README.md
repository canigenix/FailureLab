# FailureLab
**Find where vision models fail — before those failures reach production.**
FailureLab is an open-source Python framework for stress-testing computer vision models, measuring robustness degradation, discovering failure patterns, and detecting regressions between model versions.
Instead of asking only *"How accurate is my model?"*, FailureLab asks:
> **What breaks it, how badly does it break, and did the next version get worse?**
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.6.0-green)](https://github.com/canigenix/FailureLab/releases)
[![Tests](https://github.com/canigenix/FailureLab/actions/workflows/tests.yml/badge.svg)](https://github.com/canigenix/FailureLab/actions/workflows/tests.yml)
---
## FailureLab v0.6.0
Version 0.6.0 adds model progression analysis for tracking how failure behavior changes across model versions and checkpoints.
Highlights:
- Model checkpoint progression analysis
- Improved, stable, and regressed transition classification
- Improving, stable, degrading, and volatile trend detection
- Configurable progression tolerance
- Progression policy gates for CI workflows
- Checkpoint risk scoring and highest-risk checkpoint detection
- Structured progression reports and JSON export
- New `failurelab progression` CLI workflow
- Expanded public Python API
These capabilities build on FailureLab's existing stress suites, experiment history, robustness policies, visualization, model comparison, and CI regression gates.
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
- Model checkpoint progression analysis
- Progression trend classification and policy gates
- Checkpoint risk scoring
- Progression JSON export
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
failurelab 0.6.0
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
## Cross-Stress Vulnerability Analysis
FailureLab can analyze whether individual classes repeatedly fail across multiple stress conditions.
Instead of looking at each perturbation independently, cross-stress analysis identifies broader vulnerability patterns and classifies them by severity.
This helps distinguish a weakness isolated to one perturbation from a class that is systematically fragile across several stresses.
Cross-stress results can also be evaluated against configurable policies for automated robustness gating.
CLI:
```bash
failurelab cross-stress --help
```
---
## Sample-Level Failure Analysis
FailureLab can identify individual samples that repeatedly fail across different stress conditions.
Sample-level analysis tracks:
- Failure frequency
- Prediction-flip frequency
- Stresses associated with failures
- Stresses associated with prediction flips
- Stable, localized, and systemic severity
Sample failure reports can be saved to JSON and loaded later without requiring the original model evaluation to remain in memory.
CLI:
```bash
failurelab sample-report --help
```
Sample-level policies can enforce limits on systemic failures for CI and automated evaluation workflows.
---
## Failure Correlation Analysis
FailureLab can measure whether different stresses tend to fail on the same samples.
For two stresses, the correlation analysis compares their failed-sample sets and measures their overlap.
This can reveal relationships such as:
```text
blur + noise
```
repeatedly affecting the same vulnerable examples.
FailureLab can analyze every stress pair automatically and rank the results by correlation strength.
CLI:
```bash
failurelab correlation --help
```
Correlation policies can enforce limits on:
- Maximum observed failure correlation
- Number of highly correlated stress pairs
- Configurable high-correlation thresholds
---
## Failure Clustering
Pairwise correlations can be combined into larger vulnerability groups.
FailureLab groups connected stresses whose failure correlation exceeds a configurable threshold.
For example:
```text
blur + compression + noise
```
may form a single failure cluster when those perturbations repeatedly affect related samples.
Cluster analysis reports:
- Number of clusters
- Stresses belonging to each cluster
- Cluster size
- Number of correlated pairs
- Mean correlation within each cluster
- Largest vulnerability cluster
CLI:
```bash
failurelab clusters --help
```
Cluster policies can enforce limits such as:
- Maximum number of vulnerability clusters
- Maximum allowed cluster size
---
## Robustness Policies
FailureLab supports configurable robustness policies that can turn analysis results into automated PASS/FAIL gates.
Policy capabilities include:
- Global robustness thresholds
- Stress-specific thresholds
- Warning and failure severity levels
- Class-level policies
- Class-specific warning/failure thresholds
- Minimum sample requirements
- Minimum class coverage
- Sample-level systemic-failure limits
- Correlation thresholds
- High-correlation pair limits
- Failure-cluster limits
Policy evaluation is designed for local development and automated CI workflows.
CLI:
```bash
failurelab policy-evaluate --help
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
- Suite name
- Model ID
- Run ID
- Timestamp
- PASS/FAIL status
- Worst stress
- Worst degradation
- Configured threshold
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
## Model Progression Analysis
FailureLab can track failure-rate changes across model checkpoints and classify each transition as improved, stable, or regressed.
Across a full checkpoint history, FailureLab classifies the trend as improving, stable, degrading, or volatile. Progression analysis also supports configurable tolerance, CI policy gates, checkpoint risk scoring, and JSON export.
CLI:
```bash
failurelab progression --input progression.json
```
Optional policy and export controls:
```bash
failurelab progression \
--input progression.json \
--max-regression 0.05 \
--max-regressed-transitions 1 \
--reject-volatile \
--output progression-report.json
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
- Failure-threshold regressions
- Worst-case degradation regressions
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
policy-evaluate
cross-stress
sample-report
correlation
clusters
progression
```
Inspect individual commands with:
```bash
failurelab <command> --help
```
For example:
```bash
failurelab clusters --help
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
1 = robustness or policy failure detected
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
      - name: Run tests
        run: python -m pytest -q
      - name: Compare robustness snapshots
        run: |
          failurelab compare \
            --baseline reports/baseline_snapshot.json \
            --candidate reports/candidate_snapshot.json
```
A detected regression or policy violation returns a non-zero exit code and can block the pipeline.
---
## Reports and Snapshots
FailureLab supports structured output for robustness workflows.
Core reports can be exported as HTML or JSON:
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
v0.6.0 provides structured JSON reports for:
- Cross-stress analysis
- Sample-level failure analysis
- Failure correlation analysis
- Failure clustering
Model progression analysis
Snapshots allow model versions to be compared without rerunning the original evaluation during the comparison step.
---
## Public Python API
FailureLab exposes its major robustness workflows through the package-level Python API.
v0.6.0 includes public interfaces for:
- Core robustness evaluation
- Configured stress suites
- Experiment history
- Model comparison
- Class-level policy evaluation
- Cross-stress analysis
- Sample-level failure analysis
- Failure correlation
- Failure clustering
- Model progression analysis and checkpoint risk scoring
- Corresponding policy evaluators and configuration loaders
This allows the same analysis capabilities used by the CLI to be integrated directly into Python evaluation pipelines.
---
## Testing
Run the complete test suite:
```bash
python -m pytest -q
FailureLab v0.6.0 currently passes:
```text
231 automated tests
```
FailureLab's automated suite covers:
- Core robustness evaluation
- Built-in and custom stress tests
- Robustness scoring
- Per-class analysis
- Failure envelopes
- Snapshots
- Model comparison
- Visualization
- Configured suites
- Experiment history
- Batch execution
- Robustness policies
- Cross-stress analysis
- Sample-level failure analysis
- Failure correlation
- Failure clustering
- Model progression analysis and policy gates
- CLI behavior
- Public API behavior
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
For v0.6.0:
```text
failurelab-0.6.0-py3-none-any.whl
failurelab-0.6.0.tar.gz
```
---
## Current Scope
FailureLab currently focuses on image-classification robustness.
Its stress tests measure model behavior under configured image perturbations. FailureLab does not attempt to model every real-world distribution shift or establish that a model is safe for a particular deployment.
Robustness scores, thresholds, correlations, clusters, and policy gates should be treated as engineering diagnostics under the configured evaluation.
---
## Design Philosophy
FailureLab is built around a few practical questions:
1. What breaks the model?
2. How severe is the weakness?
3. At what point does failure begin?
4. Which classes and samples repeatedly fail?
5. Which stresses expose the same underlying weaknesses?
6. Did a new model version make robustness better or worse?
The goal is to make robustness testing and failure-pattern discovery part of model development and validation rather than something discovered only after deployment.
---
## Status
FailureLab is under active development.
Current version:
```text
0.6.0
```
v0.6.0 adds model progression analysis, trend classification, progression policy gates, checkpoint risk scoring, JSON progression export, and a CI-friendly progression CLI workflow.
---
## License
FailureLab is licensed under the Apache License 2.0.
See `LICENSE` and `NOTICE` for details.