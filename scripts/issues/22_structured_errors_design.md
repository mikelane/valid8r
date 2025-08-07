Title: Design structured error model and migration plan (codes, paths, context)
Labels: design, enhancement

Design a structured error object that can carry code/message/path/context and evaluate how to integrate it with `Maybe` or a new `Result`, with backward compatibility.

Acceptance Criteria:
```gherkin
Feature: Structured errors design
  Scenario: Design document approved
    Given a design markdown document under docs/development
    When it is reviewed by maintainers
    Then it outlines the data model, API signatures, compatibility plan, and migration steps
```