from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr, HttpUrl


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserBase(BaseModel):
    name: str
    email: EmailStr
    avatarUrl: HttpUrl | None = None


class UserInProject(UserBase):
    id: PydanticObjectId
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    currentUser: UserInProject


class UserCreate(UserBase):
    password: str
    password2: str
