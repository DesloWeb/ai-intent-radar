"""Seed demo data for development and demonstration.

Creates sample signals from US procurement sources
to demonstrate the intelligence pipeline.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import get_session_factory, get_engine, Base
from app.core.security import hash_password
from app.models.models import (
    Organization,
    User,
    Country,
    Signal,
    Provider,
)
from app.services.signal_service import ingest_signal


DEMO_SIGNALS = [
    # US signals
    {
        "source": "sam_gov",
        "source_id": "US-SAM-2024-001",
        "country_code": "US",
        "title": "DoD Cybersecurity Infrastructure Modernization",
        "description": (
            "Department of Defense issues RFP for cybersecurity infrastructure "
            "modernization across military installations. Services include: "
            "zero-trust architecture implementation, SIEM deployment, "
            "penetration testing, and compliance consulting. "
            "Contract value: $45M over 3 years. SAM.gov solicitation."
        ),
        "raw_data": {"source_url": "https://sam.gov/opp/2024-001"},
    },
    {
        "source": "sam_gov",
        "source_id": "US-SAM-2024-002",
        "country_code": "US",
        "title": "GSA Cloud Migration Services",
        "description": (
            "General Services Administration seeking cloud migration services "
            "for legacy federal systems. AWS/Azure migration, DevOps pipeline "
            "setup, and ongoing managed services. Budget: $28M. "
            "Small business set-aside available."
        ),
        "raw_data": {"source_url": "https://sam.gov/opp/2024-002"},
    },
    {
        "source": "grants_gov",
        "source_id": "US-GRANT-2024-001",
        "country_code": "US",
        "title": "EPA Clean Water Infrastructure Grant Program",
        "description": (
            "Environmental Protection Agency announces $120M grant program "
            "for clean water infrastructure improvements. Eligible: "
            "state/local governments, tribal authorities, water utilities. "
            "Focus: lead pipe replacement, wastewater treatment, "
            "stormwater management. Applications due March 2025."
        ),
        "raw_data": {"source_url": "https://grants.gov/2024/epa-water"},
    },
    {
        "source": "usaspending",
        "source_id": "US-SPEND-2024-001",
        "country_code": "US",
        "title": "USDOT Smart Transportation Pilot Program",
        "description": (
            "Department of Transportation launches smart transportation pilot "
            "in 5 metropolitan areas. Seeking technology partners for: "
            "IoT sensor networks, traffic management AI, electric vehicle "
            "infrastructure. Total program budget: $85M. "
            "Public-private partnership model."
        ),
        "raw_data": {"source_url": "https://usaspending.gov/2024/dot-transport"},
    },
    {
        "source": "sam_gov",
        "source_id": "US-SAM-2024-003",
        "country_code": "US",
        "title": "HHS AI-Powered Health Analytics Platform",
        "description": (
            "Department of Health and Human Services seeks AI/ML solutions "
            "for predictive health analytics. Requirements: NLP for clinical "
            "notes, disease prediction models, HIPAA-compliant data pipeline. "
            "Contract ceiling: $35M. Phase 1 pilot: $8M."
        ),
        "raw_data": {"source_url": "https://sam.gov/opp/2024-003"},
    },
]


async def seed():
    """Seed the database with demo data."""
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with get_session_factory()() as db:
        # Create demo organization
        org = Organization(
            name="Demo Corp",
            slug="demo-corp",
            enabled_countries=["US"],
            is_demo=True,
        )
        db.add(org)
        await db.flush()

        # Create demo user
        user = User(
            organization_id=org.id,
            email="demo@radar.ai",
            hashed_password=hash_password("demo1234"),
            full_name="Demo User",
            role="admin",
        )
        db.add(user)
        await db.flush()

        # Create demo provider
        provider = Provider(
            organization_id=org.id,
            name="Demo Tech Solutions",
            description="Full-service technology and consulting company",
            services=["cloud_migration", "cybersecurity", "software_development", "consulting"],
            categories=["technology", "infrastructure", "energy"],
            locations=["New York", "Washington DC", "San Francisco"],
            country_codes=["US"],
            min_project_value=50000,
            max_project_value=50000000,
        )
        db.add(provider)
        await db.flush()

        # Ingest sample signals
        for signal_data in DEMO_SIGNALS:
            signal = await ingest_signal(db, signal_data)

        await db.commit()
        print(f"Seeded: 1 org, 1 user, 1 provider, {len(DEMO_SIGNALS)} signals")
        print("Login: demo@radar.ai / demo1234")


if __name__ == "__main__":
    asyncio.run(seed())
