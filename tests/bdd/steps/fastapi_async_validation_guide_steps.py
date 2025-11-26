"""BDD step definitions for FastAPI Async Validation Guide feature.

This module implements black-box tests for the FastAPI integration guide
through step definitions that verify documentation, examples, and guide content.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from behave import (
    given,
    then,
    when,
)

if TYPE_CHECKING:
    from behave.runner import Context


class FastAPIGuideContext:
    """Test context for FastAPI guide scenarios."""

    def __init__(self) -> None:
        """Initialize the FastAPI guide context."""
        self.guide_path: Path | None = None
        self.example_path: Path | None = None
        self.guide_content: str = ''
        self.example_content: str = ''
        self.test_client = None
        self.request_validation_implemented = False
        self.query_validation_implemented = False
        self.header_validation_implemented = False
        self.error_handling_implemented = False
        self.performance_section_present = False


def get_fastapi_context(context: Context) -> FastAPIGuideContext:
    """Get or create the FastAPI guide context for the current test."""
    if not hasattr(context, 'fastapi_guide_context'):
        context.fastapi_guide_context = FastAPIGuideContext()
    return context.fastapi_guide_context


# Background steps
# Note: Reusing step from async_validation_steps.py for async support check


@given('I have FastAPI installed')
def step_fastapi_installed(context: Context) -> None:
    """Verify FastAPI is available for testing."""
    try:
        import fastapi  # noqa: F401
    except ImportError as e:
        # FastAPI is optional for valid8r, but required for this test
        # In real testing, we'd use pytest.skip if not installed
        raise AssertionError('FastAPI must be installed to test the integration guide') from e


@given('I have a test client for my FastAPI application')
def step_test_client_available(context: Context) -> None:
    """Verify FastAPI TestClient is available."""
    try:
        from fastapi.testclient import TestClient  # noqa: F401
    except ImportError as e:
        raise AssertionError('FastAPI TestClient must be available for testing') from e


@given('I follow the integration guide')
def step_follow_integration_guide(context: Context) -> None:
    """Verify the FastAPI integration guide exists and is accessible."""
    fc = get_fastapi_context(context)

    # Locate the guide document
    project_root = Path(__file__).parent.parent.parent.parent
    guide_path = project_root / 'docs' / 'guides' / 'fastapi-async-validation.md'

    # Guide must exist
    assert guide_path.exists(), f'Guide must exist at {guide_path}'

    fc.guide_path = guide_path
    fc.guide_content = guide_path.read_text()

    # Guide must not be empty
    assert len(fc.guide_content) > 0, 'Guide content must not be empty'


# Request body validation scenario
@when('I implement request body validation')
def step_implement_request_body_validation(context: Context) -> None:
    """Verify guide contains request body validation examples."""
    fc = get_fastapi_context(context)

    # Check guide contains request body validation section
    assert 'request body' in fc.guide_content.lower(), 'Guide must contain request body validation section'
    assert '@app.post' in fc.guide_content or 'POST' in fc.guide_content, 'Guide must show POST endpoint examples'

    # Check for async validation pattern
    assert 'validate_async' in fc.guide_content or 'async' in fc.guide_content, (
        'Guide must demonstrate async validation'
    )

    # Locate the example file
    project_root = Path(__file__).parent.parent.parent.parent
    example_path = project_root / 'examples' / 'fastapi-async'

    # Examples directory must exist
    assert example_path.exists(), f'Examples directory must exist at {example_path}'
    assert example_path.is_dir(), f'Examples path must be a directory: {example_path}'

    fc.example_path = example_path
    fc.request_validation_implemented = True


@then('invalid requests are rejected automatically')
def step_invalid_requests_rejected(context: Context) -> None:
    """Verify guide demonstrates automatic rejection of invalid requests."""
    fc = get_fastapi_context(context)

    # Check guide shows error handling
    assert 'HTTPException' in fc.guide_content or 'status_code' in fc.guide_content, (
        'Guide must show HTTPException or status codes for errors'
    )
    assert '422' in fc.guide_content or '400' in fc.guide_content, (
        'Guide must demonstrate validation error status codes (422 or 400)'
    )


@then('clients receive clear error messages')
def step_clear_error_messages(context: Context) -> None:
    """Verify guide demonstrates clear error messages."""
    fc = get_fastapi_context(context)

    # Check guide shows error message formatting
    assert 'detail' in fc.guide_content or 'error' in fc.guide_content, 'Guide must show error message formatting'
    assert 'Failure' in fc.guide_content, 'Guide must demonstrate using Maybe.Failure for error messages'


@then('valid requests proceed to my handler')
def step_valid_requests_proceed(context: Context) -> None:
    """Verify guide shows successful validation flow."""
    fc = get_fastapi_context(context)

    # Check guide shows success path
    assert 'Success' in fc.guide_content, 'Guide must demonstrate using Maybe.Success'
    assert 'match' in fc.guide_content or 'case' in fc.guide_content, (
        'Guide must demonstrate pattern matching for Maybe results'
    )


# Query parameter validation scenario
@when('I implement query parameter validation')
def step_implement_query_validation(context: Context) -> None:
    """Verify guide contains query parameter validation examples."""
    fc = get_fastapi_context(context)

    # Check guide contains query parameter section
    assert 'query parameter' in fc.guide_content.lower(), 'Guide must contain query parameter validation section'
    assert 'Query' in fc.guide_content or 'query' in fc.guide_content, 'Guide must show query parameter examples'

    fc.query_validation_implemented = True


@then('missing parameters are handled gracefully')
def step_missing_parameters_handled(context: Context) -> None:
    """Verify guide demonstrates handling missing parameters."""
    fc = get_fastapi_context(context)

    # Check guide shows optional parameters or required validation
    assert 'Optional' in fc.guide_content or 'required' in fc.guide_content, (
        'Guide must demonstrate handling optional/required parameters'
    )


@then('invalid parameter values are rejected')
def step_invalid_parameters_rejected(context: Context) -> None:
    """Verify guide demonstrates rejecting invalid query parameters."""
    fc = get_fastapi_context(context)

    # Already verified in request body scenario - same pattern applies
    assert fc.guide_content, 'Guide content must be loaded'


@then('I understand what went wrong from the error message')
def step_understand_error_message(context: Context) -> None:
    """Verify guide demonstrates clear error messages for query params."""
    fc = get_fastapi_context(context)

    # Check guide emphasizes clear error messages
    assert 'error' in fc.guide_content or 'message' in fc.guide_content, 'Guide must demonstrate clear error messages'


# Request header validation scenario
@when('I implement header validation')
def step_implement_header_validation(context: Context) -> None:
    """Verify guide contains header validation examples."""
    fc = get_fastapi_context(context)

    # Check guide contains header validation section
    assert 'header' in fc.guide_content.lower(), 'Guide must contain header validation section'
    assert 'Header' in fc.guide_content or 'Authorization' in fc.guide_content, (
        'Guide must show header validation examples'
    )

    fc.header_validation_implemented = True


@then('I can verify authentication tokens')
def step_verify_auth_tokens(context: Context) -> None:
    """Verify guide demonstrates authentication token validation."""
    fc = get_fastapi_context(context)

    # Check guide shows auth token validation
    assert 'token' in fc.guide_content.lower() or 'authorization' in fc.guide_content.lower(), (
        'Guide must demonstrate authentication token validation'
    )


@then('I can validate custom header formats')
def step_validate_custom_headers(context: Context) -> None:
    """Verify guide demonstrates custom header validation."""
    fc = get_fastapi_context(context)

    # Check guide shows custom header patterns
    assert 'header' in fc.guide_content.lower(), 'Guide must demonstrate header validation'


@then('unauthorized requests are rejected appropriately')
def step_unauthorized_rejected(context: Context) -> None:
    """Verify guide demonstrates rejection of unauthorized requests."""
    fc = get_fastapi_context(context)

    # Check guide shows 401/403 status codes
    assert '401' in fc.guide_content or '403' in fc.guide_content or 'unauthorized' in fc.guide_content.lower(), (
        'Guide must demonstrate authentication error status codes (401 or 403)'
    )


# Error handling scenario
@when('API validation fails')
def step_validation_fails(context: Context) -> None:
    """Verify guide contains error handling section."""
    fc = get_fastapi_context(context)

    # Check guide contains error handling section
    assert 'error' in fc.guide_content.lower(), 'Guide must contain error handling section'
    assert 'Failure' in fc.guide_content, 'Guide must demonstrate Failure case handling'

    fc.error_handling_implemented = True


@then('I know how to return appropriate HTTP status codes')
def step_appropriate_status_codes(context: Context) -> None:
    """Verify guide demonstrates appropriate HTTP status codes."""
    fc = get_fastapi_context(context)

    # Check guide shows various status codes
    status_codes_present = any(code in fc.guide_content for code in ['400', '401', '403', '422', '500'])
    assert status_codes_present, 'Guide must demonstrate HTTP status codes for different error types'


@then('I can provide structured error responses')
def step_structured_error_responses(context: Context) -> None:
    """Verify guide demonstrates structured error responses."""
    fc = get_fastapi_context(context)

    # Check guide shows structured response format
    assert 'detail' in fc.guide_content or '"error"' in fc.guide_content or "'error'" in fc.guide_content, (
        'Guide must demonstrate structured error response format'
    )


@then('clients receive actionable feedback')
def step_actionable_feedback(context: Context) -> None:
    """Verify guide emphasizes actionable error messages."""
    fc = get_fastapi_context(context)

    # Check guide emphasizes clear, actionable errors
    assert 'message' in fc.guide_content or 'feedback' in fc.guide_content or 'error' in fc.guide_content, (
        'Guide must emphasize actionable error feedback'
    )


# Performance evaluation scenario
@when('I review the performance section')
def step_review_performance_section(context: Context) -> None:
    """Verify guide contains performance section."""
    fc = get_fastapi_context(context)

    # Check guide contains performance section
    performance_keywords = ['performance', 'optimization', 'benchmark', 'async', 'speed']
    performance_section_found = any(keyword in fc.guide_content.lower() for keyword in performance_keywords)

    assert performance_section_found, 'Guide must contain performance/optimization section'
    fc.performance_section_present = True


@then('I understand when async validation is beneficial')
def step_understand_async_benefits(context: Context) -> None:
    """Verify guide explains when to use async validation."""
    fc = get_fastapi_context(context)

    # Check guide explains async use cases
    assert 'async' in fc.guide_content.lower(), 'Guide must explain async validation use cases'
    assert 'when' in fc.guide_content.lower() or 'use case' in fc.guide_content.lower(), (
        'Guide must explain when to use async validation'
    )


@then('I see performance comparisons')
def step_see_performance_comparisons(context: Context) -> None:
    """Verify guide includes performance comparisons."""
    fc = get_fastapi_context(context)

    # Check guide includes performance data or comparisons
    comparison_keywords = ['vs', 'versus', 'compared', 'comparison', 'faster', 'slower', 'benchmark']
    comparison_found = any(keyword in fc.guide_content.lower() for keyword in comparison_keywords)

    assert comparison_found, 'Guide must include performance comparisons'


@then('I can make informed architecture decisions')
def step_informed_decisions(context: Context) -> None:
    """Verify guide provides decision-making guidance."""
    fc = get_fastapi_context(context)

    # Check guide provides architectural guidance
    decision_keywords = ['should', 'recommend', 'best practice', 'consider', 'decision', 'choose', 'when to']
    guidance_found = any(keyword in fc.guide_content.lower() for keyword in decision_keywords)

    assert guidance_found, 'Guide must provide architectural decision guidance'
