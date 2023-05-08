from fastapi import APIRouter

import schemas
from api.v1.exception import EmailAlreadyRegisteredError, PasswordsDoNotMatchError, InvalidPasswordOrEmail
from core.security import create_access_token, get_password_hash

from models.user import User

router = APIRouter()


@router.post("/login")
async def login(user_credentials: schemas.UserLogin):
    if user := await User.authenticate(email=user_credentials.email, password=user_credentials.password):
        return schemas.AuthToken(authToken=create_access_token(user.id))
    else:
        raise InvalidPasswordOrEmail()


@router.post("/register")
async def register(user_create: schemas.UserCreate):
    if await User.get_by_email(email=user_create.email):
        raise EmailAlreadyRegisteredError()
    elif user_create.password != user_create.password2:
        raise PasswordsDoNotMatchError()
    else:
        user = User(
            name=user_create.name,
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
        )
        await user.save()
        return {"success": True, "message": "User created successfully."}
