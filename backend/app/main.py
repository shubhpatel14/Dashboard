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


app.include_router(macro.router)
app.include_router(assets.router)
app.include_router(institutional.router)
app.include_router(health.router)


@app.get("/")
def root():
    return {
        "status": "running"
    }
