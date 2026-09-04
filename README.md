# AI Smart Intent Radar

> **Know what the market wants before everyone else.**

Commercial intent intelligence platform for Nigerian and US markets.

## Architecture

- **Frontend**: Next.js + TypeScript + Tailwind + React Query
- **Backend**: FastAPI + SQLAlchemy async + PostgreSQL + Pydantic
- **AI**: Anthropic Claude (production) / Mock provider (development)
- **Workers**: Redis + RQ for background processing
- **Security**: JWT auth, RBAC, multi-tenant isolation

## Quick Start

### Docker (Recommended)

```bash
docker-compose up -d
```

### Local Development

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Seed demo data
python -m app.utils.seed_data

# Frontend
cd frontend
npm install
npm run dev
```

### Demo Account

- Email: `demo@radar.ai`
- Password: `demo1234`

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/register` | Register new user |
| `POST /api/v1/auth/login` | Login |
| `GET /api/v1/dashboard` | Intelligence dashboard |
| `GET /api/v1/opportunities` | List opportunities |
| `GET /api/v1/opportunities/:id` | Opportunity detail |
| `GET /api/v1/signals` | List signals |
| `POST /api/v1/signals` | Ingest signal |
| `GET /api/v1/providers` | List providers |
| `POST /api/v1/providers` | Create provider |
| `POST /api/v1/providers/:id/match` | Run matching |
| `POST /api/v1/feedback` | Submit feedback |
| `GET /api/v1/market-intelligence/summary` | Market summary |
| `GET /api/v1/countries` | Country configuration |

## Core Pipeline

```
Data Sources → Signals → AI Intent Detection → Extraction →
Scoring → Validation → Explanation/Evidence → Opportunity →
Provider Matching → User Feedback → Learning
```

## Testing

```bash
cd backend
pytest -v
```
