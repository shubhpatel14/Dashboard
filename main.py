from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    macro,
    assets,
    institutional,
    health,
)


# ==========================================
# APP
# ==========================================

app = FastAPI(
    title="Trishula Capital Terminal",
    version="1.0.0",
    description="Macro + Asset Intelligence Engine"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# ROUTES
# ==========================================

# Final URLs:
# /api/macro/dashboard
# /api/macro/{category}

app.include_router(
    macro.router,
    prefix="/api",
    tags=["Macro"]
)


# Final URLs:
# /api/assets/gold
# /api/assets/sp500

app.include_router(
    assets.router,
    prefix="/api",
    tags=["Assets"]
)


# Final URLs:
# /api/institutional/gold

app.include_router(
    institutional.router,
    prefix="/api",
    tags=["Institutional"]
)


# Final URL:
# /health

app.include_router(
    health.router,
    tags=["Health"]
)



# ==========================================
# ROOT
# ==========================================

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Trishula Capital Terminal",
        "version": "1.0.0"
    }