"""Symmetric encryption for channel credentials at rest.

A Fernet key is derived from ``SECRET_KEY`` so connected-channel secrets (API
tokens, SMTP passwords) are never stored in plaintext. Rotating SECRET_KEY
invalidates stored credentials (they must be re-entered) — acceptable for MVP.
"""

import base64
import hashlib
import json

from cryptography.fernet import Fernet

from src.core.config import settings


def _fernet() -> Fernet:
    digest = hashlib.sha256(settings.secret_key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_dict(data: dict) -> str:
    return _fernet().encrypt(json.dumps(data).encode()).decode()


def decrypt_dict(token: str) -> dict:
    return json.loads(_fernet().decrypt(token.encode()).decode())
