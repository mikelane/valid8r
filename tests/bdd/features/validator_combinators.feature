Feature: Validator Combinators
  As a developer
  I want to combine validators with logical operations
  So that I can create complex validation rules

  Background:
    Given the combinator module is available

  Scenario: Successfully validate with AND combinator
    When I validate 42 against a validator that combines minimum 0 AND maximum 100
    Then the combinator result should be a successful Maybe with value 42

  Scenario: Fail validation with AND combinator (first validator)
    When I validate -5 against a validator that combines minimum 0 AND maximum 100
    Then the combinator result should be a failure Maybe with error "Value must be at least 0"

  Scenario: Fail validation with AND combinator (second validator)
    When I validate 150 against a validator that combines minimum 0 AND maximum 100
    Then the combinator result should be a failure Maybe with error "Value must be at most 100"

  Scenario: Successfully validate with OR combinator (first validator)
    When I validate 42 against a validator that combines "is even" OR "is divisible by 5"
    Then the combinator result should be a successful Maybe with value 42

  Scenario: Successfully validate with OR combinator (second validator)
    When I validate 25 against a validator that combines "is even" OR "is divisible by 5"
    Then the combinator result should be a successful Maybe with value 25

  Scenario: Fail validation with OR combinator (both validators)
    When I validate 7 against a validator that combines "is even" OR "is divisible by 5"
    Then the combinator result should be a failure Maybe

  Scenario: Successfully validate with NOT combinator
    When I validate 7 against a validator that negates "is even"
    Then the combinator result should be a successful Maybe with value 7

  Scenario: Fail validation with NOT combinator
    When I validate 42 against a validator that negates "is even"
    Then the combinator result should be a failure Maybe

  Scenario: Successfully validate with complex combinators
    When I validate 42 against a validator that combines minimum 0 AND (is even OR is divisible by 5)
    Then the combinator result should be a successful Maybe with value 42

  Scenario: Successfully validate with operator overloading
    When I validate 42 against a validator created with operator &
    Then the combinator result should be a successful Maybe with value 42

  Scenario: Fail validation with operator overloading
    When I validate -5 against a validator created with operator &
    Then the combinator result should be a failure Maybe
