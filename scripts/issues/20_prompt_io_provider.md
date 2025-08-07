Title: Make prompt IO provider pluggable for non-interactive and TUI environments
Labels: enhancement, prompt

Refactor prompt input/output to use an injectable IO provider interface, defaulting to builtins, to support non-interactive testing and alternative UIs.

Acceptance Criteria:
```gherkin
Feature: Pluggable prompt IO
  Scenario: Custom IO provider
    Given a custom input/output provider
    When I call prompt.ask with the provider
    Then user interaction uses the provider
    And unit tests can simulate input/output without monkeypatching builtins
```