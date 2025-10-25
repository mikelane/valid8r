Title: Dataclass integration for field-level validation
Labels: enhancement, integration

Provide helpers or a decorator to validate dataclass instances using type hints and optional metadata for field validators.

Acceptance Criteria:
```gherkin
Feature: Dataclass validation
  Scenario: Validate dataclass fields
    Given a dataclass User(name: str, age: int)
    And declared validators length(1,100) for name and between(0,120) for age
    When I validate an instance with invalid values
    Then I receive a report listing field-specific errors
```