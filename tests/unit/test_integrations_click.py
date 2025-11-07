"""Unit tests for valid8r.integrations.click module."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import pytest

click = pytest.importorskip('click')

from valid8r.core import (  # noqa: E402
    parsers,
    validators,
)

if TYPE_CHECKING:
    from valid8r.core.maybe import Maybe


class DescribeParamTypeAdapter:
    """Test ParamTypeAdapter class for Click integration."""

    def it_converts_valid_input_to_success_value(self) -> None:
        """Return the unwrapped value when parser succeeds."""
        from valid8r.integrations.click import ParamTypeAdapter

        adapter = ParamTypeAdapter(parsers.parse_int)

        # Mock Click param and context
        class MockParam:
            name = '--value'

        class MockContext:
            command = None

        result = adapter.convert('42', MockParam(), MockContext())

        assert result == 42

    def it_fails_with_invalid_input(self) -> None:
        """Call self.fail() when parser returns Failure."""
        from valid8r.integrations.click import ParamTypeAdapter

        adapter = ParamTypeAdapter(parsers.parse_int)

        class MockParam:
            name = '--value'

        class MockContext:
            command = None

        # This should call self.fail() which raises click.exceptions.BadParameter
        with pytest.raises(click.exceptions.BadParameter):
            adapter.convert('not a number', MockParam(), MockContext())

    def it_uses_custom_name_parameter(self) -> None:
        """Use the custom name when provided."""
        from valid8r.integrations.click import ParamTypeAdapter

        adapter = ParamTypeAdapter(parsers.parse_int, name='port')

        assert adapter.name == 'port'

    def it_defaults_to_parser_function_name(self) -> None:
        """Use parser.__name__ when no custom name provided."""
        from valid8r.integrations.click import ParamTypeAdapter

        adapter = ParamTypeAdapter(parsers.parse_int)

        assert adapter.name == 'parse_int'

    def it_preserves_already_converted_values(self) -> None:
        """Pass through values that are not strings (already converted)."""
        from valid8r.integrations.click import ParamTypeAdapter

        adapter = ParamTypeAdapter(parsers.parse_int)

        # Click sometimes passes already-converted values
        result = adapter.convert(42, None, None)  # type: ignore[arg-type]

        assert result == 42

    def it_works_with_email_parser(self) -> None:
        """Work correctly with parse_email parser."""
        from valid8r.integrations.click import ParamTypeAdapter

        adapter = ParamTypeAdapter(parsers.parse_email)

        class MockParam:
            name = '--email'

        class MockContext:
            command = None

        result = adapter.convert('alice@example.com', MockParam(), MockContext())

        assert result.local == 'alice'
        assert result.domain == 'example.com'

    def it_works_with_chained_validators(self) -> None:
        """Work with parsers combined with validators."""
        from valid8r.integrations.click import ParamTypeAdapter

        # Create a parser that validates port range using bind
        def port_parser(value: str) -> Maybe[int]:
            return parsers.parse_int(value).bind(validators.minimum(1)).bind(validators.maximum(65535))

        adapter = ParamTypeAdapter(port_parser, name='port')

        class MockParam:
            name = '--port'

        class MockContext:
            command = None

        # Valid port
        result = adapter.convert('8080', MockParam(), MockContext())
        assert result == 8080

        # Invalid port (out of range)
        with pytest.raises(click.exceptions.BadParameter):
            adapter.convert('0', MockParam(), MockContext())

    def it_works_with_uuid_parser(self) -> None:
        """Work with UUID parser."""
        import uuid

        from valid8r.integrations.click import ParamTypeAdapter

        adapter = ParamTypeAdapter(parsers.parse_uuid)

        class MockParam:
            name = '--user-id'

        class MockContext:
            command = None

        test_uuid = str(uuid.uuid4())
        result = adapter.convert(test_uuid, MockParam(), MockContext())

        assert isinstance(result, uuid.UUID)
        assert str(result) == test_uuid

    def it_works_with_phone_parser(self) -> None:
        """Work with phone parser."""
        from valid8r.integrations.click import ParamTypeAdapter

        adapter = ParamTypeAdapter(parsers.parse_phone)

        class MockParam:
            name = '--phone'

        class MockContext:
            command = None

        # Use a valid phone number (exchange must start with 2-9)
        result = adapter.convert('(415) 234-5678', MockParam(), MockContext())

        assert result.area_code == '415'
        assert result.exchange == '234'
        assert result.subscriber == '5678'

    def it_includes_parser_error_message_in_click_error(self) -> None:
        """Include the parser's error message when failing."""
        from valid8r.integrations.click import ParamTypeAdapter

        adapter = ParamTypeAdapter(parsers.parse_email)

        class FailureCatcher:
            def __init__(self) -> None:
                self.message = ''

        catcher = FailureCatcher()

        class MockParam:
            name = '--email'

        class MockContext:
            command = None

        # Monkey-patch to capture the error message
        original_fail = adapter.fail

        def capture_fail(message: str, param: object = None, ctx: object = None) -> None:
            catcher.message = message
            original_fail(message, param, ctx)

        adapter.fail = capture_fail  # type: ignore[method-assign]

        with contextlib.suppress(click.exceptions.BadParameter):
            adapter.convert('not an email', MockParam(), MockContext())

        # The error message should include something about email validation
        assert 'email' in catcher.message.lower() or 'valid' in catcher.message.lower()


class DescribeParamTypeAdapterWithCustomErrorPrefix:
    """Test custom error prefix feature."""

    def it_uses_custom_error_prefix_when_provided(self) -> None:
        """Prepend custom error prefix to error messages."""
        from valid8r.integrations.click import ParamTypeAdapter

        adapter = ParamTypeAdapter(parsers.parse_email, error_prefix='Email address')

        class FailureCatcher:
            def __init__(self) -> None:
                self.message = ''

        catcher = FailureCatcher()

        class MockParam:
            name = '--email'

        class MockContext:
            command = None

        original_fail = adapter.fail

        def capture_fail(message: str, param: object = None, ctx: object = None) -> None:
            catcher.message = message
            original_fail(message, param, ctx)

        adapter.fail = capture_fail  # type: ignore[method-assign]

        with contextlib.suppress(click.exceptions.BadParameter):
            adapter.convert('invalid', MockParam(), MockContext())

        assert catcher.message.startswith('Email address')

    def it_does_not_prepend_when_error_prefix_is_none(self) -> None:
        """Use parser error message as-is when error_prefix is None."""
        from valid8r.integrations.click import ParamTypeAdapter

        adapter = ParamTypeAdapter(parsers.parse_email, error_prefix=None)

        class FailureCatcher:
            def __init__(self) -> None:
                self.message = ''

        catcher = FailureCatcher()

        class MockParam:
            name = '--email'

        class MockContext:
            command = None

        original_fail = adapter.fail

        def capture_fail(message: str, param: object = None, ctx: object = None) -> None:
            catcher.message = message
            original_fail(message, param, ctx)

        adapter.fail = capture_fail  # type: ignore[method-assign]

        with contextlib.suppress(click.exceptions.BadParameter):
            adapter.convert('invalid', MockParam(), MockContext())

        # Should not start with a custom prefix
        assert not catcher.message.startswith('Email address')
