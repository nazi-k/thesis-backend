from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel

from .user import UserInProject


class Comment(BaseModel):
    id: PydanticObjectId
    body: str
    createdAt: datetime
    updatedAt: datetime
    userId: PydanticObjectId
    issueId: PydanticObjectId
    user: UserInProject


class CommentPatch(BaseModel):
    body: str


class CommentCreate(BaseModel):
    body: str
    issueId: PydanticObjectId
    userId: PydanticObjectId

