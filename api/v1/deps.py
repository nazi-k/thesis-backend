from typing import Optional, cast

from beanie import PydanticObjectId
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

import schemas
from api.v1.exception import InvalidTokenError
from core import security
from core.config import settings
from models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/authentication/login",
    auto_error=False,
)


async def authenticate_token(token: str) -> Optional[User]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
        data = schemas.AuthTokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        # when the user is not authenticated and auto_error is True.
        raise InvalidTokenError()
    else:
        return await User.get(cast(PydanticObjectId, data.sub))


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """Gets the current user from the database."""
    if token:
        user = await authenticate_token(token)
    else:
        # This is the exception that is raised by the Depends() call
        # when the user is not authenticated and auto_error is True.
        raise InvalidTokenError()
    if not user:
        raise InvalidTokenError()
    return user
