# AI INTENT RADAR — MASTER PRODUCT VISION & CONTINUITY SPECIFICATION

**Status:** Active Product Vision
**Version:** 1.0
**Purpose:** This document preserves the original product vision so any developer or AI can continue building Intent Radar without losing the reasoning, differentiation, or long-term direction.

---

# 1. THE PRODUCT IN ONE SENTENCE

**AI Intent Radar is a commercial-intelligence platform that detects where money is likely to move, explains why, identifies who can benefit, and tells businesses what they should act on before the opportunity becomes obvious.**

Core promise:

> **Know what the market wants before everyone else.**

---

# 2. WHAT WE ARE ACTUALLY BUILDING

Intent Radar is NOT primarily:

* a job board
* a tender aggregator
* a lead-generation database
* a web scraper
* an AI chatbot
* a notification service
* a procurement search engine

Those may be components of the system, but they are not the product.

The product is:

> **Commercial Intent Intelligence**

The system should transform scattered public/permissioned signals into actionable intelligence.

Instead of giving a customer more information, Radar should reduce uncertainty.

The customer should be able to ask:

> What is happening?

> Who is likely to spend money?

> What are they likely to spend it on?

> How strong is the buying intent?

> Why do you believe this?

> When is the likely buying window?

> Is this relevant to my business?

> Who else might pursue it?

> What should I do next?

---

# 3. THE CORE INTELLIGENCE LOOP

The fundamental system is:

```text
DATA SOURCES
     ↓
RAW SIGNALS
     ↓
SIGNAL NORMALIZATION
     ↓
AI INTENT DETECTION
     ↓
STRUCTURED INTENT EVENT
     ↓
OPPORTUNITY EXTRACTION
     ↓
SCORING
     ↓
CONFIDENCE + URGENCY
     ↓
EVIDENCE
     ↓
MARKET CONTEXT
     ↓
PROVIDER/BUSINESS MATCHING
     ↓
RECOMMENDED ACTION
     ↓
USER ACTION
     ↓
REAL-WORLD OUTCOME
     ↓
LEARNING
     ↓
BETTER INTENT DETECTION
```

This feedback loop is strategically important.

The long-term competitive advantage should not simply be the UI or AI prompts.

It should become the accumulated dataset connecting:

**market signals → detected intent → predictions → actions → outcomes**

---

# 4. WHAT COUNTS AS A SIGNAL?

A signal is any credible piece of information that can indicate future commercial activity.

Examples include:

### Procurement

* Government tenders
* RFQs
* RFPs
* Vendor requirements
* Procurement notices
* Contract announcements

### Business expansion

* New factories
* New offices
* New branches
* Geographic expansion
* New facilities
* Capacity expansion

### Investment

* Funding
* Major investment
* Infrastructure financing
* Public/private investment
* Capital expenditure announcements

### Corporate activity

* Mergers
* Acquisitions
* New subsidiaries
* New partnerships
* Strategic initiatives

### Hiring/activity patterns

Large increases in hiring can indicate:

* expansion
* new projects
* new capabilities
* geographic expansion

Hiring itself is not necessarily a commercial opportunity, but it may be an intent signal.

### Infrastructure/development

* Construction projects
* Real estate developments
* Industrial developments
* Energy projects
* Transportation projects
* Telecommunications expansion

### Regulatory/market changes

A regulatory or policy change can create new demand.

Example:

```text
New regulation
      ↓
Companies must comply
      ↓
New business requirement
      ↓
Potential commercial demand
```

---

# 5. INTENT EVENTS

Eventually, the system should distinguish between a raw signal and an inferred commercial event.

Example:

### Raw Signal

> Company X announces construction of a new manufacturing facility.

### Intent Event

```text
Company: Company X

Intent:
Expand manufacturing capacity

Likely requirements:
- Construction
- Engineering
- Security
- Logistics
- IT infrastructure
- Equipment
- Staffing

Expected buying window:
3–9 months

Confidence:
78%

Evidence:
[Source A]
[Source B]
```

The Intent Event represents what Radar believes is actually happening commercially.

This concept should eventually become a core domain object.

---

# 6. FROM DETECTION TO PREDICTION

The MVP can focus on detecting strong existing signals.

But the long-term product should move toward:

```text
VISIBLE SIGNAL
      ↓
PATTERN DETECTION
      ↓
EMERGING INTENT
      ↓
LIKELY FUTURE REQUIREMENT
      ↓
PREDICTED OPPORTUNITY
```

The ultimate objective is to identify opportunities **before they become obvious procurement events**.

Do not build an unnecessarily complicated predictive ML system immediately.

First collect reliable historical signal/outcome data.

Prediction should evolve from real evidence.

---

# 7. THE INTENT SCORE

The score should never be presented as absolute truth.

It is an AI-assisted assessment.

Example:

```text
INTENT SCORE
87 / 100

Confidence
High

Urgency
High
```

The score should be explainable.

Potential factors:

* Explicit purchase request
* Identified buyer
* Identified budget
* Defined timeline
* Procurement activity
* Business expansion
* Project scale
* Recency
* Multiple supporting signals
* Source credibility
* Historical patterns

The exact weighting can evolve.

---

# 8. WHY NOW?

Every important opportunity should answer:

> **Why does this matter now?**

Example:

```text
WHY NOW

Company X announced a new facility two weeks ago.
The project is expected to begin in Q1.

Radar detected:
✓ Expansion announcement
✓ Estimated project value
✓ Location identified
✓ Procurement activity
✓ Relevant supplier requirements

Buying window:
Estimated 30–90 days
```

Evidence should always be traceable to the underlying source.

Never fabricate evidence.

---

# 9. OPPORTUNITY INTELLIGENCE

Each opportunity should ideally contain:

* Title
* Summary
* Buyer/company
* Country
* Location
* Industry
* Category
* Intent score
* Confidence score
* Urgency
* Estimated value
* Currency
* Timeline
* Deadline where applicable
* Requirements
* Evidence
* Source references
* Why Now
* Market context
* Potential providers
* Recommended action

---

# 10. PROVIDER MATCHING

Radar should connect demand with businesses capable of fulfilling that demand.

Example:

```text
OPPORTUNITY

Commercial solar installation
Lagos
Estimated value: ₦250M

        ↓

MATCHING ENGINE

Company A
Match: 94%
✓ Service
✓ Location
✓ Project size

Company B
Match: 81%
✓ Service
✓ Location
△ Project size

Company C
Match: 62%
✓ Service
△ Location
△ Project size
```

The score must be explainable.

Current core dimensions:

* Service fit
* Geographic fit
* Project-size fit

Future dimensions may include:

* Capacity
* Certifications
* Past performance
* Industry experience
* Availability
* Procurement eligibility

---

# 11. RECOMMENDED ACTION

Radar should eventually move beyond:

> "Here is an opportunity."

to:

> **"Here is what you should do."**

Example:

```text
RECOMMENDED ACTION

Priority: HIGH

Contact the buyer/vendor-registration team
within 7 days.

Reason:
Buying intent is high and the estimated
procurement window is approaching.
```

This is a key part of turning intelligence into business value.

---

# 12. MARKET INTELLIGENCE

Radar should understand markets, not just individual opportunities.

Example:

```text
LAGOS — LOGISTICS

Demand trend: ↑

Signals detected: 147
High-intent opportunities: 31
Estimated pipeline: ₦X
Active buying windows: 12

Emerging drivers:
• E-commerce expansion
• Warehouse development
• Distribution infrastructure
```

Users should eventually be able to see:

* emerging industries
* growing categories
* geographic demand
* major buyers
* spending patterns
* opportunity velocity
* market acceleration
* declining demand
* emerging commercial themes

---

# 13. MARKET ACCELERATION

An important future concept is detecting when activity is increasing unusually quickly.

Example:

```text
NORMAL ACTIVITY
████████

CURRENT ACTIVITY
████████████████

RADAR ALERT

"Commercial construction activity in Lagos
is accelerating."

+34% signal growth over previous period.
```

This is more valuable than simply counting opportunities.

---

# 14. COMPETITIVE INTELLIGENCE

Eventually Radar should help answer:

> Who else is likely to pursue this opportunity?

Potential intelligence:

* known suppliers
* previous winners
* incumbent vendors
* competitor activity
* market saturation
* supplier density
* historical performance

Long-term concept:

```text
OPPORTUNITY
     ↓
BUYER
     ↓
KNOWN SUPPLIERS
     ↓
COMPETITOR LANDSCAPE
     ↓
YOUR FIT
     ↓
ESTIMATED COMPETITIVE POSITION
```

Do not claim a "probability of winning" without sufficient evidence.

---

# 15. COUNTRY ARCHITECTURE

Initial markets:

🇳🇬 Nigeria
🇺🇸 United States

Country support must be configuration-driven.

Each country can define:

```text
Country
├── Currency
├── Language
├── Timezone
├── Categories
├── Location hierarchy
├── Terminology
├── Scoring adjustments
└── Data sources
```

Platform administrators should be able to enable/disable supported markets.

Organizations should be able to select which enabled markets they want to monitor.

Future examples:

* Ghana
* Kenya
* South Africa
* UK
* Canada
* etc.

Do not hard-code country logic throughout the application.

---

# 16. DATA SOURCE PRINCIPLE

Only use lawful, permitted and appropriately licensed/public sources.

The platform should prioritize:

* official procurement APIs
* official government portals
* public RSS feeds
* public company announcements
* permitted APIs
* licensed datasets
* legitimate business data sources

Do not build the product around unauthorized scraping or circumvention.

Source credibility should eventually influence confidence.

---

# 17. LEARNING LOOP

User behavior should generate structured feedback.

Examples:

```text
Opportunity
 ↓
Viewed
 ↓
Saved
 ↓
Contacted
 ↓
Won / Lost
```

or:

```text
Dismissed
Reason:
Not relevant
```

This data can eventually improve:

* scoring
* matching
* ranking
* source quality
* category detection
* timing predictions

The long-term learning loop:

```text
Signal
 ↓
Prediction
 ↓
Recommendation
 ↓
Business Action
 ↓
Outcome
 ↓
Training/Calibration Data
 ↓
Better Prediction
```

---

# 18. THE PRODUCT SHOULD PRIORITIZE SIGNAL OVER VOLUME

A common mistake would be trying to show users thousands of opportunities.

Do the opposite.

The product should aggressively filter noise.

A customer should ideally open Radar and see:

```text
TODAY

3 opportunities you should care about

1. High-intent logistics contract
2. New manufacturing expansion
3. Government infrastructure procurement
```

The goal is:

> **Less information. More useful information.**

---

# 19. THE IDEAL USER EXPERIENCE

A user opens Radar.

They immediately see:

```text
GOOD MORNING

Your Radar detected:

12 new commercial signals
4 high-intent opportunities
2 urgent opportunities
1 emerging market trend
```

Then:

### Priority Opportunities

```text
87  HIGH INTENT
New logistics requirement
Lagos
Estimated value: ₦X

WHY NOW:
...

YOUR FIT:
94%

RECOMMENDED ACTION:
Contact buyer/vendor team.
```

The experience should feel like having a **commercial intelligence analyst watching the market continuously**.

---

# 20. THE MOST IMPORTANT DIFFERENTIATOR

Do not compete primarily on:

* number of listings
* number of sources
* number of AI features
* number of countries
* number of notifications

Compete on:

### **Signal quality + interpretation + timing + actionability**

The core differentiation is:

> **Radar doesn't simply tell you what exists. It tries to tell you what is about to matter.**

---

# 21. MVP VS LONG-TERM VISION

### MVP

Focus on:

* reliable signal collection
* commercial intent classification
* structured extraction
* scoring
* confidence
* urgency
* evidence
* opportunities
* provider matching
* dashboard
* country selection
* market intelligence basics
* feedback
* secure multi-tenancy

### Phase 2

Add:

* stronger market trends
* opportunity velocity
* better evidence
* source credibility
* richer recommendations
* AI version history
* improved matching
* more country sources

### Phase 3

Add:

* emerging intent detection
* predictive opportunities
* competitive intelligence
* demand forecasting
* market acceleration alerts
* advanced outcome learning

### Long-Term

Intent Radar becomes:

> **A continuously learning commercial-intelligence network that detects emerging demand across markets and tells businesses where to position themselves before demand becomes obvious.**

---

# 22. WHAT NOT TO DO

Never allow the product to drift into:

### Generic job aggregation

If the system starts primarily showing jobs, stop and reassess.

### Generic tender aggregation

If the primary value becomes "search 10,000 tenders," stop and reassess.

### AI chatbot

The AI is the intelligence engine, not the product itself.

### Notification spam

More alerts do not equal more value.

### Fake certainty

Never present AI predictions as guaranteed facts.

### Untraceable intelligence

Important claims should have evidence.

### Premature complexity

Do not build sophisticated prediction models before enough real-world data exists.

---

# 23. THE NORTH STAR

Every major feature should be judged against this question:

> **Does this help a business identify, understand, prioritize, or act on commercial intent earlier and better than it could without Radar?**

If YES → consider building it.

If NO → it is probably not core.

---

# 24. FINAL PRODUCT DEFINITION

The simplest way to understand Intent Radar is:

```text
THE INTERNET / PUBLIC MARKET
          ↓
      SIGNALS
          ↓
     INTENT RADAR
          ↓
 ┌──────────────────────┐
 │ What is happening?   │
 │ Who will spend?      │
 │ What will they need? │
 │ How strong is intent?│
 │ Why now?             │
 │ Who can benefit?     │
 │ What should I do?    │
 └──────────────────────┘
          ↓
      BUSINESS
          ↓
       ACTION
          ↓
      OUTCOME
          ↓
      LEARNING
```

### The ultimate vision:

> **Intent Radar should become the system businesses consult when they want to know where commercial demand is forming before everyone else sees it.**

Everything we build should move toward that vision without unnecessarily complicating the MVP.
