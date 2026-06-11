from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


# FORCE load .env
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        extra="ignore"
    )

    # APP
    APP_NAME: str = "Trishula Capital Terminal"


    # API
    API_KEY: str = os.getenv("API_KEY", "")


    # DATABASE
    DATABASE_URL: str = (
        "postgresql://postgres:password@localhost/trishula"
    )


    # REDIS
    REDIS_URL: str = "redis://localhost:6379"


    # CACHE
    CACHE_TTL_SECONDS: int = 300


    # PATH
    project_root: Path = BASE_DIR


    # old compatibility

    @property
    def app_name(self):
        return self.APP_NAME


    @property
    def api_prefix(self):
        return "/api"


    @property
    def cache_ttl_seconds(self):
        return self.CACHE_TTL_SECONDS



@lru_cache()
def get_settings():
    return Settings()



settings = get_settings()

API_KEY = settings.API_KEY