# AI Intent Radar — Production Readiness Tasklist

> Hand this document to an AI agent or developer to complete before going live.
> The project is a FastAPI + Next.js commercial intelligence platform.
> Repo root: `AI-SIR/`. Backend: `backend/`. Frontend: `frontend/`.

---

## Context

- Backend: FastAPI + SQLAlchemy async, currently using SQLite locally, target is PostgreSQL
- Frontend: Next.js 14 App Router + Tailwind + React Query
- AI pipeline: mock provider locally, Anthropic Claude in production
- Data ingestion: Hacker News via `backend/app/services/hn_ingester.py` (no auth required)
- Docker: `docker-compose.yml` exists but has never been tested end-to-end
- Migrations: Alembic configured, initial migration at `backend/alembic/versions/001_initial_schema.py`

---

## Task 1 — Write Alembic Migration for Provider Model Changes

**Why:** The `providers` table in `001_initial_schema.py` is missing new columns added to
`backend/app/models/models.py`. Any fresh PostgreSQL deployment will fail or be missing columns.

**What to do:**
Create `backend/alembic/versions/002_provider_individual_support.py` with the following `upgrade()`:

```python
def upgrade() -> None:
    op.add_column("providers", sa.Column("provider_type", sa.String(20), nullable=False, server_default="business"))
    op.add_column("providers", sa.Column("skills", sa.JSON, nullable=False, server_default="[]"))
    op.add_column("providers", sa.Column("hourly_rate_min", sa.Float, nullable=True))
    op.add_column("providers", sa.Column("hourly_rate_max", sa.Float, nullable=True))
    op.add_column("providers", sa.Column("availability", sa.String(50), nullable=True))
    op.add_column("providers", sa.Column("verified", sa.Boolean, server_default="false", nullable=False))
    op.add_column("providers", sa.Column("profile_url", sa.String(500), nullable=True))
    op.create_index("ix_providers_type", "providers", ["provider_type"])
    op.create_index("ix_providers_org_type", "providers", ["organization_id", "provider_type"])

def downgrade() -> None:
    op.drop_index("ix_providers_org_type", "providers")
    op.drop_index("ix_providers_type", "providers")
    op.drop_column("providers", "profile_url")
    op.drop_column("providers", "verified")
    op.drop_column("providers", "availability")
    op.drop_column("providers", "hourly_rate_max")
    op.drop_column("providers", "hourly_rate_min")
    op.drop_column("providers", "skills")
    op.drop_column("providers", "provider_type")
```

Set `revision = "002"` and `down_revision = "001"`.

**Verify:** Run `alembic upgrade head` against a fresh PostgreSQL DB with no errors.

---

## Task 2 — Test Docker + PostgreSQL End-to-End

**Why:** `docker-compose.yml` has never been run. PostgreSQL connection, migrations, and seeding
must all work before deploying.

**What to do:**

1. In `docker-compose.yml` ensure the backend service runs migrations before starting:
   - Change the backend `command` to: `sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"`

2. Run `docker-compose up -d` from the project root.

3. Once containers are healthy, run the seed script inside the backend container:
   ```
   docker-compose exec backend python -m app.utils.seed_data
   ```

4. Run the pipeline:
   ```
   docker-compose exec backend python -m app.workers.worker pipeline
   ```

5. Verify the API responds at `http://localhost:8000/health` → `{"status":"ok"}`.

6. Verify the frontend at `http://localhost:3000` loads, login works with `demo@radar.ai / demo1234`,
   and opportunities appear on the dashboard.

**Fix any issues** with the DATABASE_URL, migrations, or container networking before proceeding.

---

## Task 3 — Set Up Scheduled HN Ingestion

**Why:** Ingestion is currently manual (API call only). Production needs automatic polling.

**Option A — Cron inside Docker (simplest):**

Add a `scheduler` service to `docker-compose.yml`:
```yaml
scheduler:
  build:
    context: ./backend
    dockerfile: Dockerfile
  command: >
    sh -c "while true; do
      python -m app.workers.worker hn_and_process;
      sleep 10800;
    done"
  environment:
    DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/radar
  depends_on:
    db:
      condition: service_healthy
```
This runs `hn_and_process` (ingest + pipeline) every 3 hours.

**Option B — RQ Scheduler (if Redis is already running):**

Install `rq-scheduler` and create a `backend/app/workers/scheduler.py` that enqueues
`ingest_and_process_hn` every 3 hours using `rq_scheduler.Scheduler`.

**Option A is preferred for MVP.**

---

## Task 4 — Production Secrets

**Why:** `JWT_SECRET_KEY` and `SECRET_KEY` are currently dev placeholder strings.
Exposing these on the internet is a critical security risk.

**What to do:**

1. Generate two strong secrets (32+ random bytes each):
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. Set these as environment variables on the deployment platform (never commit to git):
   - `SECRET_KEY=<generated>`
   - `JWT_SECRET_KEY=<generated>`
   - `AI_PROVIDER=anthropic` (for production)
   - `ANTHROPIC_API_KEY=<your key>`
   - `DATABASE_URL=<production postgres url>`

3. Confirm `.env` is in `.gitignore` (it already is — do not change this).

4. For the frontend, set:
   - `NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api/v1`

---

## Task 5 — Deploy to a Platform

**Recommended: Railway.app** (simplest for this stack — supports PostgreSQL, Python, Node.js)

**Steps:**

1. Push latest code to GitHub (already done).

2. On Railway:
   - Create a new project from the GitHub repo
   - Add a PostgreSQL plugin — Railway provides `DATABASE_URL` automatically
   - Deploy the `backend/` folder as a Python service
     - Build command: `pip install -r requirements.txt`
     - Start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Deploy the `frontend/` folder as a Node.js service
     - Build command: `npm install && npm run build`
     - Start command: `npm start`
     - Set env var: `NEXT_PUBLIC_API_URL=https://<backend-railway-url>/api/v1`

3. After deploy, run the seed script once via Railway's shell:
   ```
   python -m app.utils.seed_data
   ```

4. Trigger an initial HN ingest via the API:
   ```
   POST https://<backend>/api/v1/signals/ingest/hn
   ```

**Alternative platforms:** Render.com, Fly.io — same approach applies.

---

## Task 6 — HTTPS / CORS

**Why:** The frontend will call the backend from a different domain in production.
The CORS_ORIGINS setting must include the production frontend URL.

**What to do:**

1. In the backend production environment, set:
   ```
   CORS_ORIGINS=["https://your-frontend-domain.com"]
   ```

2. Confirm the deployment platform handles SSL termination (Railway, Render, Fly.io all do this automatically).

3. Update `frontend/.env.production` (or set as an env var on the platform):
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api/v1
   ```

---

## Verification Checklist

Run these checks after deployment before calling it live:

- [ ] `GET /health` → `{"status":"ok","version":"1.0.0"}`
- [ ] `POST /api/v1/auth/register` → creates user, returns tokens
- [ ] `POST /api/v1/auth/login` → works with demo credentials
- [ ] `POST /api/v1/signals/ingest/hn?dry_run=true` → returns `ingested > 0`
- [ ] `POST /api/v1/signals/ingest/hn` → ingests real signals
- [ ] `POST /api/v1/signals/process` → processes pipeline, creates opportunities
- [ ] `GET /api/v1/opportunities` → returns scored opportunities
- [ ] `GET /api/v1/dashboard` → returns aggregated stats
- [ ] Frontend loads at production URL
- [ ] Login redirects to dashboard with real data
- [ ] No `http://localhost` references in frontend network requests

---

## Files Modified During Development (for reference)

```
backend/app/models/models.py          — Provider model extended
backend/app/schemas/schemas.py        — Provider schemas updated
backend/app/api/v1/providers.py       — Provider API updated
backend/app/api/v1/signals.py         — HN ingest endpoint added
backend/app/services/provider_matching.py  — Individual matching logic
backend/app/services/hn_ingester.py   — Hacker News ingester (new)
backend/app/services/ai_provider.py   — Expanded intent keywords
backend/app/workers/worker.py         — HN ingest + process jobs
backend/app/core/config.py            — Config cleaned up
frontend/src/app/providers/page.tsx   — Business/individual UI
frontend/src/types/index.ts           — Provider type updated
frontend/src/lib/api.ts               — API client updated
```


---

# Security Hardening Tasklist

> Full audit performed September 2026. Fix all CRITICAL and HIGH items before going live.
> MEDIUM items should be fixed before public launch. LOW items are best-effort.

---

## SEC-1 — Fix Organisation Hijacking via Slug [CRITICAL]

**File:** `backend/app/api/v1/auth.py` — `register()` function

**Problem:** If a caller supplies `organization_slug` matching an existing org's slug, their new account is silently added to that org as an admin. Any attacker who knows or guesses a slug can take over any organization.

**Fix:** Remove the ability to join an existing org via slug during self-registration. New registrations always create a new org. Joining an existing org must be done via an invite system (future feature) or disabled entirely.

```python
# In register(), replace the org lookup block with:
slug = str(uuid.uuid4())[:8]
org = Organization(
    name=f"Org-{slug}",
    slug=slug,
)
db.add(org)
await db.flush()
```

Remove `organization_slug` from `UserCreate` schema or ignore it entirely.

---

## SEC-2 — Fix Role Assignment: New Users Should NOT Be Admins [CRITICAL]

**File:** `backend/app/api/v1/auth.py` line 52

**Problem:** Every self-registered user is assigned `role="admin"`. Any attacker who creates an account has full admin access.

**Fix:** Change default role to `"viewer"`. Only promote to admin manually via a separate admin endpoint.

```python
# Change:
role="admin",
# To:
role="viewer",
```

Also add a separate admin-only endpoint `PUT /users/{user_id}/role` protected by `require_role("admin")` to promote users.

---

## SEC-3 — Fix Hardcoded Secrets in docker-compose.yml [CRITICAL]

**File:** `docker-compose.yml` lines 28–29 and 40–41

**Problem:** `SECRET_KEY: dev-secret-key` and `JWT_SECRET_KEY: dev-jwt-secret` are committed to source. Anyone who reads the repo can forge JWTs.

**Fix:** Replace hardcoded values with environment variable references. Create a `.env` file (already gitignored) at project root:

```yaml
# In docker-compose.yml, replace:
SECRET_KEY: dev-secret-key
JWT_SECRET_KEY: dev-jwt-secret

# With:
SECRET_KEY: ${SECRET_KEY}
JWT_SECRET_KEY: ${JWT_SECRET_KEY}
```

Add to root `.env` (gitignored):
```
SECRET_KEY=<generated with: python3 -c "import secrets; print(secrets.token_hex(32))">
JWT_SECRET_KEY=<generated separately>
```

---

## SEC-4 — Fix Postgres and Redis Exposed Ports in Docker [CRITICAL]

**File:** `docker-compose.yml`

**Problem:** `postgres:5432` and `redis:6379` are bound to `0.0.0.0` (all interfaces) on the host. Anyone who can reach the host can connect directly to the database and cache.

**Fix:** Remove the `ports:` mappings for `db` and `redis` entirely. Services communicate over the internal Docker network — they do not need host-level port exposure.

```yaml
# Remove from db service:
ports:
  - "5432:5432"

# Remove from redis service:
ports:
  - "6379:6379"
```

If you need to inspect the DB locally, use `docker-compose exec db psql -U postgres radar`.

---

## SEC-5 — Fix Cross-Org Data Exposure: Scope All Queries by Organisation [CRITICAL]

**Files:** `backend/app/api/v1/opportunities.py`, `backend/app/api/v1/dashboard.py`, `backend/app/api/v1/signals.py`, `backend/app/services/opportunity_service.py`

**Problem:** All opportunity, signal, and dashboard queries are global — every authenticated user from every organization sees every other org's data.

**Fix:** Pass `organization_id` from the current user into all listing queries. This requires adding an `organization_id` foreign key to `signals` and `opportunities` tables (migration required).

**Step 1 — Add migration `003_add_org_scoping.py`:**
```python
def upgrade():
    op.add_column("signals", sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("opportunities", sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_signals_org", "signals", ["organization_id"])
    op.create_index("ix_opps_org", "opportunities", ["organization_id"])
    # Backfill existing rows with the demo org or a sentinel value
    op.execute("UPDATE signals SET organization_id = (SELECT id FROM organizations LIMIT 1)")
    op.execute("UPDATE opportunities SET organization_id = (SELECT id FROM organizations LIMIT 1)")
    op.alter_column("signals", "organization_id", nullable=False)
    op.alter_column("opportunities", "organization_id", nullable=False)
```

**Step 2 — Update `Signal` and `Opportunity` models** to add `organization_id` FK column.

**Step 3 — Update `signal_service.ingest_signal()`** to accept and store `organization_id`.

**Step 4 — Update `opportunity_service.list_opportunities()`** to filter by `organization_id`:
```python
if organization_id:
    filters.append(Opportunity.organization_id == organization_id)
```

**Step 5 — Update all API endpoints** to pass `user.organization_id` to service calls.

**Step 6 — Update `dashboard.py`** — add `Opportunity.organization_id == user.organization_id` to every query in `get_dashboard()`.

---

## SEC-6 — Add Brute-Force Protection on Login [CRITICAL]

**File:** `backend/app/api/v1/auth.py` — `login()`

**Problem:** No lockout, no delay, no attempt counter. Brute-force and credential-stuffing attacks are unconstrained.

**Fix:** Implement a per-email failed-attempt counter using Redis (already in the stack):

```python
import redis.asyncio as aioredis
from app.core.config import settings

async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    r = aioredis.from_url(settings.REDIS_URL)
    lockout_key = f"login_attempts:{payload.email.lower()}"
    
    attempts = await r.get(lockout_key)
    if attempts and int(attempts) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Try again in 15 minutes.",
        )
    
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        await r.incr(lockout_key)
        await r.expire(lockout_key, 900)  # 15 minute window
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    # Clear counter on success
    await r.delete(lockout_key)
    ...
```

Also fix account enumeration (item below) at the same time.

---

## SEC-7 — Fix Account Enumeration via Status Code Difference [HIGH]

**File:** `backend/app/api/v1/auth.py` — `login()`

**Problem:** Inactive accounts return 403 instead of 401, revealing that the email exists.

**Fix:** Always return the same 401 response regardless of whether the email exists, password is wrong, or account is inactive. Never distinguish between these cases in the response.

```python
if not user or not verify_password(payload.password, user.hashed_password) or not user.is_active:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
    )
```

---

## SEC-8 — Add Logout and Token Revocation [HIGH]

**File:** `backend/app/api/v1/auth.py`

**Problem:** No `/auth/logout` endpoint. Issued tokens (especially 30-day refresh tokens) cannot be invalidated.

**Fix:** Add a token blocklist in Redis and a logout endpoint:

```python
@router.post("/logout", status_code=204)
async def logout(
    body: RefreshTokenRequest,
    user: User = Depends(get_current_user),
):
    """Invalidate the refresh token."""
    import redis.asyncio as aioredis
    r = aioredis.from_url(settings.REDIS_URL)
    # Blocklist the refresh token until its natural expiry
    payload = decode_token(body.refresh_token)
    exp = payload.get("exp", 0)
    ttl = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
    await r.setex(f"blocklist:{body.refresh_token}", ttl, "1")
    return Response(status_code=204)
```

Update `decode_token()` to check the blocklist:
```python
async def is_token_revoked(token: str) -> bool:
    import redis.asyncio as aioredis
    r = aioredis.from_url(settings.REDIS_URL)
    return bool(await r.get(f"blocklist:{token}"))
```

Also reduce `JWT_REFRESH_TOKEN_EXPIRE_DAYS` from 30 to 7.

---

## SEC-9 — Add Role Guard to /signals/process and /signals/ingest/hn [HIGH]

**File:** `backend/app/api/v1/signals.py`

**Problem:** Any authenticated user (including `viewer` role) can trigger pipeline processing and HN ingestion, burning Anthropic API costs and polluting the DB.

**Fix:** Restrict both endpoints to `admin` and `analyst` roles:

```python
# Change:
user: User = Depends(get_current_user),

# To on both /process and /ingest/hn:
user: User = Depends(require_role("admin", "analyst")),
```

Import `require_role` from `app.core.security`.

---

## SEC-10 — Add Security Response Headers [HIGH]

**File:** `backend/app/main.py`

**Problem:** No security headers are set on any response.

**Fix:** Install `secure` package (`pip install secure==0.3.0`) and add to `requirements.txt`, then add middleware:

```python
import secure

secure_headers = secure.Secure(
    hsts=secure.StrictTransportSecurity().max_age(31536000).include_subdomains(),
    xfo=secure.XFrameOptions().deny(),
    xxp=secure.XXSSProtection().enable(),
    content=secure.XContentTypeOptions(),
    referrer=secure.ReferrerPolicy().no_referrer(),
    csp=secure.ContentSecurityPolicy()
        .default_src("'self'")
        .script_src("'self'")
        .style_src("'self'", "'unsafe-inline'")
        .img_src("'self'", "data:"),
)

@application.middleware("http")
async def set_secure_headers(request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response
```

Add to `requirements.txt`: `secure==0.3.0`

---

## SEC-11 — Tighten Rate Limiting: Redis-backed, Per-Endpoint [HIGH]

**File:** `backend/app/middleware/rate_limit.py`

**Problem:** In-memory rate limiter is bypassed in multi-worker deployments. No tighter limits on auth endpoints.

**Fix:** Replace with Redis-backed sliding window. Install `slowapi` (`pip install slowapi==0.1.9`):

```python
# In requirements.txt add: slowapi==0.1.9

# In main.py:
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)
application.state.limiter = limiter
application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In auth.py, decorate login and register:
@router.post("/login")
@limiter.limit("5/minute")   # 5 attempts per minute per IP
async def login(request: Request, ...):

@router.post("/register")
@limiter.limit("3/minute")
async def register(request: Request, ...):
```

Remove the old `RateLimitMiddleware` from `main.py` and delete `backend/app/middleware/rate_limit.py`.

Also add `X-Forwarded-For` support: set `key_func=get_remote_address` which slowapi handles correctly behind proxies when `trusted_hosts` is configured.

---

## SEC-12 — Fix Role Leak in 403 Error Message [MEDIUM]

**File:** `backend/app/core/security.py` — `require_role()`

**Problem:** Error message reveals the user's role and required roles to the caller.

**Fix:**
```python
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Insufficient permissions",
)
```

---

## SEC-13 — Add Request Size Limit [MEDIUM]

**File:** `backend/app/main.py`

**Problem:** No limit on request body size. Large JSON payloads to `POST /signals` can exhaust memory.

**Fix:** Add middleware to reject oversized requests:

```python
from starlette.middleware.trustedhost import TrustedHostMiddleware

MAX_REQUEST_SIZE = 1 * 1024 * 1024  # 1MB

@application.middleware("http")
async def limit_request_size(request: Request, call_next):
    if request.headers.get("content-length"):
        content_length = int(request.headers["content-length"])
        if content_length > MAX_REQUEST_SIZE:
            return Response(
                content='{"detail":"Request body too large"}',
                status_code=413,
                media_type="application/json",
            )
    return await call_next(request)
```

---

## SEC-14 — Add Input Length Limits to Schemas [MEDIUM]

**File:** `backend/app/schemas/schemas.py`

**Problem:** `SignalCreate`, `FeedbackCreate`, and `ProviderCreate` have unbounded string fields.

**Fix:** Add `max_length` to all text fields:

```python
class SignalCreate(BaseModel):
    source: str = Field(max_length=100)
    source_id: Optional[str] = Field(default=None, max_length=255)
    country_code: str = Field(min_length=2, max_length=2)
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1, max_length=10000)
    raw_data: Optional[Dict] = {}

class FeedbackCreate(BaseModel):
    ...
    notes: Optional[str] = Field(default=None, max_length=2000)

class ProviderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    profile_url: Optional[str] = Field(default=None, max_length=500)
```

Also add URL validation to `profile_url`:
```python
from pydantic import AnyHttpUrl
profile_url: Optional[AnyHttpUrl] = None
```

---

## SEC-15 — Authenticate GET /countries Endpoint [MEDIUM]

**File:** `backend/app/api/v1/countries.py`

**Problem:** `GET /countries` is fully unauthenticated, exposing internal signal source URLs and settings to anyone.

**Fix:** Add auth dependency:
```python
@router.get("", response_model=list[CountryResponse])
async def list_countries(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),  # ADD THIS
):
```

---

## SEC-16 — Tighten CORS Configuration [MEDIUM]

**File:** `backend/app/main.py`

**Problem:** `allow_methods=["*"]` and `allow_headers=["*"]` are overly permissive.

**Fix:**
```python
application.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)
```

---

## SEC-17 — Remove Source Volume Mounts from Docker in Production [MEDIUM]

**File:** `docker-compose.yml`

**Problem:** `./backend:/app` and `./frontend/src:/app/src` mount live source into containers. Production containers should run immutable built images.

**Fix:** Remove all `volumes:` entries that mount source code. Keep only named volumes for data persistence (`pgdata`). Production should use pre-built images pushed to a registry, not live source mounts.

---

## SEC-18 — Run Docker Containers as Non-Root User [HIGH]

**File:** `backend/Dockerfile`, `frontend/Dockerfile`

**Problem:** Containers likely run as root by default. A container escape grants full host root.

**Fix:** Add to both Dockerfiles:
```dockerfile
# At the end, before CMD:
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
```

---

## SEC-19 — Implement Audit Logging [HIGH]

**File:** `backend/app/models/models.py` (AuditLog model exists but is never used)

**Problem:** No authentication events, admin actions, or data mutations are logged. Forensic investigation after a breach is impossible.

**Fix:** Create `backend/app/services/audit_service.py`:

```python
from app.models.models import AuditLog

async def audit(
    db: AsyncSession,
    organization_id: uuid.UUID,
    user_id: Optional[uuid.UUID],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: dict = {},
    ip_address: Optional[str] = None,
):
    log = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(log)
    # Don't flush — let the caller's transaction handle it
```

Call `audit()` at minimum for:
- `auth:login_success`, `auth:login_failure`, `auth:register`, `auth:logout`
- `signal:ingest`, `signal:process`
- `provider:create`, `provider:match`
- `feedback:submit`
- `admin:role_change`, `admin:country_update`

---

## SEC-20 — Add Honeypot Endpoints [LOW]

**File:** `backend/app/main.py`

**Problem:** No canary routes to detect automated scanning and bots.

**Fix:** Add decoy endpoints that legitimate users never hit. Any request to them is logged and the IP is flagged:

```python
HONEYPOT_PATHS = ["/admin", "/wp-login.php", "/.env", "/config.php", "/api/admin"]

@application.middleware("http")
async def honeypot_middleware(request: Request, call_next):
    if request.url.path in HONEYPOT_PATHS:
        # Log the attempt (IP, user-agent, path)
        import logging
        logging.getLogger("honeypot").warning(
            f"HONEYPOT HIT: {request.client.host} → {request.url.path} "
            f"UA={request.headers.get('user-agent', 'unknown')}"
        )
        # Return a convincing fake response to keep bots engaged
        return Response(
            content='{"error":"Forbidden"}',
            status_code=403,
            media_type="application/json",
        )
    return await call_next(request)
```

---

## SEC-21 — Add Email Verification on Registration [HIGH]

**Problem:** Any email address can be used to create a fully active account immediately. No ownership verification.

**Fix (MVP approach):** For now, add a `is_email_verified` boolean to `User` model (default `False`). After registration, send a verification email with a signed token. Block access to non-health endpoints until verified.

This requires an email service (SendGrid, Resend, AWS SES). If not ready for launch, at minimum add the `is_email_verified` field and enforce it on login with a clear error message.

Migration required:
```python
op.add_column("users", sa.Column("is_email_verified", sa.Boolean, server_default="false", nullable=False))
```

---

## Security Fix Priority Order

### Before any public access (CRITICAL — do these first):
1. SEC-1 — Org hijacking via slug
2. SEC-2 — role=admin on registration
3. SEC-3 — hardcoded secrets in docker-compose
4. SEC-4 — exposed DB/Redis ports
5. SEC-5 — cross-org data exposure
6. SEC-6 — brute-force on login

### Before launch (HIGH):
7. SEC-7 — account enumeration
8. SEC-8 — logout + token revocation
9. SEC-9 — role guard on ingest/process
10. SEC-10 — security headers
11. SEC-11 — Redis-backed rate limiting
12. SEC-18 — non-root Docker containers
13. SEC-19 — audit logging
14. SEC-21 — email verification

### Before public marketing (MEDIUM):
15. SEC-12 — role leak in error message
16. SEC-13 — request size limit
17. SEC-14 — input length limits
18. SEC-15 — authenticate /countries
19. SEC-16 — tighten CORS
20. SEC-17 — remove source volume mounts

### Nice to have (LOW):
21. SEC-20 — honeypot endpoints
