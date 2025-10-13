from __future__ import annotations

import ipaddress as ip

import pytest

from valid8r.core.maybe import (
    Failure,
    Success,
)
from valid8r.core.parsers import (
    parse_cidr,
    parse_ip,
    parse_ipv4,
    parse_ipv6,
)


class DescribeIpParsers:
    @pytest.mark.parametrize(
        ('text', 'normalized'),
        [
            pytest.param('192.168.0.1', '192.168.0.1', id='v4-valid-192-168-0-1'),
            pytest.param('8.8.8.8', '8.8.8.8', id='v4-valid-8-8-8-8'),
            pytest.param(' 10.0.0.254 ', '10.0.0.254', id='v4-trim-whitespace'),
        ],
    )
    def it_parses_ipv4_success(self, text: str, normalized: str) -> None:
        match parse_ipv4(text):
            case Success(value):
                assert isinstance(value, ip.IPv4Address)
                assert str(value) == normalized
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    @pytest.mark.parametrize(
        ('text', 'message'),
        [
            pytest.param('256.0.0.1', 'not a valid IPv4 address', id='v4-invalid-octet-range'),
            pytest.param('192.168.0', 'not a valid IPv4 address', id='v4-invalid-too-few-octets'),
            pytest.param('192.168.0.1.1', 'not a valid IPv4 address', id='v4-invalid-too-many-octets'),
            pytest.param('abc', 'not a valid IPv4 address', id='v4-invalid-alpha'),
            pytest.param('', 'must not be empty', id='v4-empty'),
            pytest.param(None, 'must be a string', id='v4-wrong-type'),
        ],
    )
    def it_rejects_invalid_ipv4(self, text: object, message: str) -> None:
        match parse_ipv4(text):  # type: ignore[arg-type]
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert message in err

    @pytest.mark.parametrize(
        ('text', 'normalized'),
        [
            pytest.param('::1', '::1', id='v6-loopback'),
            pytest.param('2001:db8::1', '2001:db8::1', id='v6-doc-prefix'),
            pytest.param('  FE80::1  ', 'fe80::1', id='v6-trim-and-lowercase'),
            pytest.param('2001:db8:0:0:0:0:2:1', '2001:db8::2:1', id='v6-compress'),
        ],
    )
    def it_parses_ipv6_success(self, text: str, normalized: str) -> None:
        match parse_ipv6(text):
            case Success(value):
                assert isinstance(value, ip.IPv6Address)
                assert str(value) == normalized
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    @pytest.mark.parametrize(
        'text',
        [
            pytest.param('2001:::1', id='v6-invalid-triple-colon'),
            pytest.param('::ffff:999.1.1.1', id='v6-invalid-embedded-v4'),
            pytest.param('fe80::1%eth0', id='v6-scope-id'),
            pytest.param('abc', id='v6-alpha'),
        ],
    )
    def it_rejects_invalid_ipv6(self, text: str) -> None:
        match parse_ipv6(text):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert 'not a valid IPv6 address' in err

    @pytest.mark.parametrize(
        ('text', 'kind', 'normalized'),
        [
            pytest.param('127.0.0.1', ip.IPv4Address, '127.0.0.1', id='ip-v4'),
            pytest.param('::1', ip.IPv6Address, '::1', id='ip-v6'),
        ],
    )
    def it_parses_generic_ip(self, text: str, kind: type, normalized: str) -> None:
        match parse_ip(text):
            case Success(value):
                assert isinstance(value, kind)
                assert str(value) == normalized
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    def it_rejects_generic_non_ip(self) -> None:
        match parse_ip('hostname.local'):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert 'not a valid IP address' in err

    @pytest.mark.parametrize(
        ('text', 'normalized'),
        [
            pytest.param('10.0.0.0/8', '10.0.0.0/8', id='cidr-v4-strict-8'),
            pytest.param('192.168.1.0/24', '192.168.1.0/24', id='cidr-v4-strict-24'),
            pytest.param('0.0.0.0/0', '0.0.0.0/0', id='cidr-v4-strict-0'),
        ],
    )
    def it_parses_ipv4_cidr_strict(self, text: str, normalized: str) -> None:
        match parse_cidr(text):
            case Success(value):
                assert isinstance(value, ip.IPv4Network)
                assert str(value) == normalized
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    @pytest.mark.parametrize(
        ('text', 'normalized'),
        [
            pytest.param('2001:db8::/32', '2001:db8::/32', id='cidr-v6-strict-32'),
            pytest.param('::/0', '::/0', id='cidr-v6-strict-0'),
            pytest.param('2001:db8:abcd::/48', '2001:db8:abcd::/48', id='cidr-v6-strict-48'),
        ],
    )
    def it_parses_ipv6_cidr_strict(self, text: str, normalized: str) -> None:
        match parse_cidr(text):
            case Success(value):
                assert isinstance(value, ip.IPv6Network)
                assert str(value) == normalized
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    @pytest.mark.parametrize(
        'text',
        [
            pytest.param('10.0.0.0/33', id='cidr-v4-prefix-too-large'),
            pytest.param('2001:db8::/129', id='cidr-v6-prefix-too-large'),
            pytest.param('192.168.1.0/-1', id='cidr-negative-prefix'),
            pytest.param('192.168.1.0/x', id='cidr-non-numeric-prefix'),
        ],
    )
    def it_rejects_cidr_invalid_prefix(self, text: str) -> None:
        match parse_cidr(text):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert 'not a valid network' in err

    def it_rejects_cidr_with_host_bits_strict(self) -> None:
        match parse_cidr('10.0.0.1/24'):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert 'has host bits set' in err

    def it_masks_host_bits_when_non_strict(self) -> None:
        match parse_cidr('10.0.0.1/24', strict=False):
            case Success(value):
                assert isinstance(value, ip.IPv4Network)
                assert str(value) == '10.0.0.0/24'
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    def it_ignores_surrounding_whitespace(self) -> None:
        match parse_cidr('  172.16.0.0/16  '):
            case Success(value):
                assert isinstance(value, ip.IPv4Network)
                assert str(value) == '172.16.0.0/16'
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    @pytest.mark.parametrize(
        'text',
        [
            pytest.param('fe80::1%eth0', id='reject-scope-id'),
            pytest.param('http://192.168.0.1', id='reject-url'),
        ],
    )
    def it_rejects_non_pure_addresses(self, text: str) -> None:
        match parse_ip(text):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert 'not a valid IP address' in err
