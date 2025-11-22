Feature: Type-Based Parser Generation
  As a developer using valid8r
  I want to generate parsers automatically from Python type annotations
  So that I can validate inputs without manually creating parser functions

  Background:
    Given the type adapter module is available

  # Rule 1: Basic Types - Generate parsers for Python built-in types

  Scenario Outline: Generate parser for basic types
    Given the type annotation <type_annotation>
    When a parser is generated from the type
    And the generated parser processes "<input>"
    Then the result is a successful Maybe with value <expected>

    Examples:
      | type_annotation | input    | expected |
      | int             | 42       | 42       |
      | int             | -100     | -100     |
      | str             | hello    | hello    |
      | float           | 3.14     | 3.14     |
      | bool            | true     | True     |
      | bool            | false    | False    |

  Scenario Outline: Generated parser rejects invalid input
    Given the type annotation <type_annotation>
    When a parser is generated from the type
    And the generated parser processes "<input>"
    Then the result is a failed Maybe
    And the error contains "<error_fragment>"

    Examples:
      | type_annotation | input   | error_fragment    |
      | int             | abc     | valid integer     |
      | int             | 3.14    | valid integer     |
      | float           | xyz     | valid number      |
      | bool            | maybe   | valid boolean     |

  # Rule 2: Optional Types - Handle None values gracefully

  Scenario: Generate parser for Optional type with valid value
    Given the type annotation Optional[int]
    When a parser is generated from the type
    And the generated parser processes "42"
    Then the result is a successful Maybe with value 42

  Scenario: Generate parser for Optional type with None value
    Given the type annotation Optional[int]
    When a parser is generated from the type
    And the generated parser processes an empty string
    Then the result is a successful Maybe with None value

  Scenario: Generate parser for Optional type with invalid value
    Given the type annotation Optional[int]
    When a parser is generated from the type
    And the generated parser processes "invalid"
    Then the result is a failed Maybe
    And the error contains "valid integer"

  # Rule 3: Collection Types - Handle lists, sets, and dicts

  Scenario: Generate parser for list with valid elements
    Given the type annotation list[int]
    When a parser is generated from the type
    And the generated parser processes "[1, 2, 3]"
    Then the result is a successful Maybe with list [1, 2, 3]

  Scenario: Generate parser for list with invalid element
    Given the type annotation list[int]
    When a parser is generated from the type
    And the generated parser processes '[1, "invalid", 3]'
    Then the result is a failed Maybe
    And the error contains "valid integer"

  Scenario: Generate parser for set with unique elements
    Given the type annotation set[str]
    When a parser is generated from the type
    And the generated parser processes '["a", "b", "c"]'
    Then the result is a successful Maybe with set containing a, b, c

  Scenario: Generate parser for dictionary with valid key-value pairs
    Given the type annotation dict[str, int]
    When a parser is generated from the type
    And the generated parser processes '{"age": 30, "count": 5}'
    Then the result is a successful Maybe with dict containing age=30 and count=5

  Scenario: Generate parser for dictionary with invalid value type
    Given the type annotation dict[str, int]
    When a parser is generated from the type
    And the generated parser processes '{"age": "thirty"}'
    Then the result is a failed Maybe
    And the error contains "valid integer"

  # Rule 4: Nested Types - Handle complex nested structures

  Scenario: Generate parser for nested list
    Given the type annotation list[list[int]]
    When a parser is generated from the type
    And the generated parser processes "[[1, 2], [3, 4]]"
    Then the result is a successful Maybe with nested list [[1, 2], [3, 4]]

  Scenario: Generate parser for list of dictionaries
    Given the type annotation list[dict[str, int]]
    When a parser is generated from the type
    And the generated parser processes '[{"a": 1}, {"b": 2}]'
    Then the result is a successful Maybe with list of dictionaries

  Scenario: Generate parser for deeply nested structure
    Given the type annotation dict[str, list[int]]
    When a parser is generated from the type
    And the generated parser processes '{"scores": [95, 87, 92]}'
    Then the result is a successful Maybe with nested structure

  # Rule 5: Union Types - Handle multiple possible types

  Scenario Outline: Generate parser for Union type
    Given the type annotation Union[int, str]
    When a parser is generated from the type
    And the generated parser processes "<input>"
    Then the result is a successful Maybe with value <expected>

    Examples:
      | input  | expected |
      | 42     | 42       |
      | hello  | hello    |

  Scenario: Generate parser for Union type tries all alternatives
    Given the type annotation Union[int, float, str]
    When a parser is generated from the type
    And the generated parser processes "3.14"
    Then the result is a successful Maybe with value 3.14

  # Rule 6: Literal Types - Restrict to specific values

  Scenario Outline: Generate parser for Literal type with valid value
    Given the type annotation Literal['red', 'green', 'blue']
    When a parser is generated from the type
    And the generated parser processes "<input>"
    Then the result is a successful Maybe with value <expected>

    Examples:
      | input | expected |
      | red   | red      |
      | green | green    |
      | blue  | blue     |

  Scenario: Generate parser for Literal type rejects invalid value
    Given the type annotation Literal['red', 'green', 'blue']
    When a parser is generated from the type
    And the generated parser processes "yellow"
    Then the result is a failed Maybe
    And the error contains "must be one of"

  Scenario: Generate parser for Literal with mixed types
    Given the type annotation Literal[1, 'one', True]
    When a parser is generated from the type
    And the generated parser processes "one"
    Then the result is a successful Maybe with value one

  # Rule 7: Enum Types - Support Python enumerations

  Scenario: Generate parser for Enum type with valid member
    Given an enum Color with members RED, GREEN, BLUE
    And the type annotation Color
    When a parser is generated from the type
    And the generated parser processes "RED"
    Then the result is a successful Maybe with enum member Color.RED

  Scenario: Generate parser for Enum type rejects invalid member
    Given an enum Color with members RED, GREEN, BLUE
    And the type annotation Color
    When a parser is generated from the type
    And the generated parser processes "YELLOW"
    Then the result is a failed Maybe
    And the error contains "valid enumeration"

  Scenario: Generate parser for Enum handles case-insensitive matching
    Given an enum Status with members ACTIVE, INACTIVE
    And the type annotation Status
    When a parser is generated from the type
    And the generated parser processes "active"
    Then the result is a successful Maybe with enum member Status.ACTIVE

  # Rule 8: Annotated Types - Support metadata constraints

  Scenario: Generate parser for Annotated type ignores metadata
    Given the type annotation Annotated[int, "must be positive"]
    When a parser is generated from the type
    And the generated parser processes "42"
    Then the result is a successful Maybe with value 42

  Scenario: Generate parser for Annotated type with validator metadata
    Given the type annotation Annotated[int, validators.minimum(0)]
    When a parser is generated from the type
    And the generated parser processes "-5"
    Then the result is a failed Maybe
    And the error contains "at least 0"

  Scenario: Generate parser for Annotated type chains validators
    Given the type annotation Annotated[int, validators.minimum(0), validators.maximum(100)]
    When a parser is generated from the type
    And the generated parser processes "150"
    Then the result is a failed Maybe
    And the error contains "at most 100"

  # Rule 9: Error Handling - Graceful failures

  Scenario: Reject unsupported type annotation
    Given the type annotation typing.Callable
    When a parser generation is attempted from the type
    Then the generation fails with error "Unsupported type"

  Scenario: Reject forward reference without context
    Given the type annotation "SomeClass"
    When a parser generation is attempted from the type
    Then the generation fails with error "Invalid type annotation"

  Scenario: Handle None type annotation
    Given a None type annotation
    When a parser generation is attempted from the type
    Then the generation fails with error "Type annotation required"

  # Rule 10: Type Preservation - Generated parsers match annotation semantics

  Scenario: Generated parser returns correct type
    Given the type annotation int
    When a parser is generated from the type
    And the generated parser processes "42"
    Then the result value has Python type int

  Scenario: Generated parser for Optional preserves None
    Given the type annotation Optional[str]
    When a parser is generated from the type
    And the generated parser processes an empty string
    Then the result value is Python None

  Scenario: Generated parser for list returns Python list
    Given the type annotation list[int]
    When a parser is generated from the type
    And the generated parser processes "[1, 2, 3]"
    Then the result value has Python type list
