import base64
import hashlib
import json
import secrets
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .config import DRIVE_FILE_SCOPE, OAuthConfig

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"


class OAuthError(RuntimeError):
    pass


@dataclass
class TokenSet:
    access_token: str
    expires_at: datetime
    refresh_token: str | None = None

    def needs_refresh(self) -> bool:
        return self.expires_at <= datetime.now(timezone.utc) + timedelta(seconds=60)


def create_pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    verifier = verifier[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def parse_callback(path: str, expected_state: str) -> str:
    params = urllib.parse.parse_qs(urllib.parse.urlparse(path).query)
    if params.get("state", [""])[0] != expected_state:
        raise OAuthError("OAuth state validation failed")
    if "error" in params:
        raise OAuthError(params["error"][0])
    code = params.get("code", [""])[0]
    if not code:
        raise OAuthError("Authorization code is missing")
    return code


def build_authorization_url(
    config: OAuthConfig, redirect_uri: str, state: str, challenge: str
) -> str:
    query = urllib.parse.urlencode(
        {
            "client_id": config.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": DRIVE_FILE_SCOPE,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return f"{AUTH_URL}?{query}"


def exchange_code(
    config: OAuthConfig, code: str, verifier: str, redirect_uri: str, opener=None
) -> TokenSet:
    values = {
        "client_id": config.client_id,
        "code": code,
        "code_verifier": verifier,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    if config.client_secret:
        values["client_secret"] = config.client_secret
    return _token_request(
        values,
        opener,
    )


def refresh_access_token(
    config: OAuthConfig, refresh_token: str, opener=None
) -> TokenSet:
    values = {
        "client_id": config.client_id,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    if config.client_secret:
        values["client_secret"] = config.client_secret
    token = _token_request(
        values,
        opener,
    )
    token.refresh_token = refresh_token
    return token


def authorize_interactive(
    config: OAuthConfig, timeout: int = 180, browser_open=webbrowser.open
) -> TokenSet:
    verifier, challenge = create_pkce_pair()
    state = secrets.token_urlsafe(32)
    result = {}

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                result["code"] = parse_callback(self.path, state)
                body = "Authorization completed. You may return to QGIS."
                status = 200
            except OAuthError as error:
                result["error"] = error
                body = "Authorization failed. You may return to QGIS."
                status = 400
            encoded = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, format, *args):
            return

    server = HTTPServer(("127.0.0.1", 0), CallbackHandler)
    server.timeout = timeout
    redirect_uri = f"http://127.0.0.1:{server.server_port}/callback"
    url = build_authorization_url(config, redirect_uri, state, challenge)
    if not browser_open(url):
        server.server_close()
        raise OAuthError("The system browser could not be opened")
    try:
        server.handle_request()
    finally:
        server.server_close()
    if "error" in result:
        raise result["error"]
    if "code" not in result:
        raise OAuthError("Authorization timed out")
    return exchange_code(config, result["code"], verifier, redirect_uri)


def _token_request(values: dict[str, str], opener=None) -> TokenSet:
    request = urllib.request.Request(
        TOKEN_URL,
        data=urllib.parse.urlencode(values).encode("ascii"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    open_url = opener or urllib.request.urlopen
    try:
        with open_url(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, urllib.error.HTTPError) as error:
        raise OAuthError(f"Token request failed: {error}") from error
    access_token = str(payload.get("access_token", ""))
    if not access_token:
        raise OAuthError("Token response has no access token")
    expires_in = int(payload.get("expires_in", 3600))
    return TokenSet(
        access_token=access_token,
        refresh_token=payload.get("refresh_token"),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in),
    )
