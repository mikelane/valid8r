Feature: Pluggable IO Provider
  As a developer
  I want to use pluggable IO providers for prompt functions
  So that I can test prompts without monkeypatching builtins and support alternative UIs

  Background:
    Given the IO provider module is available

  Scenario: Using BuiltinIOProvider for standard CLI interaction
    Given a BuiltinIOProvider instance
    When I call input with prompt "Name: " and builtins returns "Alice"
    Then the provider returns "Alice"

  Scenario: Using BuiltinIOProvider for output messages
    Given a BuiltinIOProvider instance
    When I call output with message "Hello, world!"
    Then the message is printed to stdout

  Scenario: Using BuiltinIOProvider for error messages
    Given a BuiltinIOProvider instance
    When I call error with message "Invalid input"
    Then the message is printed to stderr

  Scenario: Using TestIOProvider for non-interactive testing
    Given a TestIOProvider with inputs "42" and "yes"
    When I call input twice
    Then the first input returns "42"
    And the second input returns "yes"

  Scenario: TestIOProvider raises error when inputs exhausted
    Given a TestIOProvider with input "only-one"
    When I call input once successfully
    And I call input again
    Then a RuntimeError is raised with message "No more test inputs available"

  Scenario: TestIOProvider captures output messages
    Given a TestIOProvider with no inputs
    When I call output with "Message 1"
    And I call output with "Message 2"
    Then the captured outputs are "Message 1" and "Message 2"

  Scenario: TestIOProvider captures error messages
    Given a TestIOProvider with no inputs
    When I call error with "Error 1"
    And I call error with "Error 2"
    Then the captured errors are "Error 1" and "Error 2"

  Scenario: Using IO provider with ask function for successful input
    Given a TestIOProvider with input "42"
    When I ask for a number with integer parser using the provider
    Then the prompt result is successful with value 42

  Scenario: Using IO provider with ask function for validation errors
    Given a TestIOProvider with inputs "invalid" and "42"
    When I ask for a number with retry enabled using the provider
    Then the prompt result is successful with value 42
    And the provider captured one error message

  Scenario: Using IO provider with ask function and default value
    Given a TestIOProvider with empty input
    When I ask for a port number with default 8080 using the provider
    Then the prompt result is successful with value 8080

  Scenario: Creating custom IO provider
    Given a custom IO provider that prefixes all prompts with "CUSTOM: "
    When I ask for user input "test" using the custom provider
    Then the custom provider received prompt "CUSTOM: Enter value: "
    And the prompt result is successful with value "test"

  Scenario: Custom IO provider with color-coded error messages
    Given a custom IO provider that adds color codes to errors
    When I provide invalid input "abc" using the custom provider
    Then the custom provider captured error with color codes
    And the custom error message contains "valid integer"

  Scenario: Using ask function without IO provider defaults to BuiltinIOProvider
    When I call ask without specifying an IO provider
    Then the function uses builtins.input internally
    And the prompt succeeds

  Scenario: Multiple sequential prompts with TestIOProvider
    Given a TestIOProvider with inputs "Alice", "30", and "yes"
    When I ask for name, age, and confirmation using the provider
    Then the name result is successful with value "Alice"
    And the age result is successful with value 30
    And the confirmation result is successful with value True

  Scenario: Verifying IO provider protocol compliance
    Given a BuiltinIOProvider instance
    Then it implements the IOProvider protocol
    And it has input, output, and error methods

  Scenario: Verifying TestIOProvider protocol compliance
    Given a TestIOProvider with input "test"
    Then it implements the IOProvider protocol
    And it has input, output, and error methods
