"""Tests for benchmark comparison utilities."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from benchmarks.comparison import (
    BenchmarkResult,
    ComparisonResult,
    check_for_regressions,
    compare_benchmarks,
    format_ns,
    format_ops,
    generate_markdown_table,
    generate_pr_comment,
    load_benchmark_results,
    save_baseline,
)

if TYPE_CHECKING:
    from pathlib import Path


class DescribeBenchmarkResult:
    def it_creates_from_pytest_benchmark_format(self) -> None:
        data = {
            'name': 'test_benchmark',
            'stats': {
                'median': 0.000001,
                'mean': 0.0000012,
                'min': 0.0000008,
                'max': 0.0000015,
                'ops': 1000000,
                'rounds': 100,
            },
        }

        result = BenchmarkResult.from_pytest_benchmark(data)

        assert result.name == 'test_benchmark'
        assert result.median_ns == 1000.0
        assert result.mean_ns == 1200.0
        assert result.min_ns == 800.0
        assert result.max_ns == 1500.0
        assert result.ops_per_sec == 1000000
        assert result.rounds == 100

    def it_handles_missing_stats(self) -> None:
        data = {'name': 'incomplete', 'stats': {}}

        result = BenchmarkResult.from_pytest_benchmark(data)

        assert result.name == 'incomplete'
        assert result.median_ns == 0.0
        assert result.ops_per_sec == 0


class DescribeLoadBenchmarkResults:
    def it_loads_from_json_file(self, tmp_path: Path) -> None:
        data = {
            'benchmarks': [
                {
                    'name': 'test_one',
                    'stats': {'median': 0.001, 'mean': 0.0012, 'min': 0.0008, 'max': 0.0015, 'ops': 1000, 'rounds': 50},
                },
                {
                    'name': 'test_two',
                    'stats': {'median': 0.002, 'mean': 0.0022, 'min': 0.0018, 'max': 0.0025, 'ops': 500, 'rounds': 50},
                },
            ]
        }

        file_path = tmp_path / 'results.json'
        file_path.write_text(json.dumps(data))

        results = load_benchmark_results(file_path)

        assert len(results) == 2
        assert 'test_one' in results
        assert 'test_two' in results
        assert results['test_one'].median_ns == 1_000_000.0
        assert results['test_two'].median_ns == 2_000_000.0

    def it_returns_empty_dict_for_missing_file(self, tmp_path: Path) -> None:
        results = load_benchmark_results(tmp_path / 'nonexistent.json')
        assert results == {}


class DescribeCompareBenchmarks:
    def it_detects_regressions(self) -> None:
        current = {
            'test': BenchmarkResult(
                name='test', median_ns=1100, mean_ns=1100, min_ns=1000, max_ns=1200, ops_per_sec=909, rounds=100
            )
        }
        baseline = {
            'test': BenchmarkResult(
                name='test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
            )
        }

        comparisons = compare_benchmarks(current, baseline, regression_threshold=0.05)

        assert len(comparisons) == 1
        assert comparisons[0].is_regression is True
        assert comparisons[0].delta_percent == pytest.approx(0.1, rel=0.01)

    def it_detects_improvements(self) -> None:
        current = {
            'test': BenchmarkResult(
                name='test', median_ns=900, mean_ns=900, min_ns=800, max_ns=1000, ops_per_sec=1111, rounds=100
            )
        }
        baseline = {
            'test': BenchmarkResult(
                name='test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
            )
        }

        comparisons = compare_benchmarks(current, baseline, improvement_threshold=0.05)

        assert len(comparisons) == 1
        assert comparisons[0].is_improvement is True
        assert comparisons[0].delta_percent == pytest.approx(-0.1, rel=0.01)

    def it_handles_new_benchmarks(self) -> None:
        current = {
            'new_test': BenchmarkResult(
                name='new_test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
            )
        }
        baseline: dict[str, BenchmarkResult] = {}

        comparisons = compare_benchmarks(current, baseline)

        assert len(comparisons) == 1
        assert comparisons[0].baseline is None
        assert comparisons[0].delta_percent is None
        assert comparisons[0].is_regression is False

    def it_handles_zero_baseline_median(self) -> None:
        current = {
            'test': BenchmarkResult(
                name='test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
            )
        }
        baseline = {
            'test': BenchmarkResult(name='test', median_ns=0, mean_ns=0, min_ns=0, max_ns=0, ops_per_sec=0, rounds=100)
        }

        comparisons = compare_benchmarks(current, baseline)

        assert len(comparisons) == 1
        assert comparisons[0].delta_percent == float('inf')

    def it_handles_zero_baseline_and_zero_current(self) -> None:
        current = {
            'test': BenchmarkResult(name='test', median_ns=0, mean_ns=0, min_ns=0, max_ns=0, ops_per_sec=0, rounds=100)
        }
        baseline = {
            'test': BenchmarkResult(name='test', median_ns=0, mean_ns=0, min_ns=0, max_ns=0, ops_per_sec=0, rounds=100)
        }

        comparisons = compare_benchmarks(current, baseline)

        assert len(comparisons) == 1
        assert comparisons[0].delta_percent == 0.0

    def it_marks_small_changes_as_ok(self) -> None:
        current = {
            'test': BenchmarkResult(
                name='test', median_ns=1020, mean_ns=1020, min_ns=1000, max_ns=1050, ops_per_sec=980, rounds=100
            )
        }
        baseline = {
            'test': BenchmarkResult(
                name='test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
            )
        }

        comparisons = compare_benchmarks(current, baseline, regression_threshold=0.05)

        assert len(comparisons) == 1
        assert comparisons[0].is_regression is False
        assert comparisons[0].is_improvement is False


class DescribeComparisonResult:
    def it_returns_correct_status_emoji(self) -> None:
        base = BenchmarkResult(
            name='test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
        )

        new_benchmark = ComparisonResult(
            name='test', current=base, baseline=None, delta_percent=None, is_regression=False, is_improvement=False
        )
        assert new_benchmark.status_emoji == 'NEW'

        regression = ComparisonResult(
            name='test', current=base, baseline=base, delta_percent=0.1, is_regression=True, is_improvement=False
        )
        assert regression.status_emoji == 'SLOWER'

        improvement = ComparisonResult(
            name='test', current=base, baseline=base, delta_percent=-0.1, is_regression=False, is_improvement=True
        )
        assert improvement.status_emoji == 'FASTER'

        no_change = ComparisonResult(
            name='test', current=base, baseline=base, delta_percent=0.02, is_regression=False, is_improvement=False
        )
        assert no_change.status_emoji == 'OK'


class DescribeFormatFunctions:
    @pytest.mark.parametrize(
        ('ns', 'expected'),
        [
            pytest.param(500, '500ns', id='nanoseconds'),
            pytest.param(1500, '1.50us', id='microseconds'),
            pytest.param(1_500_000, '1.50ms', id='milliseconds'),
            pytest.param(1_500_000_000, '1.50s', id='seconds'),
        ],
    )
    def it_formats_nanoseconds(self, ns: float, expected: str) -> None:
        assert format_ns(ns) == expected

    @pytest.mark.parametrize(
        ('ops', 'expected'),
        [
            pytest.param(500, '500 ops/sec', id='ops'),
            pytest.param(5000, '5.00K ops/sec', id='kilo-ops'),
            pytest.param(5_000_000, '5.00M ops/sec', id='mega-ops'),
        ],
    )
    def it_formats_operations(self, ops: float, expected: str) -> None:
        assert format_ops(ops) == expected


class DescribeGenerateMarkdownTable:
    def it_generates_table_with_comparisons(self) -> None:
        base = BenchmarkResult(
            name='test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
        )

        comparisons = [
            ComparisonResult(
                name='test_regression',
                current=BenchmarkResult(
                    name='test', median_ns=1100, mean_ns=1100, min_ns=1000, max_ns=1200, ops_per_sec=909, rounds=100
                ),
                baseline=base,
                delta_percent=0.1,
                is_regression=True,
                is_improvement=False,
            ),
            ComparisonResult(
                name='test_new',
                current=base,
                baseline=None,
                delta_percent=None,
                is_regression=False,
                is_improvement=False,
            ),
        ]

        table = generate_markdown_table(comparisons)

        assert '| Benchmark | Current | Baseline | Delta | Status |' in table
        assert 'test_new' in table
        assert 'test_regression' in table
        assert '+10.0%' in table
        assert 'SLOWER' in table
        assert 'NEW' in table


class DescribeCheckForRegressions:
    def it_returns_true_when_regressions_exist(self) -> None:
        base = BenchmarkResult(
            name='test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
        )

        comparisons = [
            ComparisonResult(
                name='regressed_test',
                current=BenchmarkResult(
                    name='test', median_ns=1100, mean_ns=1100, min_ns=1000, max_ns=1200, ops_per_sec=909, rounds=100
                ),
                baseline=base,
                delta_percent=0.1,
                is_regression=True,
                is_improvement=False,
            ),
        ]

        has_regressions, messages = check_for_regressions(comparisons)

        assert has_regressions is True
        assert len(messages) == 1
        assert 'regressed_test' in messages[0]

    def it_returns_false_when_no_regressions(self) -> None:
        base = BenchmarkResult(
            name='test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
        )

        comparisons = [
            ComparisonResult(
                name='ok_test',
                current=base,
                baseline=base,
                delta_percent=0.02,
                is_regression=False,
                is_improvement=False,
            ),
        ]

        has_regressions, messages = check_for_regressions(comparisons)

        assert has_regressions is False
        assert len(messages) == 0


class DescribeSaveBaseline:
    def it_saves_results_to_json(self, tmp_path: Path) -> None:
        results = {
            'test': BenchmarkResult(
                name='test', median_ns=1000, mean_ns=1200, min_ns=800, max_ns=1500, ops_per_sec=1000000, rounds=100
            )
        }

        file_path = tmp_path / 'baseline.json'
        save_baseline(results, file_path)

        assert file_path.exists()
        data = json.loads(file_path.read_text())
        assert 'benchmarks' in data
        assert len(data['benchmarks']) == 1
        assert data['benchmarks'][0]['name'] == 'test'

    def it_creates_parent_directories(self, tmp_path: Path) -> None:
        results = {
            'test': BenchmarkResult(
                name='test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
            )
        }

        file_path = tmp_path / 'nested' / 'dir' / 'baseline.json'
        save_baseline(results, file_path)

        assert file_path.exists()


class DescribeGeneratePrComment:
    def it_includes_regression_alert_when_regressions_exist(self) -> None:
        base = BenchmarkResult(
            name='test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
        )

        comparisons = [
            ComparisonResult(
                name='test',
                current=BenchmarkResult(
                    name='test', median_ns=1100, mean_ns=1100, min_ns=1000, max_ns=1200, ops_per_sec=909, rounds=100
                ),
                baseline=base,
                delta_percent=0.1,
                is_regression=True,
                is_improvement=False,
            ),
        ]

        comment = generate_pr_comment(comparisons, '3.12', has_regressions=True)

        assert '## Benchmark Results (Python 3.12)' in comment
        assert 'Performance Alert' in comment
        assert '1 regression(s) detected' in comment

    def it_shows_summary_when_no_regressions(self) -> None:
        base = BenchmarkResult(
            name='test', median_ns=1000, mean_ns=1000, min_ns=900, max_ns=1100, ops_per_sec=1000, rounds=100
        )

        comparisons = [
            ComparisonResult(
                name='test',
                current=base,
                baseline=base,
                delta_percent=0.02,
                is_regression=False,
                is_improvement=False,
            ),
        ]

        comment = generate_pr_comment(comparisons, '3.12', has_regressions=False)

        assert '## Benchmark Results (Python 3.12)' in comment
        assert 'No significant changes detected' in comment
        assert 'Performance Alert' not in comment
