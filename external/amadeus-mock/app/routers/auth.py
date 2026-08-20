"""
POST /v1/security/oauth2/token
Mimics the Amadeus OAuth2 client_credentials flow.

Accepted credentials (configurable via env vars):
  AMADEUS_CLIENT_ID     (default: "test")
  AMADEUS_CLIENT_SECRET (default: "test")
"""

import os
import secrets
import time
from fastapi import APIRouter, Form, HTTPException, status
from app.dependencies import issue_token

router = APIRouter(tags=["Auth"])

VALID_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID", "test")
VALID_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET", "test")
TOKEN_TTL = int(os.getenv("TOKEN_TTL_SECONDS", "1799"))


@router.post("/oauth2/token")
def get_token(
    client_id: str = Form(...),
    client_secret: str = Form(...),
    grant_type: str = Form(...),
):
    if grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "errors": [
                    {
                        "status": 400,
                        "code": 38187,
                        "title": "Invalid grant type",
                        "detail": f"Grant type '{grant_type}' is not supported. Use 'client_credentials'.",
                    }
                ]
            },
        )

    if client_id != VALID_CLIENT_ID or client_secret != VALID_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "errors": [
                    {
                        "status": 401,
                        "code": 38188,
                        "title": "Invalid client",
                        "detail": "The client_id or client_secret is invalid.",
                    }
                ]
            },
        )

    token = secrets.token_urlsafe(32)
    issue_token(token, TOKEN_TTL)

    return {
        "type": "amadeusOAuth2Token",
        "username": f"ws-with-{client_id}@amadeus-mock",
        "application_name": "AmadeusMock",
        "client_id": client_id,
        "token_type": "Bearer",
        "access_token": token,
        "expires_in": TOKEN_TTL,
        "state": "approved",
        "scope": "",
    }
