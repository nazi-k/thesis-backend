from beanie import PydanticObjectId
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from .issue import IssueInProject
from .user import UserInProject
from enums.project import ProjectCategory


class ProjectBase(BaseModel):
    name: str
    url: str | None = None
    description: str | None = None
    category: ProjectCategory

    class Config:
        use_enum_values = True


class ProjectPut(ProjectBase):
    name: str = Field(None, min_length=3, max_length=50)
    category: ProjectCategory | None = None
    emails: set[EmailStr] = []

    class Config:
        use_enum_values = True


class ProjectCreate(ProjectBase):
    emails: set[EmailStr] = []


class ProjectOut(ProjectBase):
    id: PydanticObjectId

    class Config:
        orm_mode = True


class ProjectWithIssuesAndUser(ProjectOut):
    createdAt: datetime
    updatedAt: datetime
    key: str
    issuesCount: int
    users: list[UserInProject] = []
    issues: list[IssueInProject] = []

    class Config:
        use_enum_values = True


class Project(BaseModel):
    project: ProjectWithIssuesAndUser
