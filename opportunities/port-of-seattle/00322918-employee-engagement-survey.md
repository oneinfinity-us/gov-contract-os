# 00322918 — Employee Engagement Survey

> Draft evaluation. Human review required before any go/no-bid decision or
> proposal drafting.

## 1. Opportunity summary

| Field | Value |
|---|---|
| Agency | Port of Seattle |
| Solicitation number | **00322918** |
| Procurement office | Central Procurement Office, 2711 Alaskan Way, Seattle, WA 98121 |
| Procurement type | Competitive RFP — one project-specific contract to be awarded |
| Category | Employee engagement survey design, administration & analytics (HR / organizational development consulting) |
| Status | Open |
| Advertised | 2026-09-03 |
| Last day to ask questions | 2026-09-18 12:00 PM PT |
| Pre-proposal presentation (optional, Teams) | 2026-09-10 1:00 PM PT |
| **Proposals due** | **2026-10-06 12:00 PM PT** |
| Days remaining (from 2026-09-08) | **28** |
| Shortlist notification | Week of 2026-11-02 |
| Interviews | 2026-11-11 – 2026-11-12 |
| Notice of selection | Week of 2026-11-16 |
| Execute agreement | Week of 2026-12-14 |
| Estimated value | **Not to exceed $300,000** for the full 6-year term |
| Period of performance | ~6 years: begins Q1 2027, concludes end of Q4 2032 |
| Procurement Officer | Will Zhou — zhou.w@portseattle.org |
| Proposal submission | Email to e-submittals-sa@portseattle.org (no hard copy / linked files) |
| Source URL | https://hosting.portseattle.org/sops/#/Solicitations/Detail/19b3f8a2-10a7-f111-bd46-005056aa9c71 |

**Scope (from Port's description, verbatim):**

> Consultant shall design and administer employee engagement surveys for
> approximately 2,600 PORT employees. Consultant will perform key driver
> predictive/prescriptive data analysis and provide interpretation and
> recommendations. Consultant will communicate results of completed employee
> engagement surveys to both eligible managers and the Executive Leadership
> Team. Additionally, the Consultant will work with PORT staff to identify
> and utilize tools for periodically checking in with the employee
> population, around engagement-related actions and initiatives. Work will
> begin early, in the first quarter of 2027 and conclude by end of the
> fourth quarter of 2032.

Survey cadence: full survey administration in Q2 2027, Q2 2029, and Q2 2031
(so results land before the Port's June budgeting cycle each survey year),
plus periodic check-ins in non-survey years, and closeout activity through
Q4 2032. Consultant is expected to host the survey and dashboard/reporting
platform themselves (Port has no existing tool). Content areas: EDI-linked
questions carried forward from the 2025 survey, ~60 rating-scale + up to 2
open-ended questions, ~7 job levels, anonymity-preserving design for both
represented (union) and non-represented staff, accessible format for
employees with visual impairments, English only (no translation required).

**Mandatory requirements found in the solicitation:**

- Active Washington UBI and L&I certification.
- Commercial General Liability insurance: $1M/occurrence, $2M aggregate.
- Auto liability, Professional Liability (E&O), and Stop-Gap Employer's
  Liability insurance are explicitly marked **not required** for this
  Agreement; no specialized insurance coverage is checked either.
- No bonding requirement identified.
- Proposal body limited to 8 pages (Section A ≤ 5 pages, Section B project
  list ≤ 3 pages), plus a 1-page Letter of Interest, Exhibit 3 (Company
  Information, Excel), Exhibit 4 (Mock Fee Schedule, Excel — pre-populated
  with Team Leader / Talent Strategy Consultant(s) / Senior Project Manager
  roles), and an Appendix of 1-page resumes.
- Diversity in Contracting: WMBE participation is **tracked/reported** via
  Exhibit 3, but no mandatory percentage goal was found in the solicitation
  text.
- All solicitation communication must go through the named Procurement
  Officer only.
- No AI-assisted-drafting disclosure/restriction clause found anywhere in
  the solicitation or Exhibit 2 terms.

## 2. Timeline feasibility filter (hard cutoff)

Days remaining (2026-09-08 → 2026-10-06) = 28 → **passes** (≥ 8). Proceed to
scoring.

## 3. Weighted score (per `workflows/opportunity-review.md`)

⚠️ **Company profile is completely unfilled.** `company/company-profile.md`,
`company/capabilities.md`, `company/founder-bio.md`, and
`company/past-performance/` are all `TODO` stubs — there is no record of
what services this company actually offers, so this scoring should be read
as provisional and revisited once those files are completed (see §6).

### Core Capability Fit (× 3 multiplier)

| Dimension | Points (0–max) | Reasoning |
|---|---|---|
| Microsoft AI / Copilot / Azure / agent fit (0–25) | **4** | This is an HR/organizational-psychology survey engagement, not an AI/Copilot/Azure product. "Key driver predictive/prescriptive data analysis" is data-science-adjacent but nothing in the scope references Azure, Copilot, or a conversational agent — tangential relevance only. |
| Software dev / automation fit (0–15) | **6** | Consultant must host a survey + dashboard platform and build an anonymized hierarchy/demographic data pipeline — a real secondary software component — but this scope of work reads like something typically delivered via an existing licensed people-analytics platform (e.g., an off-the-shelf engagement-survey tool), not ground-up custom software development. |

Subtotal: (4 + 6) × 3 = **30 / 120**

### Business & Market Fit (× 1.5 multiplier)

| Dimension | Points (0–max) | Reasoning |
|---|---|---|
| Seattle / WA geographic fit (0–5) | **5** | Port of Seattle — perfect. |
| Contract size for small firm (0–10) | **9** | $300,000 NTE spread over 6 years (~$50k/yr average) — solidly small-firm/prime scale. |
| Subcontracting potential (0–10) | **4** | Evaluation criteria emphasize a small, named, cohesive project team (Team Leader / Talent Strategy Consultant(s) / Senior PM) delivering directly; subs are permitted via Exhibit 3 but the structure reads prime-led, not built for a heavy teaming role. |

Subtotal: (5 + 9 + 4) × 1.5 = **27 / 37.5**

### Execution Risk (× 1 multiplier)

| Dimension | Points (0–max) | Reasoning |
|---|---|---|
| Demonstrable relevant experience (0–10) | **0** | ⚠️ Per workflow §"Missing Company Data": `company/past-performance/` and `company/capabilities.md` are TODO stubs, so this is scored 0 rather than assumed, regardless of whether the company may actually have relevant HR/survey experience. |
| Reasonable mandatory requirements (0–10) | **9** | Insurance burden is unusually light for a services RFP (only CGL $1M/$2M; auto, E&O, and stop-gap explicitly waived); no bonding; standard UBI/L&I registration only. Small-firm friendly. |

Subtotal: (0 + 9) × 1 = **9 / 20**

### Total

```
Total       = 30 + 27 + 9 = 66
Max         = 177.5
Normalized  = 66 / 177.5 × 100 = 37
```

**Score-only decision: 37 < 40 → "No Bid."**

## 4. Reasoning behind the recommendation

The score is driven almost entirely by two things:

1. **Core Capability Fit is the heaviest-weighted category in this firm's
   scoring rubric (120 of 177.5 max points, ~68%)**, and it is built around
   Microsoft AI/Copilot/Azure/agent and software-development fit. This
   solicitation's actual deliverable — designing and administering a
   6-year, multi-wave employee engagement survey program with predictive
   key-driver analytics for a 2,600-person unionized public-sector
   workforce — is fundamentally an **HR / organizational-psychology /
   people-analytics consulting engagement**, not an AI or software
   development engagement. Even generously scored, it cannot score high on
   this dimension.
2. **Zero demonstrable relevant experience can currently be credited**,
   because `company/past-performance/` has never been filled in. The
   workflow's "Missing Company Data" rule requires awarding 0 here rather
   than guessing.

Everything else about this opportunity is genuinely attractive for a small
Seattle-area firm: perfect geographic fit, small contract size ($300k over
6 years), an unusually light insurance/bonding burden, no restrictive
mandates, a workable 28-day proposal window, and no AI-disclosure
restriction that would complicate LLM-assisted drafting. If this company's
real specialty is HR/organizational development, employee survey research,
or people analytics — which is entirely possible but currently unknown —
this opportunity would likely score as a strong "Go" instead, since the
scope would then land squarely in its Core Capability Fit dimension. **The
recommendation below should be treated as provisional and re-run the
moment `company/capabilities.md` is filled in.**

## 5. Recommended decision

**No Bid** (score 37/100, provisional — see caveat in §4).

## 6. Capability gaps to close before re-evaluating this opportunity

1. `company/company-profile.md`, `company/capabilities.md`,
   `company/founder-bio.md` — all still `TODO`. Until these are filled in,
   no opportunity-review score in this system can be trusted for the two
   highest-weighted dimensions (Core Capability Fit) or the "demonstrable
   relevant experience" dimension.
2. If the company's actual practice includes employee engagement surveys,
   organizational psychology, people analytics, or HR consulting, that
   should be reflected explicitly in `company/capabilities.md` (with NAICS
   codes such as 541612 Human Resources Consulting Services or 541910
   Marketing Research and Public Opinion Polling) — the current rubric in
   `workflows/opportunity-review.md` has no dimension that credits this
   kind of work, which may itself be worth a human decision about whether
   the rubric needs a second scoring track for non-AI/software consulting
   opportunities.
3. `company/past-performance/` — needs at least one case study of a
   deployed employee/organizational survey program, if one exists, with
   metrics and scale (ideally involving a public-sector or unionized
   workforce of comparable size).

## 7. Recommended next actions (for a human — the agent does not execute these)

Per `SECURITY.md`, the AI does not send email, contact external parties, or
submit anything. These are **suggestions for a human operator**:

1. **Confirm whether this firm actually does employee-engagement-survey /
   HR-analytics work.** If yes, this evaluation should be manually
   overridden and re-run once `company/capabilities.md` reflects that — the
   current "No Bid" is an artifact of an AI/software-weighted rubric being
   applied to a non-AI/software opportunity, not evidence the opportunity
   itself is weak.
2. **If pursuing**: register interest with Procurement Officer Will Zhou
   (zhou.w@portseattle.org) via VendorConnect and consider attending the
   optional Sept 10, 2026 pre-proposal Teams presentation. All questions
   must go through VendorConnect by Sept 18, 2026.
3. **If not pursuing**: archive with reason "No Bid — outside current
   capability fit (HR/survey consulting, not AI/software)," and revisit
   only if the company profile changes.

## 8. Provenance

- Data provided by the human operator: the solicitation URL plus the full
  Solicitation PDF (`00322918_Solicitation_Final.pdf`, 44 pages) and Excel
  Exhibits 3 (Company Information) and 4 (Mock Fee Schedule), forwarded
  after the agent's live fetch of `hosting.portseattle.org` was blocked by
  this session's network egress policy.
- No login / CAPTCHA / access control was involved on the agent's side —
  the documents were supplied directly.
- Evaluation performed by the AI agent per `skills/opportunity-review/` and
  `workflows/opportunity-review.md`; **treated as draft only, requires
  human review before any external action.**
