Changelog
=========

All notable changes to Valid8r will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

Added
~~~~~

- IP parsing helpers built on ``ipaddress``:
  - ``parse_ipv4``, ``parse_ipv6``, ``parse_ip``, ``parse_cidr``
- Deterministic error messages and whitespace normalization
- Unit tests covering IPv4/IPv6/CIDR success and failure scenarios
- Documentation updates in User Guide, API reference, and examples

- Initial implementation of the Maybe monad
- Core parsers for various data types
- Core validators with operator overloading
- Validator combinators for logical operations
- Basic prompt functionality with validation
- Comprehensive test suite
- Documentation using Sphinx

[0.1.0] - 2025-02-26
--------------------

Initial release of Valid8r.

Added
~~~~~

- Maybe monad implementation
- String parsers:
  - Integer parsing
  - Float parsing
  - Boolean parsing
  - Date parsing
  - Complex number parsing
  - Enum parsing
- Validators:
  - Minimum value validator
  - Maximum value validator
  - Between (range) validator
  - Predicate validator
  - String length validator
- Validator combinators:
  - AND combinator
  - OR combinator
  - NOT combinator
- Operator overloading for validators:
  - & operator for AND
  - | operator for OR
  - ~ operator for NOT
- Interactive prompting:
  - Type parsing
  - Input validation
  - Default values
  - Retry behavior
  - Custom error messages
- Comprehensive documentation
- Unit tests with high coverage
- BDD tests for core functionality
