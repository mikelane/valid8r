"""Tests for structured error model (ValidationError and ErrorCode)."""

from __future__ import annotations

import pytest

from valid8r.core.errors import (
    ErrorCode,
    ValidationError,
)


class DescribeValidationError:
    """Tests for the ValidationError dataclass."""

    def it_creates_error_with_all_fields(self) -> None:
        """Create ValidationError with code, message, path, and context."""
        error = ValidationError(
            code='INVALID_EMAIL',
            message='Email address format is invalid',
            path='.user.email',
            context={'input': 'not-an-email', 'expected_format': 'user@domain.com'},
        )

        assert error.code == 'INVALID_EMAIL'
        assert error.message == 'Email address format is invalid'
        assert error.path == '.user.email'
        assert error.context == {'input': 'not-an-email', 'expected_format': 'user@domain.com'}

    def it_creates_error_with_minimal_fields(self) -> None:
        """Create ValidationError with only required fields (code and message)."""
        error = ValidationError(code='PARSE_ERROR', message='Failed to parse input')

        assert error.code == 'PARSE_ERROR'
        assert error.message == 'Failed to parse input'
        assert error.path == ''
        assert error.context is None

    def it_creates_error_with_path_but_no_context(self) -> None:
        """Create ValidationError with path but without context."""
        error = ValidationError(code='TOO_LONG', message='String exceeds maximum length', path='.items[0].name')

        assert error.code == 'TOO_LONG'
        assert error.message == 'String exceeds maximum length'
        assert error.path == '.items[0].name'
        assert error.context is None

    def it_is_frozen_and_immutable(self) -> None:
        """ValidationError is frozen and cannot be modified after creation."""
        error = ValidationError(code='TEST_ERROR', message='Test message')

        with pytest.raises(AttributeError, match='cannot assign to field'):
            error.code = 'DIFFERENT_CODE'  # type: ignore[misc]

        with pytest.raises(AttributeError, match='cannot assign to field'):
            error.message = 'Different message'  # type: ignore[misc]

    def it_converts_to_string_with_path(self) -> None:
        """Convert error to string with path prefix when path is present."""
        error = ValidationError(code='OUT_OF_RANGE', message='Value must be between 0 and 100', path='.user.age')

        assert str(error) == '.user.age: Value must be between 0 and 100'

    def it_converts_to_string_without_path(self) -> None:
        """Convert error to string showing only message when path is empty."""
        error = ValidationError(code='INVALID_TYPE', message='Input must be a valid integer')

        assert str(error) == 'Input must be a valid integer'

    def it_converts_to_dict_with_all_fields(self) -> None:
        """to_dict() returns dictionary with all fields for JSON serialization."""
        error = ValidationError(
            code='BELOW_MINIMUM',
            message='Value is below minimum',
            path='.temperature',
            context={'value': -10, 'min': 0},
        )

        result = error.to_dict()

        assert result == {
            'code': 'BELOW_MINIMUM',
            'message': 'Value is below minimum',
            'path': '.temperature',
            'context': {'value': -10, 'min': 0},
        }

    def it_converts_to_dict_with_empty_context_when_none(self) -> None:
        """to_dict() returns empty dict for context when None."""
        error = ValidationError(code='EMPTY_STRING', message='String cannot be empty')

        result = error.to_dict()

        assert result == {
            'code': 'EMPTY_STRING',
            'message': 'String cannot be empty',
            'path': '',
            'context': {},
        }

    @pytest.mark.parametrize(
        ('code', 'message', 'path', 'context', 'expected_str'),
        [
            pytest.param(
                'INVALID_EMAIL',
                'Invalid email format',
                '.email',
                None,
                '.email: Invalid email format',
                id='with-path-no-context',
            ),
            pytest.param(
                'OUT_OF_RANGE',
                'Value out of range',
                '',
                {'min': 0, 'max': 100, 'value': 150},
                'Value out of range',
                id='no-path-with-context',
            ),
            pytest.param(
                'PARSE_ERROR',
                'Could not parse input',
                '.items[0]',
                {'input': 'bad'},
                '.items[0]: Could not parse input',
                id='with-path-and-context',
            ),
        ],
    )
    def it_formats_different_error_combinations(
        self, code: str, message: str, path: str, context: dict[str, object] | None, expected_str: str
    ) -> None:
        """Format errors correctly with various field combinations."""
        error = ValidationError(code=code, message=message, path=path, context=context)

        assert str(error) == expected_str

    def it_includes_context_in_dict_representation(self) -> None:
        """Context data is preserved in dictionary representation."""
        error = ValidationError(
            code='PATTERN_MISMATCH',
            message='Input does not match required pattern',
            context={'pattern': r'\d{3}-\d{4}', 'input': 'abc-defg'},
        )

        result = error.to_dict()

        assert result['context'] == {'pattern': r'\d{3}-\d{4}', 'input': 'abc-defg'}

    def it_handles_nested_context_data(self) -> None:
        """Context can contain nested dictionaries and complex data."""
        error = ValidationError(
            code='VALIDATION_ERROR',
            message='Multiple validation failures',
            context={'errors': [{'field': 'name', 'issue': 'too short'}, {'field': 'age', 'issue': 'negative'}]},
        )

        assert error.context == {
            'errors': [{'field': 'name', 'issue': 'too short'}, {'field': 'age', 'issue': 'negative'}]
        }
        assert error.to_dict()['context'] == error.context


class DescribeErrorCode:
    """Tests for the ErrorCode constants registry."""

    def it_defines_parsing_error_codes(self) -> None:
        """Define standard error codes for parsing failures."""
        assert ErrorCode.INVALID_TYPE == 'INVALID_TYPE'
        assert ErrorCode.INVALID_FORMAT == 'INVALID_FORMAT'
        assert ErrorCode.PARSE_ERROR == 'PARSE_ERROR'

    def it_defines_numeric_validation_codes(self) -> None:
        """Define error codes for numeric range validation."""
        assert ErrorCode.OUT_OF_RANGE == 'OUT_OF_RANGE'
        assert ErrorCode.BELOW_MINIMUM == 'BELOW_MINIMUM'
        assert ErrorCode.ABOVE_MAXIMUM == 'ABOVE_MAXIMUM'

    def it_defines_string_validation_codes(self) -> None:
        """Define error codes for string validation."""
        assert ErrorCode.TOO_SHORT == 'TOO_SHORT'
        assert ErrorCode.TOO_LONG == 'TOO_LONG'
        assert ErrorCode.PATTERN_MISMATCH == 'PATTERN_MISMATCH'
        assert ErrorCode.EMPTY_STRING == 'EMPTY_STRING'

    def it_defines_collection_validation_codes(self) -> None:
        """Define error codes for collection validation."""
        assert ErrorCode.NOT_IN_SET == 'NOT_IN_SET'
        assert ErrorCode.DUPLICATE_ITEMS == 'DUPLICATE_ITEMS'
        assert ErrorCode.INVALID_SUBSET == 'INVALID_SUBSET'

    def it_defines_network_validation_codes(self) -> None:
        """Define error codes for network-related parsers."""
        assert ErrorCode.INVALID_EMAIL == 'INVALID_EMAIL'
        assert ErrorCode.INVALID_URL == 'INVALID_URL'
        assert ErrorCode.INVALID_IP == 'INVALID_IP'
        assert ErrorCode.INVALID_PHONE == 'INVALID_PHONE'

    def it_defines_filesystem_validation_codes(self) -> None:
        """Define error codes for filesystem validation."""
        assert ErrorCode.PATH_NOT_FOUND == 'PATH_NOT_FOUND'
        assert ErrorCode.NOT_A_FILE == 'NOT_A_FILE'
        assert ErrorCode.NOT_A_DIRECTORY == 'NOT_A_DIRECTORY'
        assert ErrorCode.FILE_TOO_LARGE == 'FILE_TOO_LARGE'

    def it_defines_dos_protection_codes(self) -> None:
        """Define error code for DoS protection."""
        assert ErrorCode.INPUT_TOO_LONG == 'INPUT_TOO_LONG'

    def it_defines_custom_error_code(self) -> None:
        """Define custom/generic error code."""
        assert ErrorCode.CUSTOM_ERROR == 'CUSTOM_ERROR'
        assert ErrorCode.VALIDATION_ERROR == 'VALIDATION_ERROR'

    def it_works_with_validation_error(self) -> None:
        """ErrorCode constants integrate with ValidationError."""
        error = ValidationError(
            code=ErrorCode.INVALID_EMAIL, message='Invalid email address format', path='.user.email'
        )

        assert error.code == 'INVALID_EMAIL'
        assert error.to_dict()['code'] == 'INVALID_EMAIL'
