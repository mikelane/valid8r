================
Schema Validation
================

The Schema API provides structured validation for complex, nested objects with error accumulation and precise field path tracking.

Overview
========

Unlike single-value parsers, schemas validate entire dict-like objects against a defined structure, collecting **all** validation errors across all fields instead of stopping at the first failure.

**Key Features:**

* Error accumulation across multiple fields
* Field path tracking (e.g., ``.user.email``, ``.addresses[0].street``)
* Nested schema composition
* Required/optional field support
* Strict mode for rejecting extra fields
* Integration with existing parsers and validators

Basic Usage
===========

Define a schema using ``Field`` definitions:

.. code-block:: python

    from valid8r.core import parsers, schema, validators

    user_schema = schema.Schema(
        fields={
            'age': schema.Field(parser=parsers.parse_int, required=True),
            'email': schema.Field(parser=parsers.parse_email, required=True),
            'name': schema.Field(
                parser=parsers.parse_str,
                validator=validators.non_empty_string(),
                required=True,
            ),
        }
    )

    # Validate input data
    result = user_schema.validate({'age': '25', 'email': 'alice@example.com', 'name': 'Alice'})

    match result:
        case Success(data):
            print(f"Validated: {data}")
        case Failure(errors):
            for err in errors:
                print(f"{err.path}: {err.message}")

Field Definition
================

Fields are defined using the ``Field`` dataclass:

.. code-block:: python

    Field(parser, required, validator=None)

**Parameters:**

* ``parser`` (callable): Function that parses/validates the raw value, returns ``Maybe[T]``
* ``required`` (bool): Whether the field must be present in the input
* ``validator`` (callable, optional): Additional validation function to apply after parsing

**Example:**

.. code-block:: python

    schema.Field(
        parser=parsers.parse_int,
        validator=validators.minimum(0) & validators.maximum(100),
        required=True,
    )

Error Accumulation
==================

Schemas collect ALL validation errors across all fields:

.. code-block:: python

    invalid_input = {
        'age': 'not-a-number',
        'email': 'bad-email',
        'name': '',
    }

    result = user_schema.validate(invalid_input)

    match result:
        case Failure(errors):
            # errors is a list of ValidationError objects
            for err in errors:
                print(f"{err.path}: {err.message}")
            # Output:
            # .age: Invalid integer format
            # .email: Invalid email address
            # .name: String cannot be empty

Field Path Tracking
====================

Errors include the precise path to the failing field:

.. code-block:: python

    address_schema = schema.Schema(
        fields={
            'street': schema.Field(parser=parsers.parse_str, required=True),
            'city': schema.Field(parser=parsers.parse_str, required=True),
        }
    )

    user_schema = schema.Schema(
        fields={
            'name': schema.Field(parser=parsers.parse_str, required=True),
            'address': schema.Field(parser=address_schema.validate, required=True),
        }
    )

    invalid_input = {
        'name': 'Bob',
        'address': {'street': '', 'city': ''},
    }

    result = user_schema.validate(invalid_input)
    # Errors will have paths: .address.street, .address.city

Nested Schemas
===============

Compose schemas by using one schema's ``validate`` method as another field's parser:

.. code-block:: python

    # Inner schema
    address_schema = schema.Schema(
        fields={
            'street': schema.Field(parser=parsers.parse_str, required=True),
            'city': schema.Field(parser=parsers.parse_str, required=True),
            'zipcode': schema.Field(parser=parsers.parse_str, required=True),
        }
    )

    # Outer schema references inner schema
    user_schema = schema.Schema(
        fields={
            'name': schema.Field(parser=parsers.parse_str, required=True),
            'address': schema.Field(
                parser=address_schema.validate,  # Use schema as parser
                required=True,
            ),
        }
    )

    input_data = {
        'name': 'Alice',
        'address': {
            'street': '123 Main St',
            'city': 'Boston',
            'zipcode': '02101',
        },
    }

    result = user_schema.validate(input_data)

Required vs Optional Fields
============================

Control whether fields must be present using the ``required`` parameter:

.. code-block:: python

    user_schema = schema.Schema(
        fields={
            'name': schema.Field(parser=parsers.parse_str, required=True),
            'age': schema.Field(parser=parsers.parse_int, required=False),
            'email': schema.Field(parser=parsers.parse_email, required=False),
        }
    )

    # Valid with only required field
    result = user_schema.validate({'name': 'Charlie'})
    # result.is_success() == True

    # Optional fields can be included
    result = user_schema.validate({'name': 'Charlie', 'age': '30'})
    # result.is_success() == True

Strict Mode
===========

By default, schemas allow extra fields not defined in the schema. Enable strict mode to reject them:

.. code-block:: python

    strict_schema = schema.Schema(
        fields={'name': schema.Field(parser=parsers.parse_str, required=True)},
        strict=True,
    )

    result = strict_schema.validate({'name': 'Alice', 'extra': 'field'})
    # Fails with error: .extra: Unexpected field

Combining Parsers and Validators
=================================

Fields can have both a parser and a validator:

.. code-block:: python

    user_schema = schema.Schema(
        fields={
            'age': schema.Field(
                parser=parsers.parse_int,
                validator=validators.minimum(18) & validators.maximum(120),
                required=True,
            ),
            'username': schema.Field(
                parser=parsers.parse_str,
                validator=validators.length(3, 20),
                required=True,
            ),
        }
    )

    result = user_schema.validate({'age': '15', 'username': 'ab'})
    # Fails with errors:
    # .age: Value must be at least 18
    # .username: String must be at least 3 characters

Validation Error Structure
===========================

Errors are structured ``ValidationError`` objects from RFC-001:

.. code-block:: python

    from valid8r.core.errors import ValidationError, ErrorCode

    result = user_schema.validate(invalid_input)

    match result:
        case Failure(errors):
            for err in errors:
                print(f"Code: {err.code}")
                print(f"Path: {err.path}")
                print(f"Message: {err.message}")
                print(f"Context: {err.context}")
                print(f"Dict: {err.to_dict()}")

Type Preservation
=================

Validated data preserves parsed types, not original strings:

.. code-block:: python

    user_schema = schema.Schema(
        fields={
            'age': schema.Field(parser=parsers.parse_int, required=True),
            'active': schema.Field(parser=parsers.parse_bool, required=True),
        }
    )

    result = user_schema.validate({'age': '25', 'active': 'true'})

    match result:
        case Success(data):
            assert isinstance(data['age'], int)  # Not str
            assert isinstance(data['active'], bool)  # Not str
            assert data['age'] == 25
            assert data['active'] is True

Use Cases
=========

API Request Validation
----------------------

.. code-block:: python

    # Define schema for API endpoint
    create_user_schema = schema.Schema(
        fields={
            'username': schema.Field(
                parser=parsers.parse_str,
                validator=validators.length(3, 30),
                required=True,
            ),
            'email': schema.Field(parser=parsers.parse_email, required=True),
            'age': schema.Field(
                parser=parsers.parse_int,
                validator=validators.minimum(13),
                required=True,
            ),
        },
        strict=True,  # Reject unexpected fields
    )

    # In your API handler
    result = create_user_schema.validate(request.json)

    match result:
        case Success(validated_data):
            user = User.create(**validated_data)
            return Response(user.to_dict(), status=201)
        case Failure(errors):
            return Response({'errors': [err.to_dict() for err in errors]}, status=400)

Configuration Validation
------------------------

.. code-block:: python

    config_schema = schema.Schema(
        fields={
            'database_url': schema.Field(parser=parsers.parse_url, required=True),
            'port': schema.Field(
                parser=parsers.parse_int,
                validator=validators.minimum(1024) & validators.maximum(65535),
                required=True,
            ),
            'workers': schema.Field(
                parser=parsers.parse_int,
                validator=validators.minimum(1),
                required=False,
            ),
        }
    )

    # Validate configuration
    result = config_schema.validate(config_dict)

    match result:
        case Success(validated_config):
            app.configure(**validated_config)
        case Failure(errors):
            for err in errors:
                logger.error(f"Config error at {err.path}: {err.message}")
            sys.exit(1)

Form Data Validation
--------------------

.. code-block:: python

    registration_schema = schema.Schema(
        fields={
            'username': schema.Field(
                parser=parsers.parse_str,
                validator=validators.length(3, 20),
                required=True,
            ),
            'password': schema.Field(
                parser=parsers.parse_str,
                validator=validators.length(8, 128),
                required=True,
            ),
            'email': schema.Field(parser=parsers.parse_email, required=True),
            'age': schema.Field(
                parser=parsers.parse_int,
                validator=validators.minimum(18),
                required=True,
            ),
            'newsletter': schema.Field(parser=parsers.parse_bool, required=False),
        }
    )

    # Validate form submission
    result = registration_schema.validate(form_data)

Best Practices
==============

1. **Define schemas once**, reuse across application
2. **Use nested schemas** for complex objects rather than flat structures
3. **Enable strict mode** for APIs to catch typos early
4. **Make fields optional** when reasonable, but require essential data
5. **Combine parsers with validators** to enforce business rules
6. **Include context in errors** for debugging
7. **Test schemas** with both valid and invalid inputs

See Also
========

* :doc:`parsers` - Available parsers for field definitions
* :doc:`validators` - Available validators for field constraints
* :doc:`error_handling` - Working with ValidationError objects
* :doc:`../examples/schema_example` - Complete examples
