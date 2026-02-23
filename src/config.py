import logging

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REMNAWAVE_URL: str = "https://api.remnawave.com"
    REMNAWAVE_API_KEY: SecretStr = SecretStr("remnawave-secret-key")
    REMNAWAVE_SSL_VERIFY: bool = True

    DATABASE_URL: str = "postgresql+asyncpg://user:password@app-db:5432/remnawave-api"
    DATABASE_ECHO: bool = False

    LOG_LEVEL: int = logging.INFO

    def configure_logging(self) -> None:
        logging.basicConfig(
            level=self.LOG_LEVEL,
            datefmt="%H:%M:%S",
            format="%(asctime)s | %(levelname)-5s|  %(filename)s:%(lineno)-4d  - %(message)s",
        )


settings = Settings()  # type:ignore
