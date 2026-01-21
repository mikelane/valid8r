"""Integration tests for CLI commands and argument parsing.

Tests follow strict TDD discipline: tests written BEFORE implementation.
These tests verify the CLI behavior matches the acceptance criteria.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

TEMPLATE_DIR = Path(__file__).parent.parent


class DescribeAddUserCommand:
    """Tests for the add-user subcommand."""

    def it_accepts_valid_arguments(self) -> None:
        """Accept valid name, age, and email arguments."""
        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'add-user',
                '--name',
                'John Doe',
                '--age',
                '25',
                '--email',
                'john@example.com',
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert 'User added successfully' in result.stdout
        assert 'Name: John Doe' in result.stdout
        assert 'Age: 25' in result.stdout
        assert 'Email: john@example.com' in result.stdout

    @pytest.mark.parametrize(
        ('invalid_age', 'expected_error'),
        [
            pytest.param('not-a-number', 'integer', id='non-numeric'),
            pytest.param('-5', 'negative', id='negative'),
            pytest.param('999', 'unrealistic', id='too-large'),
        ],
    )
    def it_rejects_invalid_age_with_clear_error(self, invalid_age: str, expected_error: str) -> None:
        """Reject invalid age values with clear error messages."""
        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'add-user',
                '--name',
                'John',
                '--age',
                invalid_age,
                '--email',
                'john@example.com',
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert expected_error.lower() in result.stderr.lower()

    def it_rejects_invalid_email_with_clear_error(self) -> None:
        """Reject invalid email addresses with clear error messages."""
        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'add-user',
                '--name',
                'John',
                '--age',
                '25',
                '--email',
                'not-an-email',
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert 'email' in result.stderr.lower()

    def it_requires_name_argument(self) -> None:
        """Require --name argument."""
        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'add-user',
                '--age',
                '25',
                '--email',
                'john@example.com',
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert 'name' in result.stderr.lower()

    def it_requires_age_argument(self) -> None:
        """Require --age argument."""
        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'add-user',
                '--name',
                'John',
                '--email',
                'john@example.com',
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert 'age' in result.stderr.lower()


class DescribeListUsersCommand:
    """Tests for the list-users subcommand."""

    def it_lists_users_from_config(self, tmp_path: Path) -> None:
        """List users from a configuration file."""
        config = {
            'users': [
                {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'},
                {'name': 'Bob', 'age': 25, 'email': 'bob@example.com'},
            ]
        }
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml.dump(config))

        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'list-users',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert 'Alice' in result.stdout
        assert 'Bob' in result.stdout

    def it_shows_empty_message_when_no_users(self, tmp_path: Path) -> None:
        """Show message when no users exist."""
        config = {'users': []}
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml.dump(config))

        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'list-users',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert 'no users' in result.stdout.lower()


class DescribeDeleteUserCommand:
    """Tests for the delete-user subcommand."""

    def it_deletes_user_by_name(self, tmp_path: Path) -> None:
        """Delete a user by name from configuration."""
        config = {
            'users': [
                {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'},
                {'name': 'Bob', 'age': 25, 'email': 'bob@example.com'},
            ]
        }
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml.dump(config))

        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'delete-user',
                '--name',
                'Alice',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert 'deleted' in result.stdout.lower() or 'removed' in result.stdout.lower()

    def it_reports_error_for_nonexistent_user(self, tmp_path: Path) -> None:
        """Report error when trying to delete nonexistent user."""
        config = {
            'users': [
                {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'},
            ]
        }
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml.dump(config))

        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'delete-user',
                '--name',
                'Bob',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert 'not found' in result.stderr.lower()


class DescribeLoadConfigCommand:
    """Tests for the load-config subcommand."""

    def it_loads_valid_yaml_config(self, tmp_path: Path) -> None:
        """Load and validate a valid YAML configuration."""
        config = {
            'users': [
                {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'},
            ]
        }
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml.dump(config))

        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'load-config',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert 'successfully' in result.stdout.lower()

    def it_loads_valid_json_config(self, tmp_path: Path) -> None:
        """Load and validate a valid JSON configuration."""
        config = {
            'users': [
                {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'},
            ]
        }
        config_file = tmp_path / 'config.json'
        config_file.write_text(json.dumps(config, indent=2))

        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'load-config',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert 'successfully' in result.stdout.lower()

    def it_reports_invalid_config_values(self, tmp_path: Path) -> None:
        """Report invalid configuration values with details."""
        config = {
            'users': [
                {'name': 'Alice', 'age': 'not-a-number', 'email': 'alice@example.com'},
            ]
        }
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml.dump(config))

        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'load-config',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert 'validation failed' in result.stderr.lower()
        assert 'age' in result.stderr.lower()

    def it_reports_missing_config_file(self) -> None:
        """Report error for missing configuration file (system error)."""
        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'load-config',
                '--file',
                '/nonexistent/config.yaml',
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 2
        assert 'not found' in result.stderr.lower()

    def it_reports_malformed_yaml(self, tmp_path: Path) -> None:
        """Report error for malformed YAML."""
        config_file = tmp_path / 'config.yaml'
        config_file.write_text('this: is: invalid: yaml: syntax')

        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'load-config',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert 'yaml' in result.stderr.lower() or 'invalid' in result.stderr.lower()


class DescribeVerboseMode:
    """Tests for verbose output mode."""

    def it_shows_extra_output_in_verbose_mode(self, tmp_path: Path) -> None:
        """Show additional information in verbose mode."""
        config = {
            'users': [
                {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'},
            ]
        }
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml.dump(config))

        result_normal = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'load-config',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        result_verbose = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                '--verbose',
                'load-config',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result_normal.returncode == 0
        assert result_verbose.returncode == 0
        assert len(result_verbose.stdout) >= len(result_normal.stdout)


class DescribeQuietMode:
    """Tests for quiet output mode."""

    def it_shows_minimal_output_in_quiet_mode(self, tmp_path: Path) -> None:
        """Show minimal output in quiet mode."""
        config = {
            'users': [
                {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'},
            ]
        }
        config_file = tmp_path / 'config.yaml'
        config_file.write_text(yaml.dump(config))

        result_normal = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'load-config',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        result_quiet = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                '--quiet',
                'load-config',
                '--file',
                str(config_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result_normal.returncode == 0
        assert result_quiet.returncode == 0
        assert len(result_quiet.stdout) <= len(result_normal.stdout)


class DescribeExitCodes:
    """Tests for proper exit codes."""

    def it_returns_0_on_success(self) -> None:
        """Return exit code 0 on successful operation."""
        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'add-user',
                '--name',
                'John Doe',
                '--age',
                '25',
                '--email',
                'john@example.com',
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def it_returns_1_on_user_error(self) -> None:
        """Return exit code 1 on user input error."""
        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'add-user',
                '--name',
                'John',
                '--age',
                'invalid',
                '--email',
                'john@example.com',
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1

    def it_returns_2_on_system_error(self) -> None:
        """Return exit code 2 on system error (e.g., file not found)."""
        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'load-config',
                '--file',
                '/nonexistent/file.yaml',
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 2


class DescribeHelpOutput:
    """Tests for help output."""

    def it_shows_help_for_main_command(self) -> None:
        """Show help when --help is passed."""
        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                '--help',
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert 'add-user' in result.stdout
        assert 'list-users' in result.stdout
        assert 'load-config' in result.stdout

    def it_shows_help_for_subcommand(self) -> None:
        """Show help for subcommands."""
        result = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_DIR / 'cli.py'),
                'add-user',
                '--help',
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert '--name' in result.stdout
        assert '--age' in result.stdout
        assert '--email' in result.stdout
