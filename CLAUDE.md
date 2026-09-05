# gov-contract-os

Government/municipal procurement opportunity + nonprofit grant opportunity automation system. Goal: discover opportunities → assess whether they're worth bidding on/applying for → draft proposals/applications (LLM-assisted, human review) → track status → periodically generate an opportunity digest.

Current scope:
- **Procurement (contracts) track**: Port of Seattle pilot is running; WA State / King County / City of Seattle / City of Bellevue to be added later. Product name: "Government Contract Opportunity Copilot".
- **Grants track** (Phase 1 complete, 2026-07): nonprofit grant opportunities — manual PDF import loop + hard eligibility pass/fail + Level-1 scoring + organization identity isolation guard. Grants.gov API / WA GovDelivery grant triage is Phase 3.

Before doing anything, read `SECURITY.md` first — the boundaries in it (do not auto-submit proposals/applications, do not send outbound email automatically, do not store employer/client confidential information, organization identity isolation, etc.) have no exceptions.

## Directory Conventions

| Directory | Purpose |
|---|---|
| `company/` | Human-readable materials for the consulting company: profile, founder bios, capability list, past performance. Must be read before drafting a procurement proposal — never fabricate qualifications or past performance. **Must not be used for grant applications**. |
| `organizations/` | Organization identity manifests (YAML). `consulting-business/` corresponds to the content in `company/`; `nonprofit/` is the 501(c)(3) nonprofit. The CLI's `--nonprofit/--organization` flag reads from here. |
| `opportunities/<agency>/` | Procurement opportunities. One folder per agency. |
| `opportunities/grants/inbox/<slug>/` | Manually submitted grant announcements — one folder per grant, containing `manifest.yaml` + the original PDF. |
| `opportunities/grants/archive/` | Archived grants (closed / awarded / do_not_apply). |
| `contacts/contacts.csv` | Procurement agency contacts. Contains PII — see `SECURITY.md` for handling. |
| `proposals/` | Draft procurement bid proposals. Requires human review before submission. |
| `templates/grants/` | Grant application section templates (LOI, statement of need, budget narrative, etc.). Real content provided starting in Phase 2. |
| `reports/` | Daily procurement opportunity digest. |
| `reports/grants/<grant-id>/` | Analysis artifacts for each grant (eligibility matrix, decision memo, etc.). Auto-generated starting in Phase 2. |
| `config/scoring/*.yaml` | Scoring weight configuration (externalized, not hardcoded). |
| `scripts/` | Deterministic collection/organization scripts; no embedded LLM judgment. |
| `skills/opportunity-review/` | Procurement opportunity analysis workflow. |
| `skills/grant-review/` | Grant opportunity analysis workflow (eligibility → scoring → recommendation). |
| `workflows/` | OpenClaw execution instructions. |

## Working Rules

- Procurement opportunity assessment follows `skills/opportunity-review/`; grant opportunity assessment follows `skills/grant-review/`.
- Read `company/` before drafting a procurement proposal; read `organizations/<nonprofit-slug>/` before drafting a grant application. **Never cross-use them**.
- Mark uncertain qualifications/past performance/project results as `[HUMAN INPUT REQUIRED]` — do not make them up.
- Grant analysis must run the hard eligibility pass/fail check first; anything marked `INELIGIBLE` does not participate in scoring/ranking.
- Code in `scripts/` must stay deterministic and reviewable — reasoning like "is this worth bidding on" or "how should this be scored" belongs in skills/workflows/scoring config, not buried in scripts.
- Follow `SECURITY.md` whenever `contacts/contacts.csv`, nonprofit EIN/banking/board PII, or non-public client/agency information is involved.
- Anything intended to be sent/submitted externally (email, procurement proposal submission, grant application submission, SAM.gov/UEI registration updates) always goes to a human for review first — never auto-executed.

## Grant Phase Roadmap

- **Phase 1 (complete)**: domain model, eligibility checker, Level-1 scoring, YAML weights, manual import, CLI (`grants import` / `grants screen` / `grants list`), organization identity isolation, tests.
- **Phase 2**: manual grant PDF → LLM field extraction into manifest, full analysis artifacts (8 markdown/csv files), grant-review LLM Level-2.
- **Phase 3**: Grants.gov Search2 API connector + reuse the existing GovDelivery connector to parse and triage WA state grant emails.
- **Phase 4**: Grant application workspace (LOI / narrative / budget drafting + budget validation).
- **Phase 5**: Foundation / corporate CSR connectors (mostly stubs only, routed to manual inbox).
