Title: Add unit test for top-level public imports
Labels: tests, api

Add a simple unit test to ensure `from valid8r import parsers, validators, prompt, Maybe` works, preventing regressions in public API.

Acceptance Criteria:
```gherkin
Feature: Public API stability tests
  Scenario: Import smoke test
    Given a fresh test environment
    When I run a test that imports "parsers, validators, prompt, Maybe" from "valid8r"
    Then the test should pass without ImportError
```