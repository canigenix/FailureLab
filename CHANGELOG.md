## [0.9.0] - 2026-08-20

### Added

- Failure recurrence analysis across model checkpoints.
- Isolated, recurring, and persistent failure classification.
- Failure persistence reports with recurrence rates and unresolved-failure tracking.
- Persistence policy gates for persistent, recurring, and unresolved failures.
- Maximum recurrence-rate enforcement.
- JSON export for persistence reports and policy results.
- Public Python API for persistence workflows.
- `persistence` CLI command.
- Failure resolution analysis across checkpoints.
- Improving, unchanged, worsening, and insufficient-history resolution classification.
- Configurable tolerance for resolution analysis.
- Resolution reports with unresolved-failure counts and worst-regression detection.
- Resolution policy gates for worsening, unchanged, and unresolved failures.
- Maximum failure-score regression enforcement.
- JSON export for resolution reports and policy results.
- Public Python API for resolution workflows.
- `resolution` CLI command.

### Improved

- FailureLab can now distinguish failures that repeatedly survive across model versions from one-off failures.
- Persistent weaknesses can be tracked to determine whether later model versions are actually resolving them.
- CI workflows can reject releases when known failures persist, worsen, or exceed configured regression limits.

### Validation

- Full automated test suite passing.
- Public v0.9.0 API imports verified.

## [0.8.0] - 2026-08-20

### Added

- Failure priority scoring using failure rate, prediction instability, affected breadth, and severity weighting.
- Low, medium, high, and critical failure priority classification.
- Ranked failure triage reports.
- Critical, high, medium, low, and actionable failure counts.
- Primary failure-driver identification.
- Structured remediation recommendations.
- Failure triage policy gates for critical, high-priority, actionable, and maximum-score limits.
- JSON export for triage reports, remediation guidance, and policy results.
- Failure triage comparison across model versions.
- Improved, stable, and regressed triage comparison classification.
- Actionable-failure, critical-failure, and highest-priority-score delta tracking.
- Configurable score tolerance for triage comparisons.
- Triage comparison regression policy gates.
- JSON export for triage comparisons and comparison policy results.
- Public Python API support for failure triage and triage comparison workflows.
- `triage` CLI command.
- `triage-compare` CLI command.

### Improved

- FailureLab can now prioritize detected weaknesses instead of treating all failures equally.
- Failure analysis now includes structured guidance for determining which weaknesses should be addressed first.
- Model-version comparisons can detect whether overall remediation burden is improving or regressing.
- CI workflows can enforce failure-priority and triage-regression limits.

### Validation

- Full automated test suite passing.
- Failure priority, triage, remediation, policy, export, API, and CLI workflows verified.
- Triage comparison, regression policy, JSON export, API, and CLI workflows verified.

## [0.7.0]

### Added

- Failure signatures for identifying model weakness patterns across stresses
- Localized, systemic, unstable, and low-risk signature classification
- Structured failure diagnostics with likely causes and recommended actions
- Failure signature comparison across model versions
- Signature regression and severity policy gates
- Dominant-stress change detection
- JSON export for signatures, diagnostics, comparisons, and policy results
- Multi-version failure signature history analysis
- Improving, stable, degrading, and volatile history trend classification
- Signature history policy gates for regressions, severity changes, dominant-stress changes, and volatility
- JSON export for signature history and policy results
- Public Python API support for signature and signature-history workflows
- `signature` CLI command
- `signature-history` CLI command

## [0.6.0] - 2026-08-19

### Added

- Model failure progression analysis across checkpoints and versions
- Improved, stable, and regressed transition classification
- Progression trend detection for improving, stable, degrading, and volatile histories
- Configurable tolerance for progression analysis
- Progression policy gates for automated regression enforcement
- Maximum overall regression and regressed-transition limits
- Optional volatile-history rejection
- Checkpoint risk scoring and highest-risk checkpoint detection
- Structured progression history reports
- JSON export for progression reports, policy results, and checkpoint risks
- Public Python API for progression workflows
- `failurelab progression` CLI command
- CLI support for progression policies, tolerance, risk analysis, and JSON output

### Testing

- Added unit tests for progression analysis, policies, risk scoring, and JSON export
- Added public API coverage for progression workflows
- Added CLI progression tests
- Full automated test suite passing

## [0.5.0] - 2026-08-17

### Added

- Cross-stress class vulnerability analysis.
- Systemic, localized, and stable cross-stress severity classification.
- Cross-stress JSON reports and policy gates.
- Sample-level repeated failure and prediction-flip analysis.
- Sample failure severity classification.
- Persistent sample failure reports.
- Sample-level policy gates and CLI workflow.
- Stress failure correlation analysis.
- Correlation reports, policies, and CLI workflow.
- Failure clustering for correlated stress groups.
- Cluster reports, policies, and CLI workflow.
- Public Python API support for all v0.5.0 analysis layers.

### Improved

- FailureLab can now identify repeated weaknesses across classes, samples, and stress types.
- CI workflows can enforce systemic vulnerability, correlation, and cluster thresholds.
- Analysis results are more actionable through structured JSON reports and severity classifications.

### Validation

- Full automated test suite passing.
- Public v0.5.0 API imports verified.

## [0.4.0] - 2026-08-16

### Added

- Configurable robustness policy engine.
- Global and stress-specific policy thresholds.
- Warning and failure severity levels.
- JSON-based robustness policy configuration.
- Class-level robustness policy gates.
- Class-specific warning and failure thresholds.
- Minimum sample requirements for class evaluation.
- Class coverage enforcement.
- Policy evaluation reports with warnings, violations, and coverage metadata.
- `policy-evaluate` CLI workflow.
- CI-friendly policy exit codes.

### Improved

- Suite result persistence now includes class robustness summaries.
- Policy reports distinguish warnings from hard failures.
- Class policy evaluation tracks evaluated and skipped classes.
- Coverage requirements prevent misleading passes when evidence is insufficient.
- Public Python API expanded for policy and reporting workflows.

### Validation

- Full automated test suite passing.
- v0.4.0 wheel and source distribution built successfully.
- Clean isolated wheel installation verified.
- Installed CLI and public API verified.

## [0.3.0] - 2026-08-16

### Added

- JSON-configured stress suites.
- Suite-level maximum degradation thresholds.
- Automated suite PASS/FAIL status.
- Experiment runner with persisted result artifacts.
- Persistent suite history.
- Model IDs and run IDs for experiment tracking.
- Robustness trend detection.
- Model-specific history queries.
- Batch experiment execution.
- Batch JSON summaries.
- `suite` and `history` CLI workflows.
- Expanded public Python API.

### Improved

- Robustness workflows can now be configured and repeated without rebuilding evaluation logic manually.
- Experiment results can be tracked across model versions and repeated runs.
- CLI workflows now support suite inspection and history analysis.
- Release packaging and public API coverage expanded for v0.3.0.

### Validation

- 116 automated tests passing.
- v0.3.0 wheel and source distribution built successfully.
- Clean isolated wheel installation verified.
- Installed CLI and public API verified.