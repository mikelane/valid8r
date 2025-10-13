from __future__ import annotations

import pytest

from valid8r.core.maybe import (
    Failure,
    Success,
)
from valid8r.core.parsers import (
    EmailAddress,
    UrlParts,
    parse_email,
    parse_url,
)


class DescribeUrlAndEmailParsers:
    @pytest.mark.parametrize(
        ('text', 'scheme', 'host', 'path', 'query'),
        [
            pytest.param('https://example.com/path?q=1', 'https', 'example.com', '/path', 'q=1', id='url-basic-http'),
        ],
    )
    def it_parses_valid_http_url(self, text: str, scheme: str, host: str, path: str, query: str) -> None:
        match parse_url(text):
            case Success(parts):
                assert isinstance(parts, UrlParts)
                assert parts.scheme == scheme
                assert parts.host == host
                assert parts.path == path
                assert parts.query == query
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    @pytest.mark.parametrize(
        ('url', 'user', 'pwd', 'host', 'port', 'frag'),
        [
            pytest.param(
                'https://alice:sekret@example.com:8443/#top',
                'alice',
                'sekret',
                'example.com',
                8443,
                'top',
                id='url-userinfo-port-fragment',
            ),
            pytest.param('http://localhost:8080/', None, None, 'localhost', 8080, '', id='url-localhost-port'),
        ],
    )
    def it_parses_userinfo_port_fragment(
        self, url: str, user: str | None, pwd: str | None, host: str, port: int | None, frag: str
    ) -> None:
        match parse_url(url):
            case Success(parts):
                assert parts.username == user
                assert parts.password == pwd
                assert parts.host == host
                assert parts.port == port
                assert parts.fragment == frag
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    def it_parses_ipv6_literal_host(self) -> None:
        match parse_url('http://[2001:db8::1]/x'):
            case Success(parts):
                assert parts.host == '2001:db8::1'
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    def it_ignores_surrounding_whitespace_for_url(self) -> None:
        match parse_url('  https://EXAMPLE.com  '):
            case Success(parts):
                assert parts.scheme == 'https'
                assert parts.host == 'example.com'
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    @pytest.mark.parametrize(
        'text',
        [
            pytest.param('example.com/path', id='no-scheme'),
            pytest.param('ftp://example.com/file', id='unsupported-scheme'),
        ],
    )
    def it_rejects_url_with_missing_or_unsupported_scheme(self, text: str) -> None:
        match parse_url(text):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert 'unsupported url scheme' in err.lower()

    @pytest.mark.parametrize(
        'text',
        [
            pytest.param('http:/just-path', id='single-slash-path'),
            pytest.param('https:///only', id='triple-slash-no-host'),
        ],
    )
    def it_rejects_url_missing_host_when_required(self, text: str) -> None:
        match parse_url(text):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert 'URL requires host' in err

    def it_rejects_url_with_invalid_host_label(self) -> None:
        match parse_url('https://-bad-.example/'):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert 'invalid host' in err.lower()

    @pytest.mark.parametrize(
        'url',
        [
            pytest.param('http://example.com:99999/', id='port-too-large'),
            pytest.param('http://example.com:70000/', id='port-exceeds-65535'),
            pytest.param('http://example.com:-1/', id='port-negative'),
        ],
    )
    def it_rejects_url_with_invalid_port(self, url: str) -> None:
        match parse_url(url):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert 'invalid host' in err.lower() or 'url requires host' in err.lower()

    def it_accepts_port_zero(self) -> None:
        """Port 0 is technically reserved but syntactically valid."""
        match parse_url('http://example.com:0/'):
            case Success(parts):
                assert parts.port == 0
                assert parts.host == 'example.com'
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    # Email parsing

    @pytest.mark.parametrize(
        ('addr', 'local', 'domain'),
        [
            pytest.param('user@example.com', 'user', 'example.com', id='email-simple'),
            pytest.param('first.last+tag@Example.COM', 'first.last+tag', 'example.com', id='email-plus-tag'),
        ],
    )
    def it_parses_simple_emails(self, addr: str, local: str, domain: str) -> None:
        match parse_email(addr):
            case Success(value):
                assert isinstance(value, EmailAddress)
                assert value.local == local
                assert value.domain == domain
            case Failure(err):
                pytest.fail(f'unexpected failure: {err}')

    @pytest.mark.parametrize(
        'addr',
        [
            pytest.param('user@[192.0.2.1]', id='email-ipv4-literal'),
            pytest.param('user@[2001:db8::1]', id='email-ipv6-literal'),
        ],
    )
    def it_rejects_emails_with_ip_domain_literals(self, addr: str) -> None:
        """email-validator rejects IP address literals by default."""
        match parse_email(addr):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                # email-validator rejects bracketed IP addresses
                assert 'bracketed' in err.lower() or 'address literal' in err.lower()

    @pytest.mark.parametrize(
        'text',
        [
            pytest.param('not-an-email', id='no-at'),
        ],
    )
    def it_rejects_malformed_email(self, text: str) -> None:
        match parse_email(text):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert 'email' in err

    @pytest.mark.parametrize(
        'addr',
        [
            pytest.param('.starts.with.dot@ex', id='local-starts-with-dot'),
            pytest.param('ends.with.dot.@ex', id='local-ends-with-dot'),
            pytest.param('double..dot@ex', id='local-double-dot'),
            pytest.param('""@ex', id='local-empty-quotes'),
        ],
    )
    def it_rejects_bad_local_parts(self, addr: str) -> None:
        match parse_email(addr):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                # email-validator provides descriptive RFC-compliant errors
                assert len(err) > 0  # Any error message is fine

    @pytest.mark.parametrize(
        'addr',
        [
            pytest.param('user@-bad-.example', id='domain-bad-label-hyphens'),
            pytest.param('user@exa_mple.com', id='domain-underscore'),
            pytest.param('user@too..many..dots', id='domain-empty-labels'),
            pytest.param('user@', id='domain-missing'),
        ],
    )
    def it_rejects_bad_domains(self, addr: str) -> None:
        match parse_email(addr):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                # email-validator provides descriptive RFC-compliant errors
                assert len(err) > 0  # Any error message is fine

    def it_rejects_multiple_at_signs(self) -> None:
        match parse_email('a@b@c'):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                # email-validator provides descriptive RFC-compliant errors
                assert len(err) > 0  # Any error message is fine

    def it_rejects_empty_string(self) -> None:
        match parse_email(''):
            case Success(value):
                pytest.fail(f'unexpected success: {value}')
            case Failure(err):
                assert 'must not be empty' in err.lower()
