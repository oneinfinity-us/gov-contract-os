# Port of Seattle Weekly Review Workflow

## Objective

Every week, scrape the Port of Seattle solicitations page, identify new
opportunities, evaluate each against company capabilities, and produce a
weekly report for human review.

## Schedule

Weekly — **Monday 06:00 UTC** (configurable via cron job; see [workflow metadata](#workflow-metadata) below).

This timing ensures:
- Fresh report early in the US work week
- Team has full 5+ days to act on "Go" opportunities
- Weekly cadence prevents decision fatigue (avoids daily/ad-hoc polling)

## Inputs

| Source | Detail |
|---|---|
| Port of Seattle solicitations | https://hosting.portseattle.org/sops/#/Solicitations |
| Previously tracked opportunities | `opportunities/port-of-seattle/` |
| Company capabilities | `company/capabilities.md` |
| Past performance | `company/past-performance/` |
| Evaluation criteria | `workflows/opportunity-review.md` |
| Security constraints | `SECURITY.md` |

## Steps

1. **Fetch** the current solicitations list from
   https://hosting.portseattle.org/sops/#/Solicitations.
2. **Diff** against `opportunities/port-of-seattle/` to find solicitations
   not yet tracked locally.
3. **Evaluate** each new solicitation using the scoring rubric defined in
   `workflows/opportunity-review.md` (0–100 across 8 dimensions).
4. **Write** one file per new opportunity to
   `opportunities/port-of-seattle/<solicitation-id>-<slug>.md`.
5. **Generate** a weekly report to
   `reports/generated/port-of-seattle-weekly-<YYYY-MM-DD>.md` using the
   template in `skills/port-of-seattle-weekly-review/SKILL.md`.

## Decision Logic

### 1. Timeline Filter (Hard Cutoff)
Apply first, before full scoring. If it fails, recommend **No Bid** immediately.

| Timeline | Decision |
|---|---|
| < 5 days remaining | **No Bid** |
| 5–7 days remaining | **Watch** (monitor for reissue; only Go if score > 70) |
| ≥ 8 days remaining | Proceed to full evaluation |

### 2. Weighted Scoring (if passes timeline filter)
See `workflows/opportunity-review.md` for full rubric. Key points:

- **Core Capability Fit** (AI/Azure + Software Dev) weighted 3×
- **Business Fit** (Geographic + Size + Sub potential) weighted 1.5×
- **Execution Risk** (Experience + Mandates) weighted 1×

**Normalized score** (0–100) determines recommendation:
- **≥ 70**: Go
- **40–69**: Watch
- **< 40**: No Bid

### 3. Handling Missing Company Data
If `company/capabilities.md`, `company/company-profile.md`, or `company/past-performance/` are incomplete:
- Award 0 for "Relevant Experience" and correlated capability scores
- Flag as "⚠️ Company profile incomplete; re-evaluate after update"
- Recommend "Priority: Complete company profile before next cycle"

## Required fields per opportunity

1. Opportunity name
2. Agency
3. Solicitation number
4. Due date
5. Estimated value
6. Mandatory requirements
7. Recommended role: Prime, Sub, Teaming Partner, or No Bid
8. Score out of 100
9. Capability gaps
10. Immediate next three actions
11. Source URL and page references

## Safety constraints

- Do not invent certifications, past performance, personnel, or pricing.
- Do not send email or contact external parties.
- Do not submit proposals.
- All generated content is a draft requiring human review before any action.
- If the solicitations page is unreachable, log the failure in the report and
  stop — do not skip silently.
