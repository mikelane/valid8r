from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from valid8r.core.maybe import Maybe
from valid8r.core.parsers import (
    parse_int,
    parse_list,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class DescribeListParser:
    @pytest.mark.parametrize(
        ('input_str', 'element_parser', 'separator', 'expected_result'),
        [
            pytest.param('1,2,3', parse_int, ',', [1, 2, 3], id='integers with default separator'),
            pytest.param('1|2|3', parse_int, '|', [1, 2, 3], id='integers with custom separator'),
            pytest.param('  1  ,  2  ,  3  ', parse_int, ',', [1, 2, 3], id='integers with whitespace'),
            pytest.param('a,b,c', lambda s: Maybe.success(s), ',', ['a', 'b', 'c'], id='strings'),
            pytest.param('', lambda s: Maybe.success(s), ',', None, id='empty string'),
        ],
    )
    def it_parses_lists_successfully(
        self, input_str: str, element_parser: Callable[[...], Maybe], separator: str, expected_result: list
    ) -> None:
        """Test that parse_list successfully parses valid list inputs."""
        result = parse_list(input_str, element_parser=element_parser, separator=separator)

        if expected_result is None:
            assert result.is_failure()
            assert result.error_or('') == 'Input must not be empty'
        else:
            assert result.is_success()
            assert result.value_or([]) == expected_result

    def it_handles_invalid_elements(self) -> None:
        """Test that parse_list handles invalid element errors."""
        result = parse_list('1,a,3', element_parser=parse_int)

        assert result.is_failure()
        assert 'Failed to parse element' in result.error_or('')

    def it_uses_default_parser_when_none_specified(self) -> None:
        """Test that parse_list uses a default parser when none is specified."""
        result = parse_list('a,b,c')

        assert result.is_success()
        assert result.value_or([]) == ['a', 'b', 'c']

    def it_handles_custom_error_messages(self) -> None:
        """Test that parse_list uses custom error messages."""
        custom_msg = 'Custom error message'
        result = parse_list('1,a,3', element_parser=parse_int, error_message=custom_msg)

        assert result.is_failure()
        assert custom_msg == result.error_or('')
