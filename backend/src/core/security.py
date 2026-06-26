"""Password hashing and session token utilities.

Backend is the source of truth for authentication (no JS auth library on the
server). Passwords are hashed with Argon2; session tokens are random opaque
strings stored hashed-by-reference in the sessions table.
"""

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def needs_rehash(password_hash: str) -> bool:
    return _ph.check_needs_rehash(password_hash)


def generate_session_token() -> str:
    """Return a cryptographically-strong opaque session token."""
    return secrets.token_urlsafe(48)


def hash_session_token(token: str) -> str:
    """Store only a hash of the session token at rest (defense in depth)."""
    return hashlib.sha256(token.encode()).hexdigest()
