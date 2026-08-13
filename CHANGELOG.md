# Changelog

All notable changes to FailureLab will be documented in this file.

## [0.2.0] - 2026-08-12

### Added

- Per-class robustness analysis.
- Per-class stressed failure rates.
- Prediction flip-rate analysis.
- Top confusion-class detection.
- Custom user-defined stress tests.
- Robustness degradation visualizations.
- `failurelab visualize` CLI command.
- Headless chart generation for CI and server environments.
- Optional `visualization` dependency.

### Improved

- Vision diagnostics now expose more detailed class-level failure behavior.
- Stress testing can be extended with custom transformations.
- Visualization dependencies are separated from the lightweight core package.
- CLI functionality expanded for robustness visualization.
- Test coverage expanded across the new v0.2.0 functionality.

### Validation

- 89 automated tests passing.
- Source distribution and wheel build successfully.
- Clean core installation verified.
- Visualization extra installation verified independently.
- CLI and headless visualization behavior verified.