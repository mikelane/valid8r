Title: Add FastAPI/Pydantic usage example in documentation
Labels: docs, integration

Create a documentation page showing how to apply Valid8r for transformations and validations with FastAPI and/or Pydantic validators.

Acceptance Criteria:
```gherkin
Feature: FastAPI example
  Scenario: Example demonstrates request validation
    Given the FastAPI example in docs
    When I run the app and call the endpoint with invalid input
    Then the response contains a clear validation error message
```