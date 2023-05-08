import re
from datetime import datetime

from beanie import Document, PydanticObjectId, Link, before_event, Replace, Update, Insert, after_event, Delete, \
    BulkWriter, DeleteRules, Save
from beanie.odm.actions import ActionDirections
from beanie.odm.operators.find.comparison import In, NE
from pydantic import Field
from pymongo.client_session import ClientSession
from pymongo.results import DeleteResult

import schemas
from enums.issue import IssuePriority, IssueStatus, IssueType

import typing

from .mixin.push_pull import PushPullMixin

if typing.TYPE_CHECKING:
    from .comment import Comment
    from .project import Project
    from .user import User


class Issue(Document, PushPullMixin):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    title: str
    type: IssueType
    status: IssueStatus
    priority: IssuePriority
    listPosition: int | None
    description: str | None = None
    descriptionText: str | None = None
    estimate: int | None = None
    timeSpent: int | None = None
    timeRemaining: int | None = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    reporter: Link["User"]
    project: Link["Project"]
    comments: list[Link["Comment"]] = []
    users: list[Link["User"]] = []

    @property
    def key(self):
        return str(self.id)

    @property
    def userIds(self):
        return [user.ref.id for user in self.users]

    @property
    def reporterId(self):
        return self.reporter.ref.id

    @property
    def projectId(self):
        return self.project.ref.id

    async def to_schema(self):
        users = [
            schemas.UserInProject.from_orm(user)
            for user in await User.find_many(In(User.id, [user.ref.id for user in self.users])).to_list()
        ]
        comments = [
            schemas.Comment(
                user=schemas.UserInProject.from_orm(await User.find_one(User.id == comment.user.ref.id)),
                userId=comment.user.ref.id,
                issueId=comment.issue.ref.id,
                **comment.dict(exclude={"user"})
            )
            for comment in await Comment.find_many(
                In(Comment.id, [comment.ref.id for comment in self.comments])
            ).to_list()
        ]
        return schemas.IssueOut(
            issue=schemas.Issue(
                users=users,
                comments=comments,
                key=self.key,
                userIds=self.userIds,
                **self.dict(exclude={"users", "comments"})
            )
        )

    @before_event(Replace, Update)
    def updated_datetime(self):
        self.updatedAt = datetime.utcnow()

    @before_event(Insert, Replace, Update, Save)
    def set_description_text(self):

        def strip_tags(html):
            return re.sub('<[^<]+?>', '', html)

        description_text = strip_tags(self.description)
        self.descriptionText = description_text

    @after_event(Insert)
    async def set_issue_link(self):
        await Project.find_one(Project.id == self.project.ref.id) \
            .update(self.push_query())
        if self.users:
            await User.find_many(In(User.id, [user.ref.id for user in self.users])) \
                .update(self.push_query())

    @before_event(Delete)
    async def del_issue_link(self):
        await Project.find_one(Project.id == self.project.ref.id) \
            .update(self.pull_query())
        if self.users:
            await User.find_many(In(User.id, [user.ref.id for user in self.users])) \
                .update(self.pull_query())
        if self.comments:
            await Comment.find_many(In(Comment.id, [comment.ref.id for comment in self.comments])) \
                .delete()

    async def calculate_list_position(self, old_list_position: int, old_status: IssueStatus,
                                      new_list_position: int, new_status: IssueStatus):
        if not new_list_position:
            max_position = await self.get_max_position(old_status)
            new_list_position = new_list_position or max_position + 1
        if new_status != old_status:
            await self.find(self.__class__.status == old_status,
                            self.__class__.listPosition > old_list_position,
                            NE(self.__class__.id, self.id)) \
                .inc({"listPosition": -1})
            await self.find(self.__class__.status == new_status,
                            self.__class__.listPosition >= new_list_position,
                            NE(self.__class__.id, self.id)) \
                .inc({"listPosition": 1})
        else:
            if old_list_position > new_list_position:
                await self.find(self.__class__.status == old_status,
                                self.__class__.listPosition > new_list_position,
                                self.__class__.listPosition < old_list_position) \
                    .inc({"listPosition": 1})
            else:
                await self.find(self.__class__.status == old_status,
                                self.__class__.listPosition > old_list_position,
                                self.__class__.listPosition <= new_list_position) \
                    .inc({"listPosition": -1})

    async def delete(
            self,
            session: ClientSession | None = None,
            bulk_writer: BulkWriter | None = None,
            link_rule: DeleteRules = DeleteRules.DO_NOTHING,
            skip_actions: list[ActionDirections | str] | None = None,
            **pymongo_kwargs,
    ) -> DeleteResult | None:
        await self.find(self.__class__.status == self.status, self.__class__.listPosition > self.listPosition) \
            .inc({"listPosition": -1})
        return await super().delete(
            session=session, bulk_writer=bulk_writer, link_rule=link_rule, skip_actions=skip_actions, **pymongo_kwargs
        )

    @classmethod
    async def get_max_position(cls, status: IssueStatus) -> int:
        max_position = await cls.find(cls.status == status) \
            .sort("-listPosition").first_or_none()
        return max_position.listPosition if max_position else 0

    @classmethod
    async def get_next_list_position(cls, status: IssueStatus):
        return await cls.get_max_position(status) + 1

    class Settings:
        name = "issues"
        use_state_management = True

    class Config:
        use_enum_values = True


from .comment import Comment
from .project import Project
from .user import User

Issue.update_forward_refs(Comment=Comment, Project=Project, User=User)
