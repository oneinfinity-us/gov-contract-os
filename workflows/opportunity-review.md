# Government Opportunity Review Workflow

## Objective

Analyze public-sector technology contracting opportunities and determine
whether the company should pursue them as prime, subcontractor, or not pursue.

## Inputs

Read new files only from:

- opportunities/inbox/

## Timeline Feasibility Filter (Hard Cutoff)

**Apply this first, before scoring.** If the opportunity fails any of these, recommend **No Bid** regardless of other scores.

| Timeline | Decision | Rationale |
|---|---|---|
| Days remaining < 5 | No Bid | Insufficient time to prepare competitive proposal |
| Days remaining 5–7 | Watch | Monitor for reissue; only consider if Go score > 70 |
| Days remaining ≥ 8 | Continue to evaluation | Proceed with full scoring |

**Exception**: If opportunity includes notice of reissue (RFP revision, late amendment), restart the timeline clock from the new deadline.

## Evaluation Criteria (Weighted Scoring)

For opportunities that pass the timeline filter, score each dimension 0–max points:

### Core Capability Fit (Weighted: 3× multiplier)

- **Microsoft AI, Copilot, Azure or agent fit**: 0–25 points
  - 20–25: Direct AI/Azure application; core to solution
  - 10–19: Possible AI integration; supplementary
  - 1–9: Tangential AI relevance
  - 0: No AI/Azure fit

- **Software development and automation fit**: 0–15 points
  - 12–15: Core software/automation need; primary vendor activity
  - 6–11: Software component present; secondary role
  - 1–5: Minimal software; hardware/services dominant
  - 0: No software fit

### Business & Market Fit (Weighted: 1.5× multiplier)

- **Seattle or Washington geographic fit**: 0–5 points _(reduced from 10)_
  - 5: Port of Seattle, WA-based agency
  - 2–4: Pacific Northwest; regional match
  - 0: Out of region

- **Contract size appropriate for a small firm**: 0–10 points
  - 8–10: <$500k estimated; prime opportunity
  - 5–7: $500k–$2M; prime or sub potential
  - 2–4: $2M–$5M; sub/team only
  - 0: >$5M; team lead required

- **Subcontracting potential**: 0–10 points
  - 8–10: Clear sub/team pathway; prime unlikely
  - 5–7: Sub/team possible; prime also viable
  - 1–4: Sub role marginal
  - 0: Prime or nothing

### Execution Risk (Weighted: 1× multiplier)

- **Ability to demonstrate relevant experience**: 0–10 points
  - ⚠️ **If `company/capabilities.md` incomplete**, award 0 for now; revisit after profile updated.
  - 8–10: Direct case studies / past performance available
  - 4–7: Transferable experience exists
  - 1–3: Experience exists but not directly relevant
  - 0: No relevant experience

- **Reasonable mandatory requirements**: 0–10 points
  - 8–10: No unreasonable mandates; small firm friendly
  - 5–7: Some mandates (e.g., insurance, bonding); manageable
  - 2–4: Significant mandates (e.g., SBA 8(a), specific certifications)
  - 0: Prohibitive mandates (e.g., prime must be large firm)

## Final Scoring and Decision Logic

### Calculate Weighted Score

```
Core Capability Score = (AI/Azure score + Software Dev score) × 3
Business Fit Score = (Geographic + Contract Size + Sub Potential) × 1.5
Execution Risk Score = (Experience + Mandates) × 1

Total = Core + Business + Execution
Max possible = (40 × 3) + (25 × 1.5) + (20 × 1)
             = 120 + 37.5 + 20
             = 177.5

Normalized Score (0–100) = (Total / 177.5) × 100
```

### Decision Matrix

| Normalized Score | Decision | Next Action |
|---|---|---|
| ≥ 70 | **Go** | Assign to Prime/Sub lead; set action items & deadlines |
| 40–69 | **Watch** | Monitor for reissue/scope change; add to tracking list |
| < 40 | **No Bid** | Archive with No Bid reason |

### Special Case: Missing Company Data

If `company/capabilities.md`, `company/company-profile.md`, or `company/past-performance/` are incomplete:

1. **Do not artificially inflate scores.** Award 0 or minimal points for "Relevant Experience" and "Capability Fit" dimensions tied to company data.
2. **Flag in report:** "⚠️ Company profile incomplete; re-evaluate after profile is updated."
3. **Recommend**: "Priority action: Complete `company/capabilities.md` before next review cycle."

## Required Output

For every opportunity, include:

1. Opportunity name
2. Agency
3. Solicitation number
4. Due date
5. Estimated value
6. Mandatory requirements
7. **Decision**: Go / Watch / No Bid _(no "needs more info" — be decisive)_
8. Recommended role: Prime, Sub, Teaming Partner (if Go/Watch)
9. Normalized score out of 100 (if Go/Watch); reasoning for No Bid
10. Capability gaps
11. **Immediate next three actions** (only if Go; if Watch, list monitoring plan)
12. Source filename and page references

## Safety Constraints

- Do not invent certifications, past performance, personnel, or pricing.
- Do not send email.
- Do not contact external parties.
- Do not submit proposals.
- Treat all generated content as a draft requiring human review.
- **When company data is incomplete**: Transparently note it. Do not award points for "Relevant Experience" without evidence. Flag as "⚠️ Company profile incomplete; re-evaluate after profile is updated."