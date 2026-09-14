import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import connect_to_mongo, close_mongo_connection
from api import routes_ocr, routes_tamper, routes_bio, routes_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    routes_ocr.router,
    prefix=f"{settings.API_V1_STR}/ocr",
    tags=["OCR & MRZ Processing (Track A)"]
)

app.include_router(
    routes_bio.router,
    prefix=f"{settings.API_V1_STR}/bio",
    tags=["Biometrics & Liveness (Track B)"]
)

app.include_router(
    routes_tamper.router,
    prefix=f"{settings.API_V1_STR}/tamper",
    tags=["Tampering Detection (Track C)"]
)



app.include_router(
    routes_db.router,
    prefix=f"{settings.API_V1_STR}/db",
    tags=["Database Cross-Verification"]
)

@app.get("/", summary="Health Check")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "project": settings.PROJECT_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
