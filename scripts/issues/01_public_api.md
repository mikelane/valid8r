Title: Expose stable public API at top-level package
Labels: enhancement, api

Create public re-exports at the `valid8r` package root so users can do concise imports as shown in the docs.

Scope:
- Re-export `parsers`, `validators`, `combinators`, `prompt` (with `ask`), and `Maybe` from the top-level package.
- Keep backward compatibility for existing deep imports.
- Add a unit test that asserts these imports succeed.

Acceptance Criteria:
```gherkin
Feature: Public API re-exports
  Scenario: Import core modules from top-level
    Given a Python environment with valid8r installed
    When I run "from valid8r import parsers, validators, prompt"
    Then the import should succeed without errors

  Scenario: Import Maybe types from top-level
    Given a Python environment with valid8r installed
    When I run "from valid8r import Maybe"
    Then the import should succeed

  Scenario: Top-level ask function
    Given a Python environment with valid8r installed
    When I run "from valid8r import prompt" and access "prompt.ask"
    Then "prompt.ask" should be callable
```