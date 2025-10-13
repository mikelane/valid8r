Feature: Validators
  As a developer
  I want to validate values against specific criteria
  So that I can ensure data quality in my applications

  Background:
    Given the validation module is available

  Scenario: Successfully validate a value above minimum
    When I validate 42 against a minimum of 0
    Then the validation result should be a successful Maybe with value 42

  Scenario: Fail validation for a value below minimum
    When I validate -5 against a minimum of 0
    Then the validation result should be a failure Maybe with error "Value must be at least 0"

  Scenario: Successfully validate a value below maximum
    When I validate 42 against a maximum of 100
    Then the validation result should be a successful Maybe with value 42

  Scenario: Fail validation for a value above maximum
    When I validate 150 against a maximum of 100
    Then the validation result should be a failure Maybe with error "Value must be at most 100"

  Scenario: Successfully validate a value within range
    When I validate 42 against a range of 0 to 100
    Then the validation result should be a successful Maybe with value 42

  Scenario: Fail validation for a value outside range
    When I validate 150 against a range of 0 to 100
    Then the validation result should be a failure Maybe with error "Value must be between 0 and 100"

  Scenario: Successfully validate a string length
    When I validate "hello" against a length of 3 to 10
    Then the validation result should be a successful Maybe with string value "hello"

  Scenario: Fail validation for a string too short
    When I validate "hi" against a length of 3 to 10
    Then the validation result should be a failure Maybe with error "String length must be between 3 and 10"

  Scenario: Fail validation for a string too long
    When I validate "hello world this is too long" against a length of 3 to 10
    Then the validation result should be a failure Maybe with error "String length must be between 3 and 10"

  Scenario: Successfully validate a value with custom predicate
    When I validate 42 with a predicate "Value must be even" that checks if a value is even
    Then the validation result should be a successful Maybe with value 42

  Scenario: Fail validation with custom predicate
    When I validate 43 with a predicate "Value must be even" that checks if a value is even
    Then the validation result should be a failure Maybe with error "Value must be even"

  Scenario: Validate with custom error message
    When I validate -5 against a minimum of 0 with error message "Must be positive"
    Then the validation result should be a failure Maybe with error "Must be positive"
