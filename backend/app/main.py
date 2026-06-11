from fastapi import FastAPI

from app.api.routes import (
    macro,
    assets,
    institutional,
    health
)

app = FastAPI(
    title="Trishula Capital Terminal",
    version="1.0.0"
)


app.include_router(
    macro.router,
    prefix="/api/macro",
    tags=["Macro"]
)

app.include_router(
    assets.router,
    prefix="/api/assets",
    tags=["Assets"]
)

app.include_router(
    institutional.router,
    prefix="/api/institutional",
    tags=["Institutional"]
)

app.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)


@app.get("/")
def root():
    return {
        "status":"running"
    }

