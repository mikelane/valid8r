"""Generators for test cases and test input data."""

from __future__ import annotations

import random
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from valid8r.core.maybe import Success

if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import CellType

    from valid8r.core.validators import Validator

T = TypeVar('T')

# Constants for test case generation
OFFSET_SMALL = 1
OFFSET_MEDIUM = 5
OFFSET_LARGE = 10
OFFSET_XLARGE = 100
MULTIPLIER_FAR = 2


def _extract_numeric_value_from_closure(closure: Iterable[CellType]) -> Any | None:  # noqa: ANN401
    """Extract a numeric value from a closure."""
    for cell in closure:
        value = cell.cell_contents
        if isinstance(value, int | float):
            return value
    return None


def _generate_minimum_validator_cases(min_value: float) -> tuple[list[Any], list[Any]]:
    """Generate test cases for a minimum validator."""
    valid_cases = [
        min_value,  # Boundary
        min_value + OFFSET_SMALL,  # Just above
        min_value + OFFSET_MEDIUM,  # Above
        min_value + OFFSET_LARGE,  # Well above
        min_value * OFFSET_LARGE if min_value > 0 else OFFSET_XLARGE,  # Far above
    ]

    invalid_cases = [
        min_value - OFFSET_SMALL,  # Just below
        min_value - OFFSET_MEDIUM if min_value >= OFFSET_MEDIUM else 0,  # Below
        min_value - OFFSET_LARGE if min_value >= OFFSET_LARGE else -1,  # Well below
        -10 if min_value > 0 else min_value - 10,  # Far below
    ]

    return valid_cases, invalid_cases


def _generate_maximum_validator_cases(max_value: float) -> tuple[list[Any], list[Any]]:
    """Generate test cases for a maximum validator."""
    valid_cases = [
        max_value,  # Boundary
        max_value - OFFSET_SMALL,  # Just below
        max_value - OFFSET_MEDIUM if max_value >= OFFSET_MEDIUM else 0,  # Below
        max_value - OFFSET_LARGE if max_value >= OFFSET_LARGE else 0,  # Well below
        0 if max_value > 0 else max_value // MULTIPLIER_FAR,  # Far below
    ]

    invalid_cases = [
        max_value + OFFSET_SMALL,  # Just above
        max_value + OFFSET_MEDIUM,  # Above
        max_value + OFFSET_LARGE,  # Well above
        max_value * MULTIPLIER_FAR,  # Far above
    ]

    return valid_cases, invalid_cases


def _generate_between_validator_cases(min_val: float, max_val: float) -> tuple[list[Any], list[Any]]:
    """Generate test cases for a between validator."""
    range_size = max_val - min_val
    valid_cases = [
        min_val,  # Min boundary
        max_val,  # Max boundary
        (min_val + max_val) // 2,  # Middle
        min_val + range_size // 4,  # First quarter
        max_val - range_size // 4,  # Last quarter
    ]

    invalid_cases = [
        min_val - 1,  # Just below min
        max_val + 1,  # Just above max
        min_val - 10,  # Well below min
        max_val + 10,  # Well above max
    ]

    return valid_cases, invalid_cases


def _identify_validator_type(validator: Validator[T]) -> tuple[str, Any, Any]:
    """Identify the type of validator and extract its parameters.

    Returns:
        A tuple of (validator_type, first_param, second_param)

    """
    if not hasattr(validator.func, '__closure__') or not validator.func.__closure__:
        return 'unknown', None, None

    func_str = str(validator.func)

    if 'minimum' in func_str:
        min_value = _extract_numeric_value_from_closure(validator.func.__closure__)
        return 'minimum', min_value, None

    if 'maximum' in func_str:
        max_value = _extract_numeric_value_from_closure(validator.func.__closure__)
        return 'maximum', max_value, None

    if 'between' in func_str:
        values = _extract_two_numeric_values(validator.func.__closure__)
        return 'between', values[0], values[1]

    return 'unknown', None, None


def _extract_two_numeric_values(closure: Iterable[CellType]) -> tuple[Any, Any]:
    """Extract two numeric values from a closure."""
    values = []
    for cell in closure:
        value = cell.cell_contents
        if isinstance(value, int | float):
            values.append(value)
            if len(values) >= 2:  # noqa: PLR2004
                break

    if len(values) < 2:  # noqa: PLR2004
        return None, None
    return values[0], values[1]


def generate_test_cases(validator: Validator[T]) -> dict[str, list[Any]]:
    """Generate test cases for a validator.

    This function analyzes the validator and generates appropriate test cases
    that should pass and fail the validation.

    Args:
        validator: The validator to generate test cases for

    Returns:
        A dictionary with 'valid' and 'invalid' lists of test cases

    Examples:
        >>> test_cases = generate_test_cases(minimum(10))
        >>> test_cases
        {'valid': [10, 11, 15, 20, 100], 'invalid': [9, 5, 0, -10]}

    """
    # Identify validator type and extract parameters
    validator_type, param1, param2 = _identify_validator_type(validator)

    # Generate test cases based on validator type
    valid_cases: list[Any] = []
    invalid_cases: list[Any] = []

    if validator_type == 'minimum' and param1 is not None:
        valid_cases, invalid_cases = _generate_minimum_validator_cases(param1)

    elif validator_type == 'maximum' and param1 is not None:
        valid_cases, invalid_cases = _generate_maximum_validator_cases(param1)

    elif validator_type == 'between' and param1 is not None and param2 is not None:
        valid_cases, invalid_cases = _generate_between_validator_cases(param1, param2)

    # Use generic cases if we couldn't determine specific ones
    if not valid_cases:
        valid_cases = [0, 1, 10, 42, 100]
    if not invalid_cases:
        invalid_cases = [-1, -10, -100]

    # Verify categorization against the actual validator
    actual_valid = []
    actual_invalid = []

    for case in valid_cases + invalid_cases:
        result = validator(case)
        if result.is_success():
            actual_valid.append(case)
        else:
            actual_invalid.append(case)

    return {'valid': actual_valid, 'invalid': actual_invalid}


def generate_random_inputs(
    validator: Validator[T], count: int = 20, range_min: int = -100, range_max: int = 100
) -> list[T]:
    """Generate random inputs that include both valid and invalid cases.

    Args:
        validator: The validator to test against
        count: Number of inputs to generate
        range_min: Minimum value for generated integers
        range_max: Maximum value for generated integers

    Returns:
        A list of random integers

    Examples:
        >>> inputs = generate_random_inputs(minimum(0), count=10)
        >>> len(inputs)
        10

    """
    inputs: list[Any] = []

    # Try to make sure we get both valid and invalid cases
    for _ in range(count):
        value = random.randint(range_min, range_max)  # noqa: S311
        inputs.append(value)

    # Verify we have at least one valid and one invalid case
    has_valid = False
    has_invalid = False

    for input_val in inputs:
        result = validator(input_val)
        match result:
            case Success(_):
                has_valid = True
            case _:
                has_invalid = True

        if has_valid and has_invalid:
            break

    # If we're missing either valid or invalid cases, add them explicitly
    if not has_valid or not has_invalid:
        # Get test cases that are known to be valid/invalid
        test_cases = generate_test_cases(validator)

        if not has_valid and test_cases['valid']:
            # Replace the first item with a valid case
            inputs[0] = test_cases['valid'][0]

        if not has_invalid and test_cases['invalid']:
            # Replace the second item with an invalid case
            inputs[1 if len(inputs) > 1 else 0] = test_cases['invalid'][0]

    return inputs


def test_validator_composition(validator: Validator[T]) -> bool:
    """Test a composed validator with various inputs to verify it works correctly.

    Args:
        validator: The composed validator to test

    Returns:
        True if the validator behaves as expected, False otherwise

    Examples:
        >>> is_valid_age = minimum(0) & maximum(120)
        >>> test_validator_composition(is_valid_age)  # Returns True

    """
    # Generate test cases
    test_cases = generate_test_cases(validator)

    # Check that all valid cases pass
    for case in test_cases['valid']:
        result = validator(case)
        if not result.is_success():
            return False

    # Check that all invalid cases fail
    for case in test_cases['invalid']:
        result = validator(case)
        if not result.is_failure():
            return False

    return True
