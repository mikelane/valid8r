"""Schema-based validation with error accumulation and field path tracking.

This module provides the Schema and Field classes for validating dict-like
objects against a defined schema, accumulating all validation errors instead
of stopping at the first failure.

Key features:
- Error accumulation across multiple fields
- Field path tracking (e.g., ".age", ".user.email")
- Nested schema composition
- Required/optional field support
- Strict mode for rejecting extra fields
- Integration with existing parsers and validators

Examples:
    Basic schema validation:

    >>> from valid8r.core import parsers, schema
    >>> s = schema.Schema(fields={
    ...     'age': schema.Field(parser=parsers.parse_int, required=True),
    ...     'email': schema.Field(parser=parsers.parse_email, required=True),
    ... })
    >>> result = s.validate({'age': '25', 'email': 'alice@example.com'})
    >>> match result:
    ...     case Success(data):
    ...         print(f"Age: {data['age']}, Email: {data['email']}")
    ...     case Failure(errors):
    ...         print(f"Errors: {errors}")
    Age: 25, Email: EmailAddress(local='alice', domain='example.com')

    Error accumulation:

    >>> result = s.validate({'age': 'invalid', 'email': 'bad'})
    >>> match result:
    ...     case Failure(errors):
    ...         for err in errors:
    ...             print(f"{err.path}: {err.message}")
    .age: ...
    .email: ...

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
)

from valid8r.core.errors import (
    ErrorCode,
    ValidationError,
)
from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class Field:
    """Schema field definition with parser, validator, and required flag.

    A Field represents a single field in a schema, specifying how to parse
    and validate the field value.

    Attributes:
        parser: Function that parses/validates the raw value, returns Maybe[T]
        validator: Optional additional validation function to apply after parsing
        required: Whether the field must be present in the input

    Examples:
        Required field with just a parser:

        >>> from valid8r.core import parsers
        >>> field = Field(parser=parsers.parse_int, required=True)
        >>> field.required
        True

        Optional field:

        >>> field = Field(parser=parsers.parse_str, required=False)
        >>> field.required
        False

        Field with parser and validator:

        >>> from valid8r.core import validators
        >>> field = Field(
        ...     parser=parsers.parse_int,
        ...     validator=validators.minimum(0),
        ...     required=True
        ... )
        >>> field.validator is not None
        True

    """

    parser: Callable[[Any], Maybe[Any]]
    required: bool
    validator: Callable[[Any], Maybe[Any]] | None = None


class Schema:
    """Schema for validating dict-like objects with error accumulation.

    A Schema defines the structure and validation rules for a dict-like object,
    accumulating all validation errors across all fields instead of stopping
    at the first failure.

    Attributes:
        fields: Dictionary mapping field names to Field definitions
        strict: If True, reject inputs with fields not defined in the schema

    Examples:
        Basic schema validation:

        >>> from valid8r.core import parsers
        >>> s = Schema(fields={
        ...     'age': Field(parser=parsers.parse_int, required=True),
        ...     'name': Field(parser=parsers.parse_str, required=True),
        ... })
        >>> result = s.validate({'age': '25', 'name': 'Alice'})
        >>> result.is_success()
        True

        Error accumulation:

        >>> result = s.validate({'age': 'bad', 'name': ''})
        >>> match result:
        ...     case Failure(errors):
        ...         len(errors) >= 1
        ...     case _:
        ...         False
        True

        Strict mode:

        >>> strict_schema = Schema(
        ...     fields={'name': Field(parser=parsers.parse_str, required=True)},
        ...     strict=True
        ... )
        >>> result = strict_schema.validate({'name': 'Alice', 'extra': 'field'})
        >>> result.is_failure()
        True

    """

    def __init__(
        self,
        *,
        fields: dict[str, Field],
        strict: bool = False,
    ) -> None:
        """Initialize a Schema with field definitions.

        Args:
            fields: Dictionary mapping field names to Field definitions
            strict: If True, reject inputs with extra fields not in schema

        """
        self.fields = fields
        self.strict = strict

    def validate(self, data: dict[str, Any] | Any, path: str = '') -> Maybe[dict[str, Any]]:  # noqa: C901, PLR0912, ANN401
        """Validate data against the schema, accumulating all errors.

        This method validates the input data against all field definitions,
        collecting all validation errors instead of stopping at the first failure.
        Field paths are tracked for nested validation (e.g., ".user.email").

        Args:
            data: Input data to validate (must be dict-like)
            path: Current field path for nested validation (internal use)

        Returns:
            Success[dict]: Validated and parsed data if all fields pass
            Failure[list[ValidationError]]: List of all validation errors

        Examples:
            Successful validation:

            >>> from valid8r.core import parsers
            >>> s = Schema(fields={
            ...     'age': Field(parser=parsers.parse_int, required=True),
            ... })
            >>> result = s.validate({'age': '30'})
            >>> match result:
            ...     case Success(data):
            ...         data['age']
            ...     case _:
            ...         None
            30

            Multiple errors:

            >>> s = Schema(fields={
            ...     'age': Field(parser=parsers.parse_int, required=True),
            ...     'email': Field(parser=parsers.parse_email, required=True),
            ... })
            >>> result = s.validate({'age': 'bad', 'email': 'bad'})
            >>> match result:
            ...     case Failure(errors):
            ...         len(errors)
            ...     case _:
            ...         0
            2

        """
        # Validate that input is dict-like
        if not isinstance(data, dict):
            error = ValidationError(
                code=ErrorCode.INVALID_TYPE,
                message=f'Expected dict, got {type(data).__name__}',
                path=path,
                context={'input_type': type(data).__name__},
            )
            return Failure([error])  # type: ignore[arg-type]

        errors: list[ValidationError] = []
        validated_data: dict[str, Any] = {}

        # Check for extra fields in strict mode
        if self.strict:
            extra_fields = set(data.keys()) - set(self.fields.keys())
            for field_name in extra_fields:
                error = ValidationError(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=f'Unexpected field: {field_name}',
                    path=f'{path}.{field_name}' if path else f'.{field_name}',
                    context={'field': field_name},
                )
                errors.append(error)

        # Validate each field in the schema
        for field_name, field_def in self.fields.items():
            field_path = f'{path}.{field_name}' if path else f'.{field_name}'

            # Check if field is present in input
            if field_name not in data:
                if field_def.required:
                    error = ValidationError(
                        code=ErrorCode.VALIDATION_ERROR,
                        message=f'Required field missing: {field_name}',
                        path=field_path,
                        context={'field': field_name, 'required': True},
                    )
                    errors.append(error)
                continue

            # Parse the field value
            raw_value = data[field_name]
            parse_result = field_def.parser(raw_value)

            match parse_result:
                case Success(parsed_value):
                    # Apply validator if present
                    if field_def.validator is not None:
                        validation_result = field_def.validator(parsed_value)
                        match validation_result:
                            case Success(validated_value):
                                validated_data[field_name] = validated_value
                            case Failure() as failure_result:
                                # Extract the actual error (could be list or single error)
                                # Access _validation_error directly to handle list case
                                error_msg = failure_result._validation_error  # noqa: SLF001
                                nested_errors = self._extract_errors(
                                    error_msg, field_path, {'value': parsed_value, 'field': field_name}
                                )
                                errors.extend(nested_errors)
                    else:
                        validated_data[field_name] = parsed_value

                case Failure() as failure_result:
                    # Extract the actual error (could be list or single error)
                    # Access _validation_error directly to handle list case
                    error_msg = failure_result._validation_error  # noqa: SLF001
                    nested_errors = self._extract_errors(
                        error_msg, field_path, {'value': raw_value, 'field': field_name}
                    )
                    errors.extend(nested_errors)

        # Return accumulated errors or success
        if errors:
            return Failure(errors)  # type: ignore[arg-type]
        return Success(validated_data)

    def _extract_errors(
        self,
        error_msg: str | ValidationError | list[ValidationError],
        path: str,
        context: dict[str, Any],
    ) -> list[ValidationError]:
        """Extract a list of ValidationErrors from various error formats.

        This helper handles conversion of string errors, ValidationError instances,
        and lists of ValidationErrors (from nested schemas) into a list of
        ValidationError objects with appropriate field paths.

        Args:
            error_msg: Error message (string, ValidationError, or list)
            path: Field path for the error
            context: Additional context for the error

        Returns:
            List of ValidationError instances with paths and context

        """
        match error_msg:
            case list() as err_list:
                # List of errors from nested schema - update all paths
                result = []
                for err in err_list:
                    if isinstance(err, ValidationError):
                        # Prepend parent path to nested error path
                        updated_error = ValidationError(
                            code=err.code,
                            message=err.message,
                            path=f'{path}{err.path}',
                            context=err.context or context,
                        )
                        result.append(updated_error)
                return result if result else [self._create_single_error(error_msg, path, context)]  # type: ignore[arg-type]
            case _:
                # Single error - wrap in list
                return [self._create_single_error(error_msg, path, context)]  # type: ignore[arg-type]

    def _create_single_error(
        self,
        error_msg: str | ValidationError,
        path: str,
        context: dict[str, Any],
    ) -> ValidationError:
        """Create a single ValidationError from a string or ValidationError.

        This helper handles conversion of string errors and ValidationError instances
        into a ValidationError with the appropriate field path.

        Args:
            error_msg: Error message (string or ValidationError)
            path: Field path for the error
            context: Additional context for the error

        Returns:
            ValidationError instance with path and context

        """
        match error_msg:
            case str(msg):
                # String error - wrap in ValidationError
                return ValidationError(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=msg,
                    path=path,
                    context=context,
                )
            case ValidationError() as err:
                # Already a ValidationError - update path if needed
                if not err.path or err.path == '':
                    return ValidationError(
                        code=err.code,
                        message=err.message,
                        path=path,
                        context=err.context or context,
                    )
                # Nested error - prepend parent path
                return ValidationError(
                    code=err.code,
                    message=err.message,
                    path=f'{path}{err.path}',
                    context=err.context or context,
                )
            case _:
                # Unknown error type - return generic error
                return ValidationError(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=str(error_msg),
                    path=path,
                    context=context,
                )


__all__ = ['Field', 'Schema']
