"""Main FastAPI application for AI Smart Intent Radar."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings

# Configure honeypot logger
logging.basicConfig(level=logging.WARNING)
honeypot_logger = logging.getLogger("honeypot")

# SEC-11: Rate limiter — use Redis if available, fall back to in-memory
try:
    limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)
except Exception:
    limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    # Startup: create tables and seed countries
    from app.core.database import get_engine, get_session_factory
    from app.models.models import Country, Base
    from sqlalchemy import select

    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with get_session_factory()() as db:
        result = await db.execute(select(Country).limit(1))
        if not result.scalar_one_or_none():
            _seed_countries(db)
            await db.commit()

    yield
    # Shutdown: nothing needed


def _seed_countries(db):
    """Seed initial country configurations."""
    from app.models.models import Country

    countries = [
        Country(
            code="US",
            name="United States",
            is_enabled=True,
            signal_sources=[
                {"name": "SAM.gov", "type": "procurement", "url": "https://sam.gov"},
                {"name": "USASpending", "type": "data", "url": "https://usaspending.gov"},
                {"name": "Grants.gov", "type": "grants", "url": "https://grants.gov"},
            ],
            settings={"currency": "USD", "default_language": "en"},
        ),
        Country(
            code="NG",
            name="Nigeria",
            is_enabled=True,
            signal_sources=[
                {"name": "BPP Nigeria", "type": "procurement", "url": "https://bpp.gov.ng"},
                {"name": "Lagos State", "type": "government", "url": "https://lagosstate.gov.ng"},
            ],
            settings={"currency": "NGN", "default_language": "en"},
        ),
    ]
    for c in countries:
        db.add(c)


# SEC-10: Honeypot paths that legitimate users never hit
HONEYPOT_PATHS = ["/admin", "/wp-login.php", "/.env", "/config.php", "/api/admin", "/phpmyadmin"]

# SEC-13: Maximum request body size (1MB)
MAX_REQUEST_SIZE = 1 * 1024 * 1024


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Commercial intent intelligence platform — know what the market wants before everyone else.",
        lifespan=lifespan,
    )

    # SEC-11: Add rate limiter to app state
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # SEC-16: Tightened CORS configuration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

    # SEC-10: Security response headers middleware
    @application.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:"
        return response

    # SEC-13: Request size limit middleware
    @application.middleware("http")
    async def limit_request_size(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            if int(content_length) > MAX_REQUEST_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large. Maximum size is 1MB."},
                )
        return await call_next(request)

    # SEC-20: Honeypot middleware
    @application.middleware("http")
    async def honeypot_middleware(request: Request, call_next):
        if request.url.path in HONEYPOT_PATHS:
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            honeypot_logger.warning(
                f"HONEYPOT HIT: {client_ip} -> {request.url.path} UA={user_agent}"
            )
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden"},
            )
        return await call_next(request)

    # Routes
    from app.api.v1 import (
        auth,
        dashboard,
        signals,
        opportunities,
        providers,
        feedback,
        countries,
        market_intelligence,
    )

    application.include_router(auth.router, prefix=settings.API_V1_PREFIX)
    application.include_router(signals.router, prefix=settings.API_V1_PREFIX)
    application.include_router(opportunities.router, prefix=settings.API_V1_PREFIX)
    application.include_router(providers.router, prefix=settings.API_V1_PREFIX)
    application.include_router(feedback.router, prefix=settings.API_V1_PREFIX)
    application.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
    application.include_router(countries.router, prefix=settings.API_V1_PREFIX)
    application.include_router(market_intelligence.router, prefix=settings.API_V1_PREFIX)

    @application.get("/health")
    async def health():
        return {"status": "ok", "version": settings.APP_VERSION}

    return application


app = create_app()
