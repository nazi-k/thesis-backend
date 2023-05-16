import secrets
from typing import List, Union

from pydantic import AnyHttpUrl, BaseSettings, MongoDsn, validator

# This adds support for 'mongodb+srv' connection schemas when using e.g. MongoDB Atlas
MongoDsn.allowed_schemes.add("mongodb+srv")


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "TaskForge"
    PROJECT_VERSION: str = "0.0.1"
    API_V1_STR: str = "v1"
    DEBUG: bool = True
    BACKEND_CORS_ORIGINS: Union[str, List[AnyHttpUrl]] = ["http://localhost:8080"]
    SECRET_KEY: str = "fd"  # secrets.token_urlsafe(32)

    # Custom validators that have 'pre' set to 'True', will be called before
    # all standard pydantic validators.
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
        cls,  # noqa
        v: Union[str, List[str]],
    ) -> Union[str, List[str]]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    MONGODB_URI: MongoDsn = "mongodb+srv://nazar:BnoYOb0wQIfFcc7m@cluster0.lco9zcb.mongodb.net/" \
                            "?retryWrites=true&w=majority"
    MONGODB_DB_NAME: str = "diploma"

    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1  # 60 minutes * 24 hours * 1 = 1 day

    IMGBB_API_KEY = "4e67c049645d3d2bf6344626f0ecb4c3"

    class Config:
        # Place your .env file under this path
        case_sensitive = True


settings = Settings()
