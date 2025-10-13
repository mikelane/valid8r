Feature: Interactive Prompts
  As a developer
  I want to prompt users for input with validation
  So that I can collect valid data interactively

  Background:
    Given the prompt module is available

  Scenario: Successfully prompt for valid input
    When basic prompt "Enter a number: " receives "42"
    Then prompt result is successful with value "42"

  Scenario: Successfully prompt for valid input with parsing
    When int parser prompt "Enter a number: " receives "42"
    Then prompt result is successful with value 42

  Scenario: Successfully prompt for valid input with validation
    When prompt "Enter a positive number: " with minimum 0 validation receives "42"
    Then prompt result is successful with value 42

  Scenario: Fail validation on prompt
    When prompt "Enter a positive number: " with minimum 0 validation receives "-5"
    Then prompt result is failure with error "Value must be at least 0"

  Scenario: Successfully prompt with default value
    When prompt "Enter a number: " with default 10 receives ""
    Then prompt result is successful with value 10

  Scenario: Successfully retry on invalid input
    When retry prompt "Enter a number: " receives inputs "abc" then "42"
    Then prompt result is successful with value 42

  Scenario: Successfully prompt with custom error message
    When custom error prompt "Enter a number: " with message "Please enter a valid number" receives "abc"
    Then prompt result is failure with error "Please enter a valid number"

  Scenario: Successfully limit retry attempts
    When limited retry prompt "Enter a number: " with 2 attempts receives "abc", "def", "42"
    Then prompt result is successful with value 42

  Scenario: Fail after maximum retries
    When limited retry prompt "Enter a number: " with 2 attempts receives "abc", "def", "ghi"
    Then prompt result is failure
