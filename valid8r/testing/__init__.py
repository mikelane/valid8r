# valid8r/testing/__init__.py
"""Testing utilities for Valid8r.

This module provides tools for testing applications that use Valid8r,
making it easier to test validation logic, user prompts, and Maybe monads.
"""

from __future__ import annotations

from valid8r.testing.assertions import (
    assert_maybe_failure,
    assert_maybe_success,
)
from valid8r.testing.generators import (
    generate_random_inputs,
    generate_test_cases,
    test_validator_composition,
)
from valid8r.testing.mock_input import (
    MockInputContext,
    configure_mock_input,
)

__all__ = [
    'MockInputContext',
    'assert_maybe_failure',
    'assert_maybe_success',
    'configure_mock_input',
    'generate_random_inputs',
    'generate_test_cases',
    'test_validator_composition',
]
