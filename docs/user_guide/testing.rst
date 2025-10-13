Testing with Valid8r
====================

This guide explains how to test applications that use Valid8r for validation.

Overview
--------

Valid8r's testing module provides utilities to make it easier to test your validation logic, including:

1. Mocking user input for testing interactive prompts
2. Asserting on Maybe results
3. Generating test cases for validators
4. Testing validator composition
5. Property-based testing utilities

All testing utilities are available in the ``valid8r.testing`` module.

Mocking User Input
------------------

When testing functions that use input prompts, you can use ``MockInputContext`` to provide predefined inputs:

.. code-block:: python

    from valid8r.testing import MockInputContext
    from valid8r.prompt import ask
    from valid8r.parsers import parse_int

    def test_age_prompt():
        # Mock user entering "42" when prompted
        with MockInputContext(["42"]):
            result = ask("Enter your age: ", parser=parse_int)
            assert result.is_success()
            assert result.value_or(0) == 42

    def test_retry_logic():
        # Mock user entering invalid input first, then valid input
        with MockInputContext(["abc", "42"]):
            result = ask(
                "Enter your age: ",
                parser=parse_int,
                retry=True
            )
            assert result.is_success()
            assert result.value_or(0) == 42

You can also configure the mock input globally:

.. code-block:: python

    from valid8r.testing import configure_mock_input

    def test_global_input():
        configure_mock_input(["yes", "no", "maybe"])

        answer1 = input("First question: ")  # Returns "yes"
        answer2 = input("Second question: ")  # Returns "no"
        answer3 = input("Third question: ")  # Returns "maybe"

        assert answer1 == "yes"
        assert answer2 == "no"
        assert answer3 == "maybe"

Asserting on Maybe Results
--------------------------

To test functions that return Maybe objects, use the assertion helpers:

.. code-block:: python

    from valid8r.testing import assert_maybe_success, assert_maybe_failure
    from valid8r.core.maybe import Maybe

    def test_successful_validation():
        result = validate_age(30)  # Returns Maybe.success(30)
        assert assert_maybe_success(result, 30)

    def test_failed_validation():
        result = validate_age(-5)  # Returns Maybe.failure("Age must be positive")
        assert assert_maybe_failure(result, "Age must be positive")

These helpers simplify assertions on Maybe objects and provide clear failure messages.

Generating Test Cases
---------------------

For thorough validator testing, use ``generate_test_cases`` to automatically create relevant test cases:

.. code-block:: python

    from valid8r.testing import generate_test_cases
    from valid8r.validators import minimum, maximum, between

    def test_minimum_validator():
        min_validator = minimum(10)
        test_cases = generate_test_cases(min_validator)

        # test_cases contains both valid and invalid examples
        assert len(test_cases["valid"]) > 0
        assert len(test_cases["invalid"]) > 0

        # Verify that all test cases work as expected
        for value in test_cases["valid"]:
            result = min_validator(value)
            assert result.is_success()

        for value in test_cases["invalid"]:
            result = min_validator(value)
            assert result.is_failure()

Testing Validator Composition
-----------------------------

To test complex validator chains, use ``test_validator_composition``:

.. code-block:: python

    from valid8r.testing import test_validator_composition
    from valid8r.validators import minimum, maximum

    def test_age_validator():
        # Valid age is between 0 and 120
        age_validator = minimum(0) & maximum(120)
        assert test_validator_composition(age_validator)

This function automatically tests the composed validator with appropriate test cases and verifies the behavior is correct.

Property-Based Testing
----------------------

For more exhaustive testing, use ``generate_random_inputs`` to perform property-based testing:

.. code-block:: python

    from valid8r.testing import generate_random_inputs
    from valid8r.validators import minimum

    def test_positive_numbers_property():
        pos_validator = minimum(0)

        # Generate 100 random inputs
        inputs = generate_random_inputs(pos_validator, count=100)

        # Test the property: values >= 0 pass, values < 0 fail
        for value in inputs:
            result = pos_validator(value)
            if value >= 0:
                assert result.is_success()
            else:
                assert result.is_failure()

Example: Testing a User Registration Function
---------------------------------------------

Here's a complete example showing how to test a function that validates user registration:

.. code-block:: python

    # Function being tested
    def register_user(username, age):
        """Register a user with validation."""
        username_result = username_validator(username)
        if username_result.is_failure():
            return Maybe.failure(f"Invalid username: {username_result.error_or('')}")

        age_result = parse_int(str(age)).bind(lambda x: age_validator(x))
        if age_result.is_failure():
            return Maybe.failure(f"Invalid age: {age_result.error_or('')}")

        # Both valid, register the user
        return Maybe.success({
            "username": username,
            "age": age_result.value_or(0)
        })

    # Test function
    def test_register_user():
        # Test valid registration
        result = register_user("johndoe", "25")
        assert assert_maybe_success(result, {"username": "johndoe", "age": 25})

        # Test invalid username
        result = register_user("j", "25")  # Too short
        assert assert_maybe_failure(result, "Invalid username: Username must be at least 3 characters")

        # Test invalid age
        result = register_user("johndoe", "abc")  # Not a number
        assert assert_maybe_failure(result, "Invalid age: Input must be a valid integer")

        result = register_user("johndoe", "-5")  # Negative
        assert assert_maybe_failure(result, "Invalid age: Age must be positive")

Best Practices
--------------

1. **Test both valid and invalid cases**: Always test both successful validations and failures
2. **Test edge cases**: Use `generate_test_cases` to include boundary values
3. **Test composition**: Verify that composed validators work as expected
4. **Use integration tests**: Test your validation logic in the context of your application
5. **Check error messages**: Verify that error messages are helpful and accurate

Using With Pytest
-----------------

Valid8r testing utilities work well with pytest. Here are some tips:

.. code-block:: python

    import pytest
    from valid8r.testing import MockInputContext

    # Fixture for mocking input
    @pytest.fixture
    def mock_input():
        # Will be automatically cleaned up after each test
        with MockInputContext(["test"]) as context:
            yield context

    def test_with_fixture(mock_input):
        result = input("Prompt: ")
        assert result == "test"

Conclusion
----------

Valid8r's testing utilities make it easier to thoroughly test your validation logic, ensuring your application behaves correctly with both valid and invalid inputs.
