from datetime import datetime

from beanie import Document, PydanticObjectId, Link, Replace, Update, Insert, Delete, before_event, after_event, Save
from pydantic import Field

import typing

from .mixin.push_pull import PushPullMixin

if typing.TYPE_CHECKING:
    from .issue import Issue
    from .user import User


class Comment(Document, PushPullMixin):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    body: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    user: Link["User"]
    issue: Link["Issue"]

    @before_event(Replace, Update)
    def updated_datetime(self):
        self.updatedAt = datetime.utcnow()

    @after_event(Insert, Save)
    async def set_coment_link(self):
        await User.find_one(User.id == self.user.ref.id) \
            .update(self.push_query())
        await Issue.find_one(Issue.id == self.issue.ref.id) \
            .update(self.push_query())

    @before_event(Delete)
    async def del_coment_link(self):
        await User.find_one(User.id == self.user.ref.id) \
            .update(self.pull_query())
        await Issue.find_one(Issue.id == self.issue.ref.id) \
            .update(self.pull_query())

    class Settings:
        name = "comments"
        use_state_management = True


from .issue import Issue
from .user import User

Comment.update_forward_refs(Issue=Issue, User=User)
