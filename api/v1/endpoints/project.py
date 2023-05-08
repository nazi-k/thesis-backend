import asyncio

from beanie import PydanticObjectId, Link
from fastapi import APIRouter, Depends

import schemas
from models.project import Project

from models.user import User

from api.v1.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=list[schemas.ProjectOut])
async def get_projects(user: User = Depends(get_current_user)):
    projects = await Project.find({"users": {"$elemMatch": {"$eq": user.to_ref()}}}).to_list(100)
    return [schemas.ProjectOut(**project.dict()) for project in projects]


@router.post("/")
async def post_project(project: schemas.ProjectCreate, user: User = Depends(get_current_user)):
    project_dict = project.dict()
    if emails := project_dict.get("emails"):
        results = await asyncio.gather(*[User.get_by_email(email=email) for email in emails])
        users = {user.to_ref() for user in results if user}
        users.add(user.to_ref())
        project_dict["users"] = users
    else:
        project_dict["users"] = [user.to_ref()]
    new_project = Project(**project_dict)
    await new_project.save()
    return {"success": True, "message": "Project created"}


@router.get("/{project_id}", response_model=schemas.Project)
async def get_project(project_id: PydanticObjectId, user: User = Depends(get_current_user)):
    project = await Project.find(
        {"_id": project_id, "users": {"$elemMatch": {"$eq": user.to_ref()}}}
    ).first_or_none()
    if project:
        return await project.to_schema()


@router.put("/{project_id}")
async def put_project(project_id: PydanticObjectId, project: schemas.ProjectPut, user: User = Depends(get_current_user)):
    project_dict = project.dict(exclude_unset=True)
    project_update = await Project.get(project_id)
    if emails := project_dict.get("emails"):
        results = await asyncio.gather(*(User.get_by_email(email=email) for email in emails))
        users = {Link(user.to_ref(), User) for user in results if user}
        project_update = project_update.copy(update=project_dict)
        for user in users:
            if user not in project_update.users:
                project_update.users.append(user)
    await project_update.save()
    return {"success": True, "message": "Project updated"}
