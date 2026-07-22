# Port of Seattle Weekly Review Workflow

## Objective

Every week, scrape the Port of Seattle solicitations page, identify new
opportunities, evaluate each against company capabilities, and produce a
weekly report for human review.

## Schedule

Weekly — recommended day: **Monday morning**, so the team can act on new
opportunities early in the week.

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

## Evaluation scoring (from opportunity-review workflow)

| Dimension | Points |
|---|---|
| Microsoft AI / Copilot / Azure / agent fit | 25 |
| Software development and automation fit | 15 |
| Seattle or Washington geographic fit | 10 |
| Contract size appropriate for a small firm | 10 |
| Subcontracting potential | 10 |
| Ability to demonstrate relevant experience | 10 |
| Reasonable mandatory requirements | 10 |
| Timeline feasibility | 10 |

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
