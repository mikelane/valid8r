from uuid import UUID

import pytest

from valid8r.core.maybe import Success, Failure
from valid8r.core.parsers import parse_uuid


def make_uuid(version: int) -> str:
    # Generate a syntactically valid UUID for the given version.
    # UUID format: 8-4-4-4-12 hex; set variant nibble to 'a' (RFC 4122) and version nibble accordingly.
    if version == 7:
        # Use a plausible current timestamp (ms) for the first 48 bits
        import time

        ts_ms = int(time.time() * 1000)
        ts_hex = f'{ts_ms:012x}'
        seg1 = ts_hex[:8]
        seg2 = ts_hex[8:12]
        seg3 = '7abc'  # version nibble '7' + 3 arbitrary hex
    else:
        seg1 = '123e4567'
        seg2 = 'e89b'
        seg3 = f'{version:x}234'  # version nibble + 3 arbitrary hex

    seg4 = 'a234'  # variant nibble in [89ab] + 3 arbitrary hex
    seg5 = '1234567890ab'
    return f'{seg1}-{seg2}-{seg3}-{seg4}-{seg5}'


def make_v7_with_timestamp(ts_ms: int) -> str:
    ts_hex = f'{ts_ms:012x}'
    seg1 = ts_hex[:8]
    seg2 = ts_hex[8:12]
    seg3 = '7def'  # version 7
    seg4 = 'a234'  # RFC 4122 variant
    seg5 = '1234567890ab'
    return f'{seg1}-{seg2}-{seg3}-{seg4}-{seg5}'


class DescribeUuidParsing:
    @pytest.mark.parametrize('v', [1, 3, 4, 5, 7])
    def it_parses_valid_uuid_versions(self, v: int) -> None:
        u = make_uuid(v)
        match parse_uuid(u, version=v):
            case Success(value):
                assert isinstance(value, UUID)
                assert value.version == v
            case Failure(error):  # pragma: no cover - easier debug
                pytest.fail(f'Unexpected failure: {error}')

    def it_rejects_wrong_version_when_strict(self) -> None:
        v1 = make_uuid(1)
        match parse_uuid(v1, version=4, strict=True):
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'expected v4' in error and 'got v1' in error

    def it_rejects_v4_when_expect_v7_strict(self) -> None:
        v4 = make_uuid(4)
        match parse_uuid(v4, version=7, strict=True):
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'expected v7' in error and 'got v4' in error

    def it_rejects_v7_with_implausible_timestamp(self) -> None:
        import time

        now_ms = int(time.time() * 1000)
        too_future_ms = now_ms + 20 * 365 * 24 * 60 * 60 * 1000  # ~20 years
        forged_v7 = make_v7_with_timestamp(too_future_ms)
        match parse_uuid(forged_v7, version=7, strict=True):
            case Success(value):
                pytest.fail(f'Unexpected success: {value}')
            case Failure(error):
                assert 'timestamp' in error or 'implausibly' in error