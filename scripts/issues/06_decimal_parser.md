Title: Add Decimal parser and ensure validators work with Decimal
Labels: enhancement, parsers, validators

Implement `parse_decimal` using `decimal.Decimal`, and verify numeric validators operate correctly with `Decimal` values.

Acceptance Criteria:
```gherkin
Feature: Decimal parsing and validation
  Scenario Outline: Parse valid decimals
    Given the input "<text>"
    When I call parse_decimal
    Then I get Success with Decimal("<expected>")
    Examples:
      | text  | expected |
      | 1.23  | 1.23     |
      | 0     | 0        |
      | -10.5 | -10.5    |

  Scenario: Reject invalid decimal
    Given the input "abc"
    When I call parse_decimal
    Then I get Failure with message containing "valid number"
```