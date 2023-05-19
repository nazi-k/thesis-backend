from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

import api
from api.v1.exception import CustomError
from core import settings
from db import init_db
from schemas import APIValidationError

tags_metadata = [
    {
        "name": "Authentication",
        "description": "Get authentication token",
    },
    {
        "name": "User",
        "description": "User registration and management",
    },
    {
        "name": "Project",
        "description": "Get project information",
    },
]

app = FastAPI(
    debug=settings.DEBUG,
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Api for diploma",
    # Set current documentation specs to v1
    openapi_url=f"/api/{settings.API_V1_STR}/openapi.json",
    docs_url=f"/docs",
    redoc_url=None,
    openapi_tags=tags_metadata,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Unprocessable Entity (Validation Error)",
            "model": APIValidationError,  # This will add OpenAPI schema to the docs
        },
    },
)


# Add the router responsible for all /api/ endpoint requests
app.include_router(api.router)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize services on startup."""
    await init_db.init()


# Custom HTTPException handler
@app.exception_handler(CustomError)
async def http_exception_handler(_, exc: CustomError):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "data": exc.error_data
                }
            }
        )
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=settings.PORT, host=settings.HOST)
