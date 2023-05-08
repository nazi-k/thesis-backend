from datetime import datetime
from beanie import Document, Link, before_event, Update, Replace, PydanticObjectId
from beanie.odm.operators.find.comparison import In
from pydantic import Field

import schemas
from enums.project import ProjectCategory

import typing

if typing.TYPE_CHECKING:
    from .user import User
    from .issue import Issue


class Project(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    name: str
    url: str | None = None
    description: str | None = None
    category: ProjectCategory
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    issues: list[Link["Issue"]] = []
    users: list[Link["User"]] = []

    @property
    def key(self):
        return str(self.id)

    @property
    def issuesCount(self):
        return len(self.issues)

    @before_event(Replace, Update)
    def updated_datetime(self):
        self.updatedAt = datetime.utcnow()

    class Settings:
        name = "projects"
        use_state_management = True

    class Config:
        use_enum_values = True

    async def to_schema(self) -> schemas.Project:
        users = [
            schemas.UserInProject.from_orm(user)
            for user in await User.find_many(In(User.id, [user.ref.id for user in self.users])).to_list()
        ]
        issue = [
            schemas.IssueInProject.from_orm(issue)
            for issue in await Issue.find(Issue.project == self.to_ref()).to_list()
        ]
        return schemas.Project(
            project=schemas.ProjectWithIssuesAndUser(
                users=users,
                issues=issue,
                key=self.key,
                issuesCount=self.issuesCount,
                **self.dict(exclude={"users", "issues"})
            )
        )


from .user import User
from .issue import Issue

Project.update_forward_refs(User=User, Issue=Issue)
