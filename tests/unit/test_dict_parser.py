from __future__ import annotations

import pytest

from valid8r.core.maybe import Maybe
from valid8r.core.parsers import (
    parse_dict,
    parse_int,
)


class DescribeDictParser:
    @pytest.mark.parametrize(
        ('input_str', 'key_parser', 'value_parser', 'pair_sep', 'kv_sep', 'expected_result'),
        [
            pytest.param(
                'a:1,b:2,c:3',
                lambda s: Maybe.success(s),
                parse_int,
                ',',
                ':',
                {'a': 1, 'b': 2, 'c': 3},
                id='string keys and int values'
            ),
            pytest.param(
                'a=1|b=2|c=3',
                lambda s: Maybe.success(s),
                parse_int,
                '|',
                '=',
                {'a': 1, 'b': 2, 'c': 3},
                id='custom separators'
            ),
            pytest.param(
                '  a  :  1  ,  b  :  2  ',
                lambda s: Maybe.success(s),
                parse_int,
                ',',
                ':',
                {'a': 1, 'b': 2},
                id='with whitespace'
            ),
            pytest.param(
                '',
                lambda s: Maybe.success(s),
                parse_int,
                ',',
                ':',
                None,
                id='empty string'
            ),
        ],
    )
    def it_parses_dicts_successfully(self, input_str, key_parser, value_parser, pair_sep, kv_sep, expected_result):
        """Test that parse_dict successfully parses valid dictionary inputs."""
        result = parse_dict(
            input_str,
            key_parser=key_parser,
            value_parser=value_parser,
            pair_separator=pair_sep,
            key_value_separator=kv_sep
        )

        if expected_result is None:
            assert result.is_failure()
            assert result.value_or('TEST') == 'Input must not be empty'
        else:
            assert result.is_success()
            assert result.value_or('TEST') == expected_result

    def it_handles_invalid_key_value_pairs(self):
        """Test that parse_dict handles invalid key-value pairs."""
        result = parse_dict('a:1,b2,c:3')

        assert result.is_failure()
        assert 'Invalid key-value pair' in result.value_or('TEST')

    def it_handles_invalid_keys(self):
        """Test that parse_dict handles invalid keys."""

        def fail_parser(s: str) -> Maybe[str]:
            return Maybe.failure('Invalid key')

        result = parse_dict('a:1,b:2', key_parser=fail_parser)

        assert result.is_failure()
        assert 'Failed to parse key' in result.value_or('TEST')

    def it_handles_invalid_values(self):
        """Test that parse_dict handles invalid values."""
        result = parse_dict('a:1,b:x,c:3', value_parser=parse_int)

        assert result.is_failure()
        assert 'Failed to parse value' in result.value_or('TEST')

    def it_uses_default_parsers_when_none_specified(self):
        """Test that parse_dict uses default parsers when none are specified."""
        result = parse_dict('a:1,b:2')

        assert result.is_success()
        assert result.value_or('TEST') == {'a': '1', 'b': '2'}

    def it_handles_custom_error_messages(self):
        """Test that parse_dict uses custom error messages."""
        custom_msg = 'Custom error message'
        result = parse_dict('a:1,b:x,c:3', value_parser=parse_int, error_message=custom_msg)

        assert result.is_failure()
        assert custom_msg == result.value_or('TEST')
