from beanie import Link, PydanticObjectId
from bson import DBRef
from fastapi import APIRouter

import schemas
from models import User, Issue

from models.comment import Comment

router = APIRouter()


@router.post("/")
async def create_comment(comment_in: schemas.CommentCreate):
    comment = Comment(
        body=comment_in.body,
        user=Link(DBRef(User.get_motor_collection().name, comment_in.userId), User),
        issue=Link(DBRef(Issue.get_motor_collection().name, comment_in.issueId), Issue)
    )
    await comment.save()
    return comment


@router.put("/{comment_id}")
async def update_comment(comment_id: PydanticObjectId, comment_in: schemas.CommentPatch):
    comment = await Comment.get(comment_id)
    if comment_in.body:
        comment.body = comment_in.body
        await comment.save()
        return comment


@router.delete("/{comment_id}")
async def delete_comment(comment_id: PydanticObjectId):
    comment = await Comment.get(comment_id)
    await comment.delete()
    return comment
