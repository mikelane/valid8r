from __future__ import annotations

import uuid as std_uuid
from uuid import UUID

import pytest
import uuid_utils as uuidu

from valid8r.core.maybe import (
    Failure,
    Success,
)
from valid8r.core.parsers import parse_uuid


def generate_uuid_of_version(v: int) -> str:
    if v == 1:
        return str(std_uuid.uuid1())
    if v == 3:
        return str(std_uuid.uuid3(std_uuid.NAMESPACE_DNS, 'example.com'))
    if v == 4:
        return str(std_uuid.uuid4())
    if v == 5:
        return str(std_uuid.uuid5(std_uuid.NAMESPACE_DNS, 'example.com'))
    if v == 6:
        return str(uuidu.uuid6())
    if v == 7:
        return str(uuidu.uuid7())
    if v == 8:
        return str(uuidu.uuid8(b'\x00' * 16))
    raise ValueError('Unsupported version for test')


class DescribeUuidParsing:
    @pytest.mark.parametrize(
        'expected',
        [
            pytest.param(1, id='uuid version 1'),
            pytest.param(3, id='uuid version 3'),
            pytest.param(4, id='uuid version 4'),
            pytest.param(5, id='uuid version 5'),
            pytest.param(6, id='uuid version 6'),
            pytest.param(7, id='uuid version 7'),
            pytest.param(8, id='uuid version 8'),
        ],
    )
    def it_validates_expected_version_against_all_others(self, expected: int) -> None:
        # Generate one valid UUID for the expected version
        correct = generate_uuid_of_version(expected)
        match parse_uuid(correct, version=expected, strict=True):
            case Success(value):
                assert isinstance(value, UUID)
                assert value.version == expected
            case Failure(error):  # pragma: no cover
                pytest.fail(f'Unexpected failure for v{expected}: {error}')

        # For all other versions, ensure strict mismatch
        for other in [v for v in (1, 3, 4, 5, 6, 7, 8) if v != expected]:
            candidate = generate_uuid_of_version(other)
            match parse_uuid(candidate, version=expected, strict=True):
                case Success(value):
                    pytest.fail(f'Unexpected success: expected v{expected}, got {value.version}')
                case Failure(error):
                    assert f'expected v{expected}' in error
