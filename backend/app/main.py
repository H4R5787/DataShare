"""FastAPI application entrypoint for Secure Pass RxQ."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.core.database import AsyncSessionLocal, Base, engine
from backend.app.core.seeder import seed_initial_data


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add OWASP recommended HTTP security headers."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:;"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Database initialization and master data seeding during startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Production-grade telecom data pack gifting & recharge platform.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Mount Static Assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health", tags=["Health Probe"])
@app.get(f"{settings.API_V1_PREFIX}/health", tags=["Health Probe"])
async def health_check():
    """Liveness & readiness probe."""
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "telecom_mode": settings.TELECOM_MODE,
        "payment_mode": settings.PAYMENT_MODE,
    }


@app.get("/", tags=["Root"])
async def root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "tagline": "Secure. Simple. Connected.",
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_PREFIX,
    }
