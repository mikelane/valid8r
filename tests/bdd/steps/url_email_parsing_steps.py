"""BDD step definitions for URL and email parsing scenarios."""

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
from valid8r.core.parsers import (
    EmailAddress,
    UrlParts,
    parse_email,
    parse_url,
)

if TYPE_CHECKING:
    from behave.runner import Context  # type: ignore[import-untyped]


@given('I have the URL string "{url_string}"')
def step_have_url_string(context: Context, url_string: str) -> None:
    """Store the URL string for parsing."""
    ctx = get_custom_context(context)
    ctx.url_input = url_string


@given('I have the URL string ""')
def step_have_empty_url_string(context: Context) -> None:
    """Store an empty URL string for parsing."""
    ctx = get_custom_context(context)
    ctx.url_input = ''


@given('I have the email string "{email_string}"')
def step_have_email_string(context: Context, email_string: str) -> None:
    """Store the email string for parsing."""
    ctx = get_custom_context(context)
    ctx.email_input = email_string


@given('I have the email string ""')
def step_have_empty_email_string(context: Context) -> None:
    """Store an empty email string for parsing."""
    ctx = get_custom_context(context)
    ctx.email_input = ''


@when('I parse it with parse_url')
def step_parse_url(context: Context) -> None:
    """Parse the URL string."""
    ctx = get_custom_context(context)
    ctx.result = parse_url(ctx.url_input)


@when('I parse it with parse_email')
def step_parse_email(context: Context) -> None:
    """Parse the email string."""
    ctx = get_custom_context(context)
    ctx.result = parse_email(ctx.email_input)


@then('the result is a Success')
def step_result_is_success(context: Context) -> None:
    """Verify the result is a Success."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(_):
            assert True
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the result is a Failure')
def step_result_is_failure(context: Context) -> None:
    """Verify the result is a Failure."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Failure(_):
            assert True
        case Success(value):
            pytest.fail(f'Expected Failure but got Success: {value}')


@then('the URL scheme is "{expected_scheme}"')
def step_url_scheme_is(context: Context, expected_scheme: str) -> None:
    """Verify the URL scheme matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(url_parts):
            assert isinstance(url_parts, UrlParts)
            assert url_parts.scheme == expected_scheme, f'Expected scheme {expected_scheme} but got {url_parts.scheme}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the URL host is "{expected_host}"')
def step_url_host_is(context: Context, expected_host: str) -> None:
    """Verify the URL host matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(url_parts):
            assert isinstance(url_parts, UrlParts)
            assert url_parts.host == expected_host, f'Expected host {expected_host} but got {url_parts.host}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the URL port is {expected_port:d}')
def step_url_port_is(context: Context, expected_port: int) -> None:
    """Verify the URL port matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(url_parts):
            assert isinstance(url_parts, UrlParts)
            assert url_parts.port == expected_port, f'Expected port {expected_port} but got {url_parts.port}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the URL path is "{expected_path}"')
def step_url_path_is(context: Context, expected_path: str) -> None:
    """Verify the URL path matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(url_parts):
            assert isinstance(url_parts, UrlParts)
            assert url_parts.path == expected_path, f'Expected path {expected_path} but got {url_parts.path}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the URL path is ""')
def step_url_path_is_empty(context: Context) -> None:
    """Verify the URL path is empty."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(url_parts):
            assert isinstance(url_parts, UrlParts)
            assert url_parts.path == '', f'Expected empty path but got {url_parts.path}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the URL query is "{expected_query}"')
def step_url_query_is(context: Context, expected_query: str) -> None:
    """Verify the URL query matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(url_parts):
            assert isinstance(url_parts, UrlParts)
            assert url_parts.query == expected_query, f'Expected query {expected_query} but got {url_parts.query}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the URL fragment is "{expected_fragment}"')
def step_url_fragment_is(context: Context, expected_fragment: str) -> None:
    """Verify the URL fragment matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(url_parts):
            assert isinstance(url_parts, UrlParts)
            assert url_parts.fragment == expected_fragment, (
                f'Expected fragment {expected_fragment} but got {url_parts.fragment}'
            )
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the URL username is "{expected_username}"')
def step_url_username_is(context: Context, expected_username: str) -> None:
    """Verify the URL username matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(url_parts):
            assert isinstance(url_parts, UrlParts)
            assert url_parts.username == expected_username, (
                f'Expected username {expected_username} but got {url_parts.username}'
            )
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the URL password is "{expected_password}"')
def step_url_password_is(context: Context, expected_password: str) -> None:
    """Verify the URL password matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(url_parts):
            assert isinstance(url_parts, UrlParts)
            assert url_parts.password == expected_password, (
                f'Expected password {expected_password} but got {url_parts.password}'
            )
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the email local part is "{expected_local}"')
def step_email_local_is(context: Context, expected_local: str) -> None:
    """Verify the email local part matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(email_addr):
            assert isinstance(email_addr, EmailAddress)
            assert email_addr.local == expected_local, f'Expected local {expected_local} but got {email_addr.local}'
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the email domain is "{expected_domain}"')
def step_email_domain_is(context: Context, expected_domain: str) -> None:
    """Verify the email domain matches expected value."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(email_addr):
            assert isinstance(email_addr, EmailAddress)
            assert email_addr.domain == expected_domain, (
                f'Expected domain {expected_domain} but got {email_addr.domain}'
            )
        case Failure(err):
            pytest.fail(f'Expected Success but got Failure: {err}')


@then('the error message contains "{expected_substring}"')
def step_error_contains(context: Context, expected_substring: str) -> None:
    """Verify the error message contains expected substring."""
    ctx = get_custom_context(context)
    match ctx.result:
        case Success(value):
            pytest.fail(f'Expected Failure but got Success: {value}')
        case Failure(err):
            assert expected_substring.lower() in err.lower(), (
                f'Expected error to contain "{expected_substring}" but got: {err}'
            )
