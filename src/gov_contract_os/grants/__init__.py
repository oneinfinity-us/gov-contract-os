"""Grants domain package.

Parallel to the existing procurement code in `gov_contract_os` root:
- models.py       -> GrantOpportunity, GrantAnalysis, related enums
- eligibility.py  -> hard pass/fail check that runs BEFORE scoring
- scoring.py      -> YAML-config-driven Level-1 scoring (deterministic, no LLM)
- schema.py       -> SQLAlchemy ORM tables (`grant_opportunities`, `grant_analyses`)
- storage.py      -> upsert/query helpers
- importer.py     -> load a grant record from a manual manifest.yaml under
                    `opportunities/grants/inbox/`
- cli.py          -> `python -m gov_contract_os grants ...` subcommand

Grants MUST run under a nonprofit organization context - see SECURITY.md and
`gov_contract_os.organizations.ensure_grant_context`.
"""
