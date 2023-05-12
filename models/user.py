import base64
from datetime import datetime
from typing import Self

import httpx
from beanie import Document, PydanticObjectId, Link, before_event, Replace, Update, Indexed
from pydantic import Field, EmailStr, HttpUrl

from core import verify_password, settings

import typing

from utils import imgbb

if typing.TYPE_CHECKING:
    from .comment import Comment
    from .issue import Issue


class User(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    name: str = Field(min_length=3, max_length=100)
    email: Indexed(EmailStr, unique=True)  # type: ignore[valid-type]
    avatarUrl: HttpUrl | None = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    comments: list[Link["Comment"]] = []
    issues: list[Link["Issue"]] = []
    hashed_password: str

    @property
    def key(self):
        return str(self.id)

    @before_event(Replace, Update)
    def updated_datetime(self):
        self.updatedAt = datetime.utcnow()

    class Settings:
        name = "users"
        use_state_management = True

    @classmethod
    async def get_by_email(cls, *, email: str) -> Self | None:
        # Because all usernames are converted to lowercase at user creation,
        # make the given 'username' parameter also lowercase.
        return await cls.find_one(cls.email == email.lower())

    @classmethod
    async def authenticate(
            cls,
            *,
            email: str,
            password: str,
    ) -> Self | None:
        user = await cls.get_by_email(email=email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def change_photo(self, *, avatar_file: bytes):
        file_data_base64 = base64.b64encode(avatar_file).decode('utf-8')
        photo_url = await imgbb.upload(file_data_base64)
        self.avatarUrl = photo_url
        await self.save()

from .comment import Comment
from .issue import Issue

User.update_forward_refs(Comment=Comment, Issue=Issue)
