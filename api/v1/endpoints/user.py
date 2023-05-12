from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, Body

import schemas

from models.user import User

from api.v1.deps import get_current_user

router = APIRouter()


@router.get("/me", response_model=schemas.UserOut)
async def get_user(user: User = Depends(get_current_user)):
    """Get current active user details."""
    return {"currentUser": user.dict()}


@router.post("/change-photo")
async def change_photo(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    file_bytes = await file.read()
    await user.change_photo(avatar_file=file_bytes)
    return {"url": user.avatarUrl}


@router.put("/name")
async def change_name(name: Annotated[str, Body(embed=True)], user: User = Depends(get_current_user)):
    user.name = name
    await user.save()
    return {"name": user.name}
