Testing Valid8r
===============

Valid8r uses a comprehensive testing strategy to ensure reliability and correctness. This document provides information about the testing framework and how to write and run tests.

Testing Framework
-----------------

Valid8r uses several testing tools:

1. **pytest**: For unit testing
2. **behave**: For behavior-driven development (BDD) testing
3. **tox**: For testing across multiple Python versions
4. **coverage**: For measuring test coverage

Directory Structure
-------------------

The test directory structure is organized as follows:

.. code-block:: text

   tests/
   ├── __init__.py
   ├── bdd/                 # Behavior-driven tests
   │   ├── __init__.py
   │   ├── conftest.py
   │   ├── environment.py
   │   ├── features/        # Feature files
   │   │   └── clean_type_parsing.feature
   │   └── steps/           # Step implementations
   │       ├── __init__.py
   │       └── clean_type_parsing_steps.py
   ├── integration/         # Integration tests
   │   ├── __init__.py
   │   └── test_validator.py
   └── unit/                # Unit tests
       ├── __init__.py
       ├── test_combinators.py
       ├── test_maybe.py
       ├── test_parsers.py
       ├── test_prompt.py
       └── test_validators.py

Running Tests
-------------

You can run tests using uv or tox:

.. code-block:: bash

   # Run all tests with the current Python version
   uv run pytest

   # Run only unit tests
   uv run pytest tests/unit

   # Run only BDD tests
   uv run behave tests/bdd/features

   # Run tests with coverage
   uv run pytest --cov=valid8r tests/unit

   # Run tests across all supported Python versions (3.11-3.14)
   uv run tox

   # Run tests for a specific Python version
   uv run tox -e py313  # primary dev version
   uv run tox -e py311  # minimum supported
   uv run tox -e py314  # latest supported

   # Run only BDD tests with tox
   uv run tox -e bdd

Continuous Integration
----------------------

Valid8r uses GitHub Actions for continuous integration. The CI pipeline runs:

1. Tests across all supported Python versions (3.11, 3.12, 3.13, 3.14)
2. Code quality checks (ruff, isort, mypy)
3. Documentation builds
4. Coverage reporting

The migration to uv has resulted in approximately 60% faster CI pipelines compared to Poetry.

Writing Unit Tests
------------------

Valid8r uses pytest for unit testing. Here are some guidelines for writing unit tests:

1. **Test file naming**: Test files should be named with the prefix `test_`.
2. **Test function naming**: Test functions should start with `it_` to describe what they test.
3. **Test classes**: Use classes to group related tests, prefixed with `Describe`.

Example:

.. code-block:: python

   from valid8r.core.maybe import Maybe

   class DescribeMaybe:
       def it_creates_just_values(self):
           maybe = Maybe.just(42)
           assert maybe.is_just()
           assert maybe.value() == 42

       def it_creates_nothing_values(self):
           maybe = Maybe.nothing("Error")
           assert maybe.is_nothing()
           assert maybe.error() == "Error"

Mocking
-------

For tests that require mocking, Valid8r uses the `unittest.mock` module from the standard library:

.. code-block:: python

   from unittest.mock import patch

   class DescribePrompt:
       @patch('builtins.input', return_value='42')
       @patch('builtins.print')
       def it_handles_user_input(self, mock_print, mock_input):
           from valid8r.prompt.basic import ask

           result = ask("Enter a number: ")

           # Verify input was called
           mock_input.assert_called_once_with("Enter a number: ")

           # Verify result
           assert result.is_just()
           assert result.value() == '42'

Writing BDD Tests
-----------------

Valid8r uses behave for BDD testing. BDD tests consist of feature files and step implementations.

Feature Files
~~~~~~~~~~~~~

Feature files use Gherkin syntax to describe functionality from a user perspective:

.. code-block:: gherkin

   Feature: Clean Type Parsing
     As a developer
     I want to parse string inputs into various Python types
     So that I can safely work with typed data in my applications

     Scenario: Successfully parse string to integer
       When I parse "42" to integer type
       Then the result should be a successful Maybe with value 42

     Scenario: Parse non-numeric string to integer
       When I parse "abc" to integer type
       Then the result should be a failure Maybe with error "Input must be a valid integer"

Step Implementations
~~~~~~~~~~~~~~~~~~~~

Step implementations connect the Gherkin scenarios to the actual code:

.. code-block:: python

   from behave import when, then
   from valid8r import parsers

   @when('I parse "{input_str}" to integer type')
   def step_parse_to_integer(context, input_str):
       context.result = parsers.parse_int(input_str)

   @then('the result should be a successful Maybe with value {expected:d}')
   def step_result_is_success_with_value(context, expected):
       assert context.result.is_just(), f"Expected success but got failure: {context.result}"
       assert context.result.value() == expected, f"Expected {expected} but got {context.result.value()}"

   @then('the result should be a failure Maybe with error "{expected_error}"')
   def step_result_is_failure_with_error(context, expected_error):
       assert context.result.is_nothing(), f"Expected failure but got success: {context.result}"
       assert context.result.error() == expected_error, f"Expected '{expected_error}' but got '{context.result.error()}'"

Test Coverage
-------------

Valid8r aims for high test coverage. You can generate a coverage report with:

.. code-block:: bash

   uv run pytest --cov=valid8r tests/
   uv run coverage report -m
   uv run coverage html

The coverage report in HTML format will be generated in the `htmlcov` directory.

Debugging Tests
---------------

When tests fail, you can use the following options to help debug:

.. code-block:: bash

   # Show print statements during tests
   uv run pytest -s

   # Increase verbosity
   uv run pytest -v

   # Run a specific test
   uv run pytest tests/unit/test_maybe.py::DescribeMaybe::it_creates_just_values

   # For BDD tests, run a specific scenario
   uv run behave tests/bdd/features/clean_type_parsing.feature:12

Testing Edge Cases
------------------

Valid8r strives to test all edge cases thoroughly:

1. **Empty inputs**: Test how functions handle empty strings, empty lists, etc.
2. **Boundary values**: Test values at the boundaries of valid ranges
3. **Invalid inputs**: Test how functions handle various types of invalid input
4. **Error messages**: Verify that error messages are clear and helpful
5. **Complex chains**: Test complex combinations of validators and parsers

Creating Test Fixtures
----------------------

For complex test setups, consider creating fixtures in `conftest.py`:

.. code-block:: python

   import pytest
   from valid8r import validators

   @pytest.fixture
   def valid_age_validator():
       return validators.between(0, 120, "Age must be between 0 and 120")

   @pytest.fixture
   def sample_user_data():
       return {
           "name": "John Doe",
           "email": "john@example.com",
           "age": 30
       }

Then use these fixtures in your tests:

.. code-block:: python

   def test_user_validation(valid_age_validator, sample_user_data):
       result = valid_age_validator(sample_user_data["age"])
       assert result.is_just()

Best Practices
--------------

1. **Test one thing per test**: Each test should focus on testing one specific functionality
2. **Make tests isolated**: Tests should not depend on each other
3. **Keep tests fast**: Minimize external dependencies in tests
4. **Use descriptive names**: Test names should clearly indicate what is being tested
5. **Test edge cases**: Include tests for boundary conditions and error cases
6. **Use parameterized tests**: For testing the same functionality with different inputs
