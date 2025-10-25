Title: Add IP address and CIDR parsers (IPv4/IPv6)
Labels: enhancement, parsers

Provide `parse_ipv4`, `parse_ipv6`, `parse_ip`, and `parse_cidr` using the `ipaddress` module.

Acceptance Criteria:
```gherkin
Feature: IP parsing
  Scenario: Parse IPv4 address
    Given "192.168.0.1"
    When I call parse_ipv4
    Then I get Success with an IPv4Address

  Scenario: Reject invalid CIDR
    Given "10.0.0.0/33"
    When I call parse_cidr
    Then I get Failure containing "valid network"
```