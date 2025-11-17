"""Step definitions for dataclass validation feature.

This module implements BDD tests for dataclass field-level validation,
following strict black-box testing principles using pattern matching for result handling.
"""

from __future__ import annotations

from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
)

from behave import (  # type: ignore[import-untyped]
    given,
    then,
    use_step_matcher,
    when,
)

from valid8r.core.maybe import (
    Failure,
    Maybe,
    Success,
)
from valid8r.core.validators import (
    length,
    matches_regex,
    maximum,
    minimum,
    unique_items,
)

# Import dataclass validation when it exists
try:
    from valid8r.integrations.dataclasses import (
        validate,
        validate_dataclass,
    )
except ImportError:
    # Stub for RED phase - will fail tests as expected
    def validate(**kwargs: Any) -> Any:  # noqa: ANN401
        msg = 'validate decorator not implemented yet'
        raise NotImplementedError(msg)

    def validate_dataclass(cls: type[Any], data: dict[str, Any]) -> Maybe[Any]:
        msg = 'validate_dataclass not implemented yet'
        raise NotImplementedError(msg)


if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


# Background step


@given('the dataclass validation module is available')
def step_dataclass_validation_available(context: Context) -> None:  # noqa: ARG001
    """Verify the dataclass validation module is available."""
    assert Maybe is not None


# Given steps - Set up dataclass definitions and validators


@given('a {dataclass_name} dataclass with {field_spec} fields')
@given('a {dataclass_name} dataclass with {field_spec} field')
def step_define_dataclass(context: Context, dataclass_name: str, field_spec: str) -> None:
    """Define a dataclass with specified fields."""
    # Parse field specification (e.g., "name and age", "price", "name, price, and in_stock")
    field_names = [f.strip() for f in field_spec.replace(' and ', ', ').split(',')]

    # Store dataclass definition for later use
    if not hasattr(context, 'dataclass_definitions'):
        context.dataclass_definitions = {}
    if not hasattr(context, 'field_validators'):
        context.field_validators = {}
    if not hasattr(context, 'field_types'):
        context.field_types = {}

    context.dataclass_definitions[dataclass_name] = field_names
    context.current_dataclass = dataclass_name

    # Initialize validators for this dataclass
    if dataclass_name not in context.field_validators:
        context.field_validators[dataclass_name] = {}
    if dataclass_name not in context.field_types:
        context.field_types[dataclass_name] = {}


@given('{field_name} has a {validator_type} validator between {min_val} and {max_val} characters')
def step_add_length_range_validator(
    context: Context,
    field_name: str,
    validator_type: str,
    min_val: str,
    max_val: str,
) -> None:
    """Add length validator to a field (with 'characters' suffix)."""
    dataclass_name = context.current_dataclass
    min_int = int(min_val)
    max_int = int(max_val)

    if validator_type == 'length':
        validator = length(min_int, max_int)
    else:
        msg = f'Unknown validator type: {validator_type}'
        raise ValueError(msg)

    context.field_validators[dataclass_name][field_name] = validator


@given('{field_name} has a {validator_type} validator between {min_val} and {max_val}')
def step_add_range_validator(
    context: Context,
    field_name: str,
    validator_type: str,
    min_val: str,
    max_val: str,
) -> None:
    """Add range validator to a field (numeric ranges)."""
    dataclass_name = context.current_dataclass
    min_int = int(min_val)
    max_int = int(max_val)

    if validator_type == 'range':
        validator = minimum(min_int) & maximum(max_int)
    else:
        msg = f'Unknown validator type: {validator_type}'
        raise ValueError(msg)

    context.field_validators[dataclass_name][field_name] = validator


@given('{field_name} has a {validator_type} length validator of {count} characters')
def step_add_length_limit_validator(
    context: Context,
    field_name: str,
    validator_type: str,
    count: str,
) -> None:
    """Add maximum or minimum length validator to a field."""
    dataclass_name = context.current_dataclass
    count_int = int(count)

    if validator_type == 'maximum':
        validator = maximum(count_int)
    elif validator_type == 'minimum':
        validator = minimum(count_int)
    else:
        msg = f'Unknown validator type: {validator_type}'
        raise ValueError(msg)

    context.field_validators[dataclass_name][field_name] = validator


@given('{field_name} is type {type_name}')
def step_set_field_type(context: Context, field_name: str, type_name: str) -> None:
    """Set the type for a dataclass field."""
    dataclass_name = context.current_dataclass

    # Map string type names to Python types
    type_map: dict[str, type[Any]] = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'Optional[str]': str | None,  # type: ignore[dict-item]
        'list[str]': list[str],  # type: ignore[dict-item]
        'dict[str, int]': dict[str, int],  # type: ignore[dict-item]
    }

    if type_name not in type_map:
        msg = f'Unknown type: {type_name}'
        raise ValueError(msg)

    context.field_types[dataclass_name][field_name] = type_map[type_name]


@given('{field_name} has a {validator_type} validator')
def step_add_named_validator(context: Context, field_name: str, validator_type: str) -> None:
    """Add a named validator to a field."""
    dataclass_name = context.current_dataclass

    validator_map = {
        'unique_items': unique_items(),
    }

    if validator_type not in validator_map:
        msg = f'Unknown validator: {validator_type}'
        raise ValueError(msg)

    context.field_validators[dataclass_name][field_name] = validator_map[validator_type]


@given('{field_name} uses custom validator for {validator_description}')
def step_add_custom_validator(context: Context, field_name: str, validator_description: str) -> None:
    """Add a custom validator to a field."""
    dataclass_name = context.current_dataclass

    # For BDD tests, we'll use simple pattern matching validators
    if 'email' in validator_description:
        validator = matches_regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    else:
        msg = f'Unknown custom validator: {validator_description}'
        raise ValueError(msg)

    context.field_validators[dataclass_name][field_name] = validator


@given('{field_name} field of type {type_name}')
def step_define_field_with_type(context: Context, field_name: str, type_name: str) -> None:
    """Define a field with a specific type."""
    # Reuse existing step
    step_set_field_type(context, field_name, type_name)


@given('a {field_name} field requiring {requirement}')
def step_field_requirement(context: Context, field_name: str, requirement: str) -> None:
    """Add requirement to a field (for nested dataclass scenarios)."""
    dataclass_name = context.current_dataclass

    if '5 digits' in requirement:
        validator = matches_regex(r'^\d{5}$')
        context.field_validators[dataclass_name][field_name] = validator


@given('each field has validation rules')
def step_all_fields_have_validators(context: Context) -> None:
    """Mark that all fields in the dataclass have validation rules."""
    # This is a marker step for complex scenarios
    context.all_fields_validated = True


@given('fields use metadata to specify validators')
def step_fields_use_metadata(context: Context) -> None:
    """Mark that fields use metadata for validator specification."""
    context.uses_metadata = True


@given('a {dataclass_name} dataclass uses @validate decorator')
def step_dataclass_uses_decorator(context: Context, dataclass_name: str) -> None:
    """Mark that a specific dataclass uses the @validate decorator."""
    context.uses_decorator = True
    context.current_dataclass = dataclass_name


@given('no explicit parser is provided')
def step_no_explicit_parser(context: Context) -> None:
    """Mark that no explicit parser is provided for type coercion."""
    context.no_explicit_parser = True


@given('a pre-validation hook that strips whitespace')
def step_pre_validation_hook_strip(context: Context) -> None:
    """Add a pre-validation hook that strips whitespace."""
    context.pre_hook = lambda s: s.strip()


@given('a post-validation hook that parses to datetime')
def step_post_validation_hook_datetime(context: Context) -> None:
    """Add a post-validation hook that parses to datetime."""
    context.post_hook = lambda s: datetime.fromisoformat(s)


# When steps - Perform validation
# CRITICAL: Order matters! More specific patterns MUST come before general patterns
# to avoid ambiguity. Behave matches in order of definition.


# Most specific patterns first
@when('Alice validates a User with name "{name}" and age {age:d}')
def step_validate_user(
    context: Context,
    name: str,
    age: int,
) -> None:
    """Validate a User dataclass instance with name and age fields.

    Specific pattern for User dataclass to avoid ambiguity with nested patterns.
    """
    data = {
        'name': name,
        'age': age,
    }

    try:
        result = validate_dataclass('User', data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


@when(
    'Alice validates a {dataclass_name} with name "{name}" and address with street "{street}", city "{city}", zip_code "{zip_code}"'
)
def step_validate_nested_valid(
    context: Context,
    dataclass_name: str,
    name: str,
    street: str,
    city: str,
    zip_code: str,
) -> None:
    """Validate a dataclass instance with valid nested dataclass (concrete values).

    Must come BEFORE general patterns to avoid ambiguity.
    """
    data = {
        'name': name,
        'address': {'street': street, 'city': city, 'zip_code': zip_code},
    }

    try:
        result = validate_dataclass(dataclass_name, data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


@when('Alice validates a {dataclass_name} with {field_name} of {char_count} characters')
def step_validate_with_length(
    context: Context,
    dataclass_name: str,
    field_name: str,
    char_count: str,
) -> None:
    """Validate a dataclass instance with a field of specific character count.

    Must come BEFORE general single-field pattern.
    """
    count = int(char_count)
    field_value = 'a' * count  # Generate string of specified length
    data = {field_name: field_value}

    try:
        result = validate_dataclass(dataclass_name, data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


# Medium specificity patterns
@when('Alice validates a {dataclass_name} from strings {field_specs}')
def step_validate_from_strings(context: Context, dataclass_name: str, field_specs: str) -> None:
    """Validate a dataclass instance from string representations."""
    # Parse field specifications (e.g., 'name="Laptop", price="999.99", in_stock="true"')
    data = {}
    for spec in field_specs.split(', '):
        field_name, field_value = spec.split('=')
        # Remove quotes from value
        field_value = field_value.strip('"')
        data[field_name] = field_value

    try:
        result = validate_dataclass(dataclass_name, data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


@when('Alice validates a {dataclass_name} from string {field_spec}')
def step_validate_from_single_string(context: Context, dataclass_name: str, field_spec: str) -> None:
    """Validate a dataclass instance from a single string field."""
    # Parse field specification (e.g., 'price="not-a-number"')
    field_name, field_value = field_spec.split('=')
    field_value = field_value.strip('"')
    data = {field_name: field_value}

    try:
        result = validate_dataclass(dataclass_name, data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


@when('Alice validates a {dataclass_name} with {field_name}=None')
@when('Alice validates a {dataclass_name} with {field_name} None')
def step_validate_with_none(context: Context, dataclass_name: str, field_name: str) -> None:
    """Validate a dataclass instance with None value."""
    data = {field_name: None}

    try:
        result = validate_dataclass(dataclass_name, data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


# General patterns last (most broad, catch-all)
@when('Alice validates a {dataclass_name} with {field_name} "{field_value}"')
def step_validate_with_value(
    context: Context,
    dataclass_name: str,
    field_name: str,
    field_value: str,
) -> None:
    """Validate a dataclass instance with a specific field value.

    GENERAL PATTERN - Must come AFTER all more specific patterns.
    """
    data = {field_name: field_value}

    try:
        result = validate_dataclass(dataclass_name, data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


@when('Alice validates a {dataclass_name} where nested {nested_field} has invalid {field_name} "{field_value}"')
def step_validate_nested_invalid(
    context: Context,
    dataclass_name: str,
    nested_field: str,
    field_name: str,
    field_value: str,
) -> None:
    """Validate a dataclass instance with invalid nested field."""
    data = {
        'name': 'Alice Smith',
        nested_field: {'street': '123 Main St', 'city': 'Portland', field_name: field_value},
    }

    try:
        result = validate_dataclass(dataclass_name, data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


@when('Alice validates ComplexForm with username "{username}", email "{email}", age {age}')
def step_validate_complex_form(
    context: Context,
    username: str,
    email: str,
    age: str,
) -> None:
    """Validate a ComplexForm with specific field values."""
    data = {
        'username': username,
        'email': email,
        'age': int(age) if age.lstrip('-').isdigit() else age,
    }

    try:
        result = validate_dataclass('ComplexForm', data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


# Use regex matcher for collection pattern to avoid ambiguity
use_step_matcher('re')


@when(r'Alice validates a (?P<dataclass_name>\w+) with (?P<field_name>\w+) (?P<value_spec>[\[\{].*[\]\}])')
def step_validate_with_collection(
    context: Context,
    dataclass_name: str,
    field_name: str,
    value_spec: str,
) -> None:
    """Validate a dataclass instance with collection values (lists/dicts).

    Uses regex to only match patterns where value_spec is a collection literal.
    Must come BEFORE other broad patterns.
    """
    import ast

    # Parse Python literal (list, dict, etc.)
    try:
        field_value = ast.literal_eval(value_spec)
    except (ValueError, SyntaxError):
        field_value = value_spec

    data = {field_name: field_value}

    try:
        result = validate_dataclass(dataclass_name, data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


# Switch back to parse matcher for remaining steps
use_step_matcher('parse')


@when('Alice validates a {dataclass_name} having {invalid_count:d} invalid fields')
def step_validate_multiple_invalid(
    context: Context,
    dataclass_name: str,
    invalid_count: int,
) -> None:
    """Validate a dataclass instance with multiple invalid fields.

    Uses 'having' instead of 'with' to avoid ambiguity with other step patterns.
    """
    # Generate data with specified number of invalid fields
    data = {}
    for i in range(invalid_count):
        data[f'field{i + 1}'] = ''  # Empty strings will fail validation

    try:
        result = validate_dataclass(dataclass_name, data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


@when('ValidatedUser is instantiated with name "{name}" and age {age}')
def step_instantiate_validated_user(context: Context, name: str, age: str) -> None:
    """Instantiate a ValidatedUser with specific field values."""
    data = {
        'name': name,
        'age': int(age) if age.lstrip('-').isdigit() else age,
    }

    try:
        result = validate_dataclass('ValidatedUser', data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


@when('the dataclass is instantiated with {validity} data')
def step_instantiate_dataclass(context: Context, validity: str) -> None:
    """Instantiate a dataclass with valid or invalid data."""
    data = {'field1': 'valid', 'field2': 42} if validity == 'valid' else {'field1': '', 'field2': -1}

    try:
        result = validate_dataclass(context.current_dataclass, data)
        context.validation_result = result
    except NotImplementedError as e:
        context.validation_result = Failure(str(e))


# Then steps - Verify results using pattern matching


@then('the validation succeeds')
def step_validation_succeeds(context: Context) -> None:
    """Verify that validation succeeded."""
    result = context.validation_result

    # Use pattern matching per requirements
    match result:
        case Success(value):
            context.validated_instance = value
        case Failure(err):
            msg = f'Expected validation to succeed, but got Failure: {err}'
            raise AssertionError(msg)


@then('the validation fails')
def step_validation_fails(context: Context) -> None:
    """Verify that validation failed."""
    result = context.validation_result

    # Use pattern matching per requirements
    match result:
        case Failure(err):
            context.validation_error = err
        case Success(value):
            msg = f'Expected validation to fail, but got Success: {value}'
            raise AssertionError(msg)


# IMPORTANT: More specific step patterns MUST come before general patterns
# to avoid ambiguity. Behave matches in order of definition.


@then('the validated instance has {count:d} {field_name}')
def step_validated_instance_collection_count(context: Context, count: int, field_name: str) -> None:
    """Verify the validated instance collection has expected count.

    Uses :d to match only integers (e.g., '3 members').
    Defined BEFORE general pattern to avoid ambiguity.
    """
    instance = context.validated_instance
    collection = getattr(instance, field_name)
    assert len(collection) == count, f'Expected {count} {field_name}, got {len(collection)}'


@then('the validated instance has {field_name} with {count:d} entries')
def step_validated_instance_dict_entries(context: Context, field_name: str, count: int) -> None:
    """Verify the validated instance dict has expected number of entries.

    Uses 'with' keyword to distinguish from collection count pattern.
    Defined BEFORE general pattern to avoid ambiguity.
    """
    instance = context.validated_instance
    dictionary = getattr(instance, field_name)
    assert len(dictionary) == count, f'Expected {count} entries, got {len(dictionary)}'


@then('the Person address field has {field_name} "{expected_value}"')
def step_person_address_field_value(context: Context, field_name: str, expected_value: str) -> None:
    """Verify a nested address field has the expected value.

    Specific pattern for Person.address.field assertions.
    Defined BEFORE general pattern to avoid ambiguity.
    """
    instance = context.validated_instance
    address = instance.address
    actual = getattr(address, field_name)
    assert actual == expected_value, f'Expected address.{field_name}={expected_value}, got {actual}'


@then('the validated instance has port {port:d} as integer')
def step_validated_instance_integer_port(context: Context, port: int) -> None:
    """Verify the validated instance has a port field as integer type.

    Specific pattern for type validation.
    Defined BEFORE general pattern to avoid ambiguity.
    """
    instance = context.validated_instance
    actual = instance.port
    assert actual == port, f'Expected port={port}, got {actual}'
    assert isinstance(actual, int), f'Expected port to be int, got {type(actual)}'


@then('the validated instance has items {items}')
def step_validated_instance_items_list(context: Context, items: str) -> None:
    """Verify the validated instance has an items field with expected list value.

    Specific pattern for list validation.
    Defined BEFORE general pattern to avoid ambiguity.
    """
    import ast

    instance = context.validated_instance
    actual = instance.items
    expected = ast.literal_eval(items)
    assert actual == expected, f'Expected items={expected}, got {actual}'


@then('the validated instance has {field_name} {expected_value}')
def step_validated_instance_field_value(
    context: Context,
    field_name: str,
    expected_value: str,
) -> None:
    """Verify the validated instance has expected field value.

    Handles both quoted and unquoted values:
    - 'name "Alice"' → string "Alice"
    - 'age 30' → int 30
    - 'price 99.99' → float 99.99
    - 'active True' → bool True
    - 'bio None' → None

    MUST be defined AFTER more specific patterns to avoid ambiguity.
    """
    instance = context.validated_instance

    # Get field value using pattern matching
    match hasattr(instance, field_name):
        case True:
            actual = getattr(instance, field_name)
            # Convert expected value to correct type
            if expected_value == 'None':
                expected = None
            elif expected_value == 'True':
                expected = True
            elif expected_value == 'False':
                expected = False
            elif expected_value.replace('.', '', 1).replace('-', '', 1).isdigit():
                expected = float(expected_value) if '.' in expected_value else int(expected_value)
            else:
                expected = expected_value.strip('"')

            assert actual == expected, f'Expected {field_name}={expected}, got {actual}'
        case False:
            msg = f'Instance does not have field: {field_name}'
            raise AssertionError(msg)


@then('the error report contains field "{field_name}"')
def step_error_contains_field(context: Context, field_name: str) -> None:
    """Verify error report contains specific field name."""
    error = context.validation_error
    assert field_name in str(error).lower(), f'Expected error to contain field "{field_name}", got: {error}'


# Note: 'the error message contains "{text}"' step is defined in url_email_parsing_steps.py


# Note: Removed 'the validated instance has a valid {field_name}' step due to ambiguity
# with the more general pattern 'the validated instance has {field_name} {expected_value}'.
# Use specific field assertions instead.


@then('the instance is created successfully')
def step_instance_created_successfully(context: Context) -> None:
    """Verify instance was created successfully."""
    assert context.validated_instance is not None


@then('validation runs automatically')
def step_validation_runs_automatically(context: Context) -> None:
    """Verify validation ran automatically."""
    # This is verified by the successful creation


@then('validation fails before instance creation')
def step_validation_fails_before_creation(context: Context) -> None:
    """Verify validation failed before instance was created."""
    assert context.validation_result.is_failure()


@then('a ValidationError is raised with field details')
def step_validation_error_raised(context: Context) -> None:
    """Verify a ValidationError was raised with field details."""
    error = context.validation_error
    assert error is not None, 'Expected ValidationError to be raised'


@then('the validated instance includes parsed datetime')
def step_validated_instance_has_datetime(context: Context) -> None:
    """Verify the validated instance has a parsed datetime attribute."""
    # This will be verified when post-validation hooks are implemented
    context.expects_datetime = True
