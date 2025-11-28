# Benchmark Baselines

This directory contains baseline benchmark results used for performance regression detection in CI.

## File Format

Each baseline file is named `baseline-py{version}.json` (e.g., `baseline-py3.12.json`) and contains benchmark results in pytest-benchmark JSON format.

## Updating Baselines

Baselines are automatically updated:
1. **Weekly**: On Monday via scheduled workflow
2. **Manual**: Via workflow dispatch with `update_baseline: true`

### Manual Update

To manually update baselines:

```bash
# Run benchmarks and generate results
uv run pytest tests/benchmarks/test_benchmarks.py \
    --benchmark-only \
    --benchmark-json=benchmark-results.json

# Copy to baselines directory
cp benchmark-results.json benchmarks/baselines/baseline-py3.12.json
```

Or trigger via GitHub Actions:
1. Go to Actions > Performance Benchmarks
2. Click "Run workflow"
3. Check "Update baseline after successful run"

## Regression Detection

CI compares current results against baselines:
- **>5% slower**: Flagged as regression (warning in PR comment)
- **>5% faster**: Flagged as improvement (noted in PR comment)
- **New benchmarks**: Marked as "NEW" (no baseline comparison)

## File Structure

```
baselines/
├── README.md              # This file
├── baseline-py3.11.json   # Python 3.11 baseline
├── baseline-py3.12.json   # Python 3.12 baseline
└── baseline-py3.13.json   # Python 3.13 baseline
```

## Notes

- Baselines should only be updated on `main` branch
- Results may vary between platforms (CI runs on Ubuntu)
- Local results (macOS, different hardware) may differ from CI baselines
