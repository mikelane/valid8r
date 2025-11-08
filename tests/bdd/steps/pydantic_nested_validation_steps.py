from __future__ import annotations

import json
from typing import TYPE_CHECKING

import parse  # type: ignore[import-untyped]
from behave import (  # type: ignore[import-untyped]
    given,
    register_type,
    then,
    when,
)

if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]
    from pydantic import ValidationError


# Register custom type for dictionary/JSON strings
@parse.with_pattern(r'\{.+\}')
def parse_dict_string(text: str) -> str:
    """Parse a dictionary string that starts and ends with braces."""
    return text


register_type(DictString=parse_dict_string)


@given('the valid8r.integrations.pydantic module exists')
def step_pydantic_module_exists(context: Context) -> None:  # noqa: ARG001
    """Verify that the pydantic integration module can be imported."""
    try:
        from valid8r.integrations import pydantic  # noqa: F401
    except ImportError:
        msg = 'valid8r.integrations.pydantic module does not exist'
        raise ImportError(msg) from None


@given('I have imported validator_from_parser')
def step_import_validator_from_parser(context: Context) -> None:
    """Import validator_from_parser function."""
    from valid8r.integrations.pydantic import validator_from_parser

    context.validator_from_parser = validator_from_parser


@given('a Pydantic model Address with phone field using validator_from_parser(parse_phone)')
def step_create_address_model(context: Context) -> None:
    """Create Address model with phone validation."""
    from pydantic import (
        BaseModel,
        field_validator,
    )

    from valid8r.core import parsers
    from valid8r.core.parsers import PhoneNumber  # noqa: TC001
    from valid8r.integrations.pydantic import validator_from_parser

    class Address(BaseModel):
        phone: PhoneNumber

        @field_validator('phone', mode='before')
        @classmethod
        def validate_phone(cls, v):  # noqa: ANN001, ANN206
            return validator_from_parser(parsers.parse_phone)(v)

    # Rebuild model to resolve forward references
    Address.model_rebuild()
    context.Address = Address


@given('a Pydantic model User with address: Address field')
def step_create_user_model_with_address(context: Context) -> None:
    """Create User model with nested Address field."""
    from pydantic import BaseModel

    Address = context.Address

    class User(BaseModel):
        name: str
        address: Address

    # Rebuild model to resolve forward references
    User.model_rebuild()
    context.User = User


@when('I validate the model with {data:DictString}')
def step_validate_model_with_data(context: Context, data: str) -> None:
    """Validate data using the Pydantic model stored in context."""
    from pydantic import ValidationError

    data_dict = json.loads(data)

    # Try to determine which model to use based on what's in context
    model_class = None
    if hasattr(context, 'User'):
        model_class = context.User
    elif hasattr(context, 'Order'):
        model_class = context.Order
    elif hasattr(context, 'Config'):
        model_class = context.Config
    elif hasattr(context, 'Company'):
        model_class = context.Company

    try:
        context.validated_model = model_class(**data_dict)
        context.validation_error = None
    except ValidationError as e:
        context.validation_error = e
        context.validated_model = None


@then('the User model validates successfully')
def step_user_validates_successfully(context: Context) -> None:
    """Verify User model validated successfully."""
    if context.validation_error:
        msg = f'Validation failed: {context.validation_error}'
        raise AssertionError(msg)
    if not context.validated_model:
        raise AssertionError('No validated model found')


@then('user.address.phone is a PhoneNumber object')
def step_verify_phone_number_object(context: Context) -> None:
    """Verify that address.phone is a PhoneNumber object."""
    from valid8r.core.parsers import PhoneNumber

    phone = context.validated_model.address.phone
    if not isinstance(phone, PhoneNumber):
        msg = f'Expected PhoneNumber, got {type(phone).__name__}'
        raise AssertionError(msg)


@given('nested models User -> Address -> phone')
def step_create_nested_user_address_phone(context: Context) -> None:
    """Create nested User -> Address -> phone models."""
    from pydantic import (
        BaseModel,
        field_validator,
    )

    from valid8r.core import parsers
    from valid8r.core.parsers import PhoneNumber  # noqa: TC001
    from valid8r.integrations.pydantic import validator_from_parser

    class Address(BaseModel):
        phone: PhoneNumber

        @field_validator('phone', mode='before')
        @classmethod
        def validate_phone(cls, v):  # noqa: ANN001, ANN206
            return validator_from_parser(parsers.parse_phone)(v)

    class User(BaseModel):
        address: Address

    # Rebuild models to resolve forward references
    Address.model_rebuild()
    User.model_rebuild()

    context.Address = Address
    context.User = User


@then('Pydantic raises ValidationError')
def step_pydantic_raises_validation_error(context: Context) -> None:
    """Verify that Pydantic raised a ValidationError."""
    from pydantic import ValidationError

    if not context.validation_error:
        raise AssertionError('Expected ValidationError but validation succeeded')
    if not isinstance(context.validation_error, ValidationError):
        msg = f'Expected ValidationError, got {type(context.validation_error).__name__}'
        raise AssertionError(msg)


@then('the error includes field path "{field_path}"')
def step_error_includes_field_path(context: Context, field_path: str) -> None:
    """Verify error includes the specified field path."""
    error: ValidationError = context.validation_error
    error_dict = error.errors()

    # Check if any error has the specified field path
    found = False
    for err in error_dict:
        loc = '.'.join(str(part) for part in err['loc'])
        if field_path in loc:
            found = True
            break

    if not found:
        msg = f"Field path '{field_path}' not found in errors: {error_dict}"
        raise AssertionError(msg)


@then('the error message contains the valid8r parse_phone error')
def step_error_contains_parse_phone_error(context: Context) -> None:
    """Verify error message contains valid8r parse_phone error text."""
    error: ValidationError = context.validation_error
    error_str = str(error)

    # Check for characteristic parse_phone error messages
    if 'phone' not in error_str.lower() and 'invalid' not in error_str.lower():
        msg = f'Error does not contain parse_phone error text: {error_str}'
        raise AssertionError(msg)


@given('a model LineItem with quantity validated by parse_int & minimum(1)')
def step_create_lineitem_model(context: Context) -> None:
    """Create LineItem model with quantity validation."""
    from pydantic import (
        BaseModel,
        field_validator,
    )

    from valid8r.core import (
        parsers,
        validators,
    )
    from valid8r.integrations.pydantic import validator_from_parser

    class LineItem(BaseModel):
        quantity: int

        @field_validator('quantity', mode='before')
        @classmethod
        def validate_quantity(cls, v):  # noqa: ANN001, ANN206
            parser = lambda value: parsers.parse_int(value).bind(validators.minimum(1))  # noqa: E731
            return validator_from_parser(parser)(v)

    context.LineItem = LineItem


@given('a model Order with items: list[LineItem]')
def step_create_order_model(context: Context) -> None:
    """Create Order model with items list."""
    from pydantic import BaseModel

    LineItem = context.LineItem

    class Order(BaseModel):
        items: list[LineItem]

    context.Order = Order


@then('Pydantic raises ValidationError for items[1].quantity')
def step_validation_error_for_items_index(context: Context) -> None:
    """Verify ValidationError for specific list item."""
    from pydantic import ValidationError

    if not context.validation_error:
        raise AssertionError('Expected ValidationError but validation succeeded')
    if not isinstance(context.validation_error, ValidationError):
        msg = f'Expected ValidationError, got {type(context.validation_error).__name__}'
        raise AssertionError(msg)

    # Check that error mentions items[1] or index 1
    error_dict = context.validation_error.errors()
    found = False
    for err in error_dict:
        loc_str = '.'.join(str(part) for part in err['loc'])
        if 'items.1' in loc_str or 'items[1]' in str(err):
            found = True
            break

    if not found:
        msg = f'Error does not reference items[1]: {error_dict}'
        raise AssertionError(msg)


@then('the error mentions "{keyword}"')
def step_error_mentions_keyword(context: Context, keyword: str) -> None:
    """Verify error message mentions the specified keyword."""
    error_str = str(context.validation_error).lower()

    # Handle synonyms for common validation messages
    keyword_lower = keyword.lower()
    if keyword_lower == 'minimum':
        # Accept "minimum" or "at least" as equivalent
        if 'minimum' not in error_str and 'least' not in error_str:
            msg = f"Error does not mention '{keyword}' or 'at least': {error_str}"
            raise AssertionError(msg)
    elif keyword_lower not in error_str:
        msg = f"Error does not mention '{keyword}': {error_str}"
        raise AssertionError(msg)


@given('a model Config with ports: dict[str, int] using validator_from_parser(parse_int)')
def step_create_config_model(context: Context) -> None:
    """Create Config model with ports dict."""
    from pydantic import (
        BaseModel,
        field_validator,
    )

    from valid8r.core import parsers
    from valid8r.integrations.pydantic import validator_from_parser

    class Config(BaseModel):
        ports: dict[str, int]

        @field_validator('ports', mode='before')
        @classmethod
        def validate_ports(cls, v):  # noqa: ANN001, ANN206
            if not isinstance(v, dict):
                msg = 'ports must be a dict'
                raise TypeError(msg)
            return {k: validator_from_parser(parsers.parse_int)(val) for k, val in v.items()}

    context.Config = Config


@then('the model validates successfully')
def step_model_validates_successfully(context: Context) -> None:
    """Verify model validated successfully."""
    if context.validation_error:
        msg = f'Validation failed: {context.validation_error}'
        raise AssertionError(msg)
    if not context.validated_model:
        raise AssertionError('No validated model found')


@then('config.ports == {data:DictString}')
def step_verify_config_ports(context: Context, data: str) -> None:
    """Verify config.ports matches expected data."""
    expected = json.loads(data)
    actual = context.validated_model.ports

    if actual != expected:
        msg = f'Expected ports={expected}, got {actual}'
        raise AssertionError(msg)


@given('a Pydantic model User with optional address: Address | None')
def step_create_user_with_optional_address(context: Context) -> None:
    """Create User model with optional Address field."""
    from pydantic import (
        BaseModel,
        field_validator,
    )

    from valid8r.core import parsers
    from valid8r.core.parsers import PhoneNumber  # noqa: TC001
    from valid8r.integrations.pydantic import validator_from_parser

    class Address(BaseModel):
        phone: PhoneNumber

        @field_validator('phone', mode='before')
        @classmethod
        def validate_phone(cls, v):  # noqa: ANN001, ANN206
            return validator_from_parser(parsers.parse_phone)(v)

    class User(BaseModel):
        name: str
        address: Address | None = None

    # Rebuild models to resolve forward references
    Address.model_rebuild()
    User.model_rebuild()

    context.Address = Address
    context.User = User


@then('user.address is None')
def step_verify_address_is_none(context: Context) -> None:
    """Verify user.address is None."""
    if context.validated_model.address is not None:
        msg = f'Expected address=None, got {context.validated_model.address}'
        raise AssertionError(msg)


@given('a model Employee with email validated by parse_email')
def step_create_employee_model(context: Context) -> None:
    """Create Employee model with email validation."""
    from pydantic import (
        BaseModel,
        field_validator,
    )

    from valid8r.core import parsers
    from valid8r.core.parsers import EmailAddress  # noqa: TC001
    from valid8r.integrations.pydantic import validator_from_parser

    class Employee(BaseModel):
        email: EmailAddress

        @field_validator('email', mode='before')
        @classmethod
        def validate_email(cls, v):  # noqa: ANN001, ANN206
            return validator_from_parser(parsers.parse_email)(v)

    # Rebuild model to resolve forward references
    Employee.model_rebuild()
    context.Employee = Employee


@given('a model Department with lead: Employee field')
def step_create_department_model(context: Context) -> None:
    """Create Department model with Employee field."""
    from pydantic import BaseModel

    Employee = context.Employee

    class Department(BaseModel):
        lead: Employee

    # Rebuild model to resolve forward references
    Department.model_rebuild()
    context.Department = Department


@given('a model Company with engineering: Department field')
def step_create_company_model(context: Context) -> None:
    """Create Company model with Department field."""
    from pydantic import BaseModel

    Department = context.Department

    class Company(BaseModel):
        engineering: Department

    # Rebuild model to resolve forward references
    Company.model_rebuild()
    context.Company = Company


@then('the Company model validates successfully')
def step_company_validates_successfully(context: Context) -> None:
    """Verify Company model validated successfully."""
    if context.validation_error:
        msg = f'Validation failed: {context.validation_error}'
        raise AssertionError(msg)
    if not context.validated_model:
        raise AssertionError('No validated model found')


@then('company.engineering.lead.email is an EmailAddress object')
def step_verify_email_address_object(context: Context) -> None:
    """Verify that engineering.lead.email is an EmailAddress object."""
    from valid8r.core.parsers import EmailAddress

    email = context.validated_model.engineering.lead.email
    if not isinstance(email, EmailAddress):
        msg = f'Expected EmailAddress, got {type(email).__name__}'
        raise AssertionError(msg)


@given('nested models Company -> Department -> Employee -> email (three levels)')
def step_create_three_level_nesting(context: Context) -> None:
    """Create three-level nested Company -> Department -> Employee -> email models."""
    from pydantic import (
        BaseModel,
        field_validator,
    )

    from valid8r.core import parsers
    from valid8r.core.parsers import EmailAddress  # noqa: TC001
    from valid8r.integrations.pydantic import validator_from_parser

    class Employee(BaseModel):
        email: EmailAddress

        @field_validator('email', mode='before')
        @classmethod
        def validate_email(cls, v):  # noqa: ANN001, ANN206
            return validator_from_parser(parsers.parse_email)(v)

    class Department(BaseModel):
        lead: Employee

    class Company(BaseModel):
        engineering: Department

    # Rebuild models to resolve forward references
    Employee.model_rebuild()
    Department.model_rebuild()
    Company.model_rebuild()

    context.Employee = Employee
    context.Department = Department
    context.Company = Company


@then('the error message contains the valid8r parse_email error')
def step_error_contains_parse_email_error(context: Context) -> None:
    """Verify error message contains valid8r parse_email error text."""
    error: ValidationError = context.validation_error
    error_str = str(error)

    # Check for characteristic parse_email error messages
    if 'email' not in error_str.lower() and 'invalid' not in error_str.lower():
        msg = f'Error does not contain parse_email error text: {error_str}'
        raise AssertionError(msg)
