# AI Intent Radar — Technologies Used

---

## Overview

AI Intent Radar is a full-stack commercial intelligence platform built on modern,
production-grade open-source technologies. Every component is chosen for reliability,
scalability, and cost efficiency.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SIGNAL SOURCES                           │
│   Hacker News API · (Roadmap: LinkedIn, SEC, SAM.gov)      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / REST
┌────────────────────────▼────────────────────────────────────┐
│                  BACKEND (FastAPI)                          │
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Auth   │  │  AI Pipeline │  │  Provider Matching   │  │
│  │ JWT/RBAC │  │  Classify →  │  │  Business + People   │  │
│  │ bcrypt   │  │  Extract →   │  │  Skill/Geo/Rate fit  │  │
│  │ Redis    │  │  Score →     │  └──────────────────────┘  │
│  └──────────┘  │  Validate    │                             │
│                └──────┬───────┘                             │
│                       │                                     │
│  ┌────────────────────▼────────────────────────────────┐    │
│  │              PostgreSQL (Neon)                      │    │
│  │  10 tables · UUID PKs · JSON fields · Indexes      │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (HTTPS)
┌────────────────────────▼────────────────────────────────────┐
│                  FRONTEND (Next.js)                         │
│   Dashboard · Opportunities · Market Intel · Providers      │
│   React Query · Tailwind CSS · TypeScript                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12 | Core language |
| **FastAPI** | 0.115 | REST API framework — async, OpenAPI auto-docs |
| **SQLAlchemy** | 2.0 (async) | ORM — async queries, relationship management |
| **Alembic** | 1.14 | Database migrations — version-controlled schema changes |
| **Pydantic v2** | 2.10 | Request/response validation and serialization |
| **pydantic-settings** | 2.7 | Environment variable configuration management |
| **Uvicorn** | 0.34 | ASGI server — high performance async HTTP |
| **python-jose** | 3.3 | JWT token creation and validation |
| **passlib + bcrypt** | 1.7 / 4.0 | Password hashing — industry standard |
| **httpx** | 0.28 | Async HTTP client — used for HN API calls |
| **slowapi** | 0.1.9 | Rate limiting per endpoint |
| **redis.asyncio** | 5.2 | Async Redis client — brute-force protection, token blocklist |

---

## AI / Intelligence Layer

| Technology | Purpose |
|------------|---------|
| **Mock AI Provider** | Keyword-based intent classification (dev/testing) |
| **Anthropic Claude** | Production AI — structured JSON intent analysis (configurable) |
| **Custom Pipeline** | Classify → Extract → Score → Validate → Match (5-stage) |
| **Intent Scoring** | 0–1 scale with confidence, urgency, and evidence |
| **Provider Matching** | Weighted scoring: skill fit (50%) + geo fit (25%) + rate fit (25%) |

---

## Database

| Technology | Purpose |
|------------|---------|
| **PostgreSQL** | Primary database — production on Neon serverless |
| **Neon** | Serverless PostgreSQL hosting — scales to zero, free tier |
| **SQLite** | Local development database |
| **aiosqlite** | Async SQLite driver for local dev |
| **asyncpg** | Async PostgreSQL driver for production |

**Schema:** 10 tables — organizations, users, countries, signals, opportunities,
providers, provider_matches, user_feedbacks, audit_logs, market_trends

---

## Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14 (App Router) | React framework — SSR, routing, TypeScript |
| **TypeScript** | 5.7 | Type safety across entire frontend |
| **Tailwind CSS** | 3.4 | Utility-first styling — responsive design |
| **React Query** | 5.62 (@tanstack) | Server state management, caching, auto-refetch |
| **Lucide React** | 0.468 | Icon library |
| **date-fns** | 4.1 | Date formatting utilities |
| **clsx** | 2.1 | Conditional class merging |

---

## Infrastructure & DevOps

| Technology | Purpose |
|------------|---------|
| **Render** | Backend hosting — Docker-based, free tier, auto-deploy from GitHub |
| **Vercel** | Frontend hosting — Next.js native, global CDN, free tier |
| **Neon** | PostgreSQL database — serverless, free tier |
| **Upstash** | Redis hosting — serverless, free tier |
| **Docker** | Container runtime — production Dockerfile with non-root user |
| **GitHub** | Source control — auto-deploy triggers on push to main |

---

## Security Stack

| Layer | Technology |
|-------|------------|
| Authentication | JWT (access + refresh tokens), bcrypt password hashing |
| Authorization | RBAC — admin / analyst / viewer roles |
| Rate limiting | slowapi (per-endpoint), Redis brute-force counter |
| Token revocation | Redis blocklist on logout |
| Multi-tenancy | organization_id scoping on all queries |
| Transport | HTTPS enforced — HSTS headers on all responses |
| Headers | CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy |
| Input validation | Pydantic v2 — all inputs validated, length-limited |
| Audit trail | AuditLog table — all auth and data events recorded |
| Bot detection | Honeypot middleware — /admin, /.env, /wp-login.php |

---

## Data Sources

| Source | Type | Status |
|--------|------|--------|
| **Hacker News Firebase API** | Job posts, Ask HN, hiring threads | ✅ Live |
| **SAM.gov API** | US federal procurement | 🔜 Roadmap |
| **USASpending.gov** | Federal spending data | 🔜 Roadmap |
| **SEC EDGAR** | Company filings | 🔜 Roadmap |
| **LinkedIn** | Hiring signals | 🔜 Roadmap (requires partnership) |

---

## Cost at Scale

| Service | Free Tier Limit | Paid Cost |
|---------|----------------|-----------|
| Render (backend) | 750hrs/month, spins down | $7/month (always on) |
| Vercel (frontend) | 100GB bandwidth | $20/month (pro) |
| Neon (database) | 0.5GB storage | $19/month (pro) |
| Upstash (Redis) | 10K commands/day | $10/month (pay-per-use) |
| Anthropic Claude | API per token | ~$5–20/month (usage-based) |

**Total estimated monthly cost at MVP scale: ~$60–80/month**
