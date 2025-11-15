"""Tests for public API exports of error handling types."""

from __future__ import annotations


class DescribePublicAPIErrorExports:
    """Tests for ValidationError and ErrorCode public API exports."""

    def it_exports_validation_error_from_top_level(self) -> None:
        """ValidationError is exported from valid8r top-level package."""
        from valid8r import ValidationError

        error = ValidationError(code='TEST_ERROR', message='Test message')
        assert error.code == 'TEST_ERROR'
        assert error.message == 'Test message'

    def it_exports_error_code_from_top_level(self) -> None:
        """ErrorCode is exported from valid8r top-level package."""
        from valid8r import ErrorCode

        assert ErrorCode.INVALID_EMAIL == 'INVALID_EMAIL'
        assert ErrorCode.OUT_OF_RANGE == 'OUT_OF_RANGE'
        assert ErrorCode.PARSE_ERROR == 'PARSE_ERROR'

    def it_allows_direct_import_from_core_errors(self) -> None:
        """Direct imports from valid8r.core.errors still work (backward compatible)."""
        from valid8r.core.errors import (
            ErrorCode,
            ValidationError,
        )

        error = ValidationError(code=ErrorCode.INVALID_TYPE, message='Type mismatch')
        assert error.code == 'INVALID_TYPE'

    def it_integrates_with_maybe_failure(self) -> None:
        """ValidationError integrates with Maybe.failure()."""
        from valid8r import (
            ErrorCode,
            Maybe,
            ValidationError,
        )

        error = ValidationError(code=ErrorCode.TOO_LONG, message='String exceeds limit', path='.name')
        failure = Maybe.failure(error)

        assert failure.is_failure()
        assert failure.validation_error.code == 'TOO_LONG'
        assert failure.validation_error.path == '.name'

    def it_supports_pattern_matching_workflow(self) -> None:
        """Complete workflow with ValidationError and pattern matching."""
        from valid8r import (
            ErrorCode,
            Maybe,
            ValidationError,
        )

        # Create error
        error = ValidationError(
            code=ErrorCode.BELOW_MINIMUM, message='Value is below minimum', context={'min': 0, 'value': -5}
        )

        # Wrap in Maybe
        result = Maybe.failure(error)

        # Pattern match
        match result:
            case Maybe() if result.is_failure():
                # Access message via pattern matching (backward compatible)
                message = result.error
                assert message == 'Value is below minimum'

                # Access full error via property
                full_error = result.validation_error
                assert full_error.code == 'BELOW_MINIMUM'
                assert full_error.context == {'min': 0, 'value': -5}

    def it_provides_complete_error_handling_api(self) -> None:
        """Demonstrate complete error handling API from top-level imports."""
        from valid8r import (
            ErrorCode,
            Maybe,
            ValidationError,
        )

        # 1. Create structured error
        error = ValidationError(
            code=ErrorCode.PATTERN_MISMATCH,
            message='Input does not match pattern',
            path='.user.email',
            context={'pattern': r'^[a-z]+@[a-z]+\.[a-z]+$', 'input': 'INVALID'},
        )

        # 2. Wrap in Maybe
        failure = Maybe.failure(error)

        # 3. Access via different methods
        assert failure.error_or('default') == 'Input does not match pattern'  # Backward compatible
        assert failure.validation_error.code == 'PATTERN_MISMATCH'  # New structured access
        assert failure.validation_error.path == '.user.email'

        # 4. Convert to dict for JSON serialization
        error_dict = failure.validation_error.to_dict()
        assert error_dict['code'] == 'PATTERN_MISMATCH'
        assert error_dict['path'] == '.user.email'
        assert error_dict['context']['pattern'] == r'^[a-z]+@[a-z]+\.[a-z]+$'
