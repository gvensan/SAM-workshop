"""
Token validation dependency.
Set REQUIRE_AUTH=false to skip token checks (useful for quick workshop demos).
"""

import os
import time
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "true").lower() != "false"

# Static token accepted alongside OAuth-issued tokens, so clients without
# OAuth2 support (e.g. SAM Desktop API connectors, which only offer HTTP
# Basic/Bearer auth) can authenticate with a fixed Bearer token.
# Set STATIC_BEARER_TOKEN="" to require OAuth-issued tokens only.
STATIC_BEARER_TOKEN = os.getenv("STATIC_BEARER_TOKEN", "workshop")

# In-memory token store: token -> expiry timestamp
_active_tokens: dict[str, float] = {}

security = HTTPBearer(auto_error=False)


def issue_token(token: str, ttl_seconds: int = 1799) -> None:
    _active_tokens[token] = time.time() + ttl_seconds


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    if not REQUIRE_AUTH:
        return "mock-token"

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "errors": [
                    {
                        "status": 401,
                        "code": 38190,
                        "title": "Missing or invalid credentials",
                        "detail": "Missing authorization header",
                    }
                ]
            },
        )

    token = credentials.credentials

    # Fixed token for OAuth2-less clients (see STATIC_BEARER_TOKEN above)
    if STATIC_BEARER_TOKEN and token == STATIC_BEARER_TOKEN:
        return token

    expiry = _active_tokens.get(token)

    if expiry is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "errors": [
                    {
                        "status": 401,
                        "code": 38190,
                        "title": "Invalid access token",
                        "detail": "The access token provided is invalid or has been revoked",
                    }
                ]
            },
        )

    if time.time() > expiry:
        del _active_tokens[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "errors": [
                    {
                        "status": 401,
                        "code": 38191,
                        "title": "Expired access token",
                        "detail": "The access token provided has expired",
                    }
                ]
            },
        )

    return token
