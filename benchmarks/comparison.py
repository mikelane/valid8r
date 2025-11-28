"""Benchmark comparison utilities for CI integration.

This module provides utilities for comparing benchmark results against baselines,
detecting performance regressions, and generating reports for PRs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

NS_PER_SECOND = 1_000_000_000
NS_PER_MILLISECOND = 1_000_000
NS_PER_MICROSECOND = 1_000
OPS_PER_MILLION = 1_000_000
OPS_PER_THOUSAND = 1_000
MIN_CLI_ARGS = 2
MIN_CLI_ARGS_WITH_BASELINE = 3


@dataclass
class BenchmarkResult:
    """Single benchmark measurement result."""

    name: str
    median_ns: float
    mean_ns: float
    min_ns: float
    max_ns: float
    ops_per_sec: float
    rounds: int

    @classmethod
    def from_pytest_benchmark(cls, data: dict[str, Any]) -> BenchmarkResult:
        """Create from pytest-benchmark JSON format."""
        stats = data.get('stats', {})
        return cls(
            name=data.get('name', 'unknown'),
            median_ns=stats.get('median', 0) * NS_PER_SECOND,
            mean_ns=stats.get('mean', 0) * NS_PER_SECOND,
            min_ns=stats.get('min', 0) * NS_PER_SECOND,
            max_ns=stats.get('max', 0) * NS_PER_SECOND,
            ops_per_sec=stats.get('ops', 0),
            rounds=stats.get('rounds', 0),
        )


@dataclass
class ComparisonResult:
    """Comparison between current and baseline benchmark."""

    name: str
    current: BenchmarkResult
    baseline: BenchmarkResult | None
    delta_percent: float | None
    is_regression: bool
    is_improvement: bool

    @property
    def status_emoji(self) -> str:
        """Get status emoji for display."""
        if self.baseline is None:
            return 'NEW'
        if self.is_regression:
            return 'SLOWER'
        if self.is_improvement:
            return 'FASTER'
        return 'OK'


def load_benchmark_results(path: Path) -> dict[str, BenchmarkResult]:
    """Load benchmark results from pytest-benchmark JSON file."""
    if not path.exists():
        return {}

    with path.open() as f:
        data = json.load(f)

    results: dict[str, BenchmarkResult] = {}
    for benchmark in data.get('benchmarks', []):
        result = BenchmarkResult.from_pytest_benchmark(benchmark)
        results[result.name] = result

    return results


def compare_benchmarks(
    current: dict[str, BenchmarkResult],
    baseline: dict[str, BenchmarkResult],
    regression_threshold: float = 0.05,
    improvement_threshold: float = 0.05,
) -> list[ComparisonResult]:
    """Compare current results against baseline.

    Args:
        current: Current benchmark results
        baseline: Baseline benchmark results
        regression_threshold: Percentage increase to flag as regression (0.05 = 5%)
        improvement_threshold: Percentage decrease to flag as improvement (0.05 = 5%)

    Returns:
        List of comparison results

    """
    comparisons: list[ComparisonResult] = []

    for name, current_result in current.items():
        baseline_result = baseline.get(name)

        if baseline_result is None:
            comparisons.append(
                ComparisonResult(
                    name=name,
                    current=current_result,
                    baseline=None,
                    delta_percent=None,
                    is_regression=False,
                    is_improvement=False,
                )
            )
            continue

        if baseline_result.median_ns == 0:
            delta_percent = float('inf') if current_result.median_ns > 0 else 0.0
        else:
            delta_percent = (current_result.median_ns - baseline_result.median_ns) / baseline_result.median_ns

        comparisons.append(
            ComparisonResult(
                name=name,
                current=current_result,
                baseline=baseline_result,
                delta_percent=delta_percent,
                is_regression=delta_percent > regression_threshold,
                is_improvement=delta_percent < -improvement_threshold,
            )
        )

    return sorted(comparisons, key=lambda c: c.name)


def format_ns(ns: float) -> str:
    """Format nanoseconds for human readability."""
    if ns >= NS_PER_SECOND:
        return f'{ns / NS_PER_SECOND:.2f}s'
    if ns >= NS_PER_MILLISECOND:
        return f'{ns / NS_PER_MILLISECOND:.2f}ms'
    if ns >= NS_PER_MICROSECOND:
        return f'{ns / NS_PER_MICROSECOND:.2f}us'
    return f'{ns:.0f}ns'


def format_ops(ops: float) -> str:
    """Format operations per second for human readability."""
    if ops >= OPS_PER_MILLION:
        return f'{ops / OPS_PER_MILLION:.2f}M ops/sec'
    if ops >= OPS_PER_THOUSAND:
        return f'{ops / OPS_PER_THOUSAND:.2f}K ops/sec'
    return f'{ops:.0f} ops/sec'


def generate_markdown_table(comparisons: list[ComparisonResult]) -> str:
    """Generate markdown table for PR comments."""
    lines = [
        '| Benchmark | Current | Baseline | Delta | Status |',
        '|-----------|---------|----------|-------|--------|',
    ]

    for comp in comparisons:
        current = format_ns(comp.current.median_ns)
        baseline = format_ns(comp.baseline.median_ns) if comp.baseline else 'N/A'
        delta = f'{comp.delta_percent:+.1%}' if comp.delta_percent is not None else 'N/A'

        lines.append(f'| {comp.name} | {current} | {baseline} | {delta} | {comp.status_emoji} |')

    return '\n'.join(lines)


def generate_pr_comment(
    comparisons: list[ComparisonResult],
    python_version: str,
    *,
    has_regressions: bool,
) -> str:
    """Generate full PR comment with benchmark results."""
    regression_count = sum(1 for c in comparisons if c.is_regression)
    improvement_count = sum(1 for c in comparisons if c.is_improvement)
    new_count = sum(1 for c in comparisons if c.baseline is None)

    header = f'## Benchmark Results (Python {python_version})\n\n'

    summary_parts = []
    if regression_count > 0:
        summary_parts.append(f'{regression_count} regression(s) detected')
    if improvement_count > 0:
        summary_parts.append(f'{improvement_count} improvement(s)')
    if new_count > 0:
        summary_parts.append(f'{new_count} new benchmark(s)')

    if has_regressions:
        summary = f'### Performance Alert\n\n{", ".join(summary_parts)}.\n\n'
    elif summary_parts:
        summary = f'### Summary\n\n{", ".join(summary_parts)}.\n\n'
    else:
        summary = '### Summary\n\nNo significant changes detected.\n\n'

    table = generate_markdown_table(comparisons)

    footer = '\n\nFull results available in workflow artifacts.'

    return header + summary + table + footer


def check_for_regressions(
    comparisons: list[ComparisonResult],
) -> tuple[bool, list[str]]:
    """Check if any benchmarks regressed beyond threshold.

    Args:
        comparisons: List of comparison results

    Returns:
        Tuple of (has_regressions, list of regression messages)

    """
    regressions = [
        f'{comp.name}: {comp.delta_percent:+.1%} regression '
        f'(current: {format_ns(comp.current.median_ns)}, '
        f'baseline: {format_ns(comp.baseline.median_ns) if comp.baseline else "N/A"})'
        for comp in comparisons
        if comp.is_regression and comp.delta_percent is not None
    ]

    return len(regressions) > 0, regressions


def save_baseline(results: dict[str, BenchmarkResult], path: Path) -> None:
    """Save benchmark results as baseline."""
    data = {
        'benchmarks': [
            {
                'name': r.name,
                'stats': {
                    'median': r.median_ns / NS_PER_SECOND,
                    'mean': r.mean_ns / NS_PER_SECOND,
                    'min': r.min_ns / NS_PER_SECOND,
                    'max': r.max_ns / NS_PER_SECOND,
                    'ops': r.ops_per_sec,
                    'rounds': r.rounds,
                },
            }
            for r in results.values()
        ]
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w') as f:
        json.dump(data, f, indent=2)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < MIN_CLI_ARGS:
        print('Usage: python -m benchmarks.comparison <current.json> [baseline.json]')
        sys.exit(1)

    current_path = Path(sys.argv[1])
    baseline_path = Path(sys.argv[2]) if len(sys.argv) >= MIN_CLI_ARGS_WITH_BASELINE else None

    current = load_benchmark_results(current_path)
    baseline = load_benchmark_results(baseline_path) if baseline_path else {}

    comparisons = compare_benchmarks(current, baseline)
    has_regressions, regression_messages = check_for_regressions(comparisons)

    print(generate_pr_comment(comparisons, '3.12', has_regressions=has_regressions))

    if has_regressions:
        print('\n### Regressions Detected:\n')
        for msg in regression_messages:
            print(f'  - {msg}')
        sys.exit(1)
