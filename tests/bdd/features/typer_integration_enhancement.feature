Feature: Typer Integration Enhancement
  As a Typer user
  I want seamless valid8r integration
  So that I can add validation to my CLI easily

  Background:
    Given the valid8r library is installed
    And the Typer integration enhancement module exists

  Scenario: Integration is straightforward to use
    Given I use Typer for my CLI
    When I add valid8r validation
    Then integration requires minimal code changes
    And validation errors display nicely in the terminal
    And error messages follow CLI conventions

  Scenario: I can validate command options
    Given I have command-line options
    When I apply validation
    Then invalid values are rejected clearly
    And help text shows what values are acceptable
    And users understand what went wrong

  Scenario: I can validate command arguments
    Given I have command-line arguments
    When I apply validation
    Then validation happens before my command runs
    And the CLI exits appropriately on errors
    And users receive actionable error messages

  Scenario: Async commands work properly
    Given I have async CLI commands
    When I use async validators
    Then validation executes asynchronously
    And Typer's async support is preserved
    And performance is optimal

  Scenario: Examples help me get started quickly
    Given I read the integration documentation
    When I want to implement validation
    Then I see complete working examples
    And I see patterns for my use case
    And I can adapt examples to my needs

  # Detailed scenarios for validator callback pattern
  Scenario: Validator callback factory for port validation
    Given a Typer CLI command with a port option
    When I create a validator callback using valid8r
    Then the callback parses the port using parse_int
    And the callback validates the port is in range 1-65535
    And invalid ports raise typer.BadParameter with the validation error
    And valid ports are returned as integers

  Scenario: Validator callback rejects out-of-range port
    Given a Typer CLI with port validation callback
    When the user provides port value "99999"
    Then Typer raises BadParameter
    And the error message explains the valid range

  Scenario: Validator callback accepts valid port
    Given a Typer CLI with port validation callback
    When the user provides port value "8080"
    Then the command executes successfully
    And the port value is 8080

  # Decorator-based validation scenarios
  Scenario: Decorator-based validation for email
    Given a Typer command decorated with @validate_with
    When the decorator specifies email validation
    And the user provides a valid email "alice@example.com"
    Then the command receives an EmailAddress object
    And the command executes successfully

  Scenario: Decorator-based validation rejects invalid email
    Given a Typer command decorated with @validate_with for email
    When the user provides an invalid email "not-an-email"
    Then Typer raises BadParameter
    And the error message explains the email format

  Scenario: Multiple decorators for multiple parameters
    Given a Typer command with @validate_with for email and age
    When the user provides valid email and age
    Then both parameters are validated and parsed
    And the command receives EmailAddress and int objects

  # Custom type classes scenarios
  Scenario: Custom Email type for type hints
    Given I create an Email type using ValidatedType
    When I use Email in a Typer option type hint
    Then Typer automatically validates email inputs
    And valid emails are parsed to EmailAddress objects
    And invalid emails raise BadParameter

  Scenario: Custom Phone type for type hints
    Given I create a Phone type using ValidatedType
    When I use Phone in a Typer option type hint
    Then Typer automatically validates phone inputs
    And valid phones are parsed to PhoneNumber objects

  Scenario: ValidatedType with optional parameters
    Given I create a Phone type with ValidatedType
    When I use it as an optional parameter
    Then None values are accepted
    And valid phone numbers are parsed
    And invalid phone numbers raise BadParameter

  # Interactive prompt integration scenarios
  Scenario: Interactive prompt with validation
    Given I use validated_prompt in a Typer command
    When the prompt asks for an email address
    And the user enters an invalid email
    Then the prompt re-asks until valid input
    And the function returns a valid EmailAddress

  Scenario: Interactive prompt uses Typer styling
    Given I use validated_prompt with typer_style=True
    When the prompt displays
    Then it uses Typer's echo and style functions
    And the output matches Typer's CLI aesthetic

  Scenario: Interactive prompt with custom retry limit
    Given I use validated_prompt with max_retries=3
    When the user provides invalid input 3 times
    Then the prompt raises a Typer exception
    And the CLI exits with an appropriate error code

  # Async command support scenarios
  Scenario: Async validator with async command
    Given I have an async Typer command
    When I use an async validator from valid8r
    Then the validator executes asynchronously
    And the command waits for validation to complete
    And Typer's async support is preserved

  Scenario: Async validation performance
    Given I have an async validator that checks a database
    When multiple async validations run
    Then they execute concurrently
    And total validation time is optimized

  # Error handling and exit codes scenarios
  Scenario: Validation failure exits with code 2
    Given a Typer CLI with valid8r validation
    When validation fails for user input
    Then Typer exits with code 2
    And the error message is sent to stderr

  Scenario: Validation error includes parameter name
    Given a Typer CLI with named parameters
    When validation fails for parameter "email"
    Then the error message includes "email"
    And users know which parameter to fix

  # Help text and documentation scenarios
  Scenario: Help text shows validation constraints
    Given a Typer CLI with validated port option
    When the user runs --help
    Then the help text shows "Server port (1-65535)"
    And users understand the valid range

  Scenario: Custom help text with ValidatedType
    Given I create a ValidatedType with help text
    When I use it in a Typer option
    Then the help command shows the custom text
    And users understand the validation requirements

  # Testing support scenarios
  Scenario: CliRunner works with validated commands
    Given I test a Typer CLI using CliRunner
    When I invoke a command with valid input
    Then CliRunner captures the output
    And I can assert on the result

  Scenario: CliRunner captures validation errors
    Given I test a Typer CLI using CliRunner
    When I invoke a command with invalid input
    Then CliRunner captures the error output
    And the exit code is 2
    And I can assert on the error message

  Scenario: MockInputContext works with validated_prompt
    Given I test a command with validated_prompt
    When I use MockInputContext to provide input
    Then the prompt receives the mocked input
    And I can test retry behavior

  # Complete example application scenarios
  Scenario: Cloud Config CLI demonstrates all patterns
    Given the example Cloud Config CLI application
    When I examine the code
    Then I see validator callbacks in use
    And I see decorator-based validation
    And I see ValidatedType custom types
    And I see interactive prompts with validation
    And I see comprehensive tests

  Scenario: Example validates AWS ARN format
    Given the Cloud Config CLI with ARN validation
    When the user provides an invalid ARN
    Then the CLI rejects it with a clear message
    And the user knows the correct ARN format

  Scenario: Example validates GCP project ID format
    Given the Cloud Config CLI with GCP validation
    When the user provides an invalid project ID
    Then the CLI rejects it with a clear message
    And the user knows the correct format

  Scenario: Example interactive mode with config file
    Given the Cloud Config CLI in interactive mode
    When the CLI prompts for configuration values
    Then each prompt validates user input
    And invalid inputs are rejected with clear messages
    And the CLI generates a valid config file
