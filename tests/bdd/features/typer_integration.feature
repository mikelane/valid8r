Feature: Typer CLI integration
  As a CLI developer using Typer
  I want to use valid8r parsers for CLI argument validation
  So that I can validate user input with the same parsers I use in FastAPI

  Background:
    Given the valid8r.integrations.typer module exists
    And I have imported TyperParser

  Scenario: Validate email address in CLI option
    Given a Typer CLI with option using TyperParser(parse_email)
    When the user provides valid email "alice@example.com"
    Then the CLI accepts the input
    And the parsed value is an EmailAddress with local "alice" and domain "example.com"

  Scenario: Reject invalid email with helpful error
    Given a Typer CLI with option using TyperParser(parse_email)
    When the user provides invalid email "not-an-email"
    Then the CLI rejects the input
    And the error message mentions "@-sign"

  Scenario: Validate phone number in CLI option
    Given a Typer CLI with option using TyperParser(parse_phone)
    When the user provides valid phone "(415) 234-5678"
    Then the CLI accepts the input
    And the parsed value is a PhoneNumber with area code "415"

  Scenario: Reject invalid phone with error
    Given a Typer CLI with option using TyperParser(parse_phone)
    When the user provides invalid phone "123"
    Then the CLI rejects the input
    And the error message mentions "phone"

  Scenario: Use chained validators for port number
    Given a parser with parse_int & minimum(1) & maximum(65535)
    And a Typer CLI with option using TyperParser(parser)
    When the user provides port "0"
    Then the CLI rejects the input
    And the error message mentions "at least 1"

  Scenario: Accept valid port with chained validators
    Given a parser with parse_int & minimum(1) & maximum(65535)
    And a Typer CLI with option using TyperParser(parser)
    When the user provides port "8080"
    Then the CLI accepts the input
    And the parsed value equals 8080

  Scenario: Validate UUID in CLI argument
    Given a Typer CLI with argument using TyperParser(parse_uuid)
    When the user provides valid UUID "550e8400-e29b-41d4-a716-446655440000"
    Then the CLI accepts the input
    And the parsed value is a UUID

  Scenario: Reject invalid UUID in CLI argument
    Given a Typer CLI with argument using TyperParser(parse_uuid)
    When the user provides invalid UUID "not-a-uuid"
    Then the CLI rejects the input
    And the error message mentions "valid UUID"

  Scenario: Validate IP address in CLI option
    Given a Typer CLI with option using TyperParser(parse_ipv4)
    When the user provides valid IP "192.168.1.1"
    Then the CLI accepts the input
    And the parsed value is an IPv4Address

  Scenario: Use custom error prefix for clarity
    Given a Typer CLI with TyperParser(parse_email, error_prefix="Email address")
    When the user provides invalid email "bad"
    Then the CLI rejects the input
    And the error message mentions "Email address must"

  Scenario: Multiple validated options in one command
    Given a Typer CLI with email option using TyperParser(parse_email)
    And the same CLI has phone option using TyperParser(parse_phone)
    When the user provides both email "user@example.com" and phone "(415) 234-5678"
    Then the CLI accepts both inputs
    And both values are correctly parsed

  Scenario: Custom name for Typer parameter type
    Given a Typer CLI with TyperParser(parse_int, name="port_number")
    When the user requests help for the CLI
    Then the help text shows type "PORT_NUMBER"
