from beanie import PydanticObjectId, Link
from bson import DBRef
from fastapi import APIRouter, Depends

import schemas
from models import User, Project

from models.issue import Issue

from api.v1.deps import get_current_user

router = APIRouter()


@router.get("/{issues_id}", response_model=schemas.IssueOut)
async def get_issue(issues_id: PydanticObjectId, user: User = Depends(get_current_user)):
    issue = await Issue.get(issues_id)
    return await issue.to_schema()


@router.put("/{issues_id}", response_model=schemas.IssueOut)
async def put_issue(issues_id: PydanticObjectId, issue: schemas.IssuePatch, user: User = Depends(get_current_user)):
    update_data = issue.dict(exclude_unset=True)
    if update_data.get("users"):
        update_data["users"] = [
            Link(DBRef(User.get_motor_collection().name, user["id"]), User) for user in update_data["users"]
        ]
    issue_update = await Issue.get(issues_id)
    if "listPosition" in update_data:
        list_position = int(update_data.get("listPosition")) or 1
        new_status = update_data.get("status")
        await issue_update.calculate_list_position(issue_update.listPosition, issue_update.status,
                                                   list_position, new_status)
    issue_update = issue_update.copy(update=update_data)
    await issue_update.save()
    return await issue_update.to_schema()


@router.delete("/{issues_id}", response_model=schemas.IssueOut)
async def delete_issue(issues_id: PydanticObjectId, user: User = Depends(get_current_user)):
    issue = await Issue.get(issues_id)
    await issue.delete()
    return await issue.to_schema()


@router.post("/", response_model=schemas.IssueOut)
async def post_issue(issue: schemas.IssueIn, user: User = Depends(get_current_user)):
    issue_dict = issue.dict()
    issue_dict["reporter"] = Link(DBRef(User.get_motor_collection().name, issue_dict["reporterId"]), User)
    issue_dict["project"] = Link(DBRef(Project.get_motor_collection().name, issue_dict["projectId"]), Project)
    if issue_dict.get("users"):
        issue_dict["users"] = [
            Link(DBRef(User.get_motor_collection().name, user["id"]), User) for user in issue_dict["users"]
        ]
    if not issue_dict.get("listPosition"):
        issue_dict["listPosition"] = await Issue.get_next_list_position(issue_dict["status"])
    new_issue = Issue(**issue_dict)
    await new_issue.save()
    return await new_issue.to_schema()
