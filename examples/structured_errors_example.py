"""Structured Error Handling Examples.

This example demonstrates how to use ValidationError and ErrorCode for
programmatic error handling, JSON serialization, and building robust
validation logic with machine-readable errors.

Run with:
    python examples/structured_errors_example.py
"""

from __future__ import annotations

import json
import sys

from valid8r import (
    Maybe,
    parsers,
    validators,
)
from valid8r.core.errors import (
    ErrorCode,
    ValidationError,
)
from valid8r.core.maybe import (
    Failure,
    Success,
)


def example_basic_usage() -> None:
    """Demonstrate basic ValidationError creation and usage."""
    print('=' * 60)
    print('Example 1: Basic ValidationError Usage')
    print('=' * 60)

    # Create a ValidationError manually
    error = ValidationError(
        code=ErrorCode.INVALID_EMAIL,
        message='Email address format is invalid',
        path='.user.email',
        context={'input': 'not-an-email'},
    )

    print(f'Error Code: {error.code}')
    print(f'Message: {error.message}')
    print(f'Path: {error.path}')
    print(f'Context: {error.context}')
    print(f'String representation: {error}')
    print()


def example_error_codes() -> None:
    """Demonstrate using ErrorCode constants for different validation scenarios."""
    print('=' * 60)
    print('Example 2: Using ErrorCode Constants')
    print('=' * 60)

    # Parsing error
    parse_error = ValidationError(code=ErrorCode.INVALID_TYPE, message='Input must be a valid integer')

    # Numeric range error
    range_error = ValidationError(
        code=ErrorCode.OUT_OF_RANGE,
        message='Value must be between 0 and 100',
        context={'value': 150, 'min': 0, 'max': 100},
    )

    # String length error
    length_error = ValidationError(code=ErrorCode.TOO_SHORT, message='Password must be at least 8 characters')

    # Network validation error
    email_error = ValidationError(code=ErrorCode.INVALID_EMAIL, message='Email format is invalid')

    print('Parsing Error:')
    print(f'  Code: {parse_error.code}')
    print(f'  Message: {parse_error.message}')
    print()

    print('Range Error:')
    print(f'  Code: {range_error.code}')
    print(f'  Message: {range_error.message}')
    print(f'  Context: {range_error.context}')
    print()

    print('Length Error:')
    print(f'  Code: {length_error.code}')
    print(f'  Message: {length_error.message}')
    print()

    print('Email Error:')
    print(f'  Code: {email_error.code}')
    print(f'  Message: {email_error.message}')
    print()


def example_programmatic_handling() -> None:
    """Demonstrate programmatic error handling using error codes."""
    print('=' * 60)
    print('Example 3: Programmatic Error Handling')
    print('=' * 60)

    def process_email(email_str: str) -> str:
        """Process email with different error handling based on error code."""
        result = parsers.parse_email(email_str)

        match result:
            case Success(email):
                return f'Valid email: {email.local}@{email.domain}'

            case Failure():
                # Access structured error
                error = result.validation_error

                # Different handling based on error code
                match error.code:
                    case ErrorCode.INVALID_EMAIL:
                        return 'Please enter a valid email address (user@domain.com)'
                    case ErrorCode.EMPTY_STRING:
                        return 'Email is required'
                    case ErrorCode.INPUT_TOO_LONG:
                        return 'Email is too long (maximum 254 characters)'
                    case _:
                        return f'Validation error: {error.message}'

    # Test with different inputs
    test_cases = ['user@example.com', 'not-an-email', '', 'x' * 300]

    max_display_length = 50
    for email in test_cases:
        display = email if email else '(empty string)'
        if len(email) > max_display_length:
            display = f'{email[:max_display_length]}... ({len(email)} chars)'
        print(f'{display:55} -> {process_email(email)}')

    print()


def example_json_serialization() -> None:
    """Demonstrate converting errors to JSON for API responses."""
    print('=' * 60)
    print('Example 4: JSON Serialization for APIs')
    print('=' * 60)

    def validate_api_request(data: dict) -> dict:
        """Validate API request data and return JSON response."""
        errors = []

        # Validate name
        if not data.get('name'):
            errors.append(
                ValidationError(code=ErrorCode.EMPTY_STRING, message='Name is required', path='.name').to_dict()
            )

        # Validate email
        email_result = parsers.parse_email(data.get('email', ''))
        match email_result:
            case Failure():
                error = email_result.validation_error
                errors.append({**error.to_dict(), 'path': '.email'})

        # Validate age
        age_result = parsers.parse_int(data.get('age', '')).bind(validators.minimum(0) & validators.maximum(120))

        match age_result:
            case Failure():
                error = age_result.validation_error
                errors.append({**error.to_dict(), 'path': '.age'})

        if errors:
            return {'status': 'error', 'errors': errors}

        return {'status': 'success', 'data': data}

    # Valid request
    valid_request = {'name': 'Alice', 'email': 'alice@example.com', 'age': '30'}

    print('Valid Request:')
    print(json.dumps(validate_api_request(valid_request), indent=2))
    print()

    # Invalid request
    invalid_request = {'name': '', 'email': 'not-an-email', 'age': 'abc'}

    print('Invalid Request:')
    print(json.dumps(validate_api_request(invalid_request), indent=2))
    print()


def example_pattern_matching() -> None:
    """Demonstrate pattern matching with structured errors."""
    print('=' * 60)
    print('Example 5: Pattern Matching with Structured Errors')
    print('=' * 60)

    def validate_age(age_str: str) -> str:
        """Validate age with pattern matching on error codes."""
        result = parsers.parse_int(age_str).bind(validators.minimum(0) & validators.maximum(120))

        adult_age_threshold = 18
        match result:
            case Success(age) if age >= adult_age_threshold:
                return f'Adult: {age} years old'
            case Success(age):
                return f'Minor: {age} years old'
            case Failure() if result.validation_error.code == ErrorCode.INVALID_TYPE:
                return 'Please enter a number'
            case Failure() if result.validation_error.code == ErrorCode.BELOW_MINIMUM:
                return 'Age cannot be negative'
            case Failure() if result.validation_error.code == ErrorCode.ABOVE_MAXIMUM:
                return 'Age seems unrealistic (max 120)'
            case Failure(error):
                return f'Validation failed: {error}'

    test_cases = ['25', '10', 'abc', '-5', '150', '']

    for age in test_cases:
        display = age if age else '(empty)'
        print(f'{display:20} -> {validate_age(age)}')

    print()


def example_multi_field_validation() -> None:
    """Demonstrate multi-field validation with paths."""
    print('=' * 60)
    print('Example 6: Multi-Field Validation with Paths')
    print('=' * 60)

    def validate_user_data(data: dict) -> list[dict]:
        """Validate user data with field paths."""
        errors = []

        # Validate username
        username = data.get('username', '')
        min_username_length = 3
        if not username:
            errors.append(
                ValidationError(code=ErrorCode.EMPTY_STRING, message='Username is required', path='.username').to_dict()
            )
        elif len(username) < min_username_length:
            errors.append(
                ValidationError(
                    code=ErrorCode.TOO_SHORT,
                    message='Username must be at least 3 characters',
                    path='.username',
                    context={'length': len(username), 'min_length': 3},
                ).to_dict()
            )

        # Validate email
        email_result = parsers.parse_email(data.get('email', ''))
        match email_result:
            case Failure():
                error = email_result.validation_error
                errors.append({**error.to_dict(), 'path': '.email'})

        # Validate age
        age_result = parsers.parse_int(data.get('age', '')).bind(validators.minimum(0) & validators.maximum(120))

        match age_result:
            case Failure():
                error = age_result.validation_error
                errors.append({**error.to_dict(), 'path': '.age'})

        return errors

    # Test with invalid data
    invalid_data = {'username': 'ab', 'email': 'not-an-email', 'age': '-5'}

    errors = validate_user_data(invalid_data)

    print('Validation Errors:')
    for error in errors:
        print(f'  {error["path"]}: [{error["code"]}] {error["message"]}')
        if error.get('context'):
            print(f'    Context: {error["context"]}')

    print()


def example_backward_compatibility() -> None:
    """Demonstrate backward compatibility with string errors."""
    print('=' * 60)
    print('Example 7: Backward Compatibility')
    print('=' * 60)

    # Old way: string errors still work
    old_failure = Maybe.failure('Something went wrong')

    print('String Error (backward compatible):')
    match old_failure:
        case Failure(error):
            print(f'  Pattern matching: {error}')

    # String is automatically wrapped in ValidationError
    print(f'  Wrapped code: {old_failure.validation_error.code}')
    print(f'  Wrapped message: {old_failure.validation_error.message}')
    print()

    # New way: structured errors
    new_failure = Maybe.failure(ValidationError(code=ErrorCode.INVALID_EMAIL, message='Bad email format'))

    print('Structured Error (new):')
    match new_failure:
        case Failure(error):
            print(f'  Pattern matching: {error}')

    print(f'  Error code: {new_failure.validation_error.code}')
    print(f'  Error message: {new_failure.validation_error.message}')
    print()


def example_real_world_scenario() -> None:  # noqa: C901
    """Real-world scenario: validating API request data."""
    print('=' * 60)
    print('Example 8: Real-World API Request Validation')
    print('=' * 60)

    def validate_string(value: str, min_len: int, max_len: int) -> Maybe[str]:
        """Validate string length."""
        if not value:
            return Maybe.failure('Value is required')
        if len(value) < min_len or len(value) > max_len:
            return Maybe.failure(f'Length must be between {min_len} and {max_len}')
        return Maybe.success(value)

    def validate_create_user_request(request_data: dict) -> dict:
        """Validate user creation API request."""
        errors = []

        # Validate username
        username = request_data.get('username', '')
        username_result = validate_string(username, 3, 50)
        match username_result:
            case Failure():
                error = username_result.validation_error
                errors.append({**error.to_dict(), 'path': '.username'})

        # Validate email
        email_result = parsers.parse_email(request_data.get('email', ''))
        match email_result:
            case Failure():
                error = email_result.validation_error
                errors.append({**error.to_dict(), 'path': '.email'})

        # Validate age
        age_result = parsers.parse_int(request_data.get('age', '')).bind(
            validators.minimum(13) & validators.maximum(120)
        )

        match age_result:
            case Failure():
                error = age_result.validation_error
                errors.append({**error.to_dict(), 'path': '.age'})

        # Optional password validation
        password = request_data.get('password', '')
        if password:
            password_result = (
                Maybe.success(password)
                .bind(validators.length(8, 128))
                .bind(
                    validators.predicate(
                        lambda p: any(c.isdigit() for c in p) and any(c.isalpha() for c in p),
                        'Password must contain both letters and numbers',
                    )
                )
            )

            match password_result:
                case Failure():
                    error = password_result.validation_error
                    errors.append({**error.to_dict(), 'path': '.password'})

        if errors:
            return {'status': 'error', 'errors': errors, 'message': 'Validation failed'}

        return {'status': 'success', 'message': 'User created successfully'}

    # Test cases
    print('Valid Request:')
    valid_request = {'username': 'alice_smith', 'email': 'alice@example.com', 'age': '25', 'password': 'secure123'}

    print(json.dumps(validate_create_user_request(valid_request), indent=2))
    print()

    print('Invalid Request:')
    invalid_request = {'username': 'ab', 'email': 'bad-email', 'age': '10', 'password': 'short'}

    print(json.dumps(validate_create_user_request(invalid_request), indent=2))
    print()


def main() -> int:
    """Run all structured error examples."""
    print()
    print('Valid8r Structured Error Handling Examples')
    print('=' * 60)
    print()

    examples = [
        example_basic_usage,
        example_error_codes,
        example_programmatic_handling,
        example_json_serialization,
        example_pattern_matching,
        example_multi_field_validation,
        example_backward_compatibility,
        example_real_world_scenario,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:  # noqa: BLE001
            print(f'ERROR: {example.__name__} failed: {e}')
            return 1

    print('=' * 60)
    print('All examples completed successfully!')
    print('=' * 60)
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
