Welcome to Valid8r's documentation!
===================================

.. image:: https://img.shields.io/badge/Python-3.11%2B-blue
   :target: https://www.python.org/downloads/
   :alt: Python 3.11+

.. image:: https://img.shields.io/github/license/yourusername/valid8r
   :target: https://github.com/yourusername/valid8r/blob/main/LICENSE
   :alt: License: MIT

**Valid8r** is a clean, flexible input validation library for Python applications. It provides a functional programming approach to validation with a Maybe monad for elegant error handling.

Key Features
------------

* **Clean Type Parsing**: Parse strings to various Python types with robust error handling
* **Monadic Error Handling**: Use the Maybe monad for clean error propagation without exceptions
* **Flexible Validation**: Chain validators and create custom validation rules
* **Input Prompting**: Prompt users for input with built-in validation

Quick Start
-----------

.. code-block:: python

   from valid8r import parsers, validators, prompt

   # Parse a string to an integer and validate it
   result = parsers.parse_int("42").bind(
       lambda x: validators.minimum(0)(x)
   )

   if result.is_just():
       print(f"Valid number: {result.value()}")
   else:
       print(f"Error: {result.error()}")

   # Ask for user input with validation
   age = prompt.ask(
       "Enter your age: ",
       parser=parsers.parse_int,
       validator=validators.between(0, 120),
       retry=True
   )

   if age.is_just():
       print(f"Your age is {age.value()}")
   else:
       print(f"Error: {age.error()}")

Installation
------------

.. code-block:: bash

   pip install valid8r

Alternatively, if you use Poetry:

.. code-block:: bash

   poetry add valid8r

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/getting_started
   user_guide/maybe_monad
   user_guide/parsers
   user_guide/validators
   user_guide/prompting
   user_guide/advanced_usage

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/basic_examples
   examples/chaining_validators
   examples/custom_validators
   examples/interactive_prompts

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/prompt

.. toctree::
   :maxdepth: 1
   :caption: Development

   development/contributing
   development/testing
   development/changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`