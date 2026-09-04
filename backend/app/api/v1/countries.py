"""Country configuration API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.models import Country, User
from app.schemas.schemas import CountryResponse, CountryUpdate

router = APIRouter(prefix="/countries", tags=["Countries"])


@router.get("", response_model=list[CountryResponse])
async def list_countries(db: AsyncSession = Depends(get_db)):
    """List all configured countries."""
    result = await db.execute(select(Country).order_by(Country.name))
    return list(result.scalars().all())


@router.put("/{country_code}", response_model=CountryResponse)
async def update_country(
    country_code: str,
    payload: CountryUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Update country configuration (admin only)."""
    result = await db.execute(
        select(Country).where(Country.code == country_code.upper())
    )
    country = result.scalar_one_or_none()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    if payload.is_enabled is not None:
        country.is_enabled = payload.is_enabled
    if payload.signal_sources is not None:
        country.signal_sources = payload.signal_sources
    if payload.settings is not None:
        country.settings = payload.settings

    await db.flush()
    return country
