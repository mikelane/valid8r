Title: Add Click/Typer integration with Valid8r-backed ParamTypes
Labels: enhancement, docs, integration

Provide wrappers or ParamTypes to use Valid8r parsers inside Click/Typer commands. Include documentation and examples.

Acceptance Criteria:
```gherkin
Feature: Click/Typer integration
  Scenario: Use a Valid8r-backed Click option
    Given a click command using a Valid8r-backed ParamType for UUID
    When I pass an invalid UUID
    Then Click shows an error produced by Valid8r
```