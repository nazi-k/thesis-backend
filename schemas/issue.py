from beanie import PydanticObjectId
from pydantic import BaseModel
from datetime import datetime

from enums.issue import IssueType, IssueStatus, IssuePriority

import typing

if typing.TYPE_CHECKING:
    from schemas import UserInProject, Comment


class IssueBase(BaseModel):
    title: str
    type: IssueType
    status: IssueStatus
    priority: IssuePriority
    listPosition: int

    class Config:
        use_enum_values = True


class IssueInDBBase(IssueBase):
    class Config:
        orm_mode = True


class IssueInProject(IssueInDBBase):
    key: str
    id: PydanticObjectId
    createdAt: datetime
    updatedAt: datetime
    userIds: list[PydanticObjectId] = []


class Issue(IssueInProject):
    description: str | None = None
    descriptionText: str | None = None
    estimate: int | None = None
    timeSpent: int | None = None
    timeRemaining: int | None = None
    users: list["UserInProject"] = []
    comments: list["Comment"] = []


class IssuePatch(BaseModel):
    title: str | None = None
    type: str | None = None
    status: str | None = None
    priority: str | None = None
    listPosition: int | None = None
    description: str | None = None
    descriptionText: str | None = None
    estimate: int | None = None
    timeSpent: int | None = None
    timeRemaining: int | None = None
    users: list["UserInProject"] = []
    comments: list["Comment"] = []


class IssueIn(BaseModel):
    title: str
    type: IssueType
    status: IssueStatus
    priority: IssuePriority
    description: str | None = None
    userIds: list[PydanticObjectId] = []
    projectId: PydanticObjectId
    reporterId: PydanticObjectId


class IssueOut(BaseModel):
    issue: Issue


from .user import UserInProject
from .comment import Comment

Issue.update_forward_refs(UserInProject=UserInProject, Comment=Comment)
IssuePatch.update_forward_refs(UserInProject=UserInProject, Comment=Comment)
