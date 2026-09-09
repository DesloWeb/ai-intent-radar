"""Seed mock providers into the PRODUCTION Neon database.

Usage:
  DATABASE_URL='postgresql://neondb_owner:YOUR_PASSWORD@ep-delicate-sky-a5oxiayn-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require' \
  python -m app.utils.seed_providers_production
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


PROVIDERS = [
    # Nigeria Businesses
    {"name": "Lagos Tech Systems Ltd", "description": "Leading technology infrastructure company in Lagos. Specializes in cloud deployment, cybersecurity, and enterprise software.", "provider_type": "business", "services": '["cloud_deployment","cybersecurity","enterprise_software","IT_consulting"]', "categories": '["technology","infrastructure","cybersecurity"]', "locations": '["Lagos","Victoria Island","Ikoyi"]', "country_codes": '["NG"]', "min_project_value": 5000000, "max_project_value": 100000000, "email": "info@lagostech.ng", "phone": "+234-801-234-5678"},
    {"name": "Abuja Construction Group", "description": "Full-service construction and civil engineering firm. 20+ years experience in road infrastructure, bridges, and public works.", "provider_type": "business", "services": '["road_construction","civil_engineering","project_management","materials_supply"]', "categories": '["infrastructure","construction","engineering"]', "locations": '["Abuja","Kaduna","Kano"]', "country_codes": '["NG"]', "min_project_value": 10000000, "max_project_value": 500000000, "email": "contracts@abujaconstruction.ng", "phone": "+234-802-345-6789"},
    {"name": "MedSupply Nigeria", "description": "Medical equipment and pharmaceutical distributor serving hospitals, clinics, and corporate health programs across Nigeria.", "provider_type": "business", "services": '["medical_equipment","pharmaceuticals","facility_management","healthcare_consulting"]', "categories": '["healthcare","medical","procurement"]', "locations": '["Lagos","Abuja","Port Harcourt"]', "country_codes": '["NG"]', "min_project_value": 2000000, "max_project_value": 50000000, "email": "sales@medsupply.ng", "phone": "+234-803-456-7890"},
    {"name": "GreenField Agri Solutions", "description": "Agricultural technology and equipment provider. Specializes in irrigation systems, farm mechanization, and cold chain logistics.", "provider_type": "business", "services": '["irrigation_systems","farm_mechanization","cold_chain","agricultural_consulting"]', "categories": '["agriculture","farming","food_processing"]', "locations": '["Abuja","Kaduna","Nasarawa"]', "country_codes": '["NG"]', "min_project_value": 5000000, "max_project_value": 100000000, "email": "info@greenfieldagri.ng", "phone": "+234-804-567-8901"},
    {"name": "PayFlow Fintech", "description": "Nigerian fintech company building payment infrastructure, digital banking solutions, and compliance systems for the financial sector.", "provider_type": "business", "services": '["payment_gateway","digital_banking","compliance_systems","fintech_integration"]', "categories": '["fintech","technology","financial_services"]', "locations": '["Lagos","Victoria Island"]', "country_codes": '["NG"]', "min_project_value": 10000000, "max_project_value": 200000000, "email": "enterprise@payflow.ng", "phone": "+234-805-678-9012"},
    # US Businesses
    {"name": "CyberShield Federal", "description": "Cybersecurity firm specializing in federal government contracts. Zero-trust architecture, SIEM, penetration testing, FedRAMP compliance.", "provider_type": "business", "services": '["zero_trust_architecture","siem_deployment","penetration_testing","fedramp_compliance"]', "categories": '["cybersecurity","defense","compliance"]', "locations": '["Washington DC","Arlington","Reston"]', "country_codes": '["US"]', "min_project_value": 1000000, "max_project_value": 100000000, "email": "contracts@cybershield.com", "phone": "+1-703-555-0101"},
    {"name": "CloudBridge Solutions", "description": "Enterprise cloud migration and DevOps consultancy. AWS Advanced Partner, Azure Gold Partner. Federal and commercial clients.", "provider_type": "business", "services": '["aws_migration","azure_migration","devops","managed_services"]', "categories": '["technology","cloud","infrastructure"]', "locations": '["San Francisco","Seattle","Austin"]', "country_codes": '["US"]', "min_project_value": 500000, "max_project_value": 50000000, "email": "solutions@cloudbridge.io", "phone": "+1-415-555-0202"},
    {"name": "EnviroTech Consulting", "description": "Environmental engineering and consulting firm. Water treatment, wastewater management, stormwater solutions for government and utilities.", "provider_type": "business", "services": '["water_treatment","wastewater_management","stormwater","environmental_compliance"]', "categories": '["environmental","water","infrastructure"]', "locations": '["New York","New Jersey","Connecticut"]', "country_codes": '["US"]', "min_project_value": 2000000, "max_project_value": 80000000, "email": "projects@envirotech.com", "phone": "+1-212-555-0303"},
    {"name": "SmartTransit AI", "description": "Transportation technology company. IoT sensor networks, traffic management AI, EV infrastructure for smart city initiatives.", "provider_type": "business", "services": '["iot_sensors","traffic_management","ev_infrastructure","smart_city"]', "categories": '["transportation","technology","infrastructure"]', "locations": '["Chicago","Detroit","San Francisco"]', "country_codes": '["US"]', "min_project_value": 1000000, "max_project_value": 75000000, "email": "partnerships@smarttransit.ai", "phone": "+1-312-555-0404"},
    {"name": "HealthAI Labs", "description": "Healthcare AI and analytics company. NLP for clinical notes, predictive disease models, HIPAA-compliant data pipelines.", "provider_type": "business", "services": '["clinical_nlp","disease_prediction","hipaa_data_pipeline","health_analytics"]', "categories": '["healthcare","technology","ai"]', "locations": '["Boston","New York","San Francisco"]', "country_codes": '["US"]', "min_project_value": 1000000, "max_project_value": 50000000, "email": "federal@healthailabs.com", "phone": "+1-617-555-0505"},
    # Individuals
    {"name": "Adebayo Ogundimu", "description": "Senior DevOps engineer with 8 years experience in cloud infrastructure, AWS, Kubernetes, and CI/CD pipelines.", "provider_type": "individual", "services": "[]", "categories": '["technology","cloud","devops"]', "locations": '["Lagos","Abuja"]', "country_codes": '["NG"]', "skills": '["aws","kubernetes","devops","ci_cd","docker","terraform","python"]', "hourly_rate_min": 50, "hourly_rate_max": 150, "availability": "contract", "verified": True, "email": "adebayo.ogundimu@gmail.com"},
    {"name": "Sarah Chen", "description": "Cybersecurity consultant specializing in federal compliance, zero-trust implementation, and security audits.", "provider_type": "individual", "services": "[]", "categories": '["cybersecurity","compliance","defense"]', "locations": '["Washington DC","Arlington"]', "country_codes": '["US"]', "skills": '["cybersecurity","zero_trust","fedramp","siem","compliance","penetration_testing"]', "hourly_rate_min": 150, "hourly_rate_max": 350, "availability": "full_time", "verified": True, "email": "sarah.chen@protonmail.com"},
    {"name": "Emeka Nwosu", "description": "Civil engineer and project manager with 15 years experience in road construction and public infrastructure across Nigeria.", "provider_type": "individual", "services": "[]", "categories": '["infrastructure","construction","engineering"]', "locations": '["Abuja","Kaduna","Enugu"]', "country_codes": '["NG"]', "skills": '["road_construction","project_management","civil_engineering","cost_estimation","site_supervision"]', "hourly_rate_min": 40, "hourly_rate_max": 120, "availability": "full_time", "verified": True, "email": "emeka.nwosu@yahoo.com"},
    {"name": "Dr. Fatima Abdullahi", "description": "Agricultural scientist specializing in irrigation design, farm mechanization, and post-harvest technology.", "provider_type": "individual", "services": "[]", "categories": '["agriculture","farming","technology"]', "locations": '["Abuja","Kaduna"]', "country_codes": '["NG"]', "skills": '["irrigation","farm_mechanization","agricultural_science","cold_chain","crop_management"]', "hourly_rate_min": 30, "hourly_rate_max": 80, "availability": "contract", "verified": True, "email": "fatima.abdullahi@gmail.com"},
    {"name": "Marcus Thompson", "description": "Full-stack developer and fintech specialist. Built payment gateways, digital banking platforms, and compliance systems.", "provider_type": "individual", "services": "[]", "categories": '["fintech","technology","financial_services"]', "locations": '["Lagos","New York"]', "country_codes": '["NG","US"]', "skills": '["fintech","payment_gateway","digital_banking","compliance","python","react"]', "hourly_rate_min": 100, "hourly_rate_max": 250, "availability": "contract", "verified": True, "email": "marcus.thompson@outlook.com"},
]


async def seed():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: Set DATABASE_URL env var")
        return

    # Ensure asyncpg driver
    if "asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://").replace("postgres://", "postgresql+asyncpg://")

    import asyncpg

    # Extract connection params from URL
    # Format: postgresql+asyncpg://user:pass@host/db?sslmode=require
    url_parts = db_url.split("://", 1)[1]
    auth_host = url_parts.split("@", 1)
    user_pass = auth_host[0].split(":", 1)
    host_db = auth_host[1].split("?", 1)
    host_port_db = host_db[0].split("/", 1)

    user = user_pass[0]
    password = user_pass[1]
    host = host_port_db[0].split(":")[0]
    port = int(host_port_db[0].split(":")[1]) if ":" in host_port_db[0] else 5432
    database = host_port_db[1]

    conn = await asyncpg.connect(user=user, password=password, host=host, port=port, database=database, ssl="require")

    # Find org
    org = await conn.fetchrow("SELECT id, name FROM organizations LIMIT 1")
    if not org:
        print("No organizations found")
        await conn.close()
        return

    org_id = org["id"]
    print(f"Organization: {org['name']} ({org_id})")

    # Check existing
    existing = await conn.fetch("SELECT name FROM providers")
    existing_names = {r["name"] for r in existing}

    created = 0
    for p in PROVIDERS:
        if p["name"] in existing_names:
            continue

        await conn.execute(
            """INSERT INTO providers (id, organization_id, provider_type, name, description, email, phone,
               services, categories, locations, country_codes, skills,
               min_project_value, max_project_value, hourly_rate_min, hourly_rate_max,
               availability, verified, is_active, created_at, updated_at)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8::jsonb,$9::jsonb,$10::jsonb,$11::jsonb,$12::jsonb,
                       $13,$14,$15,$16,$17,$18,$19,$20,$21)""",
            str(uuid.uuid4()),
            str(org_id),
            p["provider_type"],
            p["name"],
            p["description"],
            p.get("email"),
            p.get("phone"),
            p["services"],
            p["categories"],
            p["locations"],
            p["country_codes"],
            p.get("skills", "[]"),
            p.get("min_project_value"),
            p.get("max_project_value"),
            p.get("hourly_rate_min"),
            p.get("hourly_rate_max"),
            p.get("availability"),
            p.get("verified", False),
            True,
            datetime.now(timezone.utc),
            datetime.now(timezone.utc),
        )
        created += 1
        print(f"  ✅ {p['name']}")

    await conn.close()
    print(f"\nDone: {created} providers created")


if __name__ == "__main__":
    asyncio.run(seed())
