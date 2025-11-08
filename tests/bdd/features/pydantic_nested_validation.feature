Feature: Nested model validation with valid8r parsers
  As a FastAPI developer
  I want to use valid8r parsers in nested Pydantic models
  So that I can validate complex request structures consistently

  Background:
    Given the valid8r.integrations.pydantic module exists
    And I have imported validator_from_parser

  Scenario: Validate nested model with valid8r parser
    Given a Pydantic model Address with phone field using validator_from_parser(parse_phone)
    And a Pydantic model User with address: Address field
    When I validate the model with {"name": "Alice", "address": {"phone": "(206) 234-5678"}}
    Then the User model validates successfully
    And user.address.phone is a PhoneNumber object

  Scenario: Nested validation errors include field path
    Given nested models User -> Address -> phone
    When I validate the model with {"address": {"phone": "invalid"}}
    Then Pydantic raises ValidationError
    And the error includes field path "address.phone"
    And the error message contains the valid8r parse_phone error

  Scenario: Validate list of models with valid8r parsers
    Given a model LineItem with quantity validated by parse_int & minimum(1)
    And a model Order with items: list[LineItem]
    When I validate the model with {"items": [{"quantity": "5"}, {"quantity": "0"}]}
    Then Pydantic raises ValidationError for items[1].quantity
    And the error mentions "minimum"

  Scenario: Validate dict values with valid8r parsers
    Given a model Config with ports: dict[str, int] using validator_from_parser(parse_int)
    When I validate the model with {"ports": {"http": "80", "https": "443"}}
    Then the model validates successfully
    And config.ports == {"http": 80, "https": 443}

  Scenario: Handle None values in optional nested models
    Given a Pydantic model User with optional address: Address | None
    When I validate the model with {"name": "Bob", "address": null}
    Then the User model validates successfully
    And user.address is None

  Scenario: Validate deeply nested models (three levels)
    Given a model Employee with email validated by parse_email
    And a model Department with lead: Employee field
    And a model Company with engineering: Department field
    When I validate the model with {"engineering": {"lead": {"email": "cto@example.com"}}}
    Then the Company model validates successfully
    And company.engineering.lead.email is an EmailAddress object

  Scenario: Error messages preserve full field path in deep nesting
    Given nested models Company -> Department -> Employee -> email (three levels)
    When I validate the model with {"engineering": {"lead": {"email": "not-an-email"}}}
    Then Pydantic raises ValidationError
    And the error includes field path "engineering.lead.email"
    And the error message contains the valid8r parse_email error
