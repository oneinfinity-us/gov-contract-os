# 26-81 — Notice of Intent to Negotiate: PoC Location-Based Digital Assistant

> Draft evaluation. Human review required before any go/no-bid decision, protest
> filing, or outreach.

## 1. Opportunity summary

| Field | Value |
|---|---|
| Agency | Port of Seattle |
| Solicitation number | **26-81** |
| Procurement type | Notice of Intent to Negotiate (sole-source announcement) |
| Category | Goods and Services |
| Department | Customer Service (Airport Customer Service / Experience) |
| Status | Open |
| Advertised | 2026-07-22 |
| Q&A cutoff | 2026-08-03 17:00 PT |
| **Due (protest / equivalent-capability notice)** | **2026-08-06 12:59 PT** |
| Days remaining (from 2026-07-22) | **15** |
| Estimated value | Not disclosed (`EngineerEstimate` empty; `EstimateQuarter=3`, `EstimateYear=2026`) |
| Named vendor Port intends to negotiate with | **Hello Lamp Post, San Francisco, CA** |
| Port contact | Maria Mayhue — 206-787-3909 — Mayhue.M@portseattle.org |
| Source URL | https://hosting.portseattle.org/sops/#/Solicitations/Detail/f00b55c1-0086-f111-bd41-005056aa9c71 |
| Raw source reference | `sopsapi/Solicitations Id=f00b55c1-0086-f111-bd41-005056aa9c71` |

**Scope (from Port's description, verbatim):**

> The Port of Seattle intends to negotiate a contract with Hello Lamp Post, San
> Francisco, CA to provide the following: Proof of Concept (PoC): Location-Based
> Digital Assistant at SEA for Airport Innovation on behalf of Airport Customer
> Service/Experience. The primary purpose of this pilot is to evaluate whether
> an AI virtual assistant can enhance the passenger experience by providing
> timely, self-service information throughout the airport by using
> location-specific QR codes.

## 2. Timeline feasibility filter (hard cutoff)

Days remaining = 15 → **passes** (≥ 8). Proceed to scoring.

## 3. Weighted score (per `workflows/opportunity-review.md`)

### Core Capability Fit (× 3 multiplier)

| Dimension | Points (0–max) | Reasoning |
|---|---|---|
| Microsoft AI / Copilot / Azure / agent fit (0–25) | **23** | Direct AI application — "AI virtual assistant", location-aware conversational agent, self-service passenger info. Not stack-locked to Azure (Hello Lamp Post is a self-hosted platform), so 2 points shaved from 25. |
| Software dev / automation fit (0–15) | **13** | PoC deployment: agent runtime + QR-code integration + likely backend/API + content pipeline. Core software work. |

Subtotal: (23 + 13) × 3 = **108 / 120**

### Business & Market Fit (× 1.5 multiplier)

| Dimension | Points (0–max) | Reasoning |
|---|---|---|
| Seattle / WA geographic fit (0–5) | **5** | Port of Seattle — perfect. |
| Contract size for small firm (0–10) | **8** | PoC scope + no engineer estimate + typical airport-innovation PoC budgets fall in the <$500k range. Assumed small-firm friendly. |
| Subcontracting potential (0–10) | **1** | **Sole-source NOI: essentially zero sub pathway.** If Hello Lamp Post wins the sole-source negotiation they don't need us; if a competitor protests successfully, the work becomes a new competitive RFP where sub roles are speculative. |

Subtotal: (5 + 8 + 1) × 1.5 = **21 / 37.5**

### Execution Risk (× 1 multiplier)

| Dimension | Points (0–max) | Reasoning |
|---|---|---|
| Demonstrable relevant experience (0–10) | **0** | ⚠️ `company/company-profile.md`, `company/capabilities.md`, `company/founder-bio.md`, and `company/past-performance/` are all TODO stubs. Per workflow §"Missing Company Data", award 0 and flag rather than inflate. |
| Reasonable mandatory requirements (0–10) | **6** | No prohibitive mandates visible in description (goods-and-services PoC, not construction). But the NOI procedural mandate — to challenge, we must submit written evidence of equivalent capability — is unmet given our missing past-performance file. |

Subtotal: (0 + 6) × 1 = **6 / 20**

### Total

```
Total       = 108 + 21 + 6 = 135
Max         = 177.5
Normalized  = 135 / 177.5 × 100 = 76
```

**Score-only decision: 76 ≥ 70 → "Go".**

## 4. Structural override

The **Notice of Intent to Negotiate** structure changes the picture. This is
**not a competitive RFP**; it is a public announcement that the Port has already
selected Hello Lamp Post and intends to sole-source the contract. The
solicitation period exists so that **other vendors with demonstrated equivalent
capability may protest / submit written notice of interest** within the window.

To meaningfully challenge, we would need:

1. Documented past performance building a location-based conversational AI
   deployed at a comparable venue (airport, transit hub, campus, or venue of
   similar scale). We currently have **none on file**.
2. Enough runway to draft a credible written response by 2026-08-06 (15 days).
3. Willingness to spend the effort knowing the incumbent starts with strong
   institutional preference.

Given the missing company profile and past-performance file, we **cannot
credibly protest** on the merits right now.

## 4.5 Competitive intelligence — Hello Lamp Post (named vendor)

Sourced from https://www.hlp.city/en-us and linked case-study pages, fetched
2026-07-22. Vendor's own marketing content — treat performance numbers as
vendor-published (not independently audited), but the deployment list is
externally verifiable.

### Vendor summary

- **Product**: *Hello Airport* — QR-code-triggered, location-based
  conversational agent ("Digital Team Members") delivered as branded on-site
  signage + mobile-web chat (no app install required).
- **Offices**: San Francisco (per Port of Seattle NOI); UK origin visible on
  their site.

### Publicly cited airport deployments

| Airport | Country | Focus |
|---|---|---|
| Cincinnati / N. Kentucky Intl (CVG) | USA | Cross-touchpoint 24/7 Digital Team Member. Featured case study with named executive testimonial. |
| Birmingham Airport (BABS) | UK | "One Digital Front Door" / Connected Personal Experiences initiative |
| Glasgow Airport | UK | Assisted-Travel / accessibility focus |
| Atlantic City Airport | USA | In-terminal deployment, reduce frontline team load |

Multiple **US and UK airports already live** with this vendor. This is
material context for the sole-source justification.

### Vendor's claimed advantages (verbatim themes from their site)

- **24/7 support, everywhere** — no staff coverage burden
- **Real-time analytics dashboard** — engagement metrics, conversation logs,
  insight charts
- **Automates repeat queries** — staff-time recovery
- **Low-cost scale** across many touchpoints
- **Multi-language + accessibility** features (referenced repeatedly)
- **Low carbon footprint** claim — no paper, no data entry, no travel
- Airport-specific value props they list: *Location-Specific Real-Time
  Contextual Support*, *Boost Non-Aeronautical Revenue Generation*, *One
  Digital Front Door*, *Personalize Passenger Engagement*

### Concrete example — CVG Airport (their most-featured case)

Vendor-published projections based on Q1 2026 data
(https://www.hlp.city/en-us/case-studies/improving-passenger-engagement):

- **11,000+ staff hours saved**
- **31,000+ additional passengers supported**
- **12,000+ questions diverted from customer-experience teams**

Stated objectives: reduce inbound calls/emails to CVG support; provide
immediate FAQ answers; collect passenger feedback; raise CSAT; improve
special-assistance support.

Testimonial: *"The airport assistant has become a valuable part of how we
support passengers at CVG… helped us respond more efficiently, remain
accessible, and gain deeper insights…"* — attributed to Brian Cobb, Chief
Innovation Officer, CVG Airport (also quoted on hlp.city homepage).

> ⚠️ Numbers above are vendor-published projections, not independently
> audited. Useful as scale indicator, not as RFP-grade evidence.

### What this means for 26-81

1. **A protest is not a realistic path.** HLP has documented US and UK airport
   deployments in exactly the scope 26-81 describes (QR-triggered, location-
   specific, passenger-facing AI at airports). Even a well-prepared
   equivalent-capability challenge would face steep odds.
2. **The Port's sole-source is likely defensible.** The specific combination
   of physical signage + QR + location-aware agent + accessibility/multi-
   language + airport-vertical track record is genuinely narrow — few vendors
   overlap all of it.
3. **This confirms a real, funded, growing market.** SEA is a top-tier US
   airport. If this PoC succeeds, expect a follow-on production RFP with
   larger scope (permanent installation across concourses, more languages,
   deeper integrations with Port systems). That later solicitation is our
   real target.
4. **Adjacent opportunities to watch for**, where we could compete rather
   than protest:
   - Analytics / integration layers extending HLP's data feeds into Port
     dashboards
   - Staff-side operational AI (dispatch, complaint routing, ops copilots) —
     HLP does the passenger-facing side, not the operations side
   - Back-office Microsoft Copilot deployments for Port admin functions
   - Non-airport Port of Seattle divisions (Maritime, Real Estate) where the
     same signage+agent pattern could be adapted but HLP has no visible
     footprint

## 5. Recommended decision

**Watch — do not spend proposal effort. Log for relationship-building.**

Rationale: score says "Go" on capability fit, but the sole-source structure
plus our own missing evidence base makes a protest infeasible in this window.
The competitive-intelligence findings in §4.5 **reinforce** this — the named
vendor has a genuinely qualified track record and the Port's justification is
likely sound. The strategic value is in the **signal**: SEA's Airport
Innovation / Customer Service team is actively deploying AI passenger-
experience agents. That is exactly our target market. The right play is to be
in position for the *next* one — the production RFP after the PoC, or an
adjacent operations/analytics scope — not to burn cycles on this one.

## 6. Capability gaps to close before the next similar opportunity

1. `company/past-performance/` — needs at least one written case study of a
   deployed conversational-AI / agent system, with metrics.
2. `company/capabilities.md` — needs NAICS codes (likely 541511 / 541512 /
   541990) and an explicit "AI passenger experience / airport innovation" line
   item.
3. `company/company-profile.md` — needs formal company name, DBE/WMBE
   certifications (if applicable), Port of Seattle vendor registration status.
4. `company/founder-bio.md` — needs relevant industry experience section
   suitable for direct quotation in a proposal.

## 7. Recommended next actions (for a human — the agent does not execute these)

Per `SECURITY.md`, the AI does not send email, contact external parties, or
submit anything. These are **suggestions for a human operator** to consider:

1. **Add opportunity to a watch list.** Track whether the Port issues a
   follow-on competitive RFP for a broader rollout after Hello Lamp Post's PoC
   concludes (typical outcome: PoC → production RFP 6–18 months later).
2. **Register as a Port of Seattle vendor** at
   https://hosting.portseattle.org/sops/ if not already registered — required
   to bid on future non-NOI opportunities.
3. **Optionally, and only after human review**, a courteous note to Maria
   Mayhue introducing our capability for future airport-innovation
   opportunities. **Do not frame it as a protest of 26-81.** Keep it strictly
   about future work. This is a human judgment call — not automated.

## 8. Connector gap noted (for future work)

**Our current Port of Seattle connector missed 26-81** because its OData filter
uses `DisplayFutureList eq false`, but Port flags Notice-of-Intent items with
`DisplayFutureList = true` even when `SolicitationStatus = Open`. Two options
for a follow-up ticket:

- Drop the `DisplayFutureList` clause from the list filter entirely, or
- Split into two queries (current + future) and merge results.

Not fixing in this evaluation to keep scope focused — logging as a data-source
gap.

## 9. Provenance

- Data pulled live from the Port of Seattle public OData API on 2026-07-22
  (`sopsapi/Solicitations` with `$filter=ProcurementNumber eq '26-81'`).
- No login / CAPTCHA / access control bypassed (public guest endpoint).
- Human trigger: user forwarded the VendorConnect email notification.
- Evaluation performed by the AI agent per `workflows/opportunity-review.md`;
  **treated as draft only, requires human review before any external action**.
