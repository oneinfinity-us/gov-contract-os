# Nonprofit organization profile

Machine-readable profile for a 501(c)(3) nonprofit the system is helping to pursue grants for. Every grant eligibility check and scoring pass reads from `organization-profile.yaml` in this directory.

## Setup

1. Copy the example:

   ```powershell
   Copy-Item organization-profile.example.yaml organization-profile.yaml
   ```

2. Fill in what you can verify against the nonprofit's actual records. Leave anything you cannot verify as `null` — the eligibility checker treats `null` as "missing information" rather than a silent pass or fail.

3. Add human-authored context files alongside (see [Optional files](#optional-files) below).

## Rules (see [SECURITY.md](../../SECURITY.md))

- **Never commit** real EIN, banking information, board-member PII, donor lists, or private beneficiary data. The profile uses `has_...` booleans so the schema can attest "we have this on file elsewhere" without storing the sensitive value.
- **Do not** reuse the consulting business's (`../consulting-business/`) past performance, certifications, or client references in grant applications. Enforced by `gov_contract_os.organizations.ensure_grant_context`.
- **Do not** auto-submit applications, sign authorized-representative attestations, or contact funders on behalf of the nonprofit.

## Optional files

Recommended human-authored context files that Phase 2 LLM analysis will read:

- `mission.md` — mission statement, theory of change, program areas
- `programs/<program-slug>.md` — one file per active program with participant counts, outcomes, references
- `impact/YYYY-annual-report.md` — annual impact narratives
- `financials/README.md` — pointer to where audited statements live (NOT the statements themselves in-repo)
- `governance/README.md` — pointer to board list, bylaws, conflict-of-interest policy
- `attachments/README.md` — inventory of what's on-hand (501(c)(3) letter, W-9, insurance certs, etc.)
