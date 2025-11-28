# Automated Benchmark Suite

Valid8r includes an automated benchmark suite that runs in CI, tracks performance over time, and compares against competitor libraries.

## Overview

The benchmark suite provides:

- **Automated CI integration**: Benchmarks run on every PR affecting core code
- **Regression detection**: Performance changes >5% are flagged
- **Competitor comparison**: Head-to-head with Pydantic, marshmallow, and cerberus
- **Historical tracking**: Baselines stored in Git, updated weekly
- **PR comments**: Automatic performance delta tables on pull requests

## Benchmark Categories

### Parser Speed

Measures time to parse string inputs into validated types:

| Parser | Input | What It Tests |
|--------|-------|---------------|
| `parse_int` | `"42"` | Basic integer coercion |
| `parse_email` | `"user@example.com"` | Email validation with `email-validator` |
| `parse_url` | `"https://example.com/path"` | URL parsing into structured components |
| `parse_phone` | `"(555) 123-4567"` | Phone number parsing (NANP) |

### Validation Speed

Measures chained validation using bind/map:

```python
# Example: Parse and validate age
result = parse_int(text).bind(validators.minimum(0)).bind(validators.maximum(120))
```

### Nested Object Validation

Validates complex objects with multiple fields:

```python
{
    "name": "John Doe",
    "age": 30,
    "email": "john@example.com"
}
```

### Bulk Operations

Parses lists of 100 items to measure throughput:

```python
# 100 string integers to list[int]
["0", "1", "2", ..., "99"]
```

### Memory Usage

Peak memory during validation operations (planned for future releases).

## Running Benchmarks

### Full Suite

```bash
# Run all benchmarks with output
uv run pytest tests/benchmarks/test_benchmarks.py --benchmark-only

# Sort by name for comparison
uv run pytest tests/benchmarks/test_benchmarks.py --benchmark-only --benchmark-sort=name

# Generate JSON report
uv run pytest tests/benchmarks/test_benchmarks.py --benchmark-only --benchmark-json=results.json
```

### Specific Categories

```bash
# Integer parsing only
uv run pytest tests/benchmarks/test_benchmarks.py::DescribeIntegerParsing --benchmark-only

# Email validation only
uv run pytest tests/benchmarks/test_benchmarks.py::DescribeEmailValidation --benchmark-only

# Nested objects only
uv run pytest tests/benchmarks/test_benchmarks.py::DescribeNestedObjectValidation --benchmark-only
```

### Verify Correctness

Before running benchmarks, verify all scenarios are correctly implemented:

```bash
uv run pytest tests/benchmarks/test_benchmark_correctness.py -v
```

## CI Integration

### Workflow Triggers

The benchmark workflow (`.github/workflows/benchmarks.yml`) runs:

1. **On PRs**: When changes affect `valid8r/**/*.py`, `tests/benchmarks/**/*.py`, `benchmarks/**/*.py`, or `pyproject.toml`
2. **Weekly**: Every Monday at 00:00 UTC (scheduled)
3. **Manual**: Via workflow dispatch with optional baseline update

### Regression Detection

PRs receive automatic comments with performance deltas:

```
## Benchmark Results (Python 3.12)

### Summary

1 regression(s) detected, 2 improvement(s).

| Benchmark | Current | Baseline | Delta | Status |
|-----------|---------|----------|-------|--------|
| parse_int_success | 380ns | 362ns | +5.0% | SLOWER |
| parse_email_success | 38.5us | 40.9us | -5.9% | FASTER |
| parse_url_success | 4.8us | 4.9us | -2.0% | OK |
```

**Thresholds**:
- **>5% slower**: Flagged as regression (SLOWER)
- **>5% faster**: Flagged as improvement (FASTER)
- **Within 5%**: No flag (OK)

### Baseline Management

Baselines are stored in `benchmarks/baselines/`:

```
benchmarks/baselines/
├── README.md
├── baseline-py3.11.json
├── baseline-py3.12.json
└── baseline-py3.13.json
```

**Automatic Updates**:
- Weekly scheduled runs update baselines
- Manual trigger with `update_baseline: true`

**Manual Update**:

```bash
# Generate new baseline
uv run pytest tests/benchmarks/test_benchmarks.py \
    --benchmark-only \
    --benchmark-json=benchmark-results.json

# Copy to baselines
cp benchmark-results.json benchmarks/baselines/baseline-py3.12.json
```

## Competitor Comparison

### Libraries Compared

| Library | Version | Description |
|---------|---------|-------------|
| **valid8r** | 1.x | This library (Maybe monad, functional) |
| **Pydantic** | 2.x | Rust-powered, industry standard |
| **marshmallow** | 4.x | Schema-based, mature ecosystem |
| **cerberus** | 1.x | Lightweight, minimalist |

### Fair Comparison Principles

1. **Equivalent validation**: Same inputs, same validation logic
2. **Consistent returns**: All return parsed value or `None`
3. **No unfair optimizations**: No scenario favors one library
4. **Real-world patterns**: Benchmarks reflect actual usage

### Sample Results

Results vary by hardware. Here are typical results from Ubuntu CI runners:

**Integer Parsing (success)**:
| Library | Median | vs valid8r |
|---------|--------|------------|
| valid8r | 375ns | baseline |
| cerberus | 69us | 184x slower |
| marshmallow | 67us | 179x slower |
| Pydantic | 102us | 273x slower |

**Nested Object Validation (success)**:
| Library | Median | vs valid8r |
|---------|--------|------------|
| valid8r | 37us | baseline |
| marshmallow | 83us | 2.3x slower |
| cerberus | 151us | 4.1x slower |
| Pydantic | 568us | 15.5x slower |

**Note**: Pydantic's overhead includes features like JSON schema generation. For basic validation, valid8r is faster; for full-featured data models, Pydantic may be preferred.

## Adding New Benchmarks

### 1. Add Scenario Function

In `benchmarks/scenarios.py`:

```python
def benchmark_valid8r_custom(data: str) -> CustomType | None:
    """Parse custom type using valid8r."""
    result = parsers.parse_custom(data)
    return result.value_or(None)

def benchmark_pydantic_custom(data: str) -> CustomType | None:
    """Parse custom type using Pydantic."""
    class CustomModel(BaseModel):
        value: CustomType

    try:
        return CustomModel(value=data).value
    except ValidationError:
        return None
```

### 2. Add Correctness Test

In `tests/benchmarks/test_benchmark_correctness.py`:

```python
def it_validates_custom_parsing_success(self) -> None:
    """All libraries correctly parse valid custom input."""
    from benchmarks.scenarios import (
        benchmark_valid8r_custom,
        benchmark_pydantic_custom,
    )

    assert benchmark_valid8r_custom('valid') is not None
    assert benchmark_pydantic_custom('valid') is not None
```

### 3. Add Benchmark Test

In `tests/benchmarks/test_benchmarks.py`:

```python
class DescribeCustomValidation:
    def it_benchmarks_valid8r_custom_success(self, benchmark) -> None:
        """Benchmark valid8r custom validation (success)."""
        result = benchmark(benchmark_valid8r_custom, 'valid')
        assert result is not None

    def it_benchmarks_pydantic_custom_success(self, benchmark) -> None:
        """Benchmark Pydantic custom validation (success)."""
        result = benchmark(benchmark_pydantic_custom, 'valid')
        assert result is not None
```

### 4. Verify and Run

```bash
# Verify correctness
uv run pytest tests/benchmarks/test_benchmark_correctness.py -v -k custom

# Run benchmarks
uv run pytest tests/benchmarks/test_benchmarks.py::DescribeCustomValidation --benchmark-only
```

## Interpreting Results

### Timing Units

| Unit | Meaning | Example |
|------|---------|---------|
| ns | nanoseconds | 375ns = 0.000000375s |
| us | microseconds | 37us = 0.000037s |
| ms | milliseconds | 5ms = 0.005s |

### Key Metrics

| Metric | Description | Best For |
|--------|-------------|----------|
| **Median** | Middle value (50th percentile) | Comparing performance |
| **Mean** | Average | General overview |
| **Min** | Fastest iteration | Best-case scenario |
| **Max** | Slowest iteration | Worst-case scenario |
| **Ops/sec** | Operations per second | Throughput capacity |

### What to Focus On

1. **Median** is more reliable than Mean (less affected by outliers)
2. **Ops/sec** shows real-world throughput
3. Compare **same scenarios** across libraries (success vs success)
4. Consider **use case**: raw speed vs features vs developer experience

## Troubleshooting

### Benchmarks Running Slowly

```bash
# Reduce warmup and rounds for faster iteration
uv run pytest tests/benchmarks/test_benchmarks.py \
    --benchmark-only \
    --benchmark-warmup=on \
    --benchmark-warmup-iterations=1 \
    --benchmark-min-rounds=10
```

### Results Vary Between Runs

Normal variance is expected. For stable comparisons:
- Run multiple times and compare medians
- Ensure system is idle during benchmarking
- Use CI results (consistent environment) for official comparison

### Baseline Not Found

If CI reports "No baseline available":
1. Trigger workflow with `update_baseline: true`
2. Or wait for weekly scheduled update
3. Or manually create baseline (see Baseline Management above)

## Related Documentation

- [Performance Characteristics](../performance.md) - Detailed performance analysis
- [Benchmark Scenarios](../../benchmarks/README.md) - Implementation details
- [CI Workflow](../../.github/workflows/benchmarks.yml) - GitHub Actions configuration
