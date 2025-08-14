Title: Add environment variable parsing helper with schema and prefix support
Labels: enhancement, integration

Provide a helper to load configuration from environment variables using a schema, default values, and optional prefix.

Acceptance Criteria:
```gherkin
Feature: Env var parsing
  Scenario: Load config from environment
    Given environment variables "APP_PORT=8080" and "APP_DEBUG=true"
    And a schema mapping {"port": parse_int, "debug": parse_bool} with prefix "APP_"
    When I load the config
    Then I get Success with {"port": 8080, "debug": True}
```