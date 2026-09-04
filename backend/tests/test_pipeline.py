"""Tests for the AI intelligence pipeline and signal processing."""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Signal, SignalStatus
from app.services.signal_service import (
    compute_dedup_hash,
    normalize_signal,
    ingest_signal,
)
from app.services.ai_provider import MockAIProvider
from app.services.intelligence_pipeline import process_signal
from app.services.provider_matching import _calculate_business_match
from app.models.models import Opportunity, Provider


# --- Signal Normalization Tests ---


def test_normalize_signal():
    """Test signal normalization."""
    raw = {
        "source": "BPP",
        "source_id": "NG-001",
        "country_code": "ng",
        "title": "Road Construction Tender",
        "description": "Federal road construction project.",
        "raw_data": {"url": "https://example.com"},
    }
    normalized = normalize_signal(raw)
    assert normalized["source"] == "bpp"
    assert normalized["country_code"] == "NG"
    assert normalized["title"] == "Road Construction Tender"


def test_dedup_hash():
    """Test deduplication hash is deterministic."""
    h1 = compute_dedup_hash("source", "id1", "Title")
    h2 = compute_dedup_hash("source", "id1", "Title")
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex digest


def test_dedup_hash_different():
    """Test different inputs produce different hashes."""
    h1 = compute_dedup_hash("source", "id1", "Title A")
    h2 = compute_dedup_hash("source", "id1", "Title B")
    assert h1 != h2


# --- AI Provider Tests ---


@pytest.mark.asyncio
async def test_mock_classify_intent():
    """Test mock AI intent classification."""
    ai = MockAIProvider()
    result = await ai.classify_intent({
        "title": "Federal Road Construction Procurement Tender",
        "description": "The Ministry of Works invites contractors for road infrastructure procurement.",
        "country_code": "NG",
        "source": "bpp",
    })
    assert "intent_score" in result
    assert "confidence" in result
    assert "intent_label" in result
    assert 0 <= result["intent_score"] <= 1
    assert 0 <= result["confidence"] <= 1
    assert result["intent_label"] in ["high", "medium", "low"]


@pytest.mark.asyncio
async def test_mock_extract_opportunity():
    """Test mock opportunity extraction."""
    ai = MockAIProvider()
    classification = {"intent_score": 0.8, "confidence": 0.7, "intent_label": "high"}
    result = await ai.extract_opportunity(
        {
            "title": "Lagos Technology Hub Development",
            "description": "Cloud infrastructure and cybersecurity services required.",
            "country_code": "NG",
        },
        classification,
    )
    assert "category" in result
    assert "urgency" in result
    assert "why_now" in result
    assert "recommended_action" in result
    assert result["urgency"] in ["low", "medium", "high", "critical"]


# --- Pipeline Tests ---


@pytest.mark.asyncio
async def test_process_signal_end_to_end(db: AsyncSession, org):
    """Test the full pipeline: signal → classify → extract → validate → opportunity."""
    # Create a signal with organization_id
    signal = await ingest_signal(
        db,
        {
            "source": "bpp",
            "source_id": "TEST-001",
            "country_code": "NG",
            "title": "Ministry of Works Road Infrastructure Procurement",
            "description": (
                "The Federal Ministry of Works invites qualified contractors "
                "for road infrastructure procurement. Budget: ₦45 billion."
            ),
            "raw_data": {},
        },
        organization_id=org.id,
    )
    assert signal.status == SignalStatus.RAW

    # Process through pipeline
    result = await process_signal(db, signal)
    assert result is not None
    assert result.status == SignalStatus.VALIDATED
    assert result.intent_score is not None
    assert result.confidence is not None
    assert len(result.extracted_data) > 0

    # Check opportunity was created
    from sqlalchemy import select
    opp_result = await db.execute(
        select(Opportunity).where(Opportunity.signal_id == signal.id)
    )
    opp = opp_result.scalar_one_or_none()
    assert opp is not None
    assert opp.intent_score > 0
    assert opp.category is not None
    assert opp.why_now is not None
    assert opp.recommended_action is not None


@pytest.mark.asyncio
async def test_process_low_intent_signal_rejected(db: AsyncSession, org):
    """Test that low-intent signals are rejected."""
    signal = await ingest_signal(
        db,
        {
            "source": "test",
            "source_id": "LOW-001",
            "country_code": "NG",
            "title": "hello",
            "description": "just a greeting",
            "raw_data": {},
        },
        organization_id=org.id,
    )

    result = await process_signal(db, signal)
    assert result is not None
    assert result.status == SignalStatus.REJECTED


# --- Provider Matching Tests ---


def test_provider_match_strong():
    """Test matching with a strong provider."""
    import uuid as uuid_mod
    opp = Opportunity(
        organization_id=uuid_mod.uuid4(),
        signal_id=None,  # Not needed for this test
        country_code="NG",
        title="Tech Project",
        description="Technology infrastructure",
        category="technology",
        intent_score=0.8,
        confidence=0.7,
        urgency="high",
        requirements=[],
        evidence=[],
        market_context={},
    )

    provider = Provider(
        organization_id=None,
        name="Tech Corp",
        services=["cloud", "cybersecurity"],
        categories=["technology"],
        locations=["Lagos"],
        country_codes=["NG"],
        min_project_value=10000,
        max_project_value=50000000,
    )

    score = _calculate_business_match(opp, provider)
    assert score["service_fit"] >= 0.5
    assert score["geographic_fit"] >= 0.5
    assert score["total_score"] > 0.3
    assert score["reasoning"]


def test_provider_match_weak():
    """Test matching with a weak provider."""
    import uuid as uuid_mod
    opp = Opportunity(
        organization_id=uuid_mod.uuid4(),
        signal_id=None,
        country_code="US",
        title="Highway Construction",
        description="Road construction project",
        category="infrastructure",
        intent_score=0.6,
        confidence=0.5,
        urgency="medium",
        requirements=[],
        evidence=[],
        market_context={},
    )

    provider = Provider(
        organization_id=None,
        name="Agriculture Co",
        services=["farming"],
        categories=["agriculture"],
        locations=["Rural Area"],
        country_codes=["NG"],
        min_project_value=1000000,
        max_project_value=10000000,
    )

    score = _calculate_business_match(opp, provider)
    assert score["total_score"] < 0.3


# --- API Tests ---


@pytest.mark.asyncio
async def test_create_signal_api(client: AsyncClient):
    """Test creating a signal via API."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "signal@test.com",
            "password": "password123",
            "full_name": "Signal User",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "signal@test.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.post(
        "/api/v1/signals",
        json={
            "source": "bpp",
            "source_id": "API-001",
            "country_code": "NG",
            "title": "Test Signal",
            "description": "A test signal for API validation.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["source"] == "bpp"
    assert data["country_code"] == "NG"
    assert data["status"] == "raw"


@pytest.mark.asyncio
async def test_list_opportunities_api(client: AsyncClient):
    """Test listing opportunities via API."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "opp@test.com",
            "password": "password123",
            "full_name": "Opp User",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "opp@test.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/opportunities",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "opportunities" in data
    assert "total" in data
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_countries_api(client: AsyncClient):
    """Test countries endpoint (requires auth)."""
    # Register and login first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "country@test.com",
            "password": "password123",
            "full_name": "Country User",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "country@test.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/countries",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_dashboard_api(client: AsyncClient, db: AsyncSession):
    """Test dashboard endpoint."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dash@test.com",
            "password": "password123",
            "full_name": "Dash User",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "dash@test.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_opportunities" in data
    assert "top_opportunities" in data
    assert "intent_distribution" in data
