"""Test provider matching accuracy by running matching against all opportunities.

Shows how each provider scores against each opportunity with detailed reasoning.

Run: python -m app.utils.test_matching
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import select
from app.core.database import get_session_factory
from app.models.models import Opportunity, Provider, Organization


async def test_matching():
    """Run matching and display results."""
    async with get_session_factory()() as db:
        # Get the demo org
        result = await db.execute(select(Organization).where(Organization.slug == "demo-corp"))
        org = result.scalar_one_or_none()
        if not org:
            print("Demo org not found. Run seed_data.py first.")
            return

        # Get all opportunities for this org
        opp_result = await db.execute(
            select(Opportunity)
            .where(Opportunity.organization_id == org.id)
            .order_by(Opportunity.intent_score.desc())
        )
        opportunities = list(opp_result.scalars().all())

        # Get all active providers for this org
        prov_result = await db.execute(
            select(Provider)
            .where(Provider.organization_id == org.id, Provider.is_active == True)
        )
        providers = list(prov_result.scalars().all())

        if not opportunities:
            print("No opportunities found. Run the pipeline first.")
            return
        if not providers:
            print("No providers found. Run seed_providers.py first.")
            return

        print(f"📊 Matching {len(providers)} providers against {len(opportunities)} opportunities")
        print("=" * 80)

        # Import matching logic
        from app.services.provider_matching import _calculate_business_match, _calculate_individual_match

        for opp in opportunities:
            print(f"\n🎯 {opp.title}")
            print(f"   Country: {opp.country_code} | Category: {opp.category} | "
                  f"Intent: {opp.intent_score:.0%} | Urgency: {opp.urgency}")
            if opp.estimated_value_min:
                print(f"   Est. Value: {opp.currency or '$'}{opp.estimated_value_min:,.0f}")
            if opp.location:
                print(f"   Location: {opp.location}")

            matches = []
            for provider in providers:
                if provider.provider_type == "individual":
                    score = _calculate_individual_match(opp, provider)
                else:
                    score = _calculate_business_match(opp, provider)
                matches.append((provider, score))

            # Sort by total score
            matches.sort(key=lambda x: x[1]["total_score"], reverse=True)

            print(f"\n   {'Provider':<30} {'Type':<12} {'Service':<10} {'Geo':<10} {'Size':<10} {'TOTAL':<10}")
            print(f"   {'─'*30} {'─'*12} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")

            for provider, score in matches:
                ptype = "🏢" if provider.provider_type == "business" else "👤"
                marker = " ⭐" if score["total_score"] >= 0.7 else " ✓" if score["total_score"] >= 0.4 else ""
                print(f"   {provider.name:<30} {ptype:<12} "
                      f"{score['service_fit']:<10.0%} {score['geographic_fit']:<10.0%} "
                      f"{score['project_size_fit']:<10.0%} {score['total_score']:<10.0%}{marker}")
                print(f"   {'':30} └─ {score['reasoning']}")

        # Summary
        print("\n" + "=" * 80)
        print("📈 MATCHING SUMMARY")
        print("=" * 80)

        all_scores = []
        for opp in opportunities:
            for provider in providers:
                if provider.provider_type == "individual":
                    score = _calculate_individual_match(opp, provider)
                else:
                    score = _calculate_business_match(opp, provider)
                all_scores.append((opp.title, provider.name, score["total_score"]))

        all_scores.sort(key=lambda x: x[2], reverse=True)

        print(f"\nTop 10 Matches:")
        print(f"{'Opportunity':<45} {'Provider':<30} {'Score':<10}")
        print(f"{'─'*45} {'─'*30} {'─'*10}")
        for opp_title, prov_name, total in all_scores[:10]:
            print(f"{opp_title:<45} {prov_name:<30} {total:<10.0%}")

        print(f"\nBottom 5 Matches:")
        print(f"{'Opportunity':<45} {'Provider':<30} {'Score':<10}")
        print(f"{'─'*45} {'─'*30} {'─'*10}")
        for opp_title, prov_name, total in all_scores[-5:]:
            print(f"{opp_title:<45} {prov_name:<30} {total:<10.0%}")

        # Score distribution
        high = sum(1 for _, _, s in all_scores if s >= 0.7)
        med = sum(1 for _, _, s in all_scores if 0.4 <= s < 0.7)
        low = sum(1 for _, _, s in all_scores if s < 0.4)
        print(f"\nScore Distribution: {high} high (≥70%) | {med} medium (40-69%) | {low} low (<40%)")


if __name__ == "__main__":
    asyncio.run(test_matching())
