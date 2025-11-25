Feature: FastAPI Async Validation Guide
  As a FastAPI developer
  I want a guide for integrating valid8r
  So that I can validate API requests effectively

  Background:
    Given I have valid8r installed with async support
    And I have FastAPI installed
    And I have a test client for my FastAPI application

  Scenario: I can validate request bodies
    Given I follow the integration guide
    When I implement request body validation
    Then invalid requests are rejected automatically
    And clients receive clear error messages
    And valid requests proceed to my handler

  Scenario: I can validate query parameters
    Given I follow the integration guide
    When I implement query parameter validation
    Then missing parameters are handled gracefully
    And invalid parameter values are rejected
    And I understand what went wrong from the error message

  Scenario: I can validate request headers
    Given I follow the integration guide
    When I implement header validation
    Then I can verify authentication tokens
    And I can validate custom header formats
    And unauthorized requests are rejected appropriately

  Scenario: I can handle validation errors properly
    Given I follow the integration guide
    When API validation fails
    Then I know how to return appropriate HTTP status codes
    And I can provide structured error responses
    And clients receive actionable feedback

  Scenario: I can evaluate performance characteristics
    Given I follow the integration guide
    When I review the performance section
    Then I understand when async validation is beneficial
    And I see performance comparisons
    And I can make informed architecture decisions
