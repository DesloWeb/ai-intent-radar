# Security Remaining Fixes

> This document covers the 8 security issues NOT yet implemented.
> All other 20 fixes have been confirmed done.
> Work through these in order — FIX-1 through FIX-5 are blockers for production.

---

## FIX-1 — Add organization_id to Signal and Opportunity models [CRITICAL]

The multi-tenancy layer is broken because `Signal` and `Opportunity` ORM models have no
`organization_id` column. Every downstream fix (FIX-2, FIX-3, FIX-4) depends on this column
existing. Do this first.

### 1a. Edit `backend/app/models/models.py`

**In the `Signal` class**, add this column directly after the `id` column (after line
`id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)`):

```python
organization_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True
)
```

Also add `"ix_signals_org"` to `Signal.__table_args__`:
```python
__table_args__ = (
    Index("ix_signals_org", "organization_id"),
    Index("ix_signals_source_source_id", "source", "source_id", unique=True),
    Index("ix_signals_country_status", "country_code", "status"),
    Index("ix_signals_scores", "intent_score", "confidence"),
)
```

**In the `Opportunity` class**, add this column directly after the `signal_id` column:
```python
organization_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True
)
```

Also add `"ix_opps_org"` to `Opportunity.__table_args__`:
```python
__table_args__ = (
    Index("ix_opps_org", "organization_id"),
    Index("ix_opps_country_category", "country_code", "category"),
    Index("ix_opps_scores", "intent_score", "confidence"),
    Index("ix_opps_status_urgency", "status", "urgency"),
    Index("ix_opps_deadline", "deadline"),
)
```

Both columns are `nullable=True` (not `nullable=False`) to avoid breaking the existing
seeded data. Existing rows will have `NULL` organization_id.

### 1b. Edit `backend/app/services/signal_service.py`

In `ingest_signal()`, add `organization_id` as an optional parameter and store it on the model.

Change the function signature from:
```python
async def ingest_signal(db: AsyncSession, raw_signal: dict) -> Signal:
```
To:
```python
async def ingest_signal(
    db: AsyncSession,
    raw_signal: dict,
    organization_id=None,
) -> Signal:
```

In the `Signal(...)` constructor call (inside `ingest_signal`), add:
```python
organization_id=organization_id,
```

### 1c. Edit `backend/app/services/intelligence_pipeline.py`

`process_signal` creates an `Opportunity` via `_create_opportunity_from_signal`. The signal
already has `organization_id` on it — pass it through to the opportunity.

In `_create_opportunity_from_signal`, add `organization_id=signal.organization_id,` to the
`Opportunity(...)` constructor call. The full constructor currently ends with
`status=OpportunityStatus.VALIDATED,` — add the line before it:
```python
organization_id=signal.organization_id,
status=OpportunityStatus.VALIDATED,
```

### 1d. Edit `backend/app/api/v1/signals.py`

In `create_signal()`, pass `organization_id=user.organization_id` to `ingest_signal`:

Change:
```python
signal = await ingest_signal(db, {
    "source": payload.source,
    "source_id": source_id,
    "country_code": payload.country_code,
    "title": payload.title,
    "description": payload.description,
    "raw_data": payload.raw_data or {},
})
```
To:
```python
signal = await ingest_signal(
    db,
    {
        "source": payload.source,
        "source_id": source_id,
        "country_code": payload.country_code,
        "title": payload.title,
        "description": payload.description,
        "raw_data": payload.raw_data or {},
    },
    organization_id=user.organization_id,
)
```

### 1e. Edit `backend/app/utils/seed_data.py`

In `seed()`, pass `organization_id=org.id` to every `ingest_signal(db, signal_data)` call.
The loop currently is:
```python
for signal_data in DEMO_SIGNALS:
    signal = await ingest_signal(db, signal_data)
```
Change to:
```python
for signal_data in DEMO_SIGNALS:
    signal = await ingest_signal(db, signal_data, organization_id=org.id)
```

Also update `backend/app/services/hn_ingester.py` — in `ingest_hn_signals()`, the call
`await ingest_signal(db, payload)` does not pass an org_id. This is fine for now (HN signals
are platform-wide, not org-specific), leave as `None`.

### 1f. Create `backend/alembic/versions/003_org_scoping.py`

```python
"""Add organization_id to signals and opportunities for multi-tenancy.

Revision ID: 003
Revises: 002
Create Date: 2024-01-20 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "signals",
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=True,
        ),
    )
    op.create_index("ix_signals_org", "signals", ["organization_id"])

    op.add_column(
        "opportunities",
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=True,
        ),
    )
    op.create_index("ix_opps_org", "opportunities", ["organization_id"])


def downgrade() -> None:
    op.drop_index("ix_opps_org", "opportunities")
    op.drop_column("opportunities", "organization_id")
    op.drop_index("ix_signals_org", "signals")
    op.drop_column("signals", "organization_id")
```

---

## FIX-2 — Scope Opportunities Queries by organization_id [CRITICAL]

Depends on FIX-1 being done first.

### 2a. Edit `backend/app/services/opportunity_service.py`

**In `list_opportunities()`**, the `organization_id` parameter already exists in the function
signature but its filter is missing. Add the filter block. The current filters section starts at:
```python
filters = []
if country_code:
    filters.append(Opportunity.country_code == country_code)
```

Add `organization_id` filter as the FIRST filter:
```python
filters = []
if organization_id:
    filters.append(Opportunity.organization_id == organization_id)
if country_code:
    filters.append(Opportunity.country_code == country_code)
```

**In `get_opportunity_by_id()`**, add an `organization_id` parameter and scope the query.
Change the function from:
```python
async def get_opportunity_by_id(
    db: AsyncSession, opportunity_id: uuid.UUID
) -> Optional[Opportunity]:
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    return result.scalar_one_or_none()
```
To:
```python
async def get_opportunity_by_id(
    db: AsyncSession,
    opportunity_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = None,
) -> Optional[Opportunity]:
    query = select(Opportunity).where(Opportunity.id == opportunity_id)
    if organization_id:
        query = query.where(Opportunity.organization_id == organization_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()
```

**In `get_opportunity_counts()`**, add an `organization_id` parameter and apply it to all
count queries. Change the signature from:
```python
async def get_opportunity_counts(db: AsyncSession) -> dict:
```
To:
```python
async def get_opportunity_counts(
    db: AsyncSession,
    organization_id: Optional[uuid.UUID] = None,
) -> dict:
```

Then in every `select(func.count(Opportunity.id))` query inside this function, add a
`.where(Opportunity.organization_id == organization_id)` clause when `organization_id` is set.
There are 3 count queries (total, high_priority, new_this_week) and 3 group-by queries
(country, urgency, intent_distribution). Add the filter to all of them:
```python
# Example for the total count — repeat for all queries:
base_filter = (Opportunity.organization_id == organization_id) if organization_id else True
total = (await db.execute(
    select(func.count(Opportunity.id)).where(base_filter)
)).scalar() or 0
```

### 2b. Edit `backend/app/api/v1/opportunities.py`

**In `list_opps()`**, pass `organization_id=user.organization_id` to `list_opportunities()`.
Change:
```python
opportunities, total = await list_opportunities(
    db,
    country_code=country_code,
    category=category,
    urgency=urgency,
    min_intent_score=min_intent_score,
    status=status,
    page=page,
    per_page=per_page,
)
```
To:
```python
opportunities, total = await list_opportunities(
    db,
    organization_id=user.organization_id,
    country_code=country_code,
    category=category,
    urgency=urgency,
    min_intent_score=min_intent_score,
    status=status,
    page=page,
    per_page=per_page,
)
```

**In `get_opportunity()`**, pass `organization_id=user.organization_id` to
`get_opportunity_by_id()`. Change:
```python
opp = await get_opportunity_by_id(db, uuid.UUID(opportunity_id))
```
To:
```python
opp = await get_opportunity_by_id(db, uuid.UUID(opportunity_id), organization_id=user.organization_id)
```

---

## FIX-3 — Scope Dashboard Queries by organization_id [CRITICAL]

Depends on FIX-1 being done first.

### Edit `backend/app/api/v1/dashboard.py`

Pass `organization_id=user.organization_id` to `get_opportunity_counts()`:
```python
counts = await get_opportunity_counts(db, organization_id=user.organization_id)
```

Add `.where(Opportunity.organization_id == user.organization_id)` to these 4 queries:

**top_query** — change:
```python
top_query = select(Opportunity).where(
    Opportunity.status.notin_(["dismissed", "expired"])
)
```
To:
```python
top_query = select(Opportunity).where(
    Opportunity.status.notin_(["dismissed", "expired"]),
    Opportunity.organization_id == user.organization_id,
)
```

**emerging_query** — add to the `.where(and_(...))` block:
```python
.where(
    and_(
        Opportunity.organization_id == user.organization_id,
        Opportunity.created_at >= three_days,
        Opportunity.intent_score >= 0.5,
    )
)
```

**trends_query** — add:
```python
.where(
    and_(
        Opportunity.organization_id == user.organization_id,
        Opportunity.created_at >= week_ago,
    )
)
```

**country_query** — add:
```python
select(
    Opportunity.country_code,
    func.count(Opportunity.id).label("total"),
    func.avg(Opportunity.intent_score).label("avg_intent"),
)
.where(Opportunity.organization_id == user.organization_id)
.group_by(Opportunity.country_code)
```

---

## FIX-4 — Scope Providers match/get_matches by organization_id [HIGH]

### Edit `backend/app/api/v1/providers.py`

**In `match_opportunity()`**, add an org ownership check after fetching the opportunity.
Change:
```python
result = await db.execute(
    select(Opportunity).where(Opportunity.id == UUID(opportunity_id))
)
opportunity = result.scalar_one_or_none()
if not opportunity:
    raise HTTPException(status_code=404, detail="Opportunity not found")
```
To:
```python
result = await db.execute(
    select(Opportunity).where(Opportunity.id == UUID(opportunity_id))
)
opportunity = result.scalar_one_or_none()
if not opportunity:
    raise HTTPException(status_code=404, detail="Opportunity not found")
# SEC-5: Only allow matching against opportunities visible to this org
if opportunity.organization_id is not None and opportunity.organization_id != user.organization_id:
    raise HTTPException(status_code=403, detail="Insufficient permissions")
```

**In `get_matches()`**, add the same ownership check. After fetching the opportunity (add the
fetch before the matches query):
```python
@router.get("/{opportunity_id}/matches", response_model=list[ProviderMatchResponse])
async def get_matches(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get existing matches for an opportunity."""
    from uuid import UUID
    # SEC-5: Verify opportunity belongs to user's org
    opp_result = await db.execute(
        select(Opportunity).where(Opportunity.id == UUID(opportunity_id))
    )
    opportunity = opp_result.scalar_one_or_none()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if opportunity.organization_id is not None and opportunity.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(
        select(ProviderMatch).where(
            ProviderMatch.opportunity_id == UUID(opportunity_id)
        )
    )
    return list(result.scalars().all())
```

---

## FIX-5 — Fix Token Blocklist: Check it in get_current_user [HIGH]

The logout endpoint writes to the Redis blocklist but `get_current_user` never checks it.
Logged-out tokens remain valid until natural JWT expiry. This must be fixed.

### Edit `backend/app/core/security.py`

**In `get_current_user()`**, add a Redis blocklist check after `decode_token()` succeeds.

Add this import at the top of the file:
```python
import redis.asyncio as aioredis
```

In `get_current_user()`, after `payload = decode_token(credentials.credentials)`, add:
```python
# SEC-8b: Check token blocklist (tokens invalidated by logout)
try:
    r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    is_revoked = await r.get(f"blocklist:{credentials.credentials}")
    if is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
except HTTPException:
    raise
except Exception:
    pass  # Redis unavailable — degrade gracefully, token still validated by JWT sig
```

The full `get_current_user` after the change should look like:
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    # SEC-8b: Check token blocklist
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        is_revoked = await r.get(f"blocklist:{credentials.credentials}")
        if is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )
    except HTTPException:
        raise
    except Exception:
        pass  # Redis unavailable — degrade gracefully
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user
```

Also add settings import at top if not present: `from app.core.config import settings`

---

## FIX-6 — Add Audit Logging to auth/logout and signals.py [MEDIUM]

### 6a. Edit `backend/app/api/v1/auth.py` — add audit to logout

The `logout` endpoint (currently at the end of auth.py) has no audit call.
Add the import and call. The logout endpoint currently looks like:

```python
@router.post("/logout", status_code=204)
async def logout(
    body: RefreshTokenRequest,
    user: User = Depends(get_current_user),
):
```

It needs `db: AsyncSession = Depends(get_db)` added as a parameter, and an audit call.
Change to:
```python
@router.post("/logout", status_code=204)
async def logout(
    body: RefreshTokenRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Invalidate the refresh token (SEC-8)."""
    from app.services.audit_service import audit_auth_event
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        token_payload = decode_token(body.refresh_token)
        exp = token_payload.get("exp", 0)
        ttl = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
        if ttl > 0:
            await r.setex(f"blocklist:{body.refresh_token}", ttl, "1")
    except Exception:
        pass
    client_ip = request.client.host if request.client else None
    await audit_auth_event(db, "auth:logout", user.id, user.organization_id, client_ip)
    await db.commit()
    return Response(status_code=204)
```

### 6b. Edit `backend/app/api/v1/signals.py` — add audit to ingest and process

Add this import at the top of signals.py (with other imports):
```python
from app.services.audit_service import audit
```

**In `create_signal()`**, add an audit call after the signal is ingested:
```python
signal = await ingest_signal(db, {...}, organization_id=user.organization_id)
await audit(
    db, user.organization_id, user.id,
    action="signal:ingest",
    resource_type="signal",
    resource_id=str(signal.id),
    details={"source": payload.source, "title": payload.title[:100]},
)
await db.commit()
return signal
```

**In `process_pending_signals()`**, add an audit call after the loop:
```python
await audit(
    db, user.organization_id, user.id,
    action="signal:process",
    resource_type="signal",
    details={"processed": processed, "created": created, "rejected": rejected, "errors": errors},
)
await db.commit()
return ProcessResult(...)
```

**In `ingest_hn()`**, add an audit call after `ingest_hn_signals` returns:
```python
result = await ingest_hn_signals(...)
await audit(
    db, user.organization_id, user.id,
    action="signal:ingest_hn",
    resource_type="signal",
    details=result,
)
return HNIngestResult(**result)
```

Note: `ingest_hn()` currently has no `db` parameter. Add `db: AsyncSession = Depends(get_db)`
to its signature alongside the existing `user` parameter.

---

## FIX-7 — Fix profile_url Validation: Use AnyHttpUrl [MEDIUM]

### Edit `backend/app/schemas/schemas.py`

Add `AnyHttpUrl` to the pydantic imports at the top of the file. Currently the import line is:
```python
from pydantic import BaseModel, EmailStr, Field
```
Change to:
```python
from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field
```

In `ProviderCreate`, change `profile_url` from `str` to `AnyHttpUrl`:
```python
# Change from:
profile_url: Optional[str] = Field(default=None, max_length=500)
# Change to:
profile_url: Optional[AnyHttpUrl] = None
```

In `ProviderResponse`, do the same:
```python
# Change from:
profile_url: Optional[str] = None
# Change to:
profile_url: Optional[AnyHttpUrl] = None
```

---

## FIX-8 — Add is_email_verified to User model and migration [MEDIUM]

### 8a. Edit `backend/app/models/models.py`

In the `User` class, add `is_email_verified` after the `is_active` column:
```python
is_active: Mapped[bool] = mapped_column(Boolean, default=True)
is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
```

### 8b. Edit `backend/app/schemas/schemas.py`

In `UserResponse`, add the field:
```python
is_email_verified: bool
```

### 8c. Create `backend/alembic/versions/004_email_verified.py`

```python
"""Add is_email_verified to users table.

Revision ID: 004
Revises: 003
Create Date: 2024-01-21 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_email_verified",
            sa.Boolean,
            nullable=False,
            server_default="false",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_email_verified")
```

---

## Minor Cleanup — Remove Dead Code

### Delete `backend/app/middleware/rate_limit.py`

The old in-memory rate limiter has been replaced by slowapi. The file still exists and is
misleading. Delete it entirely. Confirm first that `main.py` does NOT import it:
```
grep -r "rate_limit" backend/app/main.py
```
If the import is absent, delete the file.

---

## Verification Checklist

After all fixes are applied, verify:

```
[ ] alembic upgrade head runs cleanly (migrations 003 and 004 apply without error)
[ ] POST /auth/register creates user with role="viewer" and is_email_verified=False
[ ] POST /api/v1/signals (ingest) stores organization_id on the signal row
[ ] POST /api/v1/signals/process creates opportunity with same organization_id
[ ] GET /api/v1/opportunities returns ONLY the calling user's org's opportunities
[ ] GET /api/v1/dashboard shows ONLY the calling user's org's data
[ ] POST /auth/logout returns 204
[ ] GET /api/v1/opportunities immediately after logout returns 401 (token revoked)
[ ] POST /providers/{opp_id}/match returns 403 for an opp from a different org
[ ] GET /audit_logs (or DB query) shows login, ingest, process entries
[ ] ProviderCreate with profile_url="not-a-url" returns 422 validation error
[ ] User model has is_email_verified column in DB
```
