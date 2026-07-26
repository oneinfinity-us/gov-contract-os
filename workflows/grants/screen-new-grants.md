# Workflow: screen-new-grants

## Objective

Identify grants that match a specific 501(c)(3) nonprofit's verified mission, programs, geography, populations served, and organizational capacity — and only those.

## Inputs

- `organizations/<nonprofit-slug>/organization-profile.yaml`
- `opportunities/grants/inbox/*/manifest.yaml` — any manually-imported grants
- Any grants collected in Phase 3+ (Grants.gov, WA GovDelivery, foundation stubs)
- `config/scoring/grant-scoring.yaml`

## Allowed commands

```powershell
# Import a new manual entry
py -3.12 -m gov_contract_os grants import opportunities/grants/inbox/<slug>/

# Screen everything not yet analyzed for the given nonprofit
py -3.12 -m gov_contract_os grants screen --nonprofit <slug> --new

# Or rescore everything
py -3.12 -m gov_contract_os grants screen --nonprofit <slug>

# Inspect
py -3.12 -m gov_contract_os grants list
```

## Required steps

1. Load the nonprofit profile. Refuse if `type != nonprofit`.
2. For each candidate grant, run `check_grant_eligibility` BEFORE scoring.
3. Do NOT compute a fit score for `INELIGIBLE` grants — they must not compete against eligible grants in ranked reports.
4. Score `ELIGIBLE` and `CONDITIONAL` grants using `config/scoring/grant-scoring.yaml` weights.
5. Store the `GrantAnalysis` in SQLite (`grant_analyses` table, composite key `(grant_id, nonprofit_slug)`).
6. For any grant with `requires_advanced_model=True`, queue a Level-2 LLM review (Phase 2).

## Prohibited actions

- Do NOT contact funders on behalf of the nonprofit.
- Do NOT submit applications, LOIs, or preapplications.
- Do NOT sign authorized-representative attestations.
- Do NOT create or update SAM.gov / UEI / Grants.gov registrations from this workflow.
- Do NOT expose EIN, banking information, private beneficiary data, or board-member PII to logs or reports.
- Do NOT reuse `company/` (consulting business) past performance as nonprofit past performance.
- Do NOT `git push`.

## Human review gates

- Every `GrantAnalysis` has `requires_human_review=True`. The recommendation (`Apply` / `Apply with Partner` / etc.) is an input to a human decision, not a decision itself.
- Missing information from the nonprofit profile is surfaced in `eligibility.missing_information`; the human must decide whether to fill it in or defer the grant to the next screening pass.

## Error handling

- One grant's failure (bad manifest, unparseable date, etc.) must not stop the rest of the batch — log the row and continue, per the pattern in `gov_contract_os.cli._collect_one`.
- Missing nonprofit profile is a hard stop with exit code 2, not a silent skip.
