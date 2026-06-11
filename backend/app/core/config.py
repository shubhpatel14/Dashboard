from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Trishula Capital API"
    api_prefix: str = "/api"
    database_url: str = "postgresql://trishula:trishula@localhost:5432/trishula"
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 900
    project_root: Path = Path(__file__).resolve().parents[3]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
