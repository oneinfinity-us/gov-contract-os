# Consulting business organization

The consulting-business identity — used by the government-procurement (contracts) flow.

Human-authored content for this entity lives in [`../../company/`](../../company/) (profile, capabilities, past performance). This directory holds only the machine-readable `organization-profile.yaml` manifest used by the CLI's `--organization` flag.

## Setup

Copy the example and fill in real values locally (the live file is gitignored):

```powershell
Copy-Item organization-profile.example.yaml organization-profile.yaml
```

## Rules

- **Grants MUST NOT be pursued under this organization context.** See [SECURITY.md](../../SECURITY.md) and `gov_contract_os.organizations.ensure_grant_context`. The consulting business's past performance, staff, insurance, and certifications are not eligible substitutes for a nonprofit applicant's own.
- To add or edit capabilities/past-performance, edit files under [`../../company/`](../../company/) — this directory only holds the identity manifest.
