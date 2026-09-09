# AI Intent Radar — Product Pitch

---

## The One-Line Pitch

> **"We tell businesses where money is about to move — before the opportunity becomes obvious."**

---

## The Problem

Every day, thousands of commercial opportunities are publicly signalled before they become
formal tenders or procurement notices. A company announces a new facility. A government agency
posts a hiring surge. A startup raises a Series A. A Reddit post asks "anyone recommend a
good cybersecurity firm in Austin?"

By the time these appear on job boards, tender platforms, or lead databases — everyone
already knows. The opportunity is commoditised.

**Businesses are always late to the table.**

The people who win are the ones who showed up first. But showing up first requires someone
to be watching everything, all the time. That person doesn't exist. Until now.

---

## The Solution

**AI Intent Radar** is a commercial intelligence platform that:

1. **Ingests** raw signals from public sources — hiring posts, procurement notices,
   business announcements, forum requests
2. **Classifies** commercial intent using AI — how strong is the buying signal? How urgent?
3. **Extracts** structured intelligence — who is the buyer, what do they need, how much,
   by when?
4. **Scores** every opportunity — intent score (0–100%), confidence, urgency
5. **Explains** why it matters now — "Why Now" for every opportunity
6. **Matches** opportunities to providers who can act on them

The output: a ranked feed of commercial opportunities your business should be pursuing,
with explanations, evidence, and recommended next steps.

---

## Who Is It For

**Primary:** Business development and sales teams at:
- Technology consultancies
- Federal contractors and SMBs
- Staffing and recruitment agencies
- Professional services firms
- Infrastructure and construction companies

**Secondary:** Individual freelancers and contractors looking for their next engagement

**Not for:** Job seekers (that's AI Job Radar — our sister product)

---

## The Market

- **US B2B Sales Intelligence market:** $3.4B and growing 12% YoY
- **US Federal contracting market:** $700B+ annually
- **Total addressable SMB market:** 6M+ businesses in the US actively seeking contracts

Current players (ZoomInfo, Bombora, 6sense) focus on **who to contact**. We focus on
**why right now and what they need** — a different and earlier layer of the stack.

---

## Product Flow

```
User opens Intent Radar
         │
         ▼
┌─────────────────────────────────┐
│         DASHBOARD               │
│                                 │
│  Today you have:                │
│  • 30 new opportunities         │
│  • 6 high urgency               │
│  • 1 high priority              │
│  • 5 emerging demand signals    │
└──────────────┬──────────────────┘
               │ clicks "View all"
               ▼
┌─────────────────────────────────┐
│       OPPORTUNITIES LIST        │
│                                 │
│  Filtered by: intent, urgency,  │
│  category, country              │
│                                 │
│  [Infrastructure · High · 100%] │
│  Crossref | Head of Infra...    │
│                                 │
│  [Technology · Medium · 69%]    │
│  Renaissance Philanthropy...    │
└──────────────┬──────────────────┘
               │ clicks opportunity
               ▼
┌─────────────────────────────────┐
│     OPPORTUNITY DETAIL          │
│                                 │
│  Intent Score: 100%             │
│  Confidence: High               │
│  Urgency: Medium                │
│                                 │
│  WHY NOW:                       │
│  "This opportunity shows high   │
│  buying intent. Infrastructure  │
│  sector is seeing increased     │
│  activity..."                   │
│                                 │
│  RECOMMENDED ACTION:            │
│  "Review details. Verify        │
│  requirements and prepare a     │
│  capability statement."         │
│                                 │
│  [Save] [Contact] [Dismiss]     │
└──────────────┬──────────────────┘
               │ clicks "Contact"
               ▼
┌─────────────────────────────────┐
│     PROVIDER MATCHES            │
│                                 │
│  Your providers matched:        │
│                                 │
│  1. Skyline Federal Tech  92%   │
│     ✓ Skill fit                 │
│     ✓ Geographic fit            │
│     ✓ Rate fit                  │
│                                 │
│  2. Demo Tech Solutions   78%   │
│     ✓ Skill fit                 │
│     △ Geographic fit            │
└─────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│     FEEDBACK LOOP               │
│                                 │
│  Won · Lost · Contacted ·       │
│  Saved · Dismissed              │
│                                 │
│  → Feeds back into scoring      │
│  → Improves future matches      │
└─────────────────────────────────┘
```

---

## Wireframes

### Screen 1 — Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│  Intent Radar    [All Markets ▾]                                │
├──────────┬──────────────────────────────────────────────────────┤
│          │  Intelligence Dashboard                              │
│ Dashboard│  Real-time commercial intent intelligence            │
│          │                                                       │
│Opportuni-│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │
│ties      │  │Total Opps│ │High Prior│ │New/Week  │ │Markets │  │
│          │  │    30    │ │    1     │ │   30     │ │   1    │  │
│Market    │  └──────────┘ └──────────┘ └──────────┘ └────────┘  │
│Intel     │                                                       │
│          │  ┌─────────────────┐ ┌──────────────┐ ┌──────────┐  │
│Providers │  │Intent Distrib.  │ │Urgency       │ │Market    │  │
│          │  │High    0%  ░░░░ │ │High    6     │ │Coverage  │  │
│          │  │Medium 100% ████ │ │Low    21     │ │🇺🇸 US 30 │  │
│          │  │Low     16% ██░░ │ │Medium  3     │ │  (49%)   │  │
│          │  └─────────────────┘ └──────────────┘ └──────────┘  │
│          │                                                       │
│          │  ┌──────────────────────────┐ ┌────────────────────┐ │
│          │  │Highest Priority          │ │Emerging Demand     │ │
│          │  │                          │ │                     │ │
│          │  │🇺🇸 INFRA    ● Medium    │ │🇺🇸 Infrastructure  │ │
│          │  │Ask HN: Crossref | Head.. │ │   7 new  ████ 66% │ │
│          │  │Intent ████████████ 100% │ │                     │ │
│          │  │                          │ │🇺🇸 Energy           │ │
│          │  │🇺🇸 INFRA    ● Medium    │ │   1 new  ███░ 57%  │ │
│          │  │Ask HN: Renaissance Ph.. │ │                     │ │
│          │  │Intent ███████░░░░  69%  │ │🇺🇸 Technology       │ │
│          │  │                 View all→│ │   2 new  ███░ 54%  │ │
│          │  └──────────────────────────┘ └────────────────────┘ │
└──────────┴──────────────────────────────────────────────────────┘
```

### Screen 2 — Opportunities List

```
┌─────────────────────────────────────────────────────────────────┐
│  Opportunities                                                  │
│  Commercial opportunities ranked by intent strength            │
│                                                                 │
│  [All Categories ▾]  [All Urgency ▾]          30 opportunities │
│                                                                 │
│  ┌───────────────────────────────┐ ┌───────────────────────┐   │
│  │ 🇺🇸 INFRASTRUCTURE  ● Medium │ │ 🇺🇸 TECHNOLOGY ● High │   │
│  │                               │ │                       │   │
│  │ Ask HN: Who is hiring?        │ │ DoD Cybersecurity     │   │
│  │ Crossref | Head of Infra...   │ │ Infrastructure...     │   │
│  │                               │ │                       │   │
│  │ Intent     ████████████ 100% │ │ Intent  ███████░  69% │   │
│  │ Confidence ████████████ 100% │ │ Confidence ████░  63% │   │
│  │                               │ │                       │   │
│  │ [Save] [Contact] [Dismiss]    │ │ [Save][Contact][Dism] │   │
│  └───────────────────────────────┘ └───────────────────────┘   │
│                                                                 │
│  ┌───────────────────────────────┐ ┌───────────────────────┐   │
│  │ 🇺🇸 ENERGY          ● High  │ │ 🇺🇸 CONSULTING ● Low  │   │
│  │                               │ │                       │   │
│  │ Ask HN: Apex Space |          │ │ GSA Cloud Migration   │   │
│  │ Multiple Roles | Full-Time... │ │ Services...           │   │
│  │                               │ │                       │   │
│  │ Intent     ████████░░░  57%  │ │ Intent  █████░░  45%  │   │
│  │ Confidence ████████░░░  57%  │ │ Confidence ████░  45% │   │
│  │                               │ │                       │   │
│  │ [Save] [Contact] [Dismiss]    │ │ [Save][Contact][Dism] │   │
│  └───────────────────────────────┘ └───────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Screen 3 — Opportunity Detail

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back to Opportunities                                        │
│                                                                 │
│  🇺🇸 INFRASTRUCTURE                              ● Medium      │
│  Ask HN: Who is hiring? (Sep 2026) | Crossref |                │
│  Head of Infrastructure Services                               │
│                                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐   │
│  │Intent Score  │ │Confidence    │ │Urgency               │   │
│  │ ████████ 100%│ │ ████████ 100%│ │ Medium               │   │
│  └──────────────┘ └──────────────┘ └──────────────────────┘   │
│                                                                 │
│  WHY NOW                                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ This opportunity shows high buying intent. The          │   │
│  │ infrastructure sector in US is seeing increased         │   │
│  │ activity. Acting quickly could secure first-mover       │   │
│  │ advantage.                                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  RECOMMENDED ACTION                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Review the infrastructure opportunity details. Due to   │   │
│  │ urgency, prioritize immediate response preparation.     │   │
│  │ Verify requirements and prepare a capability statement. │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  EVIDENCE                                                       │
│  • Ask HN: Who is hiring? (September 2026)                     │
│  • Crossref | Head of Infrastructure Services | Remote...      │
│                                                                 │
│  PROVIDER MATCHES                         [Run Matching →]     │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Skyline Federal Tech              ████████████  92%   │    │
│  │ Strong skill alignment; Good geographic fit            │    │
│  │                                                        │    │
│  │ Demo Tech Solutions               ████████░░░  78%   │    │
│  │ Moderate alignment; Good geographic fit                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────┐              │
│  │  💾 Save     │ │  📞 Contact  │ │  ✕ Dismiss│              │
│  └──────────────┘ └──────────────┘ └───────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### Screen 4 — Market Intelligence

```
┌─────────────────────────────────────────────────────────────────┐
│  Market Intelligence                                            │
│  Understand demand patterns and market movements               │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │Signals   │ │Validated │ │Avg Intent│ │Avg Conf. │         │
│  │   64     │ │   30     │ │   49%    │ │   49%    │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│                                                                 │
│  ┌──────────────────────────────┐ ┌────────────────────────┐  │
│  │ Top Categories by Demand     │ │ Emerging Demand Signals│  │
│  │                              │ │                        │  │
│  │ Infrastructure   ████ 66%   │ │ 🇺🇸 Infrastructure     │  │
│  │ 15 opps                      │ │    7 new  ████  66%    │  │
│  │                              │ │                        │  │
│  │ Technology       ███░ 54%   │ │ 🇺🇸 Energy              │  │
│  │ 7 opps                       │ │    1 new  ███░  57%    │  │
│  │                              │ │                        │  │
│  │ Consulting       ███░ 51%   │ │ 🇺🇸 Technology          │  │
│  │ 4 opps                       │ │    2 new  ███░  54%    │  │
│  └──────────────────────────────┘ └────────────────────────┘  │
│                                                                 │
│  Signal Intelligence Pipeline                                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐     │
│  │📡      │ │🔍      │ │📋      │ │✅      │ │⚡      │     │
│  │  64    │ │  51    │ │  38    │ │  30    │ │   9    │     │
│  │Raw     │ │Classif.│ │Extract.│ │Validat.│ │Hi-Int. │     │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## The 5-Minute Investor Demo Flow

**Minute 1 — The Problem**
> "You run a tech consultancy. Every week your BD team manually checks SAM.gov, LinkedIn,
> Reddit, HN. They spend 10 hours finding 3 leads. Most are already cold. You're always late."

**Minute 2 — The Product**
> Open dashboard. Show 30 live opportunities pulled this morning from real sources.
> "This came in 2 hours ago. Apex Space is hiring multiple roles — that means infrastructure
> spend is coming. Our AI scored it 57% intent, High urgency."

**Minute 3 — The Intelligence Layer**
> Click into an opportunity. Show Why Now, Recommended Action, Evidence.
> "We don't just show you what — we show you why it matters and what to do."

**Minute 4 — The Matching Engine**
> Show providers tab. "Your business is matched against every opportunity.
> 92% fit for this one. Here's why."

**Minute 5 — The Business Model**
> "We charge $49/month per seat for BD teams. $199/month for teams with provider matching.
> Enterprise pricing for agencies managing multiple clients.
> We're pre-revenue, live product, seeking $150K to get to 50 paying customers."

---

## Business Model

| Tier | Price | For |
|------|-------|-----|
| **Starter** | $49/month | 1 user, opportunity feed only |
| **Professional** | $149/month | 3 users, provider matching, market intel |
| **Team** | $299/month | 10 users, full platform, API access |
| **Enterprise** | Custom | Agencies, white-label, custom sources |

**Unit economics target:**
- CAC: $200 (content + outbound)
- LTV: $1,800 (avg 12-month retention at $149/month)
- LTV:CAC ratio: 9:1

---

## Traction & Proof Points

- ✅ Live product deployed at https://ai-intent-radar.vercel.app
- ✅ Real-time HN signal ingestion working in production
- ✅ AI pipeline scoring 30+ opportunities daily
- ✅ Full security hardening — JWT, RBAC, audit logs, org scoping
- ✅ Mobile-responsive UI
- 🔜 First paying customer conversations (target: month 2)
- 🔜 SAM.gov API integration (target: month 3)
- 🔜 LinkedIn signal layer (target: month 6)

---

## The Ask

**Raising:** $150,000 pre-seed  
**Use of funds:**
- 40% — Product (additional data sources, AI improvements)
- 35% — Growth (first marketing hires, content, outbound)
- 25% — Operations (infrastructure scale, legal, admin)

**Milestones with this funding:**
- 50 paying customers in 6 months
- $7,500 MRR by month 6
- Series A prep with $25K MRR target by month 12
