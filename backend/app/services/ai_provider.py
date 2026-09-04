"""AI provider abstraction — Anthropic Claude or mock for testing."""
import json
import uuid
from typing import Any

from app.core.config import settings


class MockAIProvider:
    """Deterministic mock AI provider for testing and development."""

    async def classify_intent(self, signal_data: dict) -> dict:
        title = signal_data.get("title", "").lower()
        desc = signal_data.get("description", "").lower()
        combined = f"{title} {desc}"

        # Intent keywords with weights
        high_intent = [
            # Formal procurement
            "procurement", "rfp", "rfq", "tender", "solicitation",
            "request for proposal", "bid", "contract", "award",
            "infrastructure", "construction", "technology", "digital",
            "supply", "equipment", "services", "consulting",
            "federal", "department", "agency", "government", "ministry",
            # Conversational buying intent
            "looking for", "need a", "need an", "searching for",
            "anyone recommend", "can anyone suggest", "seeking",
            "hiring", "want to hire", "looking to hire",
            "accepting proposals", "taking applications",
            "want to build", "planning to build",
            "about to launch", "about to open", "about to start",
            "ready to", "going to need", "will need",
        ]
        medium_intent = [
            "opportunity", "project", "development", "investment",
            "partnership", "growth", "expansion", "reform", "plan",
            "strategy", "budget", "allocation", "funding",
            # Softer conversational signals
            "anyone know", "recommendations", "suggestions",
            "considering", "thinking about", "exploring",
            "interested in", "open to", "would love",
            "help with", "assist with", "support with",
            "freelancer", "contractor", "consultant", "specialist",
        ]

        high_count = sum(1 for w in high_intent if w in combined)
        medium_count = sum(1 for w in medium_intent if w in combined)

        score = min(1.0, (high_count * 0.12) + (medium_count * 0.06) + 0.15)
        confidence = min(1.0, 0.4 + (high_count * 0.08) + (medium_count * 0.04))

        intent_label = "high" if score > 0.6 else "medium" if score > 0.35 else "low"

        return {
            "intent_score": round(score, 3),
            "confidence": round(confidence, 3),
            "intent_label": intent_label,
            "signals_detected": [w for w in high_intent if w in combined][:5],
            "rationale": f"Detected {high_count} high-intent and {medium_count} medium-intent keywords.",
        }

    async def extract_opportunity(self, signal_data: dict, classification: dict) -> dict:
        title = signal_data.get("title", "")
        desc = signal_data.get("description", "")
        country = signal_data.get("country_code", "US")

        # Category detection
        categories = {
            "infrastructure": ["construction", "road", "bridge", "building", "infrastructure"],
            "technology": ["technology", "digital", "software", "ICT", "cyber", "cloud"],
            "energy": ["energy", "power", "electricity", "solar", "oil", "gas", "renewable"],
            "healthcare": ["health", "medical", "hospital", "pharmaceutical"],
            "agriculture": ["agriculture", "farming", "food", "crop"],
            "education": ["education", "school", "training", "university"],
            "manufacturing": ["manufacturing", "factory", "production", "industrial"],
            "defense": ["defense", "military", "security", "armed"],
            "finance": ["finance", "banking", "insurance", "fintech"],
            "consulting": ["consulting", "advisory", "management", "professional"],
        }

        combined = f"{title} {desc}".lower()
        detected_category = "consulting"  # default
        max_hits = 0
        for cat, keywords in categories.items():
            hits = sum(1 for k in keywords if k.lower() in combined)
            if hits > max_hits:
                max_hits = hits
                detected_category = cat

        # Urgency detection
        urgent_words = [
            "urgent", "immediate", "asap", "deadline", "expiring", "quick",
            "today", "this week", "right away", "need now", "time sensitive",
            "closing soon", "limited time", "last chance",
        ]
        urgency = "low"
        if any(w in combined for w in urgent_words):
            urgency = "high"
        elif classification.get("intent_score", 0) > 0.6:
            urgency = "medium"

        # Value extraction (simplified)
        value_min = None
        value_max = None
        if "million" in combined or "₦" in combined or "$" in combined:
            value_min = 100000
            value_max = 5000000

        # Deadline
        deadline = None

        # Buyer
        buyer_name = None
        buyer_org = None
        for keyword in ["ministry", "agency", "department", "corporation", "authority"]:
            idx = combined.find(keyword)
            if idx > 0:
                start = max(0, idx - 60)
                snippet = signal_data.get("title", "")[start:idx + len(keyword)]
                buyer_org = snippet.strip("-–—").strip()
                break

        currency = "USD"

        why_now = f"This opportunity shows {classification.get('intent_label', 'medium')} buying intent. "
        if urgency == "high":
            why_now += "The timeline suggests urgency — acting quickly could secure a first-mover advantage. "
        why_now += f"The {detected_category} sector in {country} is seeing increased activity."

        recommended = f"Review the {detected_category} opportunity details. "
        if urgency == "high":
            recommended += "Due to urgency, prioritize immediate response preparation. "
        recommended += "Verify requirements and prepare a capability statement."

        return {
            "category": detected_category,
            "subcategory": None,
            "urgency": urgency,
            "buyer_name": buyer_name,
            "buyer_organization": buyer_org,
            "location": f"{country}",
            "estimated_value_min": value_min,
            "estimated_value_max": value_max,
            "currency": currency,
            "deadline": deadline,
            "requirements": [],
            "why_now": why_now,
            "recommended_action": recommended,
            "evidence": [title, desc[:200]],
            "market_context": {
                "country": country,
                "category_trend": "stable",
                "recent_competitor_activity": False,
            },
        }


class AnthropicAIProvider:
    """Production AI provider using Anthropic Claude."""

    def __init__(self):
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
        except ImportError:
            raise RuntimeError("anthropic package not installed")

    async def classify_intent(self, signal_data: dict) -> dict:
        prompt = f"""You are a commercial intent analyst. Analyze this signal and determine buying intent.

Signal Title: {signal_data.get('title', '')}
Signal Description: {signal_data.get('description', '')[:1000]}
Country: {signal_data.get('country_code', 'Unknown')}
Source: {signal_data.get('source', 'Unknown')}

Respond with JSON:
{{
  "intent_score": <0.0-1.0>,
  "confidence": <0.0-1.0>,
  "intent_label": "<high|medium|low>",
  "signals_detected": [<list of key indicators>],
  "rationale": "<brief explanation>"
}}"""
        response = await self.client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(response.content[0].text)

    async def extract_opportunity(self, signal_data: dict, classification: dict) -> dict:
        prompt = f"""Extract structured opportunity data from this classified signal.

Signal: {signal_data.get('title', '')}
Description: {signal_data.get('description', '')[:1500]}
Country: {signal_data.get('country_code', 'Unknown')}
Classification: {json.dumps(classification)}

Respond with JSON containing these fields:
{{
  "category": "<primary category>",
  "subcategory": "<optional subcategory>",
  "urgency": "<low|medium|high|critical>",
  "buyer_name": "<person name or null>",
  "buyer_organization": "<organization or null>",
  "location": "<city/region>",
  "estimated_value_min": <number or null>,
  "estimated_value_max": <number or null>,
  "currency": "<USD|GBP|EUR>",
  "deadline": <ISO date or null>,
  "requirements": [<list of requirements>],
  "why_now": "<concise explanation of why this matters now>",
  "recommended_action": "<specific next step>",
  "evidence": [<key evidence snippets>],
  "market_context": {{"country": "<code>", "category_trend": "<growing|stable|declining>", "recent_competitor_activity": <bool>}}
}}"""
        response = await self.client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(response.content[0].text)


def get_ai_provider():
    """Factory for AI providers."""
    if settings.AI_PROVIDER == "anthropic":
        return AnthropicAIProvider()
    return MockAIProvider()
