Feature: Dataclass Field Validation
  As a developer using valid8r
  I want to validate dataclass instances using field-level validators
  So that I can ensure data integrity with minimal boilerplate

  Background:
    Given the dataclass validation module is available

  # Rule 1: Basic Field Validation - Validate individual fields with type-based parsers

  Scenario: Valid dataclass instance passes validation
    Given a User dataclass with name and age fields
    And name has a length validator between 1 and 100 characters
    And age has a range validator between 0 and 120
    When Alice validates a User with name "Alice Smith" and age 30
    Then the validation succeeds
    And the validated instance has name "Alice Smith"
    And the validated instance has age 30

  Scenario: Invalid field value fails validation
    Given a User dataclass with name and age fields
    And name has a length validator between 1 and 100 characters
    And age has a range validator between 0 and 120
    When Alice validates a User with name "" and age 30
    Then the validation fails
    And the error report contains field "name"
    And the error message contains "length"

  Scenario: Multiple invalid fields report all errors
    Given a User dataclass with name and age fields
    And name has a length validator between 1 and 100 characters
    And age has a range validator between 0 and 120
    When Alice validates a User with name "" and age 150
    Then the validation fails
    And the error report contains field "name"
    And the error report contains field "age"

  # Rule 2: Type Coercion - Automatic parsing from strings using field types

  Scenario: String values are parsed to correct types
    Given a Product dataclass with name, price, and in_stock fields
    And name is type str
    And price is type float
    And in_stock is type bool
    When Alice validates a Product from strings name="Laptop", price="999.99", in_stock="true"
    Then the validation succeeds
    And the validated instance has name "Laptop"
    And the validated instance has price 999.99
    And the validated instance has in_stock True

  Scenario: Invalid type conversion fails validation
    Given a Product dataclass with price field of type float
    When Alice validates a Product from string price="not-a-number"
    Then the validation fails
    And the error report contains field "price"
    And the error message contains "valid number"

  # Rule 3: Optional Fields - Handle None values gracefully

  Scenario: Optional field accepts None value
    Given a Profile dataclass with bio field of type Optional[str]
    And bio has a maximum length validator of 500 characters
    When Alice validates a Profile with bio=None
    Then the validation succeeds
    And the validated instance has bio None

  Scenario: Optional field accepts valid value
    Given a Profile dataclass with bio field of type Optional[str]
    And bio has a maximum length validator of 500 characters
    When Alice validates a Profile with bio "Python enthusiast"
    Then the validation succeeds
    And the validated instance has bio "Python enthusiast"

  Scenario: Optional field rejects invalid value
    Given a Profile dataclass with bio field of type Optional[str]
    And bio has a maximum length validator of 500 characters
    When Alice validates a Profile with bio of 600 characters
    Then the validation fails
    And the error report contains field "bio"
    And the error message contains "maximum"

  # Rule 4: Nested Dataclasses - Validate complex object graphs

  Scenario: Nested dataclass validates successfully
    Given an Address dataclass with street, city, and zip_code fields
    And a Person dataclass with name and address fields
    And address is type Address
    When Alice validates a Person with valid name and address
    Then the validation succeeds
    And the validated instance has a valid address

  Scenario: Invalid nested dataclass fails validation
    Given an Address dataclass with zip_code field requiring 5 digits
    And a Person dataclass with name and address fields
    When Alice validates a Person with invalid address zip_code "123"
    Then the validation fails
    And the error report contains field "address.zip_code"
    And the error message contains "5 digits"

  # Rule 5: Collection Fields - Validate lists, sets, and dicts

  Scenario: List field validates all elements
    Given a Team dataclass with members field of type list[str]
    And members has a unique_items validator
    When Alice validates a Team with members ["Alice", "Bob", "Charlie"]
    Then the validation succeeds
    And the validated instance has 3 members

  Scenario: List field rejects duplicate elements
    Given a Team dataclass with members field of type list[str]
    And members has a unique_items validator
    When Alice validates a Team with members ["Alice", "Bob", "Alice"]
    Then the validation fails
    And the error report contains field "members"
    And the error message contains "unique"

  Scenario: Dict field validates keys and values
    Given a Settings dataclass with config field of type dict[str, int]
    When Alice validates Settings with config {"timeout": 30, "retries": 3}
    Then the validation succeeds
    And the validated instance has config with 2 entries

  Scenario: Dict field rejects invalid value types
    Given a Settings dataclass with config field of type dict[str, int]
    When Alice validates Settings with config {"timeout": "thirty"}
    Then the validation fails
    And the error report contains field "config"
    And the error message contains "valid integer"

  # Rule 6: Custom Validators - Apply domain-specific validation logic

  Scenario: Custom validator applies to field
    Given an Email dataclass with address field of type str
    And address has a custom email format validator
    When Alice validates an Email with address "alice@example.com"
    Then the validation succeeds

  Scenario: Custom validator rejects invalid input
    Given an Email dataclass with address field of type str
    And address has a custom email format validator
    When Alice validates an Email with address "not-an-email"
    Then the validation fails
    And the error report contains field "address"
    And the error message contains "email"

  Scenario: Multiple validators chain together
    Given a Password dataclass with value field of type str
    And value has a minimum length validator of 8 characters
    And value has a matches_regex validator for special characters
    When Alice validates a Password with value "abc123"
    Then the validation fails
    And the error message contains "minimum"

  # Rule 7: Pre and Post Validation Hooks - Execute custom logic before/after validation

  Scenario: Pre-validation hook normalizes input
    Given a Username dataclass with name field of type str
    And a pre-validation hook that strips whitespace
    When Alice validates a Username with name "  alice  "
    Then the validation succeeds
    And the validated instance has name "alice"

  Scenario: Post-validation hook enriches data
    Given a Timestamp dataclass with value field of type str
    And a post-validation hook that parses to datetime
    When Alice validates a Timestamp with value "2024-01-15"
    Then the validation succeeds
    And the validated instance has a parsed datetime attribute

  # Rule 8: Error Aggregation - Collect all field errors in single validation pass

  Scenario: All field errors are reported together
    Given a ComplexForm dataclass with 5 fields
    And each field has validation rules
    When Alice validates a ComplexForm with 3 invalid fields
    Then the validation fails
    And the error report contains exactly 3 field errors
    And each error specifies the field name
    And each error contains a descriptive message

  # Rule 9: Validator Decorator - Apply validators declaratively to dataclass fields

  Scenario: Decorator syntax applies validators to fields
    Given a dataclass definition uses @validate decorator
    And fields use metadata to specify validators
    When the dataclass is instantiated with valid data
    Then validation runs automatically
    And the instance is created successfully

  Scenario: Decorator syntax rejects invalid data
    Given a dataclass definition uses @validate decorator
    And fields use metadata to specify validators
    When the dataclass is instantiated with invalid data
    Then validation fails before instance creation
    And a ValidationError is raised with field details

  # Rule 10: Integration with from_type - Automatic parser generation from type hints

  Scenario: Type hints generate appropriate parsers
    Given a Config dataclass with port field of type int
    And no explicit parser is provided
    When Alice validates Config from string port="8080"
    Then the validation succeeds
    And the validated instance has port 8080 as integer

  Scenario: Complex type hints generate correct parsers
    Given a Data dataclass with items field of type list[int]
    And no explicit parser is provided
    When Alice validates Data from string items="[1, 2, 3]"
    Then the validation succeeds
    And the validated instance has items [1, 2, 3]
