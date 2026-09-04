"""Authentication API endpoints."""
import asyncio
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.core.config import settings
from app.models.models import Organization, User
from app.schemas.schemas import (
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

from slowapi import Limiter
from slowapi.util import get_remote_address
from app.main import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("3/minute")
async def register(request: Request, payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    from app.services.audit_service import audit_auth_event
    
    # Check existing
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Always create a new organization for self-registration
    # (joining existing orgs requires invite system - future feature)
    slug = str(uuid.uuid4())[:8]
    org = Organization(
        name=f"Org-{slug}",
        slug=slug,
    )
    db.add(org)
    await db.flush()

    user = User(
        organization_id=org.id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role="viewer",  # SEC-2: New users default to viewer, not admin
    )
    db.add(user)
    await db.flush()

    # Audit registration
    client_ip = request.client.host if request.client else None
    await audit_auth_event(
        db, "auth:register", user.id, org.id, client_ip, {"email": payload.email}
    )

    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password."""
    from app.services.audit_service import audit_auth_event
    
    # SEC-6: Brute-force protection using Redis (2s timeout to avoid hanging)
    r = None
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        lockout_key = f"login_attempts:{payload.email.lower()}"
        attempts = await asyncio.wait_for(r.get(lockout_key), timeout=2.0)
        if attempts and int(attempts) >= 5:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many failed attempts. Try again in 15 minutes."},
            )
    except Exception:
        r = None  # Redis unavailable, skip brute-force protection
    except Exception:
        r = None  # Redis unavailable, skip brute-force protection

    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    client_ip = request.client.host if request.client else None

    # SEC-7: Always return same error for invalid credentials (prevents account enumeration)
    if not user or not verify_password(payload.password, user.hashed_password) or not user.is_active:
        if r:
            try:
                await asyncio.wait_for(r.incr(lockout_key), timeout=2.0)
                await asyncio.wait_for(r.expire(lockout_key, 900), timeout=2.0)
            except Exception:
                pass
        # Audit failed login attempt
        if user:
            await audit_auth_event(
                db, "auth:login_failure", user.id, user.organization_id, client_ip
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # SEC-21: Check email verification
    # In production, set REQUIRE_EMAIL_VERIFICATION=true to enforce
    import os
    require_verification = os.getenv("REQUIRE_EMAIL_VERIFICATION", "false").lower() == "true"
    if require_verification and not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your inbox for the verification link.",
        )

    # Clear counter on success
    if r:
        try:
            await r.delete(lockout_key)
        except Exception:
            pass

    # Audit successful login
    await audit_auth_event(
        db, "auth:login_success", user.id, user.organization_id, client_ip
    )

    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Get new access token from refresh token."""
    token_payload = decode_token(body.refresh_token)
    if token_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = token_payload.get("sub")
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user profile."""
    return user


@router.post("/logout", status_code=204)
async def logout(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    request: Request = None,
):
    """Invalidate the refresh token (SEC-8)."""
    from app.services.audit_service import audit_auth_event
    
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        token_payload = decode_token(body.refresh_token)
        exp = token_payload.get("exp", 0)
        ttl = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
        if ttl > 0:
            await asyncio.wait_for(
                r.setex(f"blocklist:{body.refresh_token}", ttl, "1"),
                timeout=2.0,
            )
    except Exception:
        pass  # If Redis unavailable, token expires naturally

    # Audit logout
    client_ip = request.client.host if request and request.client else None
    await audit_auth_event(
        db, "auth:logout", user.id, user.organization_id, client_ip
    )

    return Response(status_code=204)


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user role (admin only). SEC-2: Manual role promotion."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    if role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    target_user.role = role
    await db.flush()
    return target_user


@router.post("/bootstrap-admin", status_code=200)
async def bootstrap_admin(
    email: str,
    secret: str,
    db: AsyncSession = Depends(get_db),
):
    """
    One-time bootstrap: promote a user to admin.
    Requires BOOTSTRAP_SECRET env var to be set.
    Remove or disable this endpoint after first use.
    """
    import os
    bootstrap_secret = os.getenv("BOOTSTRAP_SECRET", "")
    if not bootstrap_secret or secret != bootstrap_secret:
        raise HTTPException(status_code=403, detail="Invalid secret")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = "admin"
    await db.commit()
    return {"message": f"{email} promoted to admin"}
