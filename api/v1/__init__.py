from fastapi import APIRouter

from .endpoints import authentication, project, user, issue, comment


router = APIRouter()
router.include_router(authentication.router, prefix="/authentication", tags=["Authentication"])
router.include_router(project.router, prefix="/project", tags=["Project"])
router.include_router(issue.router, prefix="/issues", tags=["Issue"])
router.include_router(user.router, prefix="/user", tags=["User"])
router.include_router(comment.router, prefix="/comments", tags=["Comment"])
