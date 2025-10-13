Feature: Clean Type Parsing
  As a developer
  I want to parse string inputs into various Python types
  So that I can safely work with typed data in my applications

  Background:
    Given the input validation module is available

  Scenario: Successfully parse string to integer
    When I parse "42" to integer type
    Then the result should be a successful Maybe with value 42

  Scenario: Successfully parse string to float
    When I parse "3.14159" to float type
    Then the result should be a successful Maybe with value 3.14159

  Scenario: Successfully parse string to boolean
    When I parse "true" to boolean type
    Then the result should be a successful Maybe with value True

  Scenario Outline: Successfully parse various boolean string representations
    When I parse "<input>" to boolean type
    Then the result should be a successful Maybe with value <expected>

    Examples:
      | input    | expected |
      | true     | True     |
      | True     | True     |
      | TRUE     | True     |
      | t        | True     |
      | 1        | True     |
      | yes      | True     |
      | y        | True     |
      | false    | False    |
      | False    | False    |
      | FALSE    | False    |
      | f        | False    |
      | 0        | False    |
      | no       | False    |
      | n        | False    |

  Scenario: Successfully parse string to date
    When I parse "2023-01-15" to date type
    Then the result should be a successful Maybe with date value "2023-01-15"

  Scenario Outline: Successfully parse dates in different formats
    When I parse "<input>" to date type with format "<format>"
    Then the result should be a successful Maybe with date value "<expected>"

    Examples:
      | input            | format       | expected    |
      | 2023-01-15       | %Y-%m-%d     | 2023-01-15  |
      | 15/01/2023       | %d/%m/%Y     | 2023-01-15  |
      | Jan 15, 2023     | %b %d, %Y    | 2023-01-15  |
      | 20230115         | %Y%m%d       | 2023-01-15  |

  Scenario: Parse empty string to integer
    When I parse "" to integer type
    Then the result should be a failure Maybe with error "Input must not be empty"

  Scenario: Parse non-numeric string to integer
    When I parse "abc" to integer type
    Then the result should be a failure Maybe with error "Input must be a valid integer"

  Scenario: Parse decimal string to integer
    When I parse "42.5" to integer type
    Then the result should be a failure Maybe with error "Input must be a valid integer"

  Scenario: Parse non-numeric string to float
    When I parse "abc" to float type
    Then the result should be a failure Maybe with error "Input must be a valid number"

  Scenario: Parse non-boolean string to boolean
    When I parse "not-a-boolean" to boolean type
    Then the result should be a failure Maybe with error "Input must be a valid boolean"

  Scenario: Parse invalid date string to date
    When I parse "2023-13-45" to date type
    Then the result should be a failure Maybe with error "Input must be a valid date"

  Scenario: Parse string with leading/trailing whitespace
    When I parse "  42  " to integer type
    Then the result should be a successful Maybe with value 42

  Scenario: Parse complex number string
    When I parse "3+4j" to complex type
    Then the result should be a successful Maybe with complex value (3+4j)

  Scenario: Parse custom type using provided parser function
    Given I have a custom parser for "IPAddress" type
    When I parse "192.168.1.1" using the custom parser
    Then the result should be a successful Maybe with the parsed IP address

  Scenario: Parse with custom error message
    When I parse "abc" to integer type with error message "Please provide a number"
    Then the result should be a failure Maybe with error "Please provide a number"

  Scenario: Parse very large integer
    Given the input validation module is available
    When I parse "999999999999999999999999999999" to integer type
    Then the result should be a successful Maybe with value 999999999999999999999999999999

  Scenario: Parse string to enum
    Given I have defined an enum "Color" with values "RED,GREEN,BLUE"
    When I parse "RED" to the Color enum type
    Then the result should be a successful Maybe with the RED enum value

  Scenario: Parse custom type using create_parser
    Given I have created a custom parser for "IPAddress" type using create_parser
    When I parse "192.168.1.1" using the custom parser
    Then the result should be a successful Maybe with the parsed IP address

  Scenario: Create parser using make_parser decorator
  Given I have defined a parser using the make_parser decorator for "Decimal" values
  When I parse "123.45" using the decorated parser
  Then the result should be a successful Maybe with decimal value 123.45

Scenario: Handle errors with make_parser decorator
  Given I have defined a parser using the make_parser decorator for "Decimal" values
  When I parse "not-a-decimal" using the decorated parser
  Then the result should be a failure Maybe with error "Invalid format for parse_decimal, error: [<class 'decimal.ConversionSyntax'>]"

Scenario: Parse empty string with decorated parser
  Given I have defined a parser using the make_parser decorator for "Decimal" values
  When I parse "" using the decorated parser
  Then the result should be a failure Maybe with error "Input must not be empty"
