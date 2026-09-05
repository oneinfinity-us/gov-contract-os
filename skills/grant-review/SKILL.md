---
name: grant-review
description: Assess whether a grant opportunity is worth applying for — first run the hard eligibility pass/fail check, then score whatever passes eligibility and produce a recommendation (Apply / Apply with Partner / Seek Fiscal Sponsor / Request Clarification / Monitor / Do Not Apply). Use when reviewing a newly discovered or manually imported NOFO/RFA.
---

# grant-review

## Input

- A `GrantOpportunity` (either manually imported via `opportunities/grants/inbox/<slug>/manifest.yaml` or fetched by a collector)
- The target nonprofit's `organizations/<slug>/organization-profile.yaml`

## Preconditions

- Only run this workflow for organizations with `type: nonprofit`. See the organization identity isolation clause in `SECURITY.md`.
- Before drafting any narrative/budget, the mission / programs / capacity files under `organizations/<slug>/` must be read first; `company/` or consulting-business past performance must not be cited.

## Steps

1. **Eligibility pass/fail** (`gov_contract_os.grants.eligibility.check_grant_eligibility`)
   - 501(c)(3) status, eligible applicant type, geographic scope, invitation-only, SAM.gov registration, deadline feasibility, cost share cap
   - A hard failure → `INELIGIBLE`, skip directly to the "archive" step, do not score
   - Missing information → `CONDITIONAL` or `UNKNOWN`, recorded under `missing_information` / `conditional_actions`
2. **Level-1 scoring** (only for `ELIGIBLE` / `CONDITIONAL`, `gov_contract_os.grants.scoring.score_grant`, config: `config/scoring/grant-scoring.yaml`)
   - 11 dimensions: mission / program / population / geography / entity / funding amount / cost / capacity / outcomes / effort / deadline
   - Weights are externalized, not hardcoded
3. **Recommendation**
   - Apply / Apply with Partner / Seek Fiscal Sponsor / Request Clarification / Monitor / Do Not Apply
   - Score ≥ 70 → `requires_advanced_model=True`, awaiting Level-2 LLM analysis
4. **Generate analysis artifacts** (starting in Phase 2)
   Written to `reports/grants/<grant-id>/`:
   - opportunity-summary.md
   - eligibility-matrix.csv
   - application-checklist.md
   - narrative-outline.md
   - budget-framework.csv
   - questions-for-funder.md
   - risk-register.md
   - decision-memo.md
5. **Human review** — all artifacts are drafts; the final decision rests with a human.

## Output

A `GrantAnalysis` (stored in the `grant_analyses` table), with:

- `eligibility.status`, `hard_failures`, `missing_information`, `conditional_actions`
- `fit_score` (`None` when ineligible), `fit_level`, `recommendation`
- `matched_criteria`, `gaps`, `next_actions`
- `requires_human_review=True` (always)

## Boundaries

- **Does not automatically decide to apply** — `recommendation` is a recommendation for a human to see.
- **Does not communicate with the funder on the nonprofit's behalf**, **does not sign on behalf of an authorized representative**, **does not automatically submit an application**.
- **Does not fabricate** organizational capacity, program outcomes, financial data, partner commitments, board members. Anything missing must be marked `[HUMAN INPUT REQUIRED]`.
- **Does not reuse** past performance from `company/` / the consulting business in grant applications.
