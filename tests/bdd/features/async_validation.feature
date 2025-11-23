Feature: Async Validation
  As a developer building async applications
  I want to validate data using async validators
  So that I can check database uniqueness and call external APIs

  Background:
    Given I am using an async Python application
    And I have valid8r installed with async support

  Scenario: Validate email uniqueness in database
    Given a user database with email "existing@example.com"
    When I validate user registration with email "existing@example.com"
    Then validation fails with "already registered"

  Scenario: Validate new unique email
    Given a user database without email "new@example.com"
    When I validate user registration with email "new@example.com"
    Then validation succeeds

  Scenario: Validate API key with external service
    Given an external API that recognizes key "valid-key-123"
    When I validate configuration with API key "valid-key-123"
    Then validation succeeds

  Scenario: Reject invalid API key
    Given an external API that rejects key "invalid-key"
    When I validate configuration with API key "invalid-key"
    Then validation fails with "Invalid API key"

  Scenario: Multiple async validations run efficiently
    Given a schema with 3 fields requiring async validation
    When I validate data for all 3 fields
    Then validation completes in reasonable time
    And all fields are validated

  Scenario: Sync validators still work
    Given a schema with only sync validators
    When I use the regular validate method
    Then validation works as before

  Scenario: Mixed sync and async validators
    Given a schema with both sync and async validators
    When I validate data using async validation
    Then sync validators run first
    And async validators run after
    And all errors are collected

  Scenario: Timeout for slow async validators
    Given a schema with a slow async validator
    When I validate with a timeout of 1 second
    Then validation fails with timeout error

  Scenario: Geographic IP validation
    Given an external API for IP geolocation
    When I validate IP address "8.8.8.8" must be from "US"
    Then validation succeeds

  Scenario: Geographic IP rejection
    Given an external API for IP geolocation
    When I validate IP address "1.1.1.1" must be from "US"
    Then validation fails with "not from US"
