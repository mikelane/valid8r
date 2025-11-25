Feature: Async Validator Library
  As an async Python developer
  I want validators for I/O-bound operations
  So that I can validate against external systems efficiently

  Background:
    Given I am using an async Python application
    And I have the async_validators module available

  # Database Validators - Uniqueness Checks

  Scenario: Check if value is unique in database
    Given I have a database connection
    And the database table "users" has a record where "email" is "existing@example.com"
    When I use the unique_in_db validator for field "email" in table "users"
    And I validate the value "new@example.com"
    Then validation succeeds without blocking
    And the result contains the validated value

  Scenario: Reject non-unique value in database
    Given I have a database connection
    And the database table "users" has a record where "email" is "existing@example.com"
    When I use the unique_in_db validator for field "email" in table "users"
    And I validate the value "existing@example.com"
    Then validation fails without blocking
    And the error message contains "already exists"

  Scenario: Check if value exists in database
    Given I have a database connection
    And the database table "categories" has a record where "id" is "42"
    When I use the exists_in_db validator for field "id" in table "categories"
    And I validate the value "42"
    Then validation succeeds without blocking
    And the result contains the validated value

  Scenario: Reject missing value in database
    Given I have a database connection
    And the database table "categories" does not have a record where "id" is "999"
    When I use the exists_in_db validator for field "id" in table "categories"
    And I validate the value "999"
    Then validation fails without blocking
    And the error message contains "does not exist"

  # API Validators - API Key Validation

  Scenario: Validate valid API key against external service
    Given an external API at "https://api.example.com"
    And the API recognizes key "valid-key-abc123"
    When I use the valid_api_key validator with URL "https://api.example.com/validate"
    And I validate the API key "valid-key-abc123"
    Then validation succeeds without blocking
    And the result contains the validated API key

  Scenario: Reject invalid API key
    Given an external API at "https://api.example.com"
    And the API rejects key "invalid-key-xyz"
    When I use the valid_api_key validator with URL "https://api.example.com/validate"
    And I validate the API key "invalid-key-xyz"
    Then validation fails without blocking
    And the error message contains "Invalid API key"

  Scenario: API validator respects timeout
    Given an external API at "https://api.example.com"
    And the API is slow to respond
    When I use the valid_api_key validator with timeout 1.0 seconds
    And I validate the API key "timeout-test-key"
    Then validation fails with timeout error
    And the error message contains "timeout"

  # API Validators - OAuth Token Validation

  Scenario: Validate OAuth token without cache
    Given an OAuth token endpoint at "https://oauth.example.com/token"
    And the endpoint recognizes token "valid-token-123"
    When I use the valid_oauth_token validator
    And I validate the OAuth token "valid-token-123"
    Then validation succeeds without blocking
    And the token endpoint is called once

  Scenario: Validate OAuth token with cache hit
    Given an OAuth token endpoint at "https://oauth.example.com/token"
    And a cache with token "cached-token-456" marked as valid
    When I use the valid_oauth_token validator with cache
    And I validate the OAuth token "cached-token-456"
    Then validation succeeds without blocking
    And the token endpoint is not called

  Scenario: Validate OAuth token with cache miss
    Given an OAuth token endpoint at "https://oauth.example.com/token"
    And a cache without token "new-token-789"
    And the endpoint recognizes token "new-token-789"
    When I use the valid_oauth_token validator with cache
    And I validate the OAuth token "new-token-789"
    Then validation succeeds without blocking
    And the token endpoint is called once
    And the token is cached for future use

  # External Service Validators - Email Deliverability

  Scenario: Validate email with valid MX record
    Given a DNS resolver is available
    And the domain "example.com" has MX records
    When I use the valid_email_deliverable validator
    And I validate the email address "user@example.com"
    Then validation succeeds without blocking
    And the result contains the email address

  Scenario: Reject email with no MX record
    Given a DNS resolver is available
    And the domain "no-mx-record.example" has no MX records
    When I use the valid_email_deliverable validator
    And I validate the email address "user@no-mx-record.example"
    Then validation fails without blocking
    And the error message contains "No mail server found"

  Scenario: Reject email with non-existent domain
    Given a DNS resolver is available
    And the domain "nonexistent-domain-12345.test" does not exist
    When I use the valid_email_deliverable validator
    And I validate the email address "user@nonexistent-domain-12345.test"
    Then validation fails without blocking
    And the error message contains "does not exist"

  # Rate Limiting - Protecting External Services

  Scenario: Rate limiter allows calls within limit
    Given a rate-limited validator with rate 10 calls per second
    When I validate 5 values concurrently
    Then all validations complete successfully
    And no validations are delayed by rate limiting

  Scenario: Rate limiter delays calls exceeding limit
    Given a rate-limited validator with rate 2 calls per second
    When I validate 5 values concurrently
    Then all validations complete successfully
    And some validations are delayed by rate limiting

  Scenario: Rate limiter respects burst size
    Given a rate-limited validator with rate 1 call per second and burst 5
    When I validate 5 values concurrently
    Then the first 5 validations complete immediately
    And subsequent validations are rate limited

  # Retry Logic - Handling Transient Failures

  Scenario: Retry succeeds on transient failure
    Given an external service that fails once then succeeds
    And a validator with retry logic
    When I validate the value "test-value"
    Then validation succeeds without blocking
    And the validator retries once

  Scenario: Retry fails after max attempts
    Given an external service that always fails
    And a validator with retry logic and max retries 3
    When I validate the value "test-value"
    Then validation fails without blocking
    And the validator retries 3 times
    And the error message contains "max retries exceeded"

  Scenario: Retry uses exponential backoff
    Given an external service that fails twice then succeeds
    And a validator with exponential backoff retry
    When I validate the value "test-value"
    Then validation succeeds without blocking
    And retry delays increase exponentially

  # Validator Composition - Parallel Execution

  Scenario: Independent async validators run concurrently
    Given I have 3 independent async validators
    And each validator takes 0.1 seconds
    When I compose validators with parallel execution
    And I validate a value
    Then validation completes in approximately 0.1 seconds
    And all 3 validators are called

  Scenario: Dependent async validators run sequentially
    Given I have 3 dependent async validators
    And each validator takes 0.1 seconds
    When I compose validators with sequential execution
    And I validate a value
    Then validation completes in approximately 0.3 seconds
    And validators run in order

  Scenario: Mixed parallel and sequential composition
    Given I have 2 parallel validator groups
    And each group has 2 sequential validators
    And each validator takes 0.05 seconds
    When I compose validators with mixed execution
    And I validate a value
    Then validation completes in approximately 0.1 seconds
    And parallel groups run concurrently

  # Timeout Handling - Responsive Applications

  Scenario: Fast validators complete before timeout
    Given an async validator that completes in 0.1 seconds
    When I validate with a timeout of 1.0 seconds
    Then validation succeeds without blocking
    And no timeout error occurs

  Scenario: Slow validators fail with timeout
    Given an async validator that takes 2.0 seconds
    When I validate with a timeout of 0.5 seconds
    Then validation fails with timeout error
    And the error message contains "timeout"
    And the application remains responsive

  Scenario: Timeout applies per validator in composition
    Given I have 3 async validators
    And validator 2 is slow
    When I validate with per-validator timeout of 0.1 seconds
    Then validation fails at validator 2
    And the error message contains "timeout"
    And validators 1 and 3 are not affected

  # Error Handling - Descriptive Messages

  Scenario: Network error produces clear message
    Given an external API that is unreachable
    When I use an async API validator
    And I validate a value
    Then validation fails without blocking
    And the error message contains "network error"
    And the error message is actionable

  Scenario: Database error produces clear message
    Given a database connection that fails
    When I use an async database validator
    And I validate a value
    Then validation fails without blocking
    And the error message contains "database error"
    And the error message includes connection details

  Scenario: Timeout error produces clear message
    Given an async validator with timeout
    And the validator times out
    When I validate the value "test-value"
    Then validation fails without blocking
    And the error message contains "timeout after"
    And the error message includes the timeout duration

  # Integration - Works with Existing Async Parsers

  Scenario: Async validator chains with async parser
    Given I have an async email parser
    And I have an async email deliverability validator
    When I chain the parser and validator using bind_async
    And I parse and validate "user@example.com"
    Then parsing and validation both succeed
    And the result contains the validated email

  Scenario: Async validators work with parse_*_async functions
    Given I use parse_email_async for parsing
    And I use valid_email_deliverable for validation
    When I parse and validate "user@example.com"
    Then both operations complete without blocking
    And the final result is a Success with EmailAddress

  # Performance - Batch Validation

  Scenario: Batch validation runs concurrently
    Given I have 10 values to validate
    And each validation takes 0.1 seconds
    When I use parallel_validate helper
    And I validate all 10 values
    Then validation completes in approximately 0.1 seconds
    And all values are validated concurrently

  Scenario: Batch validation collects all errors
    Given I have 5 values to validate
    And 2 values are invalid
    When I use parallel_validate helper
    And I validate all 5 values
    Then validation completes without blocking
    And I receive 2 validation failures
    And I receive 3 validation successes

  # Cache Integration - Avoiding Redundant Calls

  Scenario: Cache prevents redundant API calls
    Given an external API validator with cache
    And I validate the same value twice
    When I run both validations
    Then the API is called only once
    And the second validation uses cached result

  Scenario: Cache respects TTL
    Given an external API validator with cache TTL 0.1 seconds
    And I validate a value
    When I wait 0.2 seconds
    And I validate the same value again
    Then the API is called twice
    And the cached result expired

  Scenario: Cache can be disabled
    Given an external API validator without cache
    And I validate the same value twice
    When I run both validations
    Then the API is called twice
    And no caching occurs
