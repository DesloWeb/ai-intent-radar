"""Main FastAPI application for AI Smart Intent Radar."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    # Startup: create tables and seed countries
    from app.core.database import get_engine, get_session_factory
    from app.models.models import Country
    from app.models.models import Base
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
    ]
    for c in countries:
        db.add(c)


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Commercial intent intelligence platform — know what the market wants before everyone else.",
        lifespan=lifespan,
    )

    # Middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(RateLimitMiddleware)

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
