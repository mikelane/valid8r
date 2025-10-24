Feature: Web-Focused Parsers
  As a developer building web applications
  I want to parse web-specific data formats like slugs, JSON, base64, and JWTs
  So that I can validate and process common web data safely and reliably

  # ==========================================
  # Slug Parsing (URL-safe identifiers)
  # ==========================================

  Scenario: Parse valid lowercase slug
    Given I have the slug string "hello-world"
    When I parse it with parse_slug
    Then the result is a Success
    And the parsed value is "hello-world"

  Scenario: Parse slug with numbers
    Given I have the slug string "blog-post-123"
    When I parse it with parse_slug
    Then the result is a Success
    And the parsed value is "blog-post-123"

  Scenario: Parse single character slug
    Given I have the slug string "a"
    When I parse it with parse_slug
    Then the result is a Success
    And the parsed value is "a"

  Scenario: Parse long slug
    Given I have the slug string "this-is-a-very-long-slug-name-for-testing"
    When I parse it with parse_slug
    Then the result is a Success

  Scenario: Reject empty slug
    Given I have the slug string ""
    When I parse it with parse_slug
    Then the result is a Failure
    And the error message contains "empty"

  Scenario: Reject slug with uppercase letters
    Given I have the slug string "Hello-World"
    When I parse it with parse_slug
    Then the result is a Failure
    And the error message contains "lowercase"

  Scenario: Reject slug with underscores
    Given I have the slug string "hello_world"
    When I parse it with parse_slug
    Then the result is a Failure
    And the error message contains "invalid"

  Scenario: Reject slug with spaces
    Given I have the slug string "hello world"
    When I parse it with parse_slug
    Then the result is a Failure
    And the error message contains "invalid"

  Scenario: Reject slug with leading hyphen
    Given I have the slug string "-hello-world"
    When I parse it with parse_slug
    Then the result is a Failure
    And the error message contains "start"

  Scenario: Reject slug with trailing hyphen
    Given I have the slug string "hello-world-"
    When I parse it with parse_slug
    Then the result is a Failure
    And the error message contains "end"

  Scenario: Reject slug with consecutive hyphens
    Given I have the slug string "hello--world"
    When I parse it with parse_slug
    Then the result is a Failure
    And the error message contains "consecutive"

  Scenario: Reject slug with special characters
    Given I have the slug string "hello@world"
    When I parse it with parse_slug
    Then the result is a Failure
    And the error message contains "invalid"

  Scenario: Parse slug with minimum length constraint
    Given I have the slug string "hello"
    When I parse it with parse_slug with min_length 5
    Then the result is a Success

  Scenario: Reject slug below minimum length
    Given I have the slug string "hi"
    When I parse it with parse_slug with min_length 5
    Then the result is a Failure
    And the error message contains "too short"

  Scenario: Parse slug with maximum length constraint
    Given I have the slug string "hello"
    When I parse it with parse_slug with max_length 10
    Then the result is a Success

  Scenario: Reject slug above maximum length
    Given I have the slug string "this-is-way-too-long"
    When I parse it with parse_slug with max_length 10
    Then the result is a Failure
    And the error message contains "too long"

  # ==========================================
  # JSON Parsing
  # ==========================================

  Scenario: Parse JSON object
    Given I have the JSON string '{"name": "Alice", "age": 30}'
    When I parse it with parse_json
    Then the result is a Success
    And the parsed JSON is a dict

  Scenario: Parse JSON array
    Given I have the JSON string '[1, 2, 3, 4, 5]'
    When I parse it with parse_json
    Then the result is a Success
    And the parsed JSON is a list

  Scenario: Parse JSON string primitive
    Given I have the JSON string '"hello world"'
    When I parse it with parse_json
    Then the result is a Success
    And the parsed value is "hello world"

  Scenario: Parse JSON number primitive
    Given I have the JSON string '42'
    When I parse it with parse_json
    Then the result is a Success
    And the parsed value is 42

  Scenario: Parse JSON boolean true
    Given I have the JSON string 'true'
    When I parse it with parse_json
    Then the result is a Success
    And the parsed value is True

  Scenario: Parse JSON boolean false
    Given I have the JSON string 'false'
    When I parse it with parse_json
    Then the result is a Success
    And the parsed value is False

  Scenario: Parse JSON null
    Given I have the JSON string 'null'
    When I parse it with parse_json
    Then the result is a Success
    And the parsed value is None

  Scenario: Parse nested JSON object
    Given I have the JSON string '{"user": {"name": "Bob", "roles": ["admin", "user"]}}'
    When I parse it with parse_json
    Then the result is a Success
    And the parsed JSON is a dict

  Scenario: Parse empty JSON object
    Given I have the JSON string '{}'
    When I parse it with parse_json
    Then the result is a Success
    And the parsed JSON is a dict

  Scenario: Parse empty JSON array
    Given I have the JSON string '[]'
    When I parse it with parse_json
    Then the result is a Success
    And the parsed JSON is a list

  Scenario: Reject empty string as JSON
    Given I have the JSON string ''
    When I parse it with parse_json
    Then the result is a Failure
    And the error message contains "empty"

  Scenario: Reject invalid JSON syntax
    Given I have the JSON string '{"name": "Alice"'
    When I parse it with parse_json
    Then the result is a Failure
    And the error message contains "JSON"

  Scenario: Reject JSON with trailing comma
    Given I have the JSON string '{"name": "Alice",}'
    When I parse it with parse_json
    Then the result is a Failure

  Scenario: Reject single-quoted JSON
    Given I have the JSON string "{'name': 'Alice'}"
    When I parse it with parse_json
    Then the result is a Failure

  Scenario: Reject JSON with unquoted keys
    Given I have the JSON string '{name: "Alice"}'
    When I parse it with parse_json
    Then the result is a Failure

  Scenario: Parse JSON with whitespace
    Given I have the JSON string '  {"name": "Alice"}  '
    When I parse it with parse_json
    Then the result is a Success

  # ==========================================
  # Base64 Parsing
  # ==========================================

  Scenario: Parse standard base64 with padding
    Given I have the base64 string "SGVsbG8gV29ybGQ="
    When I parse it with parse_base64
    Then the result is a Success
    And the decoded bytes represent "Hello World"

  Scenario: Parse standard base64 without padding
    Given I have the base64 string "SGVsbG8gV29ybGQ"
    When I parse it with parse_base64
    Then the result is a Success
    And the decoded bytes represent "Hello World"

  Scenario: Parse URL-safe base64 with hyphens
    Given I have the base64 string "A-A="
    When I parse it with parse_base64
    Then the result is a Success

  Scenario: Parse URL-safe base64 with underscores
    Given I have the base64 string "Pz8_"
    When I parse it with parse_base64
    Then the result is a Success

  Scenario: Parse base64 with whitespace
    Given I have the base64 string " SGVsbG8gV29ybGQ= "
    When I parse it with parse_base64
    Then the result is a Success
    And the decoded bytes represent "Hello World"

  Scenario: Parse base64 with newlines
    Given I have the base64 string "SGVsbG8g\nV29ybGQ="
    When I parse it with parse_base64
    Then the result is a Success

  Scenario: Parse single character base64
    Given I have the base64 string "QQ=="
    When I parse it with parse_base64
    Then the result is a Success

  Scenario: Reject empty base64
    Given I have the base64 string ""
    When I parse it with parse_base64
    Then the result is a Failure
    And the error message contains "empty"

  Scenario: Reject invalid base64 characters
    Given I have the base64 string "Not@Valid!"
    When I parse it with parse_base64
    Then the result is a Failure
    And the error message contains "invalid"

  Scenario: Reject only padding characters
    Given I have the base64 string "===="
    When I parse it with parse_base64
    Then the result is a Failure

  # ==========================================
  # JWT Parsing (Structure Validation)
  # ==========================================

  Scenario: Parse valid JWT with three parts
    Given I have the JWT string "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    When I parse it with parse_jwt
    Then the result is a Success
    And the parsed value is the original JWT string

  Scenario: Parse JWT and verify header is valid JSON
    Given I have the JWT string "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.sig"
    When I parse it with parse_jwt
    Then the result is a Success

  Scenario: Parse JWT and verify payload is valid JSON
    Given I have the JWT string "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ.sig"
    When I parse it with parse_jwt
    Then the result is a Success

  Scenario: Reject empty JWT
    Given I have the JWT string ""
    When I parse it with parse_jwt
    Then the result is a Failure
    And the error message contains "empty"

  Scenario: Reject JWT with only one part
    Given I have the JWT string "eyJhbGciOiJIUzI1NiJ9"
    When I parse it with parse_jwt
    Then the result is a Failure
    And the error message contains "three parts"

  Scenario: Reject JWT with only two parts
    Given I have the JWT string "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0"
    When I parse it with parse_jwt
    Then the result is a Failure
    And the error message contains "three parts"

  Scenario: Reject JWT with four parts
    Given I have the JWT string "part1.part2.part3.part4"
    When I parse it with parse_jwt
    Then the result is a Failure
    And the error message contains "three parts"

  Scenario: Reject JWT with non-base64 header
    Given I have the JWT string "not-base64!.eyJzdWIiOiIxMjM0In0.sig"
    When I parse it with parse_jwt
    Then the result is a Failure
    And the error message contains "header"

  Scenario: Reject JWT with non-base64 payload
    Given I have the JWT string "eyJhbGciOiJIUzI1NiJ9.not-base64!.sig"
    When I parse it with parse_jwt
    Then the result is a Failure
    And the error message contains "payload"

  Scenario: Reject JWT with non-JSON header
    Given I have the JWT string "bm90anNvbg==.eyJzdWIiOiIxMjM0In0.sig"
    When I parse it with parse_jwt
    Then the result is a Failure
    And the error message contains "header"

  Scenario: Reject JWT with non-JSON payload
    Given I have the JWT string "eyJhbGciOiJIUzI1NiJ9.bm90anNvbg==.sig"
    When I parse it with parse_jwt
    Then the result is a Failure
    And the error message contains "payload"

  Scenario: Parse JWT with whitespace
    Given I have the JWT string " eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.sig "
    When I parse it with parse_jwt
    Then the result is a Success
