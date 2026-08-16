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