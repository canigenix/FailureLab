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