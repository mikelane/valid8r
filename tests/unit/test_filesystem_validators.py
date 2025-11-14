"""Tests for filesystem path validators.

Following TDD principles: tests written before implementation.
Uses tmp_path fixtures for hermetic filesystem testing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from valid8r.core import (
    parsers,
    validators,
)
from valid8r.testing import (
    assert_maybe_success,
)

if TYPE_CHECKING:
    from pathlib import Path


class DescribeExistsValidator:
    """Test exists validator for filesystem paths."""

    def it_validates_existing_file(self, tmp_path: Path) -> None:
        """Validate that an existing file passes validation."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')

        result = validators.exists()(test_file)
        assert assert_maybe_success(result, test_file)

    def it_validates_existing_directory(self, tmp_path: Path) -> None:
        """Validate that an existing directory passes validation."""
        test_dir = tmp_path / 'subdir'
        test_dir.mkdir()

        result = validators.exists()(test_dir)
        assert assert_maybe_success(result, test_dir)

    def it_rejects_non_existing_path(self, tmp_path: Path) -> None:
        """Reject paths that do not exist in the filesystem."""
        non_existent = tmp_path / 'does_not_exist.txt'

        result = validators.exists()(non_existent)
        assert result.is_failure()
        assert 'Path does not exist' in result.error_or('')

    def it_chains_with_parse_path(self, tmp_path: Path) -> None:
        """Chain exists validator with parse_path using bind."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')

        result = parsers.parse_path(str(test_file)).bind(validators.exists())
        assert assert_maybe_success(result, test_file)

    def it_chains_with_parse_path_for_missing_file(self, tmp_path: Path) -> None:
        """Chain exists validator with parse_path for missing file."""
        non_existent = tmp_path / 'missing.txt'

        result = parsers.parse_path(str(non_existent)).bind(validators.exists())
        assert result.is_failure()
        assert 'Path does not exist' in result.error_or('')


class DescribeIsFileValidator:
    """Test is_file validator for filesystem paths."""

    def it_validates_regular_file(self, tmp_path: Path) -> None:
        """Validate that a regular file passes validation."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')

        result = validators.is_file()(test_file)
        assert assert_maybe_success(result, test_file)

    def it_rejects_directory(self, tmp_path: Path) -> None:
        """Reject directories when expecting a file."""
        test_dir = tmp_path / 'subdir'
        test_dir.mkdir()

        result = validators.is_file()(test_dir)
        assert result.is_failure()
        assert 'Path is not a file' in result.error_or('')

    def it_rejects_non_existing_path(self, tmp_path: Path) -> None:
        """Reject non-existing paths."""
        non_existent = tmp_path / 'missing.txt'

        result = validators.is_file()(non_existent)
        assert result.is_failure()
        assert 'Path is not a file' in result.error_or('')

    def it_chains_with_exists_validator(self, tmp_path: Path) -> None:
        """Chain is_file with exists validator."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')

        combined = validators.exists() & validators.is_file()
        result = combined(test_file)
        assert assert_maybe_success(result, test_file)


class DescribeIsDirValidator:
    """Test is_dir validator for filesystem paths."""

    def it_validates_directory(self, tmp_path: Path) -> None:
        """Validate that a directory passes validation."""
        test_dir = tmp_path / 'subdir'
        test_dir.mkdir()

        result = validators.is_dir()(test_dir)
        assert assert_maybe_success(result, test_dir)

    def it_rejects_file(self, tmp_path: Path) -> None:
        """Reject files when expecting a directory."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')

        result = validators.is_dir()(test_file)
        assert result.is_failure()
        assert 'Path is not a directory' in result.error_or('')

    def it_rejects_non_existing_path(self, tmp_path: Path) -> None:
        """Reject non-existing paths."""
        non_existent = tmp_path / 'missing_dir'

        result = validators.is_dir()(non_existent)
        assert result.is_failure()
        assert 'Path is not a directory' in result.error_or('')

    def it_chains_with_exists_validator(self, tmp_path: Path) -> None:
        """Chain is_dir with exists validator."""
        test_dir = tmp_path / 'subdir'
        test_dir.mkdir()

        combined = validators.exists() & validators.is_dir()
        result = combined(test_dir)
        assert assert_maybe_success(result, test_dir)


class DescribeMaxSizeValidator:
    """Test max_size validator for file size limits."""

    def it_validates_file_under_limit(self, tmp_path: Path) -> None:
        """Validate file that is under the size limit."""
        test_file = tmp_path / 'small.txt'
        test_file.write_text('x' * 100)  # 100 bytes

        result = validators.max_size(200)(test_file)
        assert assert_maybe_success(result, test_file)

    def it_validates_file_at_exact_limit(self, tmp_path: Path) -> None:
        """Validate file that is exactly at the size limit."""
        test_file = tmp_path / 'exact.txt'
        test_file.write_text('x' * 100)  # 100 bytes

        result = validators.max_size(100)(test_file)
        assert assert_maybe_success(result, test_file)

    def it_rejects_file_over_limit(self, tmp_path: Path) -> None:
        """Reject file that exceeds the size limit."""
        test_file = tmp_path / 'large.txt'
        test_file.write_text('x' * 200)  # 200 bytes

        result = validators.max_size(100)(test_file)
        assert result.is_failure()
        assert 'exceeds maximum size' in result.error_or('')

    def it_rejects_directory(self, tmp_path: Path) -> None:
        """Reject directories (size check only applies to files)."""
        test_dir = tmp_path / 'subdir'
        test_dir.mkdir()

        result = validators.max_size(1000)(test_dir)
        assert result.is_failure()
        assert 'not a file' in result.error_or('')

    def it_rejects_non_existing_file(self, tmp_path: Path) -> None:
        """Reject non-existing files."""
        non_existent = tmp_path / 'missing.txt'

        result = validators.max_size(1000)(non_existent)
        assert result.is_failure()
        # max_size checks is_file first, so error is "not a file" not "does not exist"
        assert 'not a file' in result.error_or('')

    def it_chains_with_is_file_validator(self, tmp_path: Path) -> None:
        """Chain max_size with is_file validator."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('x' * 50)  # 50 bytes

        combined = validators.is_file() & validators.max_size(100)
        result = combined(test_file)
        assert assert_maybe_success(result, test_file)

    def it_handles_large_size_limits(self, tmp_path: Path) -> None:
        """Handle large size limits (megabytes)."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('x' * 1024)  # 1KB

        # 1MB = 1024 * 1024 bytes
        result = validators.max_size(1024 * 1024)(test_file)
        assert assert_maybe_success(result, test_file)

    def it_provides_helpful_error_with_actual_size(self, tmp_path: Path) -> None:
        """Provide helpful error message including actual file size."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('x' * 200)  # 200 bytes

        result = validators.max_size(100)(test_file)
        assert result.is_failure()
        error = result.error_or('')
        assert '200' in error  # Should mention actual size
        assert '100' in error  # Should mention limit
