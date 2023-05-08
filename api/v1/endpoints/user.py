from fastapi import APIRouter, Depends, HTTPException, status

import schemas

from models.user import User

from api.v1.deps import get_current_user

router = APIRouter()


def user_not_found_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="The user with this username does not exist",
    )


@router.get("/currentUser", response_model=schemas.UserOut)
async def get_current_user(user: User = Depends(get_current_user)):
    """Get current active user details."""
    return {"currentUser": user.dict()}

#
# @router.post("/register", response_model=schemas.User)
# def register_user(user: schemas.UserCreate):
#     if len(user.password) < 8:
#         raise HTTPException(status_code=400, detail="password needs to be atleast 8 characters long")
#
#     if user.password != user.confirm_password:
#         raise HTTPException(status_code=400, detail="password do not match")
#
#     if await User.get_by_username(username=user.username):
#         raise HTTPException(status_code=400, detail="Username is taken")
#
#     try:
#         await User(username=user.username, hashed_password=get_password_hash(user.password)).create()
#         return {"message": "User added!"}
#     except Exception as err:
#         raise HTTPException(status_code=400, detail=str(err))