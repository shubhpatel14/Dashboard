from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = "Trishula Capital Terminal"

    API_KEY: str = ""

    DATABASE_URL: str = (
        "postgresql://postgres:password@localhost/trishula"
    )

    REDIS_URL: str = "redis://localhost:6379"


    CACHE_TTL_SECONDS: int = 300


    project_root: Path = Path(__file__).resolve().parents[3]


    @property
    def cache_ttl_seconds(self):

        return self.CACHE_TTL_SECONDS


    @property
    def app_name(self):

        return self.APP_NAME


    @property
    def api_prefix(self):

        return "/api"


    class Config:

        env_file = ".env"



@lru_cache()
def get_settings():

    return Settings()



# old compatibility
API_KEY = get_settings().API_KEY