"""BDD step definitions for phone number parsing scenarios."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from behave import (  # type: ignore[import-untyped]
    given,
    then,
    when,
)

from tests.bdd.steps import get_custom_context
from valid8r.core.maybe import (
    Failure,
    Success,
)

try:
    from valid8r.core.parsers import (
        PhoneNumber,
        parse_phone,
    )
except ImportError:
    # Phone parsing not yet implemented
    PhoneNumber = None  # type: ignore[misc,assignment]
    parse_phone = None  # type: ignore[misc,assignment]

if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


# Background steps


@given('the valid8r library is available')
def step_library_available(_context: Context) -> None:
    """Verify the valid8r library is importable."""
    # This step is implicit - if imports work, library is available
    assert True


@given('the phone parsing module supports North American numbers')
def step_supports_north_american(_context: Context) -> None:
    """Verify North American phone parsing is supported."""
    # This step documents the scope - NANP only
    assert True


# Given steps - input setup


@given('a phone number string "{phone_string}"')
def step_have_phone_string(context: Context, phone_string: str) -> None:
    """Store the phone number string for parsing."""
    ctx = get_custom_context(context)
    # Decode escape sequences like \t and \n
    ctx.phone_input = phone_string.encode().decode('unicode_escape')


@given('an empty phone number string')
def step_have_empty_phone_string(context: Context) -> None:
    """Store an empty phone number string for parsing."""
    ctx = get_custom_context(context)
    ctx.phone_input = ''


@given('a None phone number value')
def step_have_none_phone_value(context: Context) -> None:
    """Store None as the phone number value."""
    ctx = get_custom_context(context)
    ctx.phone_input = None


@given('an extremely long phone number string')
def step_have_extremely_long_phone_string(context: Context) -> None:
    """Store an extremely long phone number string."""
    ctx = get_custom_context(context)
    # 1000 characters should be enough to trigger length validation
    ctx.phone_input = '1' * 1000


@given('the region hint is "{region}"')
def step_have_region_hint(context: Context, region: str) -> None:
    """Store the region hint for parsing."""
    ctx = get_custom_context(context)
    ctx.region_hint = region


@given('strict mode is enabled')
def step_strict_mode_enabled(context: Context) -> None:
    """Enable strict parsing mode."""
    ctx = get_custom_context(context)
    ctx.strict_mode = True


@given('a successfully parsed phone "{phone_string}"')
def step_have_parsed_phone(context: Context, phone_string: str) -> None:
    """Parse and store a phone number for format conversion testing."""
    ctx = get_custom_context(context)
    # Decode escape sequences like \t and \n
    decoded_phone = phone_string.encode().decode('unicode_escape')
    result = parse_phone(decoded_phone)
    match result:
        case Success(phone):
            ctx.parsed_phone = phone
        case Failure(err):
            pytest.fail(f'Expected successful parse but got: {err}')


# When steps - actions


@when('the parser parses the phone number')
def step_parse_phone(context: Context) -> None:
    """Parse the phone number string."""
    ctx = get_custom_context(context)
    ctx.result = parse_phone(ctx.phone_input)


@when('the parser parses the phone number with region hint')
def step_parse_phone_with_region(context: Context) -> None:
    """Parse the phone number string with region hint."""
    ctx = get_custom_context(context)
    ctx.result = parse_phone(ctx.phone_input, region=ctx.region_hint)


@when('the parser parses the phone number in strict mode')
def step_parse_phone_strict(context: Context) -> None:
    """Parse the phone number string in strict mode."""
    ctx = get_custom_context(context)
    ctx.result = parse_phone(ctx.phone_input, strict=True)


@when('the E.164 format is requested')
def step_request_e164_format(context: Context) -> None:
    """Get the E.164 format from the parsed phone."""
    ctx = get_custom_context(context)
    ctx.formatted_phone = ctx.parsed_phone.e164


@when('the national format is requested')
def step_request_national_format(context: Context) -> None:
    """Get the national format from the parsed phone."""
    ctx = get_custom_context(context)
    ctx.formatted_phone = ctx.parsed_phone.national


@when('the international format is requested')
def step_request_international_format(context: Context) -> None:
    """Get the international format from the parsed phone."""
    ctx = get_custom_context(context)
    ctx.formatted_phone = ctx.parsed_phone.international


@when('the raw digits are requested')
def step_request_raw_digits(context: Context) -> None:
    """Get the raw digits from the parsed phone."""
    ctx = get_custom_context(context)
    ctx.raw_digits = ctx.parsed_phone.raw_digits


# Then steps - assertions


@then('the result is a success')
def step_result_is_success(context: Context) -> None:
    """Verify the result is a Success."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(_):
            assert True
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the result is a failure')
def step_result_is_failure(context: Context) -> None:
    """Verify the result is a Failure."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Failure(_):
            assert True
        case Success(value):
            pytest.fail(f'Expected Failure but got Success: {value}')


@then('the area code is "{expected_area_code}"')
def step_area_code_is(context: Context, expected_area_code: str) -> None:
    """Verify the area code matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            assert isinstance(phone, PhoneNumber)
            assert phone.area_code == expected_area_code, (
                f'Expected area code {expected_area_code} but got {phone.area_code}'
            )
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the exchange is "{expected_exchange}"')
def step_exchange_is(context: Context, expected_exchange: str) -> None:
    """Verify the exchange matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            assert isinstance(phone, PhoneNumber)
            assert phone.exchange == expected_exchange, (
                f'Expected exchange {expected_exchange} but got {phone.exchange}'
            )
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the subscriber number is "{expected_subscriber}"')
def step_subscriber_is(context: Context, expected_subscriber: str) -> None:
    """Verify the subscriber number matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            assert isinstance(phone, PhoneNumber)
            assert phone.subscriber == expected_subscriber, (
                f'Expected subscriber {expected_subscriber} but got {phone.subscriber}'
            )
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the country code is "{expected_country_code}"')
def step_country_code_is(context: Context, expected_country_code: str) -> None:
    """Verify the country code matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            assert isinstance(phone, PhoneNumber)
            assert phone.country_code == expected_country_code, (
                f'Expected country code {expected_country_code} but got {phone.country_code}'
            )
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the region is "{expected_region}"')
def step_region_is(context: Context, expected_region: str) -> None:
    """Verify the region matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            assert isinstance(phone, PhoneNumber)
            assert phone.region == expected_region, f'Expected region {expected_region} but got {phone.region}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the extension is "{expected_extension}"')
def step_extension_is(context: Context, expected_extension: str) -> None:
    """Verify the extension matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            assert isinstance(phone, PhoneNumber)
            assert phone.extension == expected_extension, (
                f'Expected extension {expected_extension} but got {phone.extension}'
            )
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the extension is None')
def step_extension_is_none(context: Context) -> None:
    """Verify the extension is None."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            assert isinstance(phone, PhoneNumber)
            assert phone.extension is None, f'Expected extension None but got {phone.extension}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


# Note: "the error message contains" step is defined in url_email_parsing_steps.py and is reusable


@then('the E.164 format is "{expected_e164}"')
def step_e164_format_is(context: Context, expected_e164: str) -> None:
    """Verify the E.164 format matches expected value."""
    ctx = get_custom_context(context)
    assert ctx.formatted_phone == expected_e164, f'Expected E.164 {expected_e164} but got {ctx.formatted_phone}'


@then('the national format is "{expected_national}"')
def step_national_format_is(context: Context, expected_national: str) -> None:
    """Verify the national format matches expected value."""
    ctx = get_custom_context(context)
    assert ctx.formatted_phone == expected_national, (
        f'Expected national {expected_national} but got {ctx.formatted_phone}'
    )


@then('the international format is "{expected_international}"')
def step_international_format_is(context: Context, expected_international: str) -> None:
    """Verify the international format matches expected value."""
    ctx = get_custom_context(context)
    assert ctx.formatted_phone == expected_international, (
        f'Expected international {expected_international} but got {ctx.formatted_phone}'
    )


@then('the raw digits are "{expected_raw_digits}"')
def step_raw_digits_are(context: Context, expected_raw_digits: str) -> None:
    """Verify the raw digits match expected value."""
    ctx = get_custom_context(context)
    assert ctx.raw_digits == expected_raw_digits, f'Expected raw digits {expected_raw_digits} but got {ctx.raw_digits}'
