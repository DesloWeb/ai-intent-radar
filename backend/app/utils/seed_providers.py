"""Seed diverse mock providers to test matching accuracy.

Creates 15 providers (businesses + individuals) across Nigeria and US
designed to produce a range of match scores against existing opportunities.

Run: python -m app.utils.seed_providers
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import get_session_factory, get_engine, Base
from app.core.security import hash_password
from app.models.models import Organization, User, Provider


# ─────────────────────────────────────────────────────────────────────
# Nigeria Businesses
# ─────────────────────────────────────────────────────────────────────

NG_BUSINESSES = [
    {
        "name": "Lagos Tech Systems Ltd",
        "description": "Leading technology infrastructure company in Lagos. Specializes in cloud deployment, cybersecurity, and enterprise software for government and private sector.",
        "provider_type": "business",
        "services": ["cloud_deployment", "cybersecurity", "enterprise_software", "IT_consulting"],
        "categories": ["technology", "infrastructure", "cybersecurity"],
        "locations": ["Lagos", "Victoria Island", "Ikoyi"],
        "country_codes": ["NG"],
        "min_project_value": 5_000_000,       # N5M
        "max_project_value": 100_000_000,      # N100M
        "email": "info@lagostech.ng",
        "phone": "+234-801-234-5678",
    },
    {
        "name": "Abuja Construction Group",
        "description": "Full-service construction and civil engineering firm. 20+ years experience in road infrastructure, bridges, and public works across Nigeria.",
        "provider_type": "business",
        "services": ["road_construction", "civil_engineering", "project_management", "materials_supply"],
        "categories": ["infrastructure", "construction", "engineering"],
        "locations": ["Abuja", "Kaduna", "Kano"],
        "country_codes": ["NG"],
        "min_project_value": 10_000_000,       # N10M
        "max_project_value": 500_000_000,      # N500M
        "email": "contracts@abujaconstruction.ng",
        "phone": "+234-802-345-6789",
    },
    {
        "name": "MedSupply Nigeria",
        "description": "Medical equipment and pharmaceutical distributor serving hospitals, clinics, and corporate health programs across Nigeria.",
        "provider_type": "business",
        "services": ["medical_equipment", "pharmaceuticals", "facility_management", "healthcare_consulting"],
        "categories": ["healthcare", "medical", "procurement"],
        "locations": ["Lagos", "Abuja", "Port Harcourt"],
        "country_codes": ["NG"],
        "min_project_value": 2_000_000,        # N2M
        "max_project_value": 50_000_000,       # N50M
        "email": "sales@medsupply.ng",
        "phone": "+234-803-456-7890",
    },
    {
        "name": "GreenField Agri Solutions",
        "description": "Agricultural technology and equipment provider. Specializes in irrigation systems, farm mechanization, and cold chain logistics for modern farming.",
        "provider_type": "business",
        "services": ["irrigation_systems", "farm_mechanization", "cold_chain", "agricultural_consulting"],
        "categories": ["agriculture", "farming", "food_processing"],
        "locations": ["Abuja", "Kaduna", "Nasarawa"],
        "country_codes": ["NG"],
        "min_project_value": 5_000_000,        # N5M
        "max_project_value": 100_000_000,      # N100M
        "email": "info@greenfieldagri.ng",
        "phone": "+234-804-567-8901",
    },
    {
        "name": "PayFlow Fintech",
        "description": "Nigerian fintech company building payment infrastructure, digital banking solutions, and compliance systems for the financial sector.",
        "provider_type": "business",
        "services": ["payment_gateway", "digital_banking", "compliance_systems", "fintech_integration"],
        "categories": ["fintech", "technology", "financial_services"],
        "locations": ["Lagos", "Victoria Island"],
        "country_codes": ["NG"],
        "min_project_value": 10_000_000,       # N10M
        "max_project_value": 200_000_000,      # N200M
        "email": "enterprise@payflow.ng",
        "phone": "+234-805-678-9012",
    },
]


# ─────────────────────────────────────────────────────────────────────
# US Businesses
# ─────────────────────────────────────────────────────────────────────

US_BUSINESSES = [
    {
        "name": "CyberShield Federal",
        "description": "Cybersecurity firm specializing in federal government contracts. Zero-trust architecture, SIEM, penetration testing, FedRAMP compliance.",
        "provider_type": "business",
        "services": ["zero_trust_architecture", "siem_deployment", "penetration_testing", "fedramp_compliance"],
        "categories": ["cybersecurity", "defense", "compliance"],
        "locations": ["Washington DC", "Arlington", "Reston"],
        "country_codes": ["US"],
        "min_project_value": 1_000_000,
        "max_project_value": 100_000_000,
        "email": "contracts@cybershield.com",
        "phone": "+1-703-555-0101",
    },
    {
        "name": "CloudBridge Solutions",
        "description": "Enterprise cloud migration and DevOps consultancy. AWS Advanced Partner, Azure Gold Partner. Federal and commercial clients.",
        "provider_type": "business",
        "services": ["aws_migration", "azure_migration", "devops", "managed_services"],
        "categories": ["technology", "cloud", "infrastructure"],
        "locations": ["San Francisco", "Seattle", "Austin"],
        "country_codes": ["US"],
        "min_project_value": 500_000,
        "max_project_value": 50_000_000,
        "email": "solutions@cloudbridge.io",
        "phone": "+1-415-555-0202",
    },
    {
        "name": "EnviroTech Consulting",
        "description": "Environmental engineering and consulting firm. Water treatment, wastewater management, stormwater solutions for government and utilities.",
        "provider_type": "business",
        "services": ["water_treatment", "wastewater_management", "stormwater", "environmental_compliance"],
        "categories": ["environmental", "water", "infrastructure"],
        "locations": ["New York", "New Jersey", "Connecticut"],
        "country_codes": ["US"],
        "min_project_value": 2_000_000,
        "max_project_value": 80_000_000,
        "email": "projects@envirotech.com",
        "phone": "+1-212-555-0303",
    },
    {
        "name": "SmartTransit AI",
        "description": "Transportation technology company. IoT sensor networks, traffic management AI, EV infrastructure for smart city initiatives.",
        "provider_type": "business",
        "services": ["iot_sensors", "traffic_management", "ev_infrastructure", "smart_city"],
        "categories": ["transportation", "technology", "infrastructure"],
        "locations": ["Chicago", "Detroit", "San Francisco"],
        "country_codes": ["US"],
        "min_project_value": 1_000_000,
        "max_project_value": 75_000_000,
        "email": "partnerships@smarttransit.ai",
        "phone": "+1-312-555-0404",
    },
    {
        "name": "HealthAI Labs",
        "description": "Healthcare AI and analytics company. NLP for clinical notes, predictive disease models, HIPAA-compliant data pipelines.",
        "provider_type": "business",
        "services": ["clinical_nlp", "disease_prediction", "hipaa_data_pipeline", "health_analytics"],
        "categories": ["healthcare", "technology", "ai"],
        "locations": ["Boston", "New York", "San Francisco"],
        "country_codes": ["US"],
        "min_project_value": 1_000_000,
        "max_project_value": 50_000_000,
        "email": "federal@healthailabs.com",
        "phone": "+1-617-555-0505",
    },
]


# ─────────────────────────────────────────────────────────────────────
# Individuals
# ─────────────────────────────────────────────────────────────────────

INDIVIDUALS = [
    {
        "name": "Adebayo Ogundimu",
        "description": "Senior DevOps engineer with 8 years experience in cloud infrastructure, AWS, Kubernetes, and CI/CD pipelines.",
        "provider_type": "individual",
        "skills": ["aws", "kubernetes", "devops", "ci_cd", "docker", "terraform", "python"],
        "categories": ["technology", "cloud", "devops"],
        "locations": ["Lagos", "Abuja"],
        "country_codes": ["NG"],
        "hourly_rate_min": 50,
        "hourly_rate_max": 150,
        "availability": "contract",
        "verified": True,
        "email": "adebayo.ogundimu@gmail.com",
    },
    {
        "name": "Sarah Chen",
        "description": "Cybersecurity consultant specializing in federal compliance, zero-trust implementation, and security audits.",
        "provider_type": "individual",
        "skills": ["cybersecurity", "zero_trust", "fedramp", "siem", "compliance", "penetration_testing"],
        "categories": ["cybersecurity", "compliance", "defense"],
        "locations": ["Washington DC", "Arlington"],
        "country_codes": ["US"],
        "hourly_rate_min": 150,
        "hourly_rate_max": 350,
        "availability": "full_time",
        "verified": True,
        "email": "sarah.chen@protonmail.com",
    },
    {
        "name": "Emeka Nwosu",
        "description": "Civil engineer and project manager with 15 years experience in road construction and public infrastructure across Nigeria.",
        "provider_type": "individual",
        "skills": ["road_construction", "project_management", "civil_engineering", "cost_estimation", "site_supervision"],
        "categories": ["infrastructure", "construction", "engineering"],
        "locations": ["Abuja", "Kaduna", "Enugu"],
        "country_codes": ["NG"],
        "hourly_rate_min": 40,
        "hourly_rate_max": 120,
        "availability": "full_time",
        "verified": True,
        "email": "emeka.nwosu@yahoo.com",
    },
    {
        "name": "Dr. Fatima Abdullahi",
        "description": "Agricultural scientist specializing in irrigation design, farm mechanization, and post-harvest technology.",
        "provider_type": "individual",
        "skills": ["irrigation", "farm_mechanization", "agricultural_science", "cold_chain", "crop_management"],
        "categories": ["agriculture", "farming", "technology"],
        "locations": ["Abuja", "Kaduna"],
        "country_codes": ["NG"],
        "hourly_rate_min": 30,
        "hourly_rate_max": 80,
        "availability": "contract",
        "verified": True,
        "email": "fatima.abdullahi@gmail.com",
    },
    {
        "name": "Marcus Thompson",
        "description": "Full-stack developer and fintech specialist. Built payment gateways, digital banking platforms, and compliance systems.",
        "provider_type": "individual",
        "skills": ["fintech", "payment_gateway", "digital_banking", "compliance", "python", "react"],
        "categories": ["fintech", "technology", "financial_services"],
        "locations": ["Lagos", "New York"],
        "country_codes": ["NG", "US"],
        "hourly_rate_min": 100,
        "hourly_rate_max": 250,
        "availability": "contract",
        "verified": True,
        "email": "marcus.thompson@outlook.com",
    },
]


async def seed_providers():
    """Seed mock providers (idempotent — skips if providers already exist)."""
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with get_session_factory()() as db:
        from sqlalchemy import select, func

        # Check if these specific providers already exist
        existing_result = await db.execute(select(Provider.name))
        existing_names = set(row[0] for row in existing_result.all())

        # Get or create the demo org
        result = await db.execute(select(Organization).where(Organization.slug == "demo-corp"))
        org = result.scalar_one_or_none()
        if not org:
            print("Demo org not found. Run seed_data.py first.")
            return

        created = []

        # Create Nigeria businesses
        for data in NG_BUSINESSES:
            if data["name"] not in existing_names:
                provider = Provider(organization_id=org.id, **data)
                db.add(provider)
                created.append(data["name"])

        # Create US businesses
        for data in US_BUSINESSES:
            if data["name"] not in existing_names:
                provider = Provider(organization_id=org.id, **data)
                db.add(provider)
                created.append(data["name"])

        # Create individuals
        for data in INDIVIDUALS:
            if data["name"] not in existing_names:
                provider = Provider(organization_id=org.id, **data)
                db.add(provider)
                created.append(data["name"])

        await db.commit()

        print(f"✅ Seeded {len(created)} providers:")
        print(f"   🏢 Nigeria businesses: {len(NG_BUSINESSES)}")
        print(f"   🏢 US businesses: {len(US_BUSINESSES)}")
        print(f"   👤 Individuals: {len(INDIVIDUALS)}")
        print()
        for name in created:
            print(f"   • {name}")
        print()
        print("Run matching against opportunities to test scores:")
        print("  POST /api/v1/providers/{opportunity_id}/match")


if __name__ == "__main__":
    asyncio.run(seed_providers())
