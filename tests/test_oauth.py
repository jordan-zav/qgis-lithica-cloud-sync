import base64
import hashlib

import pytest
import urllib.parse

from lithica_drive_sync.config import OAuthConfig
from lithica_drive_sync.oauth import (
    OAuthError,
    build_authorization_url,
    create_pkce_pair,
    parse_callback,
)


def test_pkce_challenge_matches_verifier():
    verifier, challenge = create_pkce_pair()

    expected = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    assert challenge == expected
    assert 43 <= len(verifier) <= 128


def test_callback_rejects_wrong_state():
    with pytest.raises(OAuthError, match="state"):
        parse_callback("/callback?code=abc&state=wrong", "expected")


def test_callback_returns_code_for_matching_state():
    assert parse_callback("/callback?code=abc&state=expected", "expected") == "abc"


def test_authorization_url_uses_only_drive_file_scope():
    url = build_authorization_url(
        OAuthConfig("client-id", "project-id"),
        "http://127.0.0.1:1234/callback",
        "state",
        "challenge",
    )

    assert "drive.file" in url
    assert "drive.readonly" not in url


def test_code_exchange_sends_desktop_client_secret():
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"access_token":"token","expires_in":3600}'

    def opener(request, timeout):
        captured.update(urllib.parse.parse_qs(request.data.decode("ascii")))
        return Response()

    from lithica_drive_sync.oauth import exchange_code

    exchange_code(
        OAuthConfig("client-id", "project-id", "desktop-secret"),
        "code",
        "verifier",
        "http://127.0.0.1/callback",
        opener,
    )

    assert captured["client_secret"] == ["desktop-secret"]
