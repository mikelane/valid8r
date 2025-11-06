Contributing to Valid8r
=======================

Thank you for your interest in contributing to Valid8r! This document provides guidelines for contributing to the project.

Setting Up Your Development Environment
---------------------------------------

1. **Fork the repository**

   First, create a fork of the Valid8r repository on GitHub.

2. **Clone your fork**

   .. code-block:: bash

      git clone https://github.com/your-username/valid8r.git
      cd valid8r

3. **Set up uv**

   Valid8r uses uv for fast dependency management. Make sure you have uv installed:

   .. code-block:: bash

      # Install uv if you don't have it
      curl -LsSf https://astral.sh/uv/install.sh | sh

      # Verify installation
      uv --version

      # Install dependencies
      uv sync

4. **Set up pre-commit hooks**

   .. code-block:: bash

      uv run pre-commit install

Development Workflow
--------------------

1. **Create a new branch**

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make your changes**

   When making changes, follow these guidelines:

   - Follow the existing code style and conventions
   - Keep your changes focused on a single feature or bug fix
   - Write tests for your changes
   - Update documentation as needed

3. **Run tests locally**

   .. code-block:: bash

      # Run unit tests
      uv run pytest tests/unit

      # Run BDD tests
      uv run behave tests/bdd/features

      # Run all tests with tox (multiple Python versions)
      uv run tox

4. **Check code quality**

   .. code-block:: bash

      # Run ruff for linting
      uv run ruff check .

      # Run isort to check imports
      uv run isort --check-only valid8r tests

      # Run mypy for type checking
      uv run mypy valid8r

5. **Commit your changes**

   .. code-block:: bash

      git add .
      git commit -m "feat: add your feature description"

   We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages.

6. **Push your changes**

   .. code-block:: bash

      git push origin feature/your-feature-name

7. **Create a pull request**

   Open a pull request from your fork to the main Valid8r repository.

Code Style Guidelines
---------------------

Valid8r follows a strict code style to maintain consistency across the codebase:

- **PEP 8**: Follow PEP 8 style guidelines
- **Type hints**: Use type hints throughout the codebase
- **Docstrings**: Document all modules, classes, and functions using Google-style docstrings
- **Line length**: Maximum line length is 120 characters
- **Imports**: Use isort to organize imports

Testing Guidelines
------------------

Valid8r uses a combination of unit tests and behavior-driven development (BDD) tests:

1. **Unit Tests**

   - Unit tests should be written for all new functionality
   - Tests should be placed in the `tests/unit` directory
   - Use pytest for unit testing
   - Aim for 100% test coverage for new code

2. **BDD Tests**

   - BDD tests define the behavior of the library from a user perspective
   - Use behave for BDD testing
   - Feature files should be placed in `tests/bdd/features`
   - Step implementations should be placed in `tests/bdd/steps`

Documentation Guidelines
------------------------

Documentation is a crucial part of Valid8r:

1. **Code Documentation**

   - All public APIs should be fully documented with docstrings
   - Use Google-style docstrings with type annotations
   - Include examples in docstrings where appropriate

2. **User Documentation**

   - User documentation is written in reStructuredText
   - Place documentation in the `docs` directory
   - Update the documentation when adding or changing features
   - Include examples demonstrating the new functionality

3. **Building and Testing Documentation**

   .. code-block:: bash

      # Build documentation
      uv run docs-build

      # Serve documentation locally
      uv run docs-serve

Security Guidelines
-------------------

When contributing parsers or validators:

1. **DoS Protection Required**

   All parsers must include early length validation:

   .. code-block:: python

      def parse_example(text: str) -> Maybe[Example]:
          # Check length BEFORE expensive operations
          if len(text) > MAX_LENGTH:
              return Maybe.failure(f'Input too long (max {MAX_LENGTH})')

          # Now safe to use regex, external libraries, etc.
          ...

2. **Security Testing Required**

   New parsers must include DoS protection tests:

   .. code-block:: python

      def test_rejects_extremely_long_input():
          import time
          malicious = 'x' * 10000

          start = time.perf_counter()
          result = parse_example(malicious)
          elapsed_ms = (time.perf_counter() - start) * 1000

          assert result.is_failure()
          assert 'too long' in result.error_or('').lower()
          assert elapsed_ms < 10, f'Took {elapsed_ms}ms, should be < 10ms'

3. **Consult Security Documentation**

   - :doc:`/security/secure-parser-development` - DoS prevention guidelines
   - :doc:`/security/production-deployment` - Real-world security patterns
   - Review recent security fixes in CHANGELOG.md

.. warning::
   **Report security vulnerabilities privately** to mikelane@gmail.com.
   Do not open public GitHub issues for security bugs.

Pull Request Process
--------------------

1. **Submit your PR with a clear title and description**
2. **Ensure all tests pass**
3. **Make sure the CI/CD pipeline passes**
4. **Request a review from a maintainer**
5. **Address any feedback or requested changes**
6. **Once approved, a maintainer will merge your PR**

Versioning Guidelines
---------------------

Valid8r follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

Code of Conduct
---------------

Please note that Valid8r has a Code of Conduct. By participating in this project, you agree to abide by its terms.

Questions and Support
---------------------

If you have questions about contributing to Valid8r, please open an issue on GitHub or reach out to the maintainers.

Thank you for contributing to Valid8r!
