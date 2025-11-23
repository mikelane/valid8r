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
    >>> from valid8r.core.maybe import Success, Failure
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
    >>> result.is_failure()
    True

"""

from __future__ import annotations

import asyncio
import inspect
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
    """Schema field definition with parser, validators, and required flag.

    A Field represents a single field in a schema, specifying how to parse
    and validate the field value.

    Attributes:
        parser: Function that parses/validates the raw value, returns Maybe[T]
        validators: Optional list of validation functions to apply after parsing
        validator: Deprecated single validator (for backward compatibility)
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

        Field with parser and validators:

        >>> from valid8r.core import validators
        >>> field = Field(
        ...     parser=parsers.parse_int,
        ...     validators=[validators.minimum(0), validators.maximum(100)],
        ...     required=True
        ... )
        >>> len(field.validators)
        2

        Field with single validator (backward compatible):

        >>> field = Field(
        ...     parser=parsers.parse_int,
        ...     validator=validators.minimum(0),
        ...     required=True
        ... )
        >>> field.validators is not None
        True

    """

    parser: Callable[[Any], Maybe[Any]]
    required: bool
    validators: list[Callable[[Any], Maybe[Any]]] | None = None
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

        >>> from valid8r.core.maybe import Failure
        >>> result = s.validate({'age': 'bad', 'name': ''})
        >>> result.is_failure()
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

    def validate(self, data: dict[str, Any] | Any, path: str = '') -> Maybe[dict[str, Any]]:  # noqa: ANN401
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
            >>> from valid8r.core.maybe import Success
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
            >>> result.is_failure()
            True

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
        self._check_extra_fields(data, path, errors)

        # Validate each field in the schema
        for field_name, field_def in self.fields.items():
            field_path = f'{path}.{field_name}' if path else f'.{field_name}'

            # Check if field is present in input
            if field_name not in data:
                self._handle_missing_field(field_name, field_def, field_path, errors)
                continue

            # Parse and validate the field value
            raw_value = data[field_name]
            self._parse_and_validate_field(field_name, field_def, raw_value, field_path, validated_data, errors)

        # Return accumulated errors or success
        if errors:
            return Failure(errors)  # type: ignore[arg-type]
        return Success(validated_data)

    async def validate_async(
        self,
        data: dict[str, Any] | Any,  # noqa: ANN401
        path: str = '',
        *,
        timeout: float | None = None,  # noqa: ASYNC109
    ) -> Maybe[dict[str, Any]]:
        """Validate data against the schema asynchronously with async validators.

        This method validates input data supporting both sync and async validators.
        Sync validators are run first for fail-fast behavior, then async validators
        are run concurrently for better performance.

        Args:
            data: Input data to validate (must be dict-like)
            path: Current field path for nested validation (internal use)
            timeout: Optional timeout in seconds for async operations

        Returns:
            Success[dict]: Validated and parsed data if all fields pass
            Failure[list[ValidationError]]: List of all validation errors

        Raises:
            asyncio.TimeoutError: If validation exceeds the timeout

        Examples:
            Basic async validation:

            >>> import asyncio
            >>> from valid8r.core import parsers, schema
            >>> from valid8r.core.maybe import Maybe
            >>> async def async_validator(val: str) -> Maybe[str]:
            ...     await asyncio.sleep(0.001)
            ...     return Maybe.success(val)
            >>> s = schema.Schema(fields={
            ...     'field': schema.Field(
            ...         parser=parsers.parse_str,
            ...         validators=[async_validator],
            ...         required=True
            ...     ),
            ... })
            >>> result = asyncio.run(s.validate_async({'field': 'value'}))
            >>> result.is_success()
            True

            With timeout:

            >>> async def slow_validator(val: str) -> Maybe[str]:
            ...     await asyncio.sleep(2.0)
            ...     return Maybe.success(val)
            >>> s = schema.Schema(fields={
            ...     'field': schema.Field(
            ...         parser=parsers.parse_str,
            ...         validators=[slow_validator],
            ...         required=True
            ...     ),
            ... })
            >>> try:
            ...     result = asyncio.run(s.validate_async({'field': 'value'}, timeout=0.1))
            ... except asyncio.TimeoutError:
            ...     print("Timed out")
            Timed out

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
        self._check_extra_fields(data, path, errors)

        # Collect validation tasks for concurrent execution
        validation_tasks = []
        for field_name, field_def in self.fields.items():
            field_path = f'{path}.{field_name}' if path else f'.{field_name}'

            # Check if field is present in input
            if field_name not in data:
                self._handle_missing_field(field_name, field_def, field_path, errors)
                continue

            # Create validation task for each field
            raw_value = data[field_name]
            task = self._parse_and_validate_field_async(
                field_name, field_def, raw_value, field_path, validated_data, errors, timeout
            )
            validation_tasks.append(task)

        # Run all field validations concurrently
        if validation_tasks:
            if timeout:
                await asyncio.wait_for(asyncio.gather(*validation_tasks), timeout=timeout)
            else:
                await asyncio.gather(*validation_tasks)

        # Return accumulated errors or success
        if errors:
            return Failure(errors)  # type: ignore[arg-type]
        return Success(validated_data)

    async def _parse_and_validate_field_async(  # noqa: PLR0913
        self,
        field_name: str,
        field_def: Field,
        raw_value: Any,  # noqa: ANN401
        field_path: str,
        validated_data: dict[str, Any],
        errors: list[ValidationError],
        timeout: float | None = None,  # noqa: ASYNC109
    ) -> None:
        """Parse and validate a single field value asynchronously.

        Args:
            field_name: Name of the field
            field_def: Field definition with parser and validators
            raw_value: Raw input value to parse
            field_path: Full path to the field
            validated_data: Dictionary to accumulate validated values
            errors: List to accumulate errors
            timeout: Optional timeout for async operations

        """
        parse_result = field_def.parser(raw_value)

        match parse_result:
            case Success(parsed_value):
                await self._apply_validators_async(
                    field_name, field_def, parsed_value, field_path, validated_data, errors, timeout
                )
            case Failure() as failure_result:
                self._handle_parse_failure(failure_result, field_name, raw_value, field_path, errors)

    async def _apply_validators_async(  # noqa: PLR0913, PLR0912, C901
        self,
        field_name: str,
        field_def: Field,
        parsed_value: Any,  # noqa: ANN401
        field_path: str,
        validated_data: dict[str, Any],
        errors: list[ValidationError],
        timeout: float | None = None,  # noqa: ASYNC109
    ) -> None:
        """Apply sync and async validators to parsed value.

        This method runs sync validators first (fail-fast), then runs async
        validators concurrently if sync validators pass.

        Args:
            field_name: Name of the field
            field_def: Field definition with optional validators
            parsed_value: Successfully parsed value
            field_path: Full path to the field
            validated_data: Dictionary to accumulate validated values
            errors: List to accumulate errors
            timeout: Optional timeout for async operations

        """
        # Combine validators and validator into a single list
        validators_to_apply = []
        if field_def.validators:
            validators_to_apply.extend(field_def.validators)
        elif field_def.validator:
            # Backward compatibility: convert single validator to list
            validators_to_apply.append(field_def.validator)

        if not validators_to_apply:
            validated_data[field_name] = parsed_value
            return

        # Separate sync and async validators
        sync_validators = [v for v in validators_to_apply if not inspect.iscoroutinefunction(v)]
        async_validators = [v for v in validators_to_apply if inspect.iscoroutinefunction(v)]

        # Run sync validators first (fail-fast)
        current_value = parsed_value
        for validator in sync_validators:
            validation_result = validator(current_value)
            match validation_result:
                case Success(validated_value):
                    current_value = validated_value
                case Failure() as failure_result:
                    self._handle_validation_failure(failure_result, field_name, current_value, field_path, errors)
                    return  # Stop if sync validation fails

        # Run async validators concurrently
        if async_validators:
            try:
                async_task = self._run_async_validators(async_validators, current_value)
                if timeout:
                    async_result = await asyncio.wait_for(async_task, timeout=timeout)
                else:
                    async_result = await async_task

                match async_result:
                    case Success(validated_value):
                        current_value = validated_value
                    case Failure() as failure_result:
                        self._handle_validation_failure(failure_result, field_name, current_value, field_path, errors)
                        return
            except TimeoutError:
                raise
            except Exception as e:  # noqa: BLE001
                # Convert exception to validation error
                error = ValidationError(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=f'Unexpected error in validator: {e!s}',
                    path=field_path,
                    context={'field': field_name, 'error': str(e)},
                )
                errors.append(error)
                return

        validated_data[field_name] = current_value

    async def _run_async_validators(
        self,
        async_validators: list[Callable[[Any], Any]],
        value: Any,  # noqa: ANN401
    ) -> Maybe[Any]:
        """Run async validators sequentially on a value.

        Args:
            async_validators: List of async validator functions
            value: Value to validate

        Returns:
            Maybe with final validated value or first error

        """
        current_value = value
        for validator in async_validators:
            try:
                result = await validator(current_value)
                match result:
                    case Success(validated_value):
                        current_value = validated_value
                    case Failure() as failure:
                        return failure
            except (asyncio.CancelledError, KeyboardInterrupt, SystemExit):
                # Never swallow cancellation or shutdown signals
                raise
            except Exception as e:  # noqa: BLE001
                return Maybe.failure(f'Unexpected error in validator: {e!s}')

        return Maybe.success(current_value)

    def _check_extra_fields(self, data: dict[str, Any], path: str, errors: list[ValidationError]) -> None:
        """Check for extra fields in strict mode and add errors.

        Args:
            data: Input data dictionary
            path: Current field path
            errors: List to accumulate errors

        """
        if not self.strict:
            return

        extra_fields = set(data.keys()) - set(self.fields.keys())
        for field_name in extra_fields:
            error = ValidationError(
                code=ErrorCode.VALIDATION_ERROR,
                message=f'Unexpected field: {field_name}',
                path=f'{path}.{field_name}' if path else f'.{field_name}',
                context={'field': field_name},
            )
            errors.append(error)

    def _handle_missing_field(
        self,
        field_name: str,
        field_def: Field,
        field_path: str,
        errors: list[ValidationError],
    ) -> None:
        """Handle missing field by adding error if required.

        Args:
            field_name: Name of the missing field
            field_def: Field definition
            field_path: Full path to the field
            errors: List to accumulate errors

        """
        if not field_def.required:
            return

        error = ValidationError(
            code=ErrorCode.VALIDATION_ERROR,
            message=f'Required field missing: {field_name}',
            path=field_path,
            context={'field': field_name, 'required': True},
        )
        errors.append(error)

    def _parse_and_validate_field(  # noqa: PLR0913
        self,
        field_name: str,
        field_def: Field,
        raw_value: Any,  # noqa: ANN401
        field_path: str,
        validated_data: dict[str, Any],
        errors: list[ValidationError],
    ) -> None:
        """Parse and validate a single field value.

        This method parses the raw field value and optionally applies a validator,
        adding the result to validated_data or accumulating errors.

        Args:
            field_name: Name of the field
            field_def: Field definition with parser and validator
            raw_value: Raw input value to parse
            field_path: Full path to the field
            validated_data: Dictionary to accumulate validated values
            errors: List to accumulate errors

        """
        parse_result = field_def.parser(raw_value)

        match parse_result:
            case Success(parsed_value):
                self._apply_validator_if_present(
                    field_name, field_def, parsed_value, field_path, validated_data, errors
                )
            case Failure() as failure_result:
                self._handle_parse_failure(failure_result, field_name, raw_value, field_path, errors)

    def _apply_validator_if_present(  # noqa: PLR0913
        self,
        field_name: str,
        field_def: Field,
        parsed_value: Any,  # noqa: ANN401
        field_path: str,
        validated_data: dict[str, Any],
        errors: list[ValidationError],
    ) -> None:
        """Apply validators to parsed value if validators are present.

        This method handles both the new validators list and the deprecated
        single validator for backward compatibility.

        Args:
            field_name: Name of the field
            field_def: Field definition with optional validators
            parsed_value: Successfully parsed value
            field_path: Full path to the field
            validated_data: Dictionary to accumulate validated values
            errors: List to accumulate errors

        """
        # Combine validators and validator into a single list
        validators_to_apply = []
        if field_def.validators:
            validators_to_apply.extend(field_def.validators)
        elif field_def.validator:
            # Backward compatibility: convert single validator to list
            validators_to_apply.append(field_def.validator)

        if not validators_to_apply:
            validated_data[field_name] = parsed_value
            return

        # Apply validators sequentially (sync validators only)
        current_value = parsed_value
        for validator in validators_to_apply:
            # Skip async validators in sync validation
            if inspect.iscoroutinefunction(validator):
                continue

            validation_result = validator(current_value)
            match validation_result:
                case Success(validated_value):
                    current_value = validated_value
                case Failure() as failure_result:
                    self._handle_validation_failure(failure_result, field_name, current_value, field_path, errors)
                    return

        validated_data[field_name] = current_value

    def _handle_parse_failure(
        self,
        failure_result: Failure[Any],
        field_name: str,
        raw_value: Any,  # noqa: ANN401
        field_path: str,
        errors: list[ValidationError],
    ) -> None:
        """Handle parser failure by extracting and accumulating errors.

        Args:
            failure_result: Failure result from parser
            field_name: Name of the field
            raw_value: Raw input value that failed to parse
            field_path: Full path to the field
            errors: List to accumulate errors

        """
        error_msg = failure_result._validation_error  # noqa: SLF001
        nested_errors = self._extract_errors(error_msg, field_path, {'value': raw_value, 'field': field_name})
        errors.extend(nested_errors)

    def _handle_validation_failure(
        self,
        failure_result: Failure[Any],
        field_name: str,
        parsed_value: Any,  # noqa: ANN401
        field_path: str,
        errors: list[ValidationError],
    ) -> None:
        """Handle validator failure by extracting and accumulating errors.

        Args:
            failure_result: Failure result from validator
            field_name: Name of the field
            parsed_value: Parsed value that failed validation
            field_path: Full path to the field
            errors: List to accumulate errors

        """
        error_msg = failure_result._validation_error  # noqa: SLF001
        nested_errors = self._extract_errors(error_msg, field_path, {'value': parsed_value, 'field': field_name})
        errors.extend(nested_errors)

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
                return [self._create_single_error(error_msg, path, context)]

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
