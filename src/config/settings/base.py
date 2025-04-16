import logging
import pathlib
import pydantic
import decouple

from pydantic_settings import BaseSettings

ROOT_DIR: pathlib.Path = pathlib.Path(
    __file__).parent.parent.parent.parent.parent.resolve()


class BackendBaseSettings(BaseSettings):
    TITLE: str = "Backend FastAPI"
    VERSION: str = "0.1.0"
    TIMEZONE: str = "UTC"
    DESCRIPTION: str | None = None
    DEBUG: bool = False

    SERVER_HOST: str = decouple.config(
        "BACKEND_SERVER_HOST", cast=str)
    SERVER_PORT: int = decouple.config(
        "BACKEND_SERVER_PORT", cast=int)
    SERVER_WORKERS: int = decouple.config(
        "BACKEND_SERVER_WORKERS", cast=int)
    API_PREFIX: str = "/api"
    DOCS_URL: str = "/docs"

    IS_ALLOWED_CREDENTIALS: bool = decouple.config(
        "IS_ALLOWED_CREDENTIALS", cast=bool)

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://0.0.0.0:3000",
        "http://127.0.0.1:3000",
    ]

    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]

    LOGGING_LEVEL: int = logging.INFO
    LOGGERS: tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    class Config(pydantic.ConfigDict):
        case_sensitive: bool = True
        env_file: str = f"{str(ROOT_DIR)}/.env"
        validate_assignment: bool = True

    @property
    def set_backend_app_attributes(self) -> dict[str, str | bool | None]:
        """
        Set all `FastAPI` class' attributes with the custom values defined in `BackendBaseSettings`.
        """
        return {
            "title": self.TITLE,
            "version": self.VERSION,
            "debug": self.DEBUG,
            "description": self.DESCRIPTION,
            "docs_url": self.DOCS_URL,
            "api_prefix": self.API_PREFIX,
        }
