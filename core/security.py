from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Algorithm used to generate the JWT token
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a hashed password and a plain password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    payload = {
        "exp": expire,
        "sub": str(subject),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)