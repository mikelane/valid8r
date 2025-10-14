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

if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


# ============================================================================
# Given Steps - Test Setup
# ============================================================================


@given('the valid8r library is available')
def step_library_available(context: Context) -> None:
    """Verify the valid8r library can be imported."""
    ctx = get_custom_context(context)
    # Reset any previous state
    ctx.phone_input = None
    ctx.region = None
    ctx.strict = False
    ctx.result = None


@given('a phone number string "{phone_string}"')
def step_have_phone_string(context: Context, phone_string: str) -> None:
    """Store the phone number string for parsing."""
    ctx = get_custom_context(context)
    ctx.phone_input = phone_string


@given('a phone number string ""')
def step_have_empty_phone_string(context: Context) -> None:
    """Store an empty phone number string for parsing."""
    ctx = get_custom_context(context)
    ctx.phone_input = ''


@given('the region hint is "{region}"')
def step_region_hint(context: Context, region: str) -> None:
    """Store the region hint for parsing."""
    ctx = get_custom_context(context)
    ctx.region = region


@given('strict mode is enabled')
def step_strict_mode_enabled(context: Context) -> None:
    """Enable strict mode for parsing."""
    ctx = get_custom_context(context)
    ctx.strict = True


# ============================================================================
# When Steps - Actions
# ============================================================================


@when('the parser parses the phone number')
def step_parse_phone(context: Context) -> None:
    """Parse the phone number string using parse_phone."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.parsers import parse_phone

        ctx.result = parse_phone(ctx.phone_input)
    except (ImportError, AttributeError) as e:
        # Parser doesn't exist yet - store the exception
        ctx.result = Failure(f'Parser not implemented: {e}')


@when('the parser parses the phone number with region')
def step_parse_phone_with_region(context: Context) -> None:
    """Parse the phone number string with region hint."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.parsers import parse_phone

        ctx.result = parse_phone(ctx.phone_input, region=ctx.region)
    except (ImportError, AttributeError) as e:
        ctx.result = Failure(f'Parser not implemented: {e}')


@when('the parser parses the phone number in strict mode')
def step_parse_phone_strict(context: Context) -> None:
    """Parse the phone number string in strict mode."""
    ctx = get_custom_context(context)
    try:
        from valid8r.core.parsers import parse_phone

        ctx.result = parse_phone(ctx.phone_input, strict=ctx.strict)
    except (ImportError, AttributeError) as e:
        ctx.result = Failure(f'Parser not implemented: {e}')


# ============================================================================
# Then Steps - Assertions
# ============================================================================
# Note: Common steps "the result is a Success/Failure" are defined in
# url_email_parsing_steps.py and reused across all BDD features


@then('the area code is "{expected_area_code}"')
def step_area_code_is(context: Context, expected_area_code: str) -> None:
    """Verify the area code matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            try:
                actual = phone.area_code
                assert actual == expected_area_code, f'Expected area code {expected_area_code} but got {actual}'
            except AttributeError as e:
                pytest.fail(f'PhoneNumber missing area_code attribute: {e}')
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the exchange is "{expected_exchange}"')
def step_exchange_is(context: Context, expected_exchange: str) -> None:
    """Verify the exchange matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            try:
                actual = phone.exchange
                assert actual == expected_exchange, f'Expected exchange {expected_exchange} but got {actual}'
            except AttributeError as e:
                pytest.fail(f'PhoneNumber missing exchange attribute: {e}')
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the subscriber number is "{expected_subscriber}"')
def step_subscriber_is(context: Context, expected_subscriber: str) -> None:
    """Verify the subscriber number matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            try:
                actual = phone.subscriber
                assert actual == expected_subscriber, f'Expected subscriber {expected_subscriber} but got {actual}'
            except AttributeError as e:
                pytest.fail(f'PhoneNumber missing subscriber attribute: {e}')
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the country code is "{expected_country_code}"')
def step_country_code_is(context: Context, expected_country_code: str) -> None:
    """Verify the country code matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            try:
                actual = phone.country_code
                assert actual == expected_country_code, (
                    f'Expected country code {expected_country_code} but got {actual}'
                )
            except AttributeError as e:
                pytest.fail(f'PhoneNumber missing country_code attribute: {e}')
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the region is "{expected_region}"')
def step_region_is(context: Context, expected_region: str) -> None:
    """Verify the region matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            try:
                actual = phone.region
                assert actual == expected_region, f'Expected region {expected_region} but got {actual}'
            except AttributeError as e:
                pytest.fail(f'PhoneNumber missing region attribute: {e}')
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the extension is "{expected_extension}"')
def step_extension_is_string(context: Context, expected_extension: str) -> None:
    """Verify the extension matches expected string value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            try:
                actual = phone.extension
                assert actual == expected_extension, f'Expected extension {expected_extension} but got {actual}'
            except AttributeError as e:
                pytest.fail(f'PhoneNumber missing extension attribute: {e}')
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the extension is None')
def step_extension_is_none(context: Context) -> None:
    """Verify the extension is None."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            try:
                actual = phone.extension
                assert actual is None, f'Expected extension None but got {actual}'
            except AttributeError as e:
                pytest.fail(f'PhoneNumber missing extension attribute: {e}')
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the E.164 format is "{expected_e164}"')
def step_e164_format_is(context: Context, expected_e164: str) -> None:
    """Verify the E.164 format matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            try:
                actual = phone.e164
                assert actual == expected_e164, f'Expected E.164 format {expected_e164} but got {actual}'
            except AttributeError as e:
                pytest.fail(f'PhoneNumber missing e164 property: {e}')
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the national format is "{expected_national}"')
def step_national_format_is(context: Context, expected_national: str) -> None:
    """Verify the national format matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            try:
                actual = phone.national
                assert actual == expected_national, f'Expected national format {expected_national} but got {actual}'
            except AttributeError as e:
                pytest.fail(f'PhoneNumber missing national property: {e}')
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the international format is "{expected_international}"')
def step_international_format_is(context: Context, expected_international: str) -> None:
    """Verify the international format matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            try:
                actual = phone.international
                assert actual == expected_international, (
                    f'Expected international format {expected_international} but got {actual}'
                )
            except AttributeError as e:
                pytest.fail(f'PhoneNumber missing international property: {e}')
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the raw digits are "{expected_raw}"')
def step_raw_digits_are(context: Context, expected_raw: str) -> None:
    """Verify the raw digits match expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(phone):
            try:
                actual = phone.raw_digits
                assert actual == expected_raw, f'Expected raw digits {expected_raw} but got {actual}'
            except AttributeError as e:
                pytest.fail(f'PhoneNumber missing raw_digits property: {e}')
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


# Note: "the error message contains" step is defined in url_email_parsing_steps.py
# and is reused across all BDD features for consistency
