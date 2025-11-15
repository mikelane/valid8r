"""Tests for Failure class with ValidationError integration and backward compatibility."""

from __future__ import annotations

import pytest

from valid8r.core.errors import (
    ErrorCode,
    ValidationError,
)
from valid8r.core.maybe import Failure


class DescribeFailureBackwardCompatibility:
    """Tests ensuring backward compatibility with string errors."""

    def it_accepts_string_error_as_before(self) -> None:
        """Accept string error message (backward compatible)."""
        failure = Failure('Input is invalid')

        assert failure.is_failure()
        assert not failure.is_success()

    def it_returns_string_error_via_error_or(self) -> None:
        """error_or() returns string message (backward compatible)."""
        failure = Failure('Something went wrong')

        assert failure.error_or('default') == 'Something went wrong'
        assert failure.error_or('') == 'Something went wrong'

    def it_returns_string_error_via_get_error(self) -> None:
        """get_error() returns string message (backward compatible)."""
        failure = Failure('Parse error')

        assert failure.get_error() == 'Parse error'

    def it_propagates_error_through_bind(self) -> None:
        """bind() propagates string error (backward compatible)."""
        failure = Failure('Original error')

        result = failure.bind(lambda _x: Failure('Should not reach'))

        assert result.is_failure()
        assert result.error_or('') == 'Original error'

    def it_propagates_error_through_map(self) -> None:
        """map() propagates string error (backward compatible)."""
        failure = Failure('Original error')

        result = failure.map(lambda x: x * 2)

        assert result.is_failure()
        assert result.error_or('') == 'Original error'

    def it_converts_to_string_representation(self) -> None:
        """Convert Failure to string matching original behavior."""
        failure = Failure('Test error message')

        assert str(failure) == 'Failure(Test error message)'
        assert repr(failure) == "Failure('Test error message')"


class DescribeFailureWithValidationError:
    """Tests for new ValidationError support in Failure."""

    def it_accepts_validation_error_directly(self) -> None:
        """Accept ValidationError object directly."""
        error = ValidationError(code='INVALID_TYPE', message='Expected integer', path='.age')
        failure = Failure(error)

        assert failure.is_failure()

    def it_wraps_string_in_validation_error_automatically(self) -> None:
        """Automatically wrap string error in ValidationError."""
        failure = Failure('Simple error message')

        # Access structured error via validation_error property
        error = failure.validation_error
        assert isinstance(error, ValidationError)
        assert error.code == 'VALIDATION_ERROR'
        assert error.message == 'Simple error message'
        assert error.path == ''
        assert error.context is None

    def it_exposes_validation_error_via_validation_error_property(self) -> None:
        """validation_error property returns ValidationError instance."""
        validation_error = ValidationError(
            code=ErrorCode.OUT_OF_RANGE,
            message='Value out of range',
            path='.temperature',
            context={'min': 0, 'max': 100},
        )
        failure = Failure(validation_error)

        error = failure.validation_error
        assert isinstance(error, ValidationError)
        assert error.code == 'OUT_OF_RANGE'
        assert error.message == 'Value out of range'
        assert error.path == '.temperature'
        assert error.context == {'min': 0, 'max': 100}

    def it_maintains_error_or_backward_compatibility_with_validation_error(self) -> None:
        """error_or() returns message string even with ValidationError."""
        validation_error = ValidationError(code='INVALID_EMAIL', message='Email is invalid', path='.user.email')
        failure = Failure(validation_error)

        assert failure.error_or('default') == 'Email is invalid'

    def it_maintains_get_error_backward_compatibility(self) -> None:
        """get_error() returns message string for ValidationError."""
        validation_error = ValidationError(code='PARSE_ERROR', message='Failed to parse input')
        failure = Failure(validation_error)

        assert failure.get_error() == 'Failed to parse input'

    def it_propagates_validation_error_through_bind(self) -> None:
        """bind() propagates ValidationError unchanged."""
        original_error = ValidationError(code='CUSTOM_ERROR', message='Original', path='.field')
        failure = Failure(original_error)

        result = failure.bind(lambda _x: Failure('Should not reach'))

        assert result.is_failure()
        assert result.validation_error.code == 'CUSTOM_ERROR'
        assert result.validation_error.message == 'Original'
        assert result.validation_error.path == '.field'

    def it_propagates_validation_error_through_map(self) -> None:
        """map() propagates ValidationError unchanged."""
        original_error = ValidationError(code='TOO_LONG', message='String too long')
        failure = Failure(original_error)

        result = failure.map(lambda x: x.upper())

        assert result.is_failure()
        assert result.validation_error.code == 'TOO_LONG'
        assert result.validation_error.message == 'String too long'


class DescribeFailurePatternMatching:
    """Tests for pattern matching with Failure and ValidationError."""

    def it_pattern_matches_with_string_error(self) -> None:
        """Pattern match works with string error (backward compatible)."""
        failure = Failure('Test error')

        match failure:
            case Failure(error):
                # error is the message string (backward compatible)
                assert error == 'Test error'
            case _:
                pytest.fail('Pattern match failed')

    def it_pattern_matches_with_validation_error(self) -> None:
        """Pattern match works with ValidationError."""
        validation_error = ValidationError(code='INVALID_URL', message='URL is malformed')
        failure = Failure(validation_error)

        match failure:
            case Failure(error):
                # error is the message string (backward compatible)
                assert error == 'URL is malformed'
            case _:
                pytest.fail('Pattern match failed')


class DescribeFailureStringRepresentation:
    """Tests for string representation of Failure with ValidationError."""

    def it_shows_message_for_wrapped_string_error(self) -> None:
        """Show string representation for wrapped string error."""
        failure = Failure('Error message')

        assert str(failure) == 'Failure(Error message)'
        assert repr(failure) == "Failure('Error message')"

    def it_shows_validation_error_string_representation(self) -> None:
        """Show ValidationError string representation with backward compatibility."""
        validation_error = ValidationError(code='BELOW_MINIMUM', message='Value too small', path='.age')
        failure = Failure(validation_error)

        # Backward compatible: shows only message, not path
        assert str(failure) == 'Failure(Value too small)'
        assert repr(failure) == "Failure('Value too small')"


class DescribeMaybeFactoryMethod:
    """Tests for Maybe.failure() factory method with ValidationError."""

    def it_creates_failure_from_string(self) -> None:
        """Maybe.failure() accepts string."""
        from valid8r.core.maybe import Maybe

        failure = Maybe.failure('Test error')

        assert failure.is_failure()
        assert failure.error_or('') == 'Test error'

    def it_creates_failure_from_validation_error(self) -> None:
        """Maybe.failure() accepts ValidationError."""
        from valid8r.core.maybe import Maybe

        validation_error = ValidationError(code='INVALID_TYPE', message='Type error')
        failure = Maybe.failure(validation_error)

        assert failure.is_failure()
        assert failure.validation_error.code == 'INVALID_TYPE'
        assert failure.validation_error.message == 'Type error'
