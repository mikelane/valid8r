import re
from uuid import UUID

import pytest

from valid8r.core.maybe import Success, Failure
from valid8r.core.parsers import parse_uuid


def make_uuid(version: int) -> str:
    # Generate a syntactically valid UUID for the given version.
    # UUID format: 8-4-4-4-12 hex; set variant nibble to 'a' (RFC 4122) and version nibble accordingly.
    seg1 = '123e4567'
    seg2 = 'e89b'
    seg3 = f'{version:x}234'  # version nibble + 3 arbitrary hex
    seg4 = 'a234'  # variant nibble in [89ab] + 3 arbitrary hex
    seg5 = '1234567890ab'
    return f'{seg1}-{seg2}-{seg3}-{seg4}-{seg5}'


@pytest.mark.parametrize('v', [1, 3, 4, 5, 7])
def test_parse_valid_uuid_versions(v: int) -> None:
    u = make_uuid(v)
    match parse_uuid(u, version=v):
        case Success(value):
            assert isinstance(value, UUID)
            assert value.version == v
        case Failure(error):  # pragma: no cover - easier debug
            pytest.fail(f'Unexpected failure: {error}')


def test_reject_wrong_version_when_strict() -> None:
    v1 = make_uuid(1)
    match parse_uuid(v1, version=4, strict=True):
        case Success(value):
            pytest.fail(f'Unexpected success: {value}')
        case Failure(error):
            assert 'expected v4' in error and 'got v1' in error