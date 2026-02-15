from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

TOKEN_FILE = Path("token.json")
CREDENTIALS_FILE = Path("client_secrets.json")


class AuthError(RuntimeError):
    """Raised when credentials cannot be loaded."""


def get_credentials(scopes: list[str]) -> Credentials:
    """Load OAuth credentials for the provided scopes."""
    creds: Credentials | None = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise AuthError(
                    "client_secrets.json not found. Place OAuth client credentials in project root."
                )

            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), scopes)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return creds
