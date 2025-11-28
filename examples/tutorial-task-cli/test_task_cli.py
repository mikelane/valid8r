"""Tests for Task Manager CLI - Demonstrates valid8r testing utilities.

This test file shows how to test CLI applications that use valid8r,
including testing interactive prompts with MockInputContext.

Run tests:
    pytest test_task_cli.py -v
    pytest test_task_cli.py::DescribeParsePriority -v
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

# Import from the task_cli module
from task_cli import (
    add_task_interactive,
    load_tasks,
    parse_priority,
    save_tasks,
)

from valid8r.testing import (
    MockInputContext,
    assert_maybe_success,
)

if TYPE_CHECKING:
    from pathlib import Path


class DescribeParsePriority:
    """Tests for the parse_priority function."""

    @pytest.mark.parametrize(
        ('raw', 'expected'),
        [
            pytest.param('1', 1, id='critical'),
            pytest.param('2', 2, id='high'),
            pytest.param('3', 3, id='medium'),
            pytest.param('4', 4, id='low'),
            pytest.param('5', 5, id='someday'),
        ],
    )
    def it_parses_valid_priorities(self, raw: str, expected: int) -> None:
        result = parse_priority(raw)
        assert assert_maybe_success(result, expected)

    @pytest.mark.parametrize(
        'raw',
        [
            pytest.param('0', id='zero-invalid'),
            pytest.param('6', id='six-invalid'),
            pytest.param('-1', id='negative-invalid'),
            pytest.param('100', id='too-high'),
        ],
    )
    def it_rejects_out_of_range_priorities(self, raw: str) -> None:
        result = parse_priority(raw)
        assert result.is_failure()
        assert '1-5' in result.error_or('')

    @pytest.mark.parametrize(
        'raw',
        [
            pytest.param('', id='empty'),
            pytest.param('high', id='text'),
            pytest.param('3.5', id='float'),
        ],
    )
    def it_rejects_non_integer_input(self, raw: str) -> None:
        result = parse_priority(raw)
        assert result.is_failure()


class DescribeTaskStorage:
    """Tests for task storage functions."""

    def it_saves_and_loads_tasks(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # Use temp directory for tasks file
        tasks_file = tmp_path / 'tasks.json'
        monkeypatch.setattr('task_cli.TASKS_FILE', tasks_file)

        tasks = [
            {'description': 'Test task', 'priority': 3, 'notify_email': None, 'completed': False},
        ]

        save_tasks(tasks)
        loaded = load_tasks()

        assert loaded == tasks

    def it_returns_empty_list_when_no_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        tasks_file = tmp_path / 'nonexistent.json'
        monkeypatch.setattr('task_cli.TASKS_FILE', tasks_file)

        loaded = load_tasks()

        assert loaded == []


class DescribeInteractiveMode:
    """Tests for interactive mode using MockInputContext.

    These tests demonstrate how to test interactive prompts
    without actual user input.
    """

    def it_creates_task_with_all_inputs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        tasks_file = tmp_path / 'tasks.json'
        monkeypatch.setattr('task_cli.TASKS_FILE', tasks_file)

        # Simulate user typing these responses in order:
        # 1. Task description
        # 2. Priority (2 = High)
        # 3. Enable notifications? (yes)
        # 4. Email address
        with MockInputContext(['Review the PR', '2', 'yes', 'alice@example.com']):
            exit_code = add_task_interactive()

        assert exit_code == 0

        # Verify the task was saved correctly
        with tasks_file.open() as f:
            tasks = json.load(f)

        assert len(tasks) == 1
        assert tasks[0]['description'] == 'Review the PR'
        assert tasks[0]['priority'] == 2
        assert tasks[0]['notify_email'] == 'alice@example.com'
        assert tasks[0]['completed'] is False

    def it_creates_task_without_notification(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        tasks_file = tmp_path / 'tasks.json'
        monkeypatch.setattr('task_cli.TASKS_FILE', tasks_file)

        # User declines notification
        with MockInputContext(['Send report', '1', 'no']):
            exit_code = add_task_interactive()

        assert exit_code == 0

        with tasks_file.open() as f:
            tasks = json.load(f)

        assert len(tasks) == 1
        assert tasks[0]['description'] == 'Send report'
        assert tasks[0]['priority'] == 1
        assert tasks[0]['notify_email'] is None

    def it_uses_default_priority_when_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        tasks_file = tmp_path / 'tasks.json'
        monkeypatch.setattr('task_cli.TASKS_FILE', tasks_file)

        # User presses Enter for default priority (3)
        with MockInputContext(['Quick task', '', 'no']):
            exit_code = add_task_interactive()

        assert exit_code == 0

        with tasks_file.open() as f:
            tasks = json.load(f)

        assert tasks[0]['priority'] == 3  # Default priority

    def it_retries_on_invalid_priority(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        tasks_file = tmp_path / 'tasks.json'
        monkeypatch.setattr('task_cli.TASKS_FILE', tasks_file)

        # User enters invalid priority first, then valid one
        with MockInputContext(['Fix bug', '10', '2', 'no']):
            exit_code = add_task_interactive()

        assert exit_code == 0

        with tasks_file.open() as f:
            tasks = json.load(f)

        assert tasks[0]['priority'] == 2  # Accepted after retry


class DescribeValidatorComposition:
    """Tests demonstrating validator composition with valid8r.

    Shows how to combine validators using & (and) operators.
    """

    def it_validates_priority_with_combined_validators(self) -> None:
        # parse_priority chains parsing with range validation using bind()
        # Valid: parses to int AND is between 1-5
        assert parse_priority('3').is_success()

        # Invalid: parses to int but NOT between 1-5
        assert parse_priority('0').is_failure()
        assert parse_priority('6').is_failure()

        # Invalid: doesn't even parse to int
        assert parse_priority('abc').is_failure()
