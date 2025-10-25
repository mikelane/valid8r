Title: Add common validators: matches_regex, in_set, non_empty_string, unique_items, subset_of/superset_of, is_sorted
Labels: enhancement, validators

Expand the validator set to include common patterns while maintaining the `Validator` composition style.

Acceptance Criteria:
```gherkin
Feature: Additional validators
  Scenario: Regex match
    Given "abc123"
    When I validate with matches_regex "^[a-z]+\d+$"
    Then I get Success

  Scenario: Unique items
    Given list [1, 2, 2]
    When I validate with unique_items
    Then I get Failure mentioning "unique"
```