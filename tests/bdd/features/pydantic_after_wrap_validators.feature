Feature: Pydantic AfterValidator and WrapValidator support
  As a developer using Pydantic v2
  I want to use valid8r parsers with AfterValidator and WrapValidator
  So that I can choose the validation style that fits my use case

  Background:
    Given the valid8r.integrations.pydantic module exists
    And I have imported make_after_validator and make_wrap_validator

  Scenario: Use AfterValidator with valid8r parser
    Given a Pydantic model with field: Annotated[str, AfterValidator(make_after_validator(parse_email))]
    When I create an instance with email "alice@example.com"
    Then the model validates successfully
    And email is an EmailAddress object

  Scenario: AfterValidator converts Failure to ValidationError
    Given a field using AfterValidator(make_after_validator(parse_phone))
    When I validate with "invalid"
    Then Pydantic raises ValidationError
    And the error message contains the valid8r parse_phone error

  Scenario: Use WrapValidator for pre-processing
    Given a WrapValidator(make_wrap_validator(parse_int))
    When I validate with "42"
    Then the validator receives the raw string
    And returns parsed integer 42

  Scenario: Chain multiple AfterValidators
    Given a field with: Annotated[int, AfterValidator(make_after_validator(parse_int)), AfterValidator(make_after_validator(minimum(0)))]
    When I validate with "-1"
    Then Pydantic raises ValidationError mentioning "minimum"

  Scenario: Mix AfterValidator with field_validator
    Given a model using both AfterValidator and field_validator
    When I validate the model
    Then both validators execute in correct order
    And errors are properly aggregated

  Scenario: AfterValidator works with optional fields
    Given a model with optional field: Annotated[str | None, AfterValidator(make_after_validator(parse_email))]
    When I create an instance with email None
    Then the model validates successfully
    And email is None

  Scenario: WrapValidator handles ValidationInfo context
    Given a WrapValidator that accesses ValidationInfo
    When I validate a field
    Then the validator receives the ValidationInfo context
    And can access field_name and other metadata

  Scenario: AfterValidator error includes field path
    Given a nested model with validated field using AfterValidator
    When validation fails on the nested field
    Then the error message includes the full field path
    And preserves Pydantic's error structure

  Scenario: WrapValidator can delegate to next validator
    Given a WrapValidator that calls the next handler
    When I validate a value
    Then WrapValidator pre-processes the value
    And delegates to Pydantic's default validation
    And post-processes the result

  Scenario: Multiple WrapValidators chain correctly
    Given a field with multiple WrapValidators
    When I validate a value
    Then validators execute in correct order
    And each receives output from previous validator
