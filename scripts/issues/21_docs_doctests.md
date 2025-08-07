Title: Enable doctest/snippet checking for documentation examples
Labels: docs, ci

Add tooling to execute code snippets in the documentation (doctest or equivalent) as part of CI to prevent drift.

Acceptance Criteria:
```gherkin
Feature: Docs tests
  Scenario: Run doctests
    Given the documentation build pipeline
    When I run doctests for user guide and examples
    Then all code snippets pass or are explicitly skipped
```