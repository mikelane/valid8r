"""Tests for the validator functions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)

import pytest

from valid8r.core.validators import (
    Validator,
    between,
    in_set,
    is_sorted,
    length,
    matches_regex,
    maximum,
    minimum,
    non_empty_string,
    predicate,
    subset_of,
    superset_of,
    unique_items,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class DescribeValidators:
    @pytest.mark.parametrize(
        ('validator_factory', 'threshold', 'test_values', 'expected_results'),
        [
            pytest.param(
                minimum,
                5,
                [(10, True), (5, True), (4, False), (0, False)],
                'Value must be at least 5',
                id='minimum validator',
            ),
            pytest.param(
                maximum,
                10,
                [(5, True), (10, True), (11, False), (20, False)],
                'Value must be at most 10',
                id='maximum validator',
            ),
        ],
    )
    def it_validates_threshold_values(
        self,
        validator_factory: Callable[[Any], Validator[Any]],
        threshold: int,
        test_values: list[tuple[Any, bool]],
        expected_results: str,
    ) -> None:
        """Test threshold-based validators (minimum and maximum)."""
        validator = validator_factory(threshold)

        for value, should_pass in test_values:
            result = validator(value)

            if should_pass:
                assert result.is_success()
                assert result.value_or(value) == value
            else:
                assert result.is_failure()
                assert result.error_or('') == expected_results

    @pytest.mark.parametrize(
        ('min_val', 'max_val', 'test_value', 'should_pass'),
        [
            pytest.param(1, 10, 5, True, id='in range'),
            pytest.param(1, 10, 1, True, id='min value'),
            pytest.param(1, 10, 10, True, id='max value'),
            pytest.param(1, 10, 0, False, id='below range'),
            pytest.param(1, 10, 11, False, id='above range'),
        ],
    )
    def it_validates_range_with_between(
        self,
        min_val: int,
        max_val: int,
        test_value: int,
        should_pass: bool,
    ) -> None:
        """Test the between validator with various inputs."""
        validator = between(min_val, max_val)
        result = validator(test_value)

        if should_pass:
            assert result.is_success()
            assert result.value_or(test_value) == test_value
        else:
            assert result.is_failure()
            assert f'Value must be between {min_val} and {max_val}' in result.error_or('')

    def it_validates_custom_predicates(self) -> None:
        """Test predicate validator with custom functions."""
        is_even = predicate(lambda x: x % 2 == 0, 'Value must be even')

        # Test valid case
        result = is_even(4)
        assert result.is_success()
        assert result.value_or(0) == 4

        # Test invalid case
        result = is_even(3)
        assert result.is_failure()
        assert result.error_or('') == 'Value must be even'

    @pytest.mark.parametrize(
        ('min_len', 'max_len', 'test_string', 'should_pass'),
        [
            pytest.param(3, 10, 'hello', True, id='valid string'),
            pytest.param(3, 10, 'abc', True, id='valid string with length 3'),
            pytest.param(3, 10, 'helloworld', True, id='valid string with length 10'),
            pytest.param(3, 10, 'hi', False, id='invalid string with length 2'),
            pytest.param(3, 10, 'helloworldplus', False, id='invalid string with length 11'),
        ],
    )
    def it_validates_string_length(
        self,
        min_len: int,
        max_len: int,
        test_string: str,
        should_pass: bool,
    ) -> None:
        """Test the length validator with various inputs."""
        validator = length(min_len, max_len)
        result = validator(test_string)

        if should_pass:
            assert result.is_success()
            assert result.value_or('') == test_string
        else:
            assert result.is_failure()
            assert f'String length must be between {min_len} and {max_len}' in result.error_or('')


class DescribeMatchesRegex:
    """Tests for the matches_regex validator."""

    def it_validates_string_matching_pattern(self) -> None:
        """Test matches_regex accepts a string matching the pattern."""
        validator = matches_regex(r'^\d{3}-\d{2}-\d{4}$')

        result = validator('123-45-6789')

        assert result.is_success()
        assert result.value_or('') == '123-45-6789'

    def it_rejects_string_not_matching_pattern(self) -> None:
        """Test matches_regex rejects a string that doesn't match the pattern."""
        validator = matches_regex(r'^\d{3}-\d{2}-\d{4}$')

        result = validator('abc-de-fghi')

        assert result.is_failure()
        assert 'must match pattern' in result.error_or('').lower()

    def it_accepts_compiled_regex_pattern(self) -> None:
        """Test matches_regex works with pre-compiled regex patterns."""
        pattern = re.compile(r'^\d{3}-\d{3}-\d{4}$')
        validator = matches_regex(pattern)

        result = validator('123-456-7890')

        assert result.is_success()
        assert result.value_or('') == '123-456-7890'

    def it_supports_custom_error_messages(self) -> None:
        """Test matches_regex uses custom error message when provided."""
        validator = matches_regex(r'^\d{5}$', error_message='Must be a 5-digit ZIP code')

        result = validator('1234')

        assert result.is_failure()
        assert result.error_or('') == 'Must be a 5-digit ZIP code'


class DescribeInSet:
    """Tests for the in_set validator."""

    def it_accepts_value_in_allowed_set(self) -> None:
        """Test in_set accepts a value that is in the allowed set."""
        validator = in_set({'red', 'green', 'blue'})

        result = validator('red')

        assert result.is_success()
        assert result.value_or('') == 'red'

    def it_rejects_value_not_in_allowed_set(self) -> None:
        """Test in_set rejects a value that is not in the allowed set."""
        validator = in_set({'red', 'green', 'blue'})

        result = validator('yellow')

        assert result.is_failure()
        assert 'must be one of' in result.error_or('').lower()

    def it_supports_custom_error_messages(self) -> None:
        """Test in_set uses custom error message when provided."""
        validator = in_set({'small', 'medium', 'large'}, error_message='Size must be S, M, or L')

        result = validator('extra-large')

        assert result.is_failure()
        assert result.error_or('') == 'Size must be S, M, or L'


class DescribeNonEmptyString:
    """Tests for the non_empty_string validator."""

    def it_accepts_non_empty_string(self) -> None:
        """Test non_empty_string accepts a string with content."""
        validator = non_empty_string()

        result = validator('hello')

        assert result.is_success()
        assert result.value_or('') == 'hello'

    def it_rejects_empty_string(self) -> None:
        """Test non_empty_string rejects an empty string."""
        validator = non_empty_string()

        result = validator('')

        assert result.is_failure()
        assert 'must not be empty' in result.error_or('').lower()

    def it_rejects_whitespace_only_string(self) -> None:
        """Test non_empty_string rejects a string with only whitespace."""
        validator = non_empty_string()

        result = validator('   ')

        assert result.is_failure()
        assert 'must not be empty' in result.error_or('').lower()


class DescribeUniqueItems:
    """Tests for the unique_items validator."""

    def it_accepts_list_with_unique_items(self) -> None:
        """Test unique_items accepts a list where all items are unique."""
        validator = unique_items()

        result = validator([1, 2, 3, 4, 5])

        assert result.is_success()
        assert result.value_or([]) == [1, 2, 3, 4, 5]

    def it_rejects_list_with_duplicate_items(self) -> None:
        """Test unique_items rejects a list with duplicate items."""
        validator = unique_items()

        result = validator([1, 2, 2, 3, 4])

        assert result.is_failure()
        assert 'must be unique' in result.error_or('').lower()


class DescribeSubsetOf:
    """Tests for the subset_of validator."""

    def it_accepts_set_that_is_subset(self) -> None:
        """Test subset_of accepts a set that is a subset of the allowed set."""
        validator = subset_of({1, 2, 3, 4, 5})

        result = validator({1, 2, 3})

        assert result.is_success()
        assert result.value_or(set()) == {1, 2, 3}

    def it_rejects_set_that_is_not_subset(self) -> None:
        """Test subset_of rejects a set that is not a subset of the allowed set."""
        validator = subset_of({1, 2, 3})

        result = validator({1, 2, 3, 4, 5})

        assert result.is_failure()
        assert 'subset' in result.error_or('').lower()


class DescribeSupersetOf:
    """Tests for the superset_of validator."""

    def it_accepts_set_that_is_superset(self) -> None:
        """Test superset_of accepts a set that is a superset of the required set."""
        validator = superset_of({1, 2, 3})

        result = validator({1, 2, 3, 4, 5})

        assert result.is_success()
        assert result.value_or(set()) == {1, 2, 3, 4, 5}

    def it_rejects_set_that_is_not_superset(self) -> None:
        """Test superset_of rejects a set that is not a superset of the required set."""
        validator = superset_of({1, 2, 3, 4, 5})

        result = validator({1, 2, 3})

        assert result.is_failure()
        assert 'superset' in result.error_or('').lower()


class DescribeIsSorted:
    """Tests for the is_sorted validator."""

    def it_accepts_ascending_sorted_list(self) -> None:
        """Test is_sorted accepts a list sorted in ascending order."""
        validator = is_sorted()

        result = validator([1, 2, 3, 4, 5])

        assert result.is_success()
        assert result.value_or([]) == [1, 2, 3, 4, 5]

    def it_rejects_unsorted_list(self) -> None:
        """Test is_sorted rejects an unsorted list."""
        validator = is_sorted()

        result = validator([3, 1, 4, 2, 5])

        assert result.is_failure()
        assert 'sorted' in result.error_or('').lower()

    def it_accepts_descending_sorted_list_when_reverse_true(self) -> None:
        """Test is_sorted accepts descending order when reverse=True."""
        validator = is_sorted(reverse=True)

        result = validator([5, 4, 3, 2, 1])

        assert result.is_success()
        assert result.value_or([]) == [5, 4, 3, 2, 1]


class DescribeFilesystemValidators:
    """Tests for filesystem validators (exists, is_file, is_dir)."""

    def it_accepts_existing_file_with_exists(self, tmp_path: Path) -> None:
        """Test exists() accepts a path that exists on the filesystem."""
        from valid8r.core.validators import exists

        # Create temporary file
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')

        # Validate
        validator = exists()
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_rejects_non_existent_path_with_exists(self) -> None:
        """Test exists() rejects a path that does not exist."""
        from valid8r.core.validators import exists

        non_existent = Path('/nonexistent/file.txt')

        validator = exists()
        result = validator(non_existent)

        assert result.is_failure()
        assert 'does not exist' in result.error_or('').lower()

    def it_accepts_file_with_is_file(self, tmp_path: Path) -> None:
        """Test is_file() accepts a path that is a regular file."""
        from valid8r.core.validators import is_file

        # Create temporary file
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')

        # Validate
        validator = is_file()
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_rejects_directory_with_is_file(self, tmp_path: Path) -> None:
        """Test is_file() rejects a path that is a directory."""
        from valid8r.core.validators import is_file

        # Validate directory
        validator = is_file()
        result = validator(tmp_path)

        assert result.is_failure()
        assert 'not a file' in result.error_or('').lower()

    def it_rejects_non_existent_path_with_is_file(self) -> None:
        """Test is_file() rejects a path that does not exist."""
        from valid8r.core.validators import is_file

        non_existent = Path('/nonexistent/file.txt')

        validator = is_file()
        result = validator(non_existent)

        assert result.is_failure()
        # Should mention it's not a file (existence is checked by is_file)
        assert 'not a file' in result.error_or('').lower()

    def it_accepts_directory_with_is_dir(self, tmp_path: Path) -> None:
        """Test is_dir() accepts a path that is a directory."""
        from valid8r.core.validators import is_dir

        # Validate directory
        validator = is_dir()
        result = validator(tmp_path)

        assert result.is_success()
        assert result.value_or(None) == tmp_path

    def it_rejects_file_with_is_dir(self, tmp_path: Path) -> None:
        """Test is_dir() rejects a path that is a file."""
        from valid8r.core.validators import is_dir

        # Create temporary file
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')

        # Validate
        validator = is_dir()
        result = validator(test_file)

        assert result.is_failure()
        assert 'not a directory' in result.error_or('').lower()

    def it_rejects_non_existent_path_with_is_dir(self) -> None:
        """Test is_dir() rejects a path that does not exist."""
        from valid8r.core.validators import is_dir

        non_existent = Path('/nonexistent/dir')

        validator = is_dir()
        result = validator(non_existent)

        assert result.is_failure()
        assert 'not a directory' in result.error_or('').lower()

    def it_chains_validators_for_complete_validation(self, tmp_path: Path) -> None:
        """Test chaining exists() and is_file() for complete validation."""
        from valid8r.core.validators import (
            exists,
            is_file,
        )

        # Create temporary file
        test_file = tmp_path / 'data.csv'
        test_file.write_text('data')

        # Chain validators
        validator = exists() & is_file()
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_fails_chained_validation_at_first_error(self) -> None:
        """Test chained validation fails at first error (exists before is_file)."""
        from valid8r.core.validators import (
            exists,
            is_file,
        )

        non_existent = Path('/nonexistent/file.txt')

        # Chain validators
        validator = exists() & is_file()
        result = validator(non_existent)

        assert result.is_failure()
        # Should fail at exists() check
        assert 'does not exist' in result.error_or('').lower()

    def it_validates_with_parse_path_pipeline(self, tmp_path: Path) -> None:
        """Test validation works in parse_path pipeline."""
        from valid8r.core import parsers
        from valid8r.core.validators import (
            exists,
            is_file,
        )

        # Create temporary file
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test')

        # Parse and validate
        result = parsers.parse_path(str(test_file)).bind(lambda p: (exists() & is_file())(p))

        assert result.is_success()
        assert isinstance(result.value_or(None), Path)

    def it_handles_symbolic_links_with_exists(self, tmp_path: Path) -> None:
        """Test exists() follows symbolic links and validates target exists."""
        from valid8r.core.validators import exists

        # Create real file and symlink
        real_file = tmp_path / 'real.txt'
        real_file.write_text('content')

        link = tmp_path / 'link.txt'
        link.symlink_to(real_file)

        # Validate symlink
        validator = exists()
        result = validator(link)

        assert result.is_success()
        assert result.value_or(None) == link

    def it_rejects_broken_symbolic_link_with_exists(self, tmp_path: Path) -> None:
        """Test exists() rejects broken symbolic links."""
        from valid8r.core.validators import exists

        # Create broken symlink
        broken_link = tmp_path / 'broken'
        broken_link.symlink_to(tmp_path / 'nonexistent')

        # Validate
        validator = exists()
        result = validator(broken_link)

        assert result.is_failure()
        assert 'does not exist' in result.error_or('').lower()


class DescribeIsReadable:
    """Tests for the is_readable filesystem permission validator."""

    def it_accepts_readable_file(self, tmp_path: Path) -> None:
        """Test is_readable accepts a file with read permissions."""
        from valid8r.core.validators import is_readable

        # Create file with read permissions
        test_file = tmp_path / 'readable.txt'
        test_file.write_text('content')
        test_file.chmod(0o444)  # r--r--r--

        validator = is_readable()
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_rejects_non_readable_file(self, tmp_path: Path) -> None:
        """Test is_readable rejects a file without read permissions."""
        from valid8r.core.validators import is_readable

        # Create file without read permissions
        test_file = tmp_path / 'not_readable.txt'
        test_file.write_text('content')
        test_file.chmod(0o200)  # -w-------

        validator = is_readable()
        result = validator(test_file)

        assert result.is_failure()
        assert 'not readable' in result.error_or('').lower()

    def it_accepts_readable_directory(self, tmp_path: Path) -> None:
        """Test is_readable accepts a directory with read permissions."""
        from valid8r.core.validators import is_readable

        # Create directory with read permissions
        test_dir = tmp_path / 'readable_dir'
        test_dir.mkdir()
        test_dir.chmod(0o555)  # r-xr-xr-x

        validator = is_readable()
        result = validator(test_dir)

        assert result.is_success()
        assert result.value_or(None) == test_dir

    def it_rejects_non_existent_path(self, tmp_path: Path) -> None:
        """Test is_readable rejects a non-existent path."""
        from valid8r.core.validators import is_readable

        non_existent = tmp_path / 'nonexistent.txt'

        validator = is_readable()
        result = validator(non_existent)

        assert result.is_failure()
        assert 'not readable' in result.error_or('').lower()

    def it_accepts_readable_symlink(self, tmp_path: Path) -> None:
        """Test is_readable accepts a symlink to a readable file."""
        from valid8r.core.validators import is_readable

        # Create readable file and symlink
        real_file = tmp_path / 'real.txt'
        real_file.write_text('content')
        real_file.chmod(0o444)

        symlink = tmp_path / 'link.txt'
        symlink.symlink_to(real_file)

        validator = is_readable()
        result = validator(symlink)

        assert result.is_success()
        assert result.value_or(None) == symlink

    def it_rejects_broken_symlink(self, tmp_path: Path) -> None:
        """Test is_readable rejects a broken symlink."""
        from valid8r.core.validators import is_readable

        # Create broken symlink
        broken_link = tmp_path / 'broken'
        broken_link.symlink_to(tmp_path / 'nonexistent')

        validator = is_readable()
        result = validator(broken_link)

        assert result.is_failure()
        assert 'not readable' in result.error_or('').lower()

    def it_chains_with_exists_and_is_file(self, tmp_path: Path) -> None:
        """Test is_readable chains with exists and is_file validators."""
        from valid8r.core.validators import (
            exists,
            is_file,
            is_readable,
        )

        # Create readable file
        test_file = tmp_path / 'data.txt'
        test_file.write_text('content')
        test_file.chmod(0o644)

        # Chain validators
        validator = exists() & is_file() & is_readable()
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file


class DescribeIsWritable:
    """Tests for the is_writable filesystem permission validator."""

    def it_accepts_writable_file(self, tmp_path: Path) -> None:
        """Test is_writable accepts a file with write permissions."""
        from valid8r.core.validators import is_writable

        # Create file with write permissions
        test_file = tmp_path / 'writable.txt'
        test_file.write_text('content')
        test_file.chmod(0o644)  # rw-r--r--

        validator = is_writable()
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_rejects_non_writable_file(self, tmp_path: Path) -> None:
        """Test is_writable rejects a file without write permissions."""
        from valid8r.core.validators import is_writable

        # Create file without write permissions
        test_file = tmp_path / 'not_writable.txt'
        test_file.write_text('content')
        test_file.chmod(0o444)  # r--r--r--

        validator = is_writable()
        result = validator(test_file)

        assert result.is_failure()
        assert 'not writable' in result.error_or('').lower()

    def it_accepts_writable_directory(self, tmp_path: Path) -> None:
        """Test is_writable accepts a directory with write permissions."""
        from valid8r.core.validators import is_writable

        # Create directory with write permissions
        test_dir = tmp_path / 'writable_dir'
        test_dir.mkdir()
        test_dir.chmod(0o755)  # rwxr-xr-x

        validator = is_writable()
        result = validator(test_dir)

        assert result.is_success()
        assert result.value_or(None) == test_dir

    def it_rejects_non_existent_path(self, tmp_path: Path) -> None:
        """Test is_writable rejects a non-existent path."""
        from valid8r.core.validators import is_writable

        non_existent = tmp_path / 'nonexistent.txt'

        validator = is_writable()
        result = validator(non_existent)

        assert result.is_failure()
        assert 'not writable' in result.error_or('').lower()

    def it_chains_with_is_readable(self, tmp_path: Path) -> None:
        """Test is_writable chains with is_readable validator."""
        from valid8r.core.validators import (
            is_readable,
            is_writable,
        )

        # Create file with read and write permissions
        test_file = tmp_path / 'rw.txt'
        test_file.write_text('content')
        test_file.chmod(0o644)

        # Chain validators
        validator = is_readable() & is_writable()
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_fails_chain_when_readable_but_not_writable(self, tmp_path: Path) -> None:
        """Test chain fails when file is readable but not writable."""
        from valid8r.core.validators import (
            is_readable,
            is_writable,
        )

        # Create read-only file
        test_file = tmp_path / 'readonly.txt'
        test_file.write_text('content')
        test_file.chmod(0o444)

        # Chain validators
        validator = is_readable() & is_writable()
        result = validator(test_file)

        assert result.is_failure()
        assert 'not writable' in result.error_or('').lower()


class DescribeIsExecutable:
    """Tests for the is_executable filesystem permission validator."""

    def it_accepts_executable_file(self, tmp_path: Path) -> None:
        """Test is_executable accepts a file with execute permissions."""
        from valid8r.core.validators import is_executable

        # Create file with execute permissions
        test_file = tmp_path / 'executable.sh'
        test_file.write_text('#!/bin/bash\necho "test"')
        test_file.chmod(0o755)  # rwxr-xr-x

        validator = is_executable()
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_rejects_non_executable_file(self, tmp_path: Path) -> None:
        """Test is_executable rejects a file without execute permissions."""
        from valid8r.core.validators import is_executable

        # Create file without execute permissions
        test_file = tmp_path / 'not_executable.sh'
        test_file.write_text('#!/bin/bash\necho "test"')
        test_file.chmod(0o644)  # rw-r--r--

        validator = is_executable()
        result = validator(test_file)

        assert result.is_failure()
        assert 'not executable' in result.error_or('').lower()

    def it_rejects_non_existent_path(self, tmp_path: Path) -> None:
        """Test is_executable rejects a non-existent path."""
        from valid8r.core.validators import is_executable

        non_existent = tmp_path / 'nonexistent.sh'

        validator = is_executable()
        result = validator(non_existent)

        assert result.is_failure()
        assert 'not executable' in result.error_or('').lower()

    def it_chains_with_is_readable_and_is_writable(self, tmp_path: Path) -> None:
        """Test is_executable chains with is_readable and is_writable."""
        from valid8r.core.validators import (
            is_executable,
            is_readable,
            is_writable,
        )

        # Create file with all permissions
        test_file = tmp_path / 'all_perms.sh'
        test_file.write_text('#!/bin/bash\necho "test"')
        test_file.chmod(0o777)  # rwxrwxrwx

        # Chain validators
        validator = is_readable() & is_writable() & is_executable()
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_works_in_full_validation_pipeline(self, tmp_path: Path) -> None:
        """Test is_executable works in complete validation pipeline."""
        from valid8r.core import parsers
        from valid8r.core.validators import (
            exists,
            is_executable,
            is_file,
        )

        # Create executable file
        test_file = tmp_path / 'script.sh'
        test_file.write_text('#!/bin/bash\necho "test"')
        test_file.chmod(0o755)

        # Full pipeline: parse → exists → is_file → is_executable
        result = parsers.parse_path(str(test_file)).bind(lambda p: (exists() & is_file() & is_executable())(p))

        assert result.is_success()
        assert isinstance(result.value_or(None), Path)


class DescribeMaxSize:
    """Tests for the max_size validator."""

    def it_accepts_file_under_maximum_size(self, tmp_path: Path) -> None:
        """Test max_size accepts a file smaller than the limit."""
        from valid8r.core.validators import max_size

        # Create file of 1024 bytes
        test_file = tmp_path / 'test.txt'
        test_file.write_bytes(b'x' * 1024)

        validator = max_size(2048)
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_accepts_file_exactly_at_maximum_size(self, tmp_path: Path) -> None:
        """Test max_size accepts a file exactly at the limit."""
        from valid8r.core.validators import max_size

        # Create file of 2048 bytes
        test_file = tmp_path / 'test.txt'
        test_file.write_bytes(b'x' * 2048)

        validator = max_size(2048)
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_rejects_file_exceeding_maximum_size(self, tmp_path: Path) -> None:
        """Test max_size rejects a file larger than the limit."""
        from valid8r.core.validators import max_size

        # Create file of 5120 bytes
        test_file = tmp_path / 'test.txt'
        test_file.write_bytes(b'x' * 5120)

        validator = max_size(1024)
        result = validator(test_file)

        assert result.is_failure()
        assert 'exceeds maximum size' in result.error_or('').lower()

    def it_includes_actual_size_in_error_message(self, tmp_path: Path) -> None:
        """Test max_size error message includes the actual file size."""
        from valid8r.core.validators import max_size

        # Create file of 5120 bytes
        test_file = tmp_path / 'test.txt'
        test_file.write_bytes(b'x' * 5120)

        validator = max_size(1024)
        result = validator(test_file)

        assert result.is_failure()
        assert '5120' in result.error_or('')

    def it_accepts_empty_file(self, tmp_path: Path) -> None:
        """Test max_size accepts an empty file."""
        from valid8r.core.validators import max_size

        # Create empty file
        test_file = tmp_path / 'empty.txt'
        test_file.write_bytes(b'')

        validator = max_size(1024)
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_rejects_non_file_paths(self, tmp_path: Path) -> None:
        """Test max_size rejects directories."""
        from valid8r.core.validators import max_size

        validator = max_size(1024)
        result = validator(tmp_path)

        assert result.is_failure()
        assert 'not a file' in result.error_or('').lower()

    def it_handles_symbolic_links_with_exists(self, tmp_path: Path) -> None:
        """Test exists() follows symbolic links and validates target exists."""
        from valid8r.core.validators import exists

        # Create real file and symlink
        real_file = tmp_path / 'real.txt'
        real_file.write_text('content')

        link = tmp_path / 'link.txt'
        link.symlink_to(real_file)

        # Validate symlink
        validator = exists()
        result = validator(link)

        assert result.is_success()
        assert result.value_or(None) == link

    def it_rejects_broken_symbolic_link_with_exists(self, tmp_path: Path) -> None:
        """Test exists() rejects broken symbolic links."""
        from valid8r.core.validators import exists

        # Create broken symlink
        broken_link = tmp_path / 'broken'
        broken_link.symlink_to(tmp_path / 'nonexistent')

        # Validate
        validator = exists()
        result = validator(broken_link)

        assert result.is_failure()
        assert 'does not exist' in result.error_or('').lower()


class DescribeMinSize:
    """Tests for the min_size validator."""

    def it_accepts_file_above_minimum_size(self, tmp_path: Path) -> None:
        """Test min_size accepts a file larger than the limit."""
        from valid8r.core.validators import min_size

        # Create file of 2048 bytes
        test_file = tmp_path / 'test.txt'
        test_file.write_bytes(b'x' * 2048)

        validator = min_size(1024)
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_accepts_file_exactly_at_minimum_size(self, tmp_path: Path) -> None:
        """Test min_size accepts a file exactly at the limit."""
        from valid8r.core.validators import min_size

        # Create file of 1024 bytes
        test_file = tmp_path / 'test.txt'
        test_file.write_bytes(b'x' * 1024)

        validator = min_size(1024)
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_rejects_file_below_minimum_size(self, tmp_path: Path) -> None:
        """Test min_size rejects a file smaller than the limit."""
        from valid8r.core.validators import min_size

        # Create file of 512 bytes
        test_file = tmp_path / 'test.txt'
        test_file.write_bytes(b'x' * 512)

        validator = min_size(1024)
        result = validator(test_file)

        assert result.is_failure()
        assert 'smaller than minimum size' in result.error_or('').lower()

    def it_includes_minimum_size_in_error_message(self, tmp_path: Path) -> None:
        """Test min_size error message includes the minimum size."""
        from valid8r.core.validators import min_size

        # Create file of 512 bytes
        test_file = tmp_path / 'test.txt'
        test_file.write_bytes(b'x' * 512)

        validator = min_size(1024)
        result = validator(test_file)

        assert result.is_failure()
        assert '1024' in result.error_or('')

    def it_rejects_empty_file(self, tmp_path: Path) -> None:
        """Test min_size rejects an empty file when minimum is positive."""
        from valid8r.core.validators import min_size

        # Create empty file
        test_file = tmp_path / 'empty.txt'
        test_file.write_bytes(b'')

        validator = min_size(1)
        result = validator(test_file)

        assert result.is_failure()
        assert 'smaller than minimum size' in result.error_or('').lower()

    def it_rejects_non_file_paths(self, tmp_path: Path) -> None:
        """Test min_size rejects directories."""
        from valid8r.core.validators import min_size

        validator = min_size(1024)
        result = validator(tmp_path)

        assert result.is_failure()
        assert 'not a file' in result.error_or('').lower()


class DescribeHasExtension:
    """Tests for the has_extension validator."""

    def it_accepts_file_with_single_allowed_extension(self, tmp_path: Path) -> None:
        """Test has_extension accepts a file with the correct extension."""
        from valid8r.core.validators import has_extension

        # Create file with .pdf extension
        test_file = tmp_path / 'document.pdf'
        test_file.write_text('content')

        validator = has_extension('.pdf')
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_accepts_file_with_one_of_multiple_extensions(self, tmp_path: Path) -> None:
        """Test has_extension accepts file with one of several allowed extensions."""
        from valid8r.core.validators import has_extension

        # Create file with .docx extension
        test_file = tmp_path / 'document.docx'
        test_file.write_text('content')

        validator = has_extension('.pdf', '.doc', '.docx')
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_rejects_file_with_wrong_extension(self, tmp_path: Path) -> None:
        """Test has_extension rejects file with incorrect extension."""
        from valid8r.core.validators import has_extension

        # Create file with .png extension
        test_file = tmp_path / 'image.png'
        test_file.write_text('content')

        validator = has_extension('.pdf', '.docx')
        result = validator(test_file)

        assert result.is_failure()
        assert 'allowed extensions' in result.error_or('').lower()

    def it_rejects_file_with_no_extension(self, tmp_path: Path) -> None:
        """Test has_extension rejects file without extension."""
        from valid8r.core.validators import has_extension

        # Create file without extension
        test_file = tmp_path / 'README'
        test_file.write_text('content')

        validator = has_extension('.md', '.txt')
        result = validator(test_file)

        assert result.is_failure()
        assert 'allowed extensions' in result.error_or('').lower()

    def it_accepts_file_with_uppercase_extension(self, tmp_path: Path) -> None:
        """Test has_extension is case-insensitive (uppercase)."""
        from valid8r.core.validators import has_extension

        # Create file with uppercase extension
        test_file = tmp_path / 'DOCUMENT.PDF'
        test_file.write_text('content')

        validator = has_extension('.pdf')
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_accepts_file_with_mixed_case_extension(self, tmp_path: Path) -> None:
        """Test has_extension is case-insensitive (mixed case)."""
        from valid8r.core.validators import has_extension

        # Create file with mixed case extension
        test_file = tmp_path / 'Report.Pdf'
        test_file.write_text('content')

        validator = has_extension('.pdf')
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_accepts_file_with_multiple_dots_in_name(self, tmp_path: Path) -> None:
        """Test has_extension handles files with multiple dots correctly."""
        from valid8r.core.validators import has_extension

        # Create file with multiple dots
        test_file = tmp_path / 'my.backup.file.tar.gz'
        test_file.write_text('content')

        validator = has_extension('.gz')
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file

    def it_rejects_file_with_multiple_dots_but_wrong_extension(self, tmp_path: Path) -> None:
        """Test has_extension validates final extension only."""
        from valid8r.core.validators import has_extension

        # Create file with .tar.gz but validate for .zip
        test_file = tmp_path / 'my.backup.file.tar.gz'
        test_file.write_text('content')

        validator = has_extension('.zip', '.7z')
        result = validator(test_file)

        assert result.is_failure()
        assert 'allowed extensions' in result.error_or('').lower()

    def it_lists_all_allowed_extensions_in_error(self, tmp_path: Path) -> None:
        """Test has_extension error message includes all allowed extensions."""
        from valid8r.core.validators import has_extension

        # Create file with .png extension
        test_file = tmp_path / 'image.png'
        test_file.write_text('content')

        validator = has_extension('.pdf', '.docx', '.txt')
        result = validator(test_file)

        assert result.is_failure()
        error_msg = result.error_or('')
        assert '.pdf' in error_msg
        assert '.docx' in error_msg
        assert '.txt' in error_msg

    def it_accepts_dot_file_with_proper_extension(self, tmp_path: Path) -> None:
        """Test has_extension handles dot files with extensions correctly."""
        from valid8r.core.validators import has_extension

        # Create dot file with extension
        test_file = tmp_path / '.config.json'
        test_file.write_text('content')

        validator = has_extension('.json')
        result = validator(test_file)

        assert result.is_success()
        assert result.value_or(None) == test_file
