"""Benchmark scenarios for comparing validation libraries.

This module implements equivalent validation scenarios across all tested libraries:
- valid8r (this library)
- Pydantic (Rust-powered)
- marshmallow (schema-based)
- cerberus (lightweight)

Each function returns the parsed value on success, or None on failure.
"""

from __future__ import annotations

from typing import Any

from cerberus import Validator
from marshmallow import Schema, fields
from marshmallow import ValidationError as MarshmallowValidationError
from pydantic import (
    BaseModel,
    EmailStr,
    HttpUrl,
    ValidationError,
)

from valid8r import parsers

# =============================================================================
# Basic Type Parsing Benchmarks
# =============================================================================


def benchmark_valid8r_int(value: str) -> int | None:
    """Parse integer using valid8r."""
    result = parsers.parse_int(value)
    return result.value_or(None)


def benchmark_pydantic_int(value: str) -> int | None:
    """Parse integer using Pydantic."""

    class IntModel(BaseModel):
        value: int

    try:
        model = IntModel(value=value)
        return model.value
    except ValidationError:
        return None


def benchmark_marshmallow_int(value: str) -> int | None:
    """Parse integer using marshmallow."""

    class IntSchema(Schema):
        value = fields.Integer()

    schema = IntSchema()
    try:
        result = schema.load({'value': value})
        return result['value']
    except MarshmallowValidationError:
        return None


def benchmark_cerberus_int(value: str) -> int | None:
    """Parse integer using cerberus."""
    v = Validator({'value': {'type': 'integer', 'coerce': int}})
    try:
        result = v.validated({'value': value})
        if result is not None:
            return result['value']
        return None
    except (ValueError, TypeError):
        return None


# =============================================================================
# Email Validation Benchmarks
# =============================================================================


def benchmark_valid8r_email(value: str) -> str | None:
    """Parse email using valid8r."""
    result = parsers.parse_email(value)
    if result.is_success():
        email_obj = result.value_or(None)
        if email_obj:
            return f'{email_obj.local}@{email_obj.domain}'
    return None


def benchmark_pydantic_email(value: str) -> str | None:
    """Parse email using Pydantic."""

    class EmailModel(BaseModel):
        email: EmailStr

    try:
        model = EmailModel(email=value)
        return str(model.email)
    except ValidationError:
        return None


def benchmark_marshmallow_email(value: str) -> str | None:
    """Parse email using marshmallow."""

    class EmailSchema(Schema):
        email = fields.Email()

    schema = EmailSchema()
    try:
        result = schema.load({'email': value})
        return result['email']
    except MarshmallowValidationError:
        return None


def benchmark_cerberus_email(value: str) -> str | None:
    """Parse email using cerberus."""
    # Cerberus doesn't have built-in email validation, use regex
    import re

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, value):
        return value
    return None


# =============================================================================
# URL Validation Benchmarks
# =============================================================================


def benchmark_valid8r_url(value: str) -> str | None:
    """Parse URL using valid8r."""
    result = parsers.parse_url(value)
    if result.is_success():
        url_obj = result.value_or(None)
        if url_obj:
            # Reconstruct URL from parts
            return f'{url_obj.scheme}://{url_obj.host}{url_obj.path or ""}'
    return None


def benchmark_pydantic_url(value: str) -> str | None:
    """Parse URL using Pydantic."""

    class UrlModel(BaseModel):
        url: HttpUrl

    try:
        model = UrlModel(url=value)
        return str(model.url)
    except ValidationError:
        return None


def benchmark_marshmallow_url(value: str) -> str | None:
    """Parse URL using marshmallow."""

    class UrlSchema(Schema):
        url = fields.Url()

    schema = UrlSchema()
    try:
        result = schema.load({'url': value})
        return result['url']
    except MarshmallowValidationError:
        return None


def benchmark_cerberus_url(value: str) -> str | None:
    """Parse URL using cerberus."""
    # Cerberus doesn't have built-in URL validation, use regex
    import re

    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if re.match(url_pattern, value, re.IGNORECASE):
        return value
    return None


# =============================================================================
# Nested Object Validation Benchmarks
# =============================================================================


def benchmark_valid8r_nested(data: dict[str, Any]) -> dict[str, Any] | None:
    """Parse nested object using valid8r."""
    # Parse individual fields
    name = data.get('name')
    age_result = parsers.parse_int(str(data.get('age')))
    email_result = parsers.parse_email(data.get('email', ''))

    if age_result.is_success() and email_result.is_success():
        email_obj = email_result.value_or(None)
        if email_obj:
            return {
                'name': name,
                'age': age_result.value_or(None),
                'email': f'{email_obj.local}@{email_obj.domain}',
            }
    return None


def benchmark_pydantic_nested(data: dict[str, Any]) -> dict[str, Any] | None:
    """Parse nested object using Pydantic."""

    class UserModel(BaseModel):
        name: str
        age: int
        email: EmailStr

    try:
        model = UserModel(**data)
        return {'name': model.name, 'age': model.age, 'email': str(model.email)}
    except ValidationError:
        return None


def benchmark_marshmallow_nested(data: dict[str, Any]) -> dict[str, Any] | None:
    """Parse nested object using marshmallow."""

    class UserSchema(Schema):
        name = fields.String(required=True)
        age = fields.Integer(required=True)
        email = fields.Email(required=True)

    schema = UserSchema()
    try:
        return schema.load(data)
    except MarshmallowValidationError:
        return None


def benchmark_cerberus_nested(data: dict[str, Any]) -> dict[str, Any] | None:
    """Parse nested object using cerberus."""
    schema = {
        'name': {'type': 'string', 'required': True},
        'age': {'type': 'integer', 'required': True, 'coerce': int},
        'email': {'type': 'string', 'required': True, 'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
    }
    v = Validator(schema)
    try:
        result = v.validated(data)
        return result if result is not None else None
    except (ValueError, TypeError):
        return None


# =============================================================================
# List Validation Benchmarks
# =============================================================================


def benchmark_valid8r_list(data: list[str]) -> list[int] | None:
    """Parse list of integers using valid8r."""
    # valid8r's parse_list takes a string, so we manually parse each item
    results = []
    for item in data:
        result = parsers.parse_int(item)
        if result.is_failure():
            return None
        results.append(result.value_or(0))
    return results


def benchmark_pydantic_list(data: list[str]) -> list[int] | None:
    """Parse list of integers using Pydantic."""

    class ListModel(BaseModel):
        items: list[int]

    try:
        model = ListModel(items=data)
        return model.items
    except ValidationError:
        return None


def benchmark_marshmallow_list(data: list[str]) -> list[int] | None:
    """Parse list of integers using marshmallow."""

    class ListSchema(Schema):
        items = fields.List(fields.Integer())

    schema = ListSchema()
    try:
        result = schema.load({'items': data})
        return result['items']
    except MarshmallowValidationError:
        return None


def benchmark_cerberus_list(data: list[str]) -> list[int] | None:
    """Parse list of integers using cerberus."""
    schema = {'items': {'type': 'list', 'schema': {'type': 'integer', 'coerce': int}}}
    v = Validator(schema)
    try:
        result = v.validated({'items': data})
        if result is not None:
            return result['items']
        return None
    except (ValueError, TypeError):
        return None
