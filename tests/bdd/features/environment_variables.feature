Feature: Environment variable parsing with schema
  As an application developer
  I want to load typed configuration from environment variables
  So that I can deploy applications with validated config

  Background:
    Given the valid8r.integrations.env module exists
    And I have imported load_env_config

  Scenario: Load simple config from environment
    Given environment variables:
      | name       | value |
      | APP_PORT   | 8080  |
      | APP_DEBUG  | true  |
    And a schema:
      | field | parser      |
      | port  | parse_int   |
      | debug | parse_bool  |
    When I call load_env_config(schema, prefix="APP_")
    Then I get Success with {"port": 8080, "debug": True}

  Scenario: Use default values for missing variables
    Given environment variable APP_PORT is not set
    And a schema with field "port" using parse_int and default 3000
    When I call load_env_config(schema, prefix="APP_")
    Then I get Success with {"port": 3000}

  Scenario: Fail validation for invalid environment variable
    Given environment variable APP_PORT="invalid"
    And a schema with field "port" using parse_int
    When I call load_env_config(schema, prefix="APP_")
    Then I get Failure mentioning "port" and "valid integer"

  Scenario: Support nested configuration with underscore delimiters
    Given environment variables:
      | name                  | value                |
      | APP_DATABASE_HOST     | localhost            |
      | APP_DATABASE_PORT     | 5432                 |
      | APP_DATABASE_NAME     | mydb                 |
    And a nested schema for "database" with host, port, name
    When I call load_env_config with prefix "APP_" and delimiter "_"
    Then I get Success with {}:
      """
      {
        "database": {
          "host": "localhost",
          "port": 5432,
          "name": "mydb"
        }
      }
      """

  Scenario: Use chained validators for environment variables
    Given environment variable APP_MAX_CONNECTIONS="0"
    And a schema with "max_connections" using parse_int & minimum(1)
    When I call load_env_config(schema, prefix="APP_")
    Then I get Failure mentioning "at least"

  Scenario: Required vs optional fields
    Given a schema with required field "api_key" and optional field "log_level"
    And environment variable APP_API_KEY is not set
    When I call load_env_config(schema, prefix="APP_")
    Then I get Failure mentioning "api_key" and "required"

  Scenario: Parse list values from comma-separated strings
    Given environment variable APP_ALLOWED_HOSTS="localhost,example.com,api.example.com"
    And a schema with "allowed_hosts" using parse_list(parse_str)
    When I call load_env_config(schema, prefix="APP_")
    Then I get Success with {"allowed_hosts": ["localhost", "example.com", "api.example.com"]}
