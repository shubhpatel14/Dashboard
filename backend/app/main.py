from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    macro,
    assets,
    institutional,
    health,
    calendar
)

app = FastAPI(
    title="Trishula Capital Terminal",
    version="1.0.0"
)

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)


app.include_router(macro.router)
app.include_router(assets.router)
app.include_router(institutional.router)
app.include_router(health.router)
app.include_router(calendar.router)


@app.get("/")
def root():
    return {
        "status": "running"
    }
