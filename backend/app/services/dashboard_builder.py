from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from threading import Thread

from app.api.routes import assets, health, institutional, macro
from app.core.config import get_settings
from app.services.engine_registry import (
    ASSET_BUILDERS,
    get_asset_engine,
    get_macro_engine,
    get_trend_engine,
)


settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(macro.router, prefix=settings.api_prefix)
app.include_router(assets.router, prefix=settings.api_prefix)
app.include_router(institutional.router, prefix=settings.api_prefix)


def _prewarm_engines():
    try:
        get_macro_engine()
        get_trend_engine()
        for slug in ASSET_BUILDERS:
            get_asset_engine(slug)
    except Exception:
        pass


@app.on_event("startup")
def prewarm_engine_cache():
    Thread(target=_prewarm_engines, daemon=True).start()


