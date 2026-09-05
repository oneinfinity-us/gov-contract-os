# Opportunity Assessment Report (Manual Review)

- Process followed: `workflows/opportunity-review.md`
- Generated: 2026-07-21 (UTC)
- Input file: `opportunities/inbox/Presentation - 2026.06.17 ICT First Look.pdf` (38 pages, Port of Seattle "PortGen First Look: Information and Communication Technology Contracts", presented 2026-06-17)
- Note: This document is **informational briefing material (First Look), not a formal solicitation**. The amounts, dates, and requirements in it are all "estimates, subject to change" — official terms will be governed by the actual future solicitation documents (see the disclaimer on page 2 of the PDF). This report assesses each identifiable opportunity in the document separately.

> **Important precondition**: the company profile, capability list, and founder bio under `company/` are currently **all TODO placeholders**, and `past-performance/` has no case studies. Per `SECURITY.md` and workflow boundaries, **qualifications/past performance must not be fabricated**. Accordingly, every "capability match, provability of past performance, whether mandatory qualifications are met" item below is marked as **pending human confirmation**; scores are a **preliminary directional score** under the assumption that "the company has general software/AI/Azure delivery capability" — final scores should be recalculated once `company/` is filled in with real information.

---

## Summary Table

| # | Opportunity | Type | Estimated value | WMBE goal | Expected release | Recommended role | Preliminary score |
|---|---|---|---|---|---|---|---|
| 1 | AI Consulting Services IDIQ | IDIQ | $400K–$500K | TBD | Q3 2026 | Prime / Sub (TBD) | 72 |
| 2 | Azure Consulting Services IDIQ | IDIQ | $1.8M | TBD | Q3 2026 | Sub / Teaming | 70 |
| 3 | Technology Services IDIQ (staff augmentation) | IDIQ | $4.5M–$5M | TBD | Q4 2026 | Sub / Teaming | 63 |
| 4 | HubSpot Consulting Services IDIQ | IDIQ | NTE $500K | No Goal | 6–7/2026 (soonest) | Sub / Teaming | 55 |
| 5 | PeopleSoft Technical Services | Project/IDIQ | NTE $1.9M | 6% | 7/2026 (soon) | No Bid / Sub | 40 |
| 6 | Virtualization Consulting IDIQ | IDIQ | $150K–$200K | TBD | Q1 2027 | Sub / No Bid | 42 |
| 7 | Property Management System Refresh | Procurement | $800K–$1.2M | N/A | Q3 2026 | No Bid | 25 |
| 8 | Fire Alarm Monitoring System Refresh | Procurement | $250K–$350K | N/A | Q2 2027 | No Bid | 12 |

Priority recommendation: **#1 AI IDIQ and #2 Azure IDIQ are the primary targets** (they hit the highest-weighted Microsoft AI/Azure category, and are releasing in Q3 2026, the tightest timeline).

---

## 1. AI Consulting Services IDIQ

1. **Opportunity name**: AI Consulting Services IDIQ
2. **Agency**: Port of Seattle — ICT Department
3. **Solicitation number**: Not yet published (First Look stage, not formally advertised)
4. **Due date**: Not yet set; expected release Q3 2026, typically ~2 weeks after advertisement for a pre-bid conference, ~30 days to submit (inferred from the HubSpot/PeopleSoft timeline in the PDF)
5. **Estimated value**: $400K–$500K
6. **Mandatory requirements**: Not listed in the document; WMBE goal TBD. → **Pending human confirmation** (check once the formal RFP is released)
7. **Recommended role**: Prime or Sub — **TBD** (depends on the company's AI delivery track record and capacity, once `company/` is filled in)
8. **Score**: **72 / 100**
   - MS AI/Copilot/Azure/agent fit: **25/25** (exactly matches Port's need for AI adoption and implementation consulting)
   - Software development/automation fit: 12/15
   - Seattle/WA geographic fit: 10/10
   - Contract size fit for small business: 10/10 ($400–500K, IDIQ is small-business friendly)
   - Subcontracting potential: 8/10
   - Provable relevant experience: **?/10 → pending confirmation** (counted as 0 for now, no data in `company/`)
   - Mandatory requirement reasonableness: 7/10 (unknown, neutral for now)
   - Timeline feasibility: **pending confirmation** (Q3 2026, one of the tightest) → counted as 0 for now
9. **Capability gaps**: need to confirm whether the company has citable AI consulting/implementation case studies, and whether it holds any WMBE/SBE certification (Port's five-year goal is 16% WMBE; certification is a plus/threshold).
10. **Next three steps**:
    1. Register on **VendorConnect** and join the Diversity in Contracting mailing list to ensure notification when this IDIQ is formally advertised (PDF page 5).
    2. Fill in AI-related capabilities and case studies in `company/capabilities.md` + `past-performance/`, and assess whether to position as Prime or Sub.
    3. Follow up with Harold Federow (Contract & Compliance Advisor, ICT, Federow.h@portseattle.org) to confirm this IDIQ's timeline and certification requirements — **requires human review before sending**.
11. **Source**: `Presentation - 2026.06.17 ICT First Look.pdf` page 28 ("Future Consulting Opportunity — AI Consulting Services IDIQ")

---

## 2. Azure Consulting Services IDIQ

1. **Opportunity name**: Azure Consulting Services IDIQ
2. **Agency**: Port of Seattle — ICT Department
3. **Solicitation number**: Not yet published (First Look stage)
4. **Due date**: Not yet set; expected release Q3 2026
5. **Estimated value**: $1.8M
6. **Mandatory requirements**: Not listed in the document; likely requires Azure/cloud architecture, security, and resilience-related qualifications and track record. → **Pending human confirmation**
7. **Recommended role**: Sub / Teaming Partner ($1.8M is fairly large — if the company is small, recommend subcontracting or teaming; PDF page 34 explicitly notes Microsoft certification helps for IT contracts)
8. **Score**: **70 / 100**
   - MS AI/Copilot/Azure/agent fit: **25/25** (pure Azure cloud adoption/modernization/optimization)
   - Software development/automation fit: 10/15
   - Seattle/WA geographic fit: 10/10
   - Contract size fit for small business: 6/10 ($1.8M is on the large side — capacity risk for an independent Prime)
   - Subcontracting potential: 9/10
   - Provable relevant experience: **?/10 → pending confirmation** (counted as 0 for now)
   - Mandatory requirement reasonableness: 7/10 (unknown, neutral for now)
   - Timeline feasibility: **pending confirmation** (Q3 2026) → counted as 0 for now
9. **Capability gaps**: citable track record in Azure architecture assessment/security posture/resilience; whether the company holds a Microsoft partner certification (Azure); capacity and bonding ability for a small business to independently take on $1.8M.
10. **Next three steps**:
    1. VendorConnect registration + mailing list (same as #1 — one registration covers all Port opportunities).
    2. Assess a teaming strategy: find an Azure partner who can serve as Prime, with the company entering as a specialty subcontractor (build out `contacts/contacts.csv`).
    3. Inventory/confirm the company's Azure certifications and case studies, and write them into `company/` and `past-performance/`.
11. **Source**: `Presentation - 2026.06.17 ICT First Look.pdf` page 29

---

## 3. Technology Services IDIQ (Staff Augmentation)

1. **Opportunity name**: Technology Services IDIQ (Staff Augmentation: development, PM, QA, etc.)
2. **Agency**: Port of Seattle — ICT Department
3. **Solicitation number**: Not yet published
4. **Due date**: Not yet set; expected release Q4 2026
5. **Estimated value**: $4.5M–$5M
6. **Mandatory requirements**: Not listed; scope is extremely broad (task-order based). → **Pending human confirmation**
7. **Recommended role**: Sub / Teaming Partner (large total value, suited to entering via a staffing subcontract)
8. **Score**: **63 / 100**
   - MS AI/Azure fit: 12/25 (broad scope, not AI-specific, but could include it)
   - Software development/automation fit: 13/15 (dev/QA/PM augmentation is exactly software delivery)
   - Geographic fit: 10/10
   - Contract size fit for small business: 5/10 ($4.5–5M is large, but as an IDIQ with task orders, small entries are possible)
   - Subcontracting potential: 9/10
   - Provable relevant experience: **pending confirmation** → counted as 0 for now
   - Mandatory requirement reasonableness: 7/10
   - Timeline feasibility: **pending confirmation** (Q4 2026, fairly comfortable) → counted as 0 for now
9. **Capability gaps**: deployable dev/QA/PM capacity and staff résumé pool; past staff-augmentation-type track record.
10. **Next three steps**:
    1. VendorConnect registration + mailing list.
    2. Build a capability matrix of deployable staff/subcontractors (skills, availability, rates).
    3. Lock in 1–2 Prime teaming partners before Q4.
11. **Source**: `Presentation - 2026.06.17 ICT First Look.pdf` page 30

---

## 4. HubSpot Consulting Services IDIQ

1. **Opportunity name**: HubSpot Consulting Services IDIQ
2. **Agency**: Port of Seattle — ICT Department
3. **Solicitation number**: Not yet published
4. **Due date**: Not yet set; PDF page 20 timeline: advertised 6–7/2026, pre-bid conference ~2 weeks after advertisement, ~30 days to submit → **one of the soonest opportunities, tight timeline**
5. **Estimated value**: Not to Exceed $500K
6. **Mandatory requirements**: Category=Consulting Services; WMBE Goal=**No Goal**; Certifications=**TBD**; scope includes HubSpot requirements gathering, data model/process design, custom development and integration, automated workflows, training, system support, project management. → requires HubSpot platform expertise
7. **Recommended role**: Sub / Teaming Partner (unless the company has HubSpot expertise, teaming is the primary path; PDF page 34 lists HubSpot as a WMBE participation opportunity)
8. **Score**: **55 / 100**
   - MS AI/Azure fit: 3/25 (HubSpot is not a Microsoft-stack product, only weakly related)
   - Software development/automation fit: 13/15 (custom development, integration, automated workflows are a strong fit)
   - Geographic fit: 10/10
   - Contract size fit for small business: 10/10 (NTE $500K, IDIQ)
   - Subcontracting potential: 8/10
   - Provable relevant experience: **pending confirmation** → counted as 0 for now
   - Mandatory requirement reasonableness: 8/10 (no WMBE goal, relatively low threshold)
   - Timeline feasibility: 3/10 (earliest release, shortest window — insufficient prep time if there's no existing HubSpot capability now)
9. **Capability gaps**: dedicated experience and citable case studies in HubSpot platform implementation/development; whether HubSpot certification is required (TBD).
10. **Next three steps**:
    1. **Immediately** register on VendorConnect (this is the fastest-releasing item, don't miss the advertisement).
    2. Assess whether the company has hands-on HubSpot capability/certification — if not, decide between No Bid or quickly finding a HubSpot subcontracting partner.
    3. Watch for the advertisement, become a Plan Holder promptly, and attend the pre-bid conference.
11. **Source**: `Presentation - 2026.06.17 ICT First Look.pdf` pages 18–20

---

## 5. PeopleSoft Technical Services

1. **Opportunity name**: PeopleSoft Technical Services (supporting PeopleSoft HCM/Financials 9.2 and Oracle Taleo)
2. **Agency**: Port of Seattle — ICT Department
3. **Solicitation number**: Not yet published
4. **Due date**: Not yet set; PDF page 25: advertised 7/2026, pre-bid conference ~2 weeks after advertisement, ~30 days to submit → **imminent**
5. **Estimated value**: Not to Exceed $1.9M
6. **Mandatory requirements**: **Certification: Oracle at vendor level**; WMBE Goal 6%; requires PeopleSoft development/administration/functional analysis/PM roles; assessment relies on deep PeopleSoft technical capability (SQR, App Engine, PeopleCode, Integration Broker, Fluid, AWE, etc.). → high, specialized threshold
7. **Recommended role**: **No Bid** (unless the company happens to have PeopleSoft/Oracle expertise) / otherwise Sub
8. **Score**: **40 / 100**
   - MS AI/Azure fit: 0/25 (Oracle PeopleSoft ecosystem, unrelated to the Microsoft stack)
   - Software development/automation fit: 8/15 (it is development work, but a PeopleSoft-specific skill)
   - Geographic fit: 10/10
   - Contract size fit for small business: 6/10 (NTE $1.9M)
   - Subcontracting potential: 6/10
   - Provable relevant experience: **pending confirmation** → counted as 0 for now
   - Mandatory requirement reasonableness: **2/10** (vendor-level Oracle certification is a hard threshold small businesses usually don't meet)
   - Timeline feasibility: **pending confirmation** (imminent, 7/2026) → counted as 0 for now (not realistically feasible without an existing PeopleSoft team)
9. **Capability gaps**: vendor-level Oracle certification, a PeopleSoft/Taleo specialist consulting team and track record — this is a clear hard threshold.
10. **Next three steps**:
    1. Confirm whether the company holds vendor-level Oracle certification and a PeopleSoft team — **if not met, clearly No Bid**.
    2. If not bidding, consider offering peripheral capability (e.g., PM) as a subcontractor to a qualified Prime.
    3. Record the decision to avoid re-assessing this repeatedly later.
11. **Source**: `Presentation - 2026.06.17 ICT First Look.pdf` pages 22–25

---

## 6. Virtualization Consulting IDIQ

1. **Opportunity name**: Virtualization Consulting IDIQ (virtualization platform assessment/optimization roadmap)
2. **Agency**: Port of Seattle — ICT Department
3. **Solicitation number**: Not yet published
4. **Due date**: Not yet set; expected release Q1 2027 (further out)
5. **Estimated value**: $150K–$200K
6. **Mandatory requirements**: Not listed; requires virtualization platform (health/performance/security/architecture) assessment capability. → **Pending human confirmation**
7. **Recommended role**: Sub / No Bid (depends on whether the company has virtualization/infrastructure expertise)
8. **Score**: **42 / 100**
   - MS AI/Azure fit: 5/25 (may touch Hyper-V/Azure, but the core is virtualization platform assessment)
   - Software development/automation fit: 4/15
   - Geographic fit: 10/10
   - Contract size fit for small business: 10/10 ($150–200K, small and friendly)
   - Subcontracting potential: 6/10
   - Provable relevant experience: **pending confirmation** → 0
   - Mandatory requirement reasonableness: 7/10
   - Timeline feasibility: **pending confirmation** (Q1 2027, plenty of time) → 0
9. **Capability gaps**: specialized experience in virtualization platform (VMware/Hyper-V, etc.) assessment and security posture.
10. **Next three steps**:
    1. Archive for observation, no urgent action needed before Q1 2027.
    2. Reassess if the company develops infrastructure/virtualization capability.
    3. Already covered by the VendorConnect mailing list notification.
11. **Source**: `Presentation - 2026.06.17 ICT First Look.pdf` page 31

---

## 7. Property Management System Refresh (Procurement)

1. **Opportunity name**: Property Management System Refresh
2. **Agency**: Port of Seattle
3. **Solicitation number**: Not yet published
4. **Due date**: Not yet set; expected release Q3 2026
5. **Estimated value**: $800K–$1.2M
6. **Mandatory requirements**: Not listed; this is fundamentally a **property management system (software product) procurement**, not a consulting/development service. → requires an off-the-shelf PMS solution
7. **Recommended role**: **No Bid** (unless the company is a PMS product vendor/reseller)
8. **Score**: **25 / 100**
   - MS AI/Azure: 2/25; development/automation: 2/15; geographic: 10/10; size: 6/10; subcontracting: 3/10; track record: 0; requirement reasonableness: 2/10 (requires a product); timeline: 0
9. **Capability gaps**: requires an off-the-shelf property management system product and implementation capability — does not fit the company's AI/software consulting positioning.
10. **Next three steps**: (1) Mark No Bid; (2) if there's a partnering PMS vendor, consider a referral/teaming arrangement; (3) archive.
11. **Source**: `Presentation - 2026.06.17 ICT First Look.pdf` page 32

---

## 8. Fire Alarm Monitoring System Refresh (Procurement)

1. **Opportunity name**: Fire Alarm Monitoring System Refresh (replacement of the SEA airport fire alarm monitoring system)
2. **Agency**: Port of Seattle
3. **Solicitation number**: Not yet published
4. **Due date**: Not yet set; expected release Q2 2027
5. **Estimated value**: $250K–$350K
6. **Mandatory requirements**: Not listed; this is specialized **fire/building safety systems** engineering, requiring related industry qualifications. → unrelated to the company's IT/AI positioning
7. **Recommended role**: **No Bid**
8. **Score**: **12 / 100** (barely fits any scoring dimension: AI/Azure 0, development 0, geographic 10, everything else low)
9. **Capability gaps**: fire alarm system integration qualifications and track record — outside the company's business scope.
10. **Next three steps**: (1) Mark No Bid; (2) no action needed; (3) archive.
11. **Source**: `Presentation - 2026.06.17 ICT First Look.pdf` page 33

---

## Cross-Opportunity Notes and Human Confirmation Checklist

**AI-assisted disclosure check (per SECURITY.md step 4)**: this input is briefing material and contains no solicitation terms, so it **cannot be confirmed** whether any of these IDIQs will have AI-assisted bid drafting disclosure/restriction requirements. → **must be checked individually against each one's RFP once formally released.**

**Items requiring human confirmation:**
1. The three `company/` files (profile, capabilities, founder bio) and the `past-performance/` case studies — until filled in, all "provability of past performance/timeline feasibility" items are counted as 0, which will noticeably depress scores; recalculate once filled in.
2. Whether the company holds any **WMBE / SBE / DBE** certification (Port's five-year goal is 16% WMBE; most opportunities have a WMBE goal or treat it as a plus).
3. For #5: whether the company holds **vendor-level Oracle certification** (hard threshold).
4. For #4: whether the company has hands-on **HubSpot** capability/certification (earliest release, shortest window).
5. For #1/#2: whether the company holds a **Microsoft partner certification (Azure)** and citable AI/Azure case studies.
6. The VendorConnect platform entry URL / whether there is an official API (for automating future opportunity collection; ToS/robots must be checked before scraping, see SECURITY.md).

**Common first step (covers all opportunities)**: register on Port of Seattle **VendorConnect** and subscribe to the Diversity in Contracting mailing list to get notified as soon as formal advertisements are released.

**Key contacts (from the PDF)**:
- Harold Federow — Contract & Compliance Advisor, ICT — Federow.h@portseattle.org
- Kelvin Dankwa — Community Engagement & Training Program Specialist — dankwa.k@portseattle.org

> Everything above is a **draft requiring human review**. No email was sent, no external party was contacted, no proposal was submitted, no input file was modified, and no `git push` was executed.
