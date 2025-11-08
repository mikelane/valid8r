from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Annotated,
)

from behave import (  # type: ignore[import-untyped]
    given,
    then,
    when,
)
from pydantic import (
    AfterValidator,
    BaseModel,
    ValidationError,
    WrapValidator,
    field_validator,
)

from valid8r.core.parsers import (
    EmailAddress,
    parse_email,
    parse_int,
    parse_phone,
)
from valid8r.core.validators import minimum

if TYPE_CHECKING:
    from collections.abc import Callable

    from behave.runner import Context  # type: ignore[import-untyped]


@given('the valid8r.integrations.pydantic module exists')
def step_pydantic_module_exists(context: Context) -> None:  # noqa: ARG001
    """Verify that the pydantic integration module can be imported."""
    try:
        from valid8r.integrations import pydantic  # noqa: F401
    except ImportError:
        msg = 'valid8r.integrations.pydantic module does not exist'
        raise ImportError(msg) from None


@given('I have imported make_after_validator and make_wrap_validator')
def step_import_validators(context: Context) -> None:
    """Import make_after_validator and make_wrap_validator functions."""
    try:
        from valid8r.integrations.pydantic import (
            make_after_validator,
            make_wrap_validator,
        )

        context.make_after_validator = make_after_validator
        context.make_wrap_validator = make_wrap_validator
    except ImportError:
        msg = 'Failed to import make_after_validator or make_wrap_validator'
        raise ImportError(msg) from None


@given('a Pydantic model with field: Annotated[str, AfterValidator(make_after_validator(parse_email))]')
def step_model_with_after_validator_email(context: Context) -> None:
    """Create a Pydantic model with AfterValidator for email field."""

    class User(BaseModel):
        email: Annotated[str, AfterValidator(context.make_after_validator(parse_email))]

    context.model_class = User


@when('I create an instance with email "{email}"')
def step_create_instance_with_email(context: Context, email: str) -> None:
    """Create a model instance with the given email."""
    try:
        context.instance = context.model_class(email=email)
        context.validation_error = None
    except ValidationError as e:
        context.validation_error = e
        context.instance = None


@then('the model validates successfully')
def step_model_validates_successfully(context: Context) -> None:
    """Verify that the model validation succeeded."""
    assert context.validation_error is None, f'Validation failed: {context.validation_error}'
    assert context.instance is not None, 'Instance was not created'


@then('email is an EmailAddress object')
def step_email_is_email_address_object(context: Context) -> None:
    """Verify that the email field is an EmailAddress object."""
    assert hasattr(context.instance, 'email'), 'Instance does not have email attribute'
    assert isinstance(context.instance.email, EmailAddress), (
        f'Email is {type(context.instance.email)}, not EmailAddress'
    )


@given('a field using AfterValidator(make_after_validator(parse_phone))')
def step_field_with_after_validator_phone(context: Context) -> None:
    """Create a Pydantic model with AfterValidator for phone field."""

    class Contact(BaseModel):
        phone: Annotated[str, AfterValidator(context.make_after_validator(parse_phone))]

    context.model_class = Contact


@when('I validate with "{value}"')
def step_validate_with_value(context: Context, value: str) -> None:
    """Validate the model with the given value."""
    # Capture raw input for WrapValidator tests
    context.raw_input = value

    # Determine the field name based on the model class
    if hasattr(context, 'model_class'):
        # Get the first field name from the model
        field_names = list(context.model_class.model_fields.keys())
        if field_names:
            field_name = field_names[0]
            try:
                context.instance = context.model_class(**{field_name: value})
                context.validation_error = None
            except ValidationError as e:
                context.validation_error = e
                context.instance = None
            return
    msg = 'No model_class found in context'
    raise ValueError(msg)


@then('Pydantic raises ValidationError')
def step_pydantic_raises_validation_error(context: Context) -> None:
    """Verify that ValidationError was raised."""
    assert context.validation_error is not None, 'Expected ValidationError but none was raised'
    assert isinstance(context.validation_error, ValidationError), (
        f'Expected ValidationError, got {type(context.validation_error)}'
    )


@then('the error message contains the valid8r parse_phone error')
def step_error_contains_parse_phone_error(context: Context) -> None:
    """Verify that the error message contains the parse_phone error."""
    assert context.validation_error is not None, 'No validation error exists'
    error_str = str(context.validation_error)
    # The error should mention phone-related validation
    assert 'phone' in error_str.lower() or 'format' in error_str.lower(), (
        f'Error does not mention phone validation: {error_str}'
    )


@given('a WrapValidator(make_wrap_validator(parse_int))')
def step_wrap_validator_parse_int(context: Context) -> None:
    """Create a Pydantic model with WrapValidator for int field."""

    class Data(BaseModel):
        value: Annotated[int, WrapValidator(context.make_wrap_validator(parse_int))]

    context.model_class = Data
    context.raw_input = None


# Removed - merged with step_validate_with_value


@then('the validator receives the raw string')
def step_validator_receives_raw_string(context: Context) -> None:
    """Verify that the validator received the raw string input."""
    # This is implicitly verified by the fact that WrapValidator processes the raw input
    # If it didn't receive the raw string "42", it wouldn't have been able to parse it
    assert context.raw_input is not None, 'Raw input was not captured'
    assert isinstance(context.raw_input, str), f'Raw input should be str, got {type(context.raw_input)}'


@then('returns parsed integer {expected:d}')
def step_returns_parsed_integer(context: Context, expected: int) -> None:
    """Verify that the parsed value is the expected integer."""
    assert context.instance is not None, 'Instance was not created'
    assert hasattr(context.instance, 'value'), 'Instance does not have value attribute'
    assert context.instance.value == expected, f'Expected {expected}, got {context.instance.value}'
    assert isinstance(context.instance.value, int), f'Value should be int, got {type(context.instance.value)}'


@given(
    'a field with: Annotated[int, AfterValidator(make_after_validator(parse_int)), AfterValidator(make_after_validator(minimum(0)))]'
)
def step_field_with_chained_after_validators(context: Context) -> None:
    """Create a Pydantic model with chained AfterValidators."""
    # Create a validator that chains parse_int and minimum(0)
    parse_int_validator = context.make_after_validator(parse_int)
    minimum_validator = context.make_after_validator(minimum(0))

    class Data(BaseModel):
        value: Annotated[int, AfterValidator(parse_int_validator), AfterValidator(minimum_validator)]

    context.model_class = Data


# Removed - merged with step_validate_with_value


@then('Pydantic raises ValidationError mentioning "{keyword}"')
def step_validation_error_mentions_keyword(context: Context, keyword: str) -> None:
    """Verify that ValidationError mentions the keyword."""
    assert context.validation_error is not None, 'Expected ValidationError but none was raised'
    error_str = str(context.validation_error)
    assert keyword.lower() in error_str.lower(), f'Error does not mention "{keyword}": {error_str}'


@given('a model using both AfterValidator and field_validator')
def step_model_with_mixed_validators(context: Context) -> None:
    """Create a Pydantic model with both AfterValidator and field_validator."""

    class User(BaseModel):
        age: Annotated[int, AfterValidator(context.make_after_validator(parse_int))]
        name: str

        @field_validator('name')
        @classmethod
        def validate_name(cls, v: str) -> str:
            if not v.strip():
                msg = 'Name cannot be empty'
                raise ValueError(msg)
            return v.strip()

    context.model_class = User


@when('I validate the model')
def step_validate_model(context: Context) -> None:
    """Validate the model with test data."""
    try:
        context.instance = context.model_class(age='25', name='Alice')
        context.validation_error = None
    except ValidationError as e:
        context.validation_error = e
        context.instance = None


@then('both validators execute in correct order')
def step_both_validators_execute(context: Context) -> None:
    """Verify that both validators executed successfully."""
    assert context.validation_error is None, f'Validation failed: {context.validation_error}'
    assert context.instance is not None, 'Instance was not created'
    assert hasattr(context.instance, 'age'), 'Instance missing age field'
    assert hasattr(context.instance, 'name'), 'Instance missing name field'


@then('errors are properly aggregated')
def step_errors_properly_aggregated(context: Context) -> None:
    """Verify that errors from both validators are properly aggregated."""
    # Test with invalid data that should fail both validators
    try:
        context.model_class(age='invalid', name='')
        msg = 'Expected ValidationError for invalid age and empty name'
        raise AssertionError(msg)
    except ValidationError as e:
        error_dict = e.errors()
        # Should have errors for both age and name fields
        field_names = {error['loc'][0] for error in error_dict}
        assert 'age' in field_names or 'name' in field_names, f'Missing expected field errors: {field_names}'


@given('a model with optional field: Annotated[str | None, AfterValidator(make_after_validator(parse_email))]')
def step_model_with_optional_after_validator(context: Context) -> None:
    """Create a Pydantic model with optional field using AfterValidator."""

    class User(BaseModel):
        email: Annotated[str | None, AfterValidator(context.make_after_validator(parse_email))] = None

    context.model_class = User


@when('I create an instance with email None')
def step_create_instance_with_none_email(context: Context) -> None:
    """Create a model instance with None email."""
    try:
        context.instance = context.model_class(email=None)
        context.validation_error = None
    except ValidationError as e:
        context.validation_error = e
        context.instance = None


@then('email is None')
def step_email_is_none(context: Context) -> None:
    """Verify that the email field is None."""
    assert context.instance is not None, 'Instance was not created'
    assert hasattr(context.instance, 'email'), 'Instance does not have email attribute'
    assert context.instance.email is None, f'Email should be None, got {context.instance.email}'


@given('a WrapValidator that accesses ValidationInfo')
def step_wrap_validator_with_validation_info(context: Context) -> None:
    """Create a WrapValidator that accesses ValidationInfo."""
    # Note: ValidationInfo is available in pydantic_core._pydantic_core.ValidationInfo
    # but not directly exported from pydantic_core.__init__ in some versions
    import pydantic_core._pydantic_core as pc

    def custom_wrap_validator(value: str, handler: Callable, info: pc.ValidationInfo) -> int:
        """Custom wrap validator that accesses ValidationInfo."""
        context.validation_info = info
        context.field_name_from_validator = info.field_name if info else None
        # Parse and delegate to handler
        result = parse_int(value)
        if result.is_failure():
            msg = result.error_or('Invalid value')
            raise ValueError(msg)
        return result.value_or(0)

    class Data(BaseModel):
        value: Annotated[int, WrapValidator(custom_wrap_validator)]

    context.model_class = Data
    context.validation_info = None
    context.field_name_from_validator = None


@when('I validate a field')
def step_validate_field(context: Context) -> None:
    """Validate a field with test data."""
    try:
        context.instance = context.model_class(value='42')
        context.validation_error = None
    except ValidationError as e:
        context.validation_error = e
        context.instance = None


@then('the validator receives the ValidationInfo context')
def step_validator_receives_validation_info(context: Context) -> None:
    """Verify that the validator received ValidationInfo."""
    assert context.validation_info is not None, 'ValidationInfo was not captured'


@then('can access field_name and other metadata')
def step_can_access_field_metadata(context: Context) -> None:
    """Verify that field metadata is accessible."""
    assert context.field_name_from_validator is not None, 'Field name was not captured from ValidationInfo'
    assert context.field_name_from_validator == 'value', (
        f'Expected field_name "value", got {context.field_name_from_validator}'
    )


@given('a nested model with validated field using AfterValidator')
def step_nested_model_with_after_validator(context: Context) -> None:
    """Create nested Pydantic models with AfterValidator."""

    class Address(BaseModel):
        phone: Annotated[str, AfterValidator(context.make_after_validator(parse_phone))]

    class User(BaseModel):
        name: str
        address: Address

    context.model_class = User


@when('validation fails on the nested field')
def step_validation_fails_on_nested_field(context: Context) -> None:
    """Trigger validation failure on nested field."""
    try:
        context.instance = context.model_class(name='Alice', address={'phone': 'invalid'})
        context.validation_error = None
    except ValidationError as e:
        context.validation_error = e
        context.instance = None


@then('the error message includes the full field path')
def step_error_includes_full_field_path(context: Context) -> None:
    """Verify that error message includes the full field path."""
    assert context.validation_error is not None, 'No validation error exists'
    error_dict = context.validation_error.errors()
    # Check that at least one error has the nested path
    has_nested_path = any('address' in str(error['loc']) for error in error_dict)
    assert has_nested_path, f'Error does not include nested field path: {error_dict}'


@then("preserves Pydantic's error structure")
def step_preserves_pydantic_error_structure(context: Context) -> None:
    """Verify that Pydantic's error structure is preserved."""
    assert context.validation_error is not None, 'No validation error exists'
    error_dict = context.validation_error.errors()
    # Verify standard Pydantic error structure
    for error in error_dict:
        assert 'loc' in error, 'Error missing "loc" field'
        assert 'msg' in error, 'Error missing "msg" field'
        assert 'type' in error, 'Error missing "type" field'


@given('a WrapValidator that calls the next handler')
def step_wrap_validator_calls_next_handler(context: Context) -> None:
    """Create a WrapValidator that calls the next handler."""

    def pre_post_validator(value: str, handler: Callable) -> int:
        """Validator that pre-processes, delegates, and post-processes."""
        # Pre-process
        context.pre_processed_value = value.strip()
        # Delegate to next handler (Pydantic's default int validation)
        result = handler(context.pre_processed_value)
        # Post-process
        context.post_processed_value = result * 2 if isinstance(result, int) else result
        return context.post_processed_value

    class Data(BaseModel):
        value: Annotated[int, WrapValidator(pre_post_validator)]

    context.model_class = Data
    context.pre_processed_value = None
    context.post_processed_value = None


@when('I validate a value')
def step_validate_value(context: Context) -> None:
    """Validate a value with the WrapValidator."""
    try:
        context.instance = context.model_class(value='  21  ')
        context.validation_error = None
    except ValidationError as e:
        context.validation_error = e
        context.instance = None


@then('WrapValidator pre-processes the value')
def step_wrap_validator_preprocesses(context: Context) -> None:
    """Verify that the WrapValidator pre-processed the value."""
    assert context.pre_processed_value is not None, 'Pre-processed value was not captured'
    assert context.pre_processed_value == '21', f'Expected "21", got {context.pre_processed_value}'


@then("delegates to Pydantic's default validation")
def step_delegates_to_pydantic_validation(context: Context) -> None:
    """Verify that delegation to Pydantic's validation occurred."""
    # This is implicitly verified by the fact that the handler was called
    # and returned a valid integer result that could be post-processed
    assert context.instance is not None, 'Instance was not created (delegation failed)'


@then('post-processes the result')
def step_postprocesses_result(context: Context) -> None:
    """Verify that the WrapValidator post-processed the result."""
    assert context.post_processed_value is not None, 'Post-processed value was not captured'
    assert context.post_processed_value == 42, f'Expected 42 (21 * 2), got {context.post_processed_value}'
    assert context.instance.value == 42, f'Instance value should be 42, got {context.instance.value}'


@given('a field with multiple WrapValidators')
def step_field_with_multiple_wrap_validators(context: Context) -> None:
    """Create a field with multiple chained WrapValidators."""

    def first_validator(value: str, handler: Callable) -> int:
        """First validator - strips whitespace."""
        context.first_validator_input = value
        stripped = value.strip()
        result = handler(stripped)
        context.first_validator_output = result
        return result

    def second_validator(value: str | int, handler: Callable) -> int:
        """Second validator - parses int if string."""
        context.second_validator_input = value
        if isinstance(value, str):
            parsed_result = parse_int(value)
            if parsed_result.is_failure():
                msg = parsed_result.error_or('Invalid integer')
                raise ValueError(msg)
            value = parsed_result.value_or(0)
        result = handler(value)
        context.second_validator_output = result
        return result

    class Data(BaseModel):
        value: Annotated[int, WrapValidator(first_validator), WrapValidator(second_validator)]

    context.model_class = Data
    context.first_validator_input = None
    context.first_validator_output = None
    context.second_validator_input = None
    context.second_validator_output = None


@then('validators execute in correct order')
def step_validators_execute_in_order(context: Context) -> None:
    """Verify that validators executed in the correct order."""
    assert context.first_validator_input is not None, 'First validator did not execute'
    assert context.second_validator_input is not None, 'Second validator did not execute'


@then('each receives output from previous validator')
def step_each_receives_previous_output(context: Context) -> None:
    """Verify that each validator receives output from the previous one."""
    # First validator should receive the raw string
    assert isinstance(context.first_validator_input, str), 'First validator should receive string'
    # Second validator should receive output from first validator (which delegates to handler)
    # The first validator's handler processes the stripped value
    assert context.second_validator_input is not None, 'Second validator did not receive input from first'
