# Architecture Overview

## Layered Design

```
models/       Pydantic data models (Opportunity, Analysis) - the single data contract for the whole system
storage/      SQLAlchemy ORM + SQLite, deduplicating upsert keyed on Opportunity.id
collectors/   One connector per procurement agency, implementing the unified Connector abstract interface
normalizers/  Cleaning/normalization helper functions for fields like agency name/date/amount
scoring/      Level-1 deterministic keyword scoring rules + scoring entry point
reports/      Daily opportunity digest generation (Markdown)
cli.py        Typer CLI, wiring together the layers above
```

Dependency direction: `collectors` produce `Opportunity` (using `normalizers`) → `storage` persists it
→ `scoring` reads unscored opportunities and produces `Analysis` → `storage` persists it → `reports` aggregates and generates the digest.
`cli.py` is the only orchestration layer — OpenClaw should only invoke CLI commands, not import internal modules directly.

## Deduplication Strategy

`Opportunity.build_id()` is the source of the primary key:

1. Prefer `f"{normalize_agency_name(source_agency)}::{solicitation_number}"`.
2. If there is no solicitation number, fall back to `f"{agency}::{source_url}::{normalized_title}::{due_at_iso}"`.
3. Take the first 32 hex characters of the `sha256` of the above string as the `id`.

When the same opportunity is scraped multiple times, its `id` stays the same, so `storage.db.upsert_opportunity`
updates it in place rather than inserting a duplicate.
A `content_hash` (a hash of title/description/status/due date/amount) is also maintained, for future use in
detecting "whether the content has substantively changed" — change-notification logic is not wired up in this round.

## Two-Level Scoring (Level 1 implemented, Level 2 not implemented)

- **Level 1 (implemented this round)**: `scoring/rules.py` + `scoring/scorer.py`, pure keyword/rule-based scoring,
  0-100 points, across 5 categories of capability keywords (AI/Agent/Copilot/Azure weighted highest at 25 points) +
  small-company size fit + mandatory-requirement match (currently a constant 50%, since Level 1 cannot actually
  parse mandatory requirement clauses) + timeline feasibility.
  Deterministic, unit-testable, and does not call any external API.
- **Level 2 (not implemented)**: planned to have an LLM read the full opportunity text, combine it with the
  `company/` directory to judge real fit, and extract `capability_gaps`/`mandatory_requirement_risks`, only calling
  the LLM for opportunities with `requires_advanced_model=True` (i.e., Level 1 score ≥ 75) to control paid API cost.
  The `requires_advanced_model` field is already computed and written into `Analysis` this round, but no code
  actually calls a paid model yet.

`Analysis.requires_human_review` is always `True` — no output from this system may be treated as a basis for an automated decision.

## Unified Connector Interface

`collectors/base.py` defines the `Connector` abstract base class: `discover()` / `fetch_details()` /
`fetch_documents()` / `health_check()`. Any failure to scrape a given source must be reported through
`ConnectorHealth` (status + reason + alternative + manual-inbox hint), and must not raise an unhandled exception
that interrupts scraping of other sources (`cli.py`'s `collect --all` wraps each source in its own try/except).

Implemented:
- `PortOfSeattleConnector`: calls the public OData API.
- `CityOfSeattleConnector`: parses the official public RSS feed (see `docs/data-sources.md`).
- The other 3 (Washington State / King County / City of Bellevue) are all stubs:
  `discover()` simply `raise NotImplementedError`, and `health_check()` returns a
  `NOT_IMPLEMENTED` status along with research leads/manual alternatives.

## Implemented Features

- Data models (`Opportunity`/`Analysis`) + deduplication/content hashing
- SQLite storage + upsert semantics
- Unified connector interface + 2 real connectors (Port of Seattle, City of Seattle) + 3 honest stubs
- Field normalization (agency name/date/amount)
- Level-1 deterministic scoring
- Daily Markdown report generation
- CLI: `collect` / `analyze --new` / `report daily` / `export`
- Unit tests (61, covering models/normalization/scoring/storage/connectors/CLI), all running offline
- Passes ruff lint + format

## Not Yet Implemented (left for the next round)

- Level-2 LLM analysis (actually calling the Anthropic API)
- Full RFP text parsing and a compliance matrix (`rfp analyze` currently just prints "not implemented" and exits with code 2)
- Proposal drafting assistance
- Demo (Streamlit/FastAPI) — the `demo` command is currently just a placeholder
- Real connectors for Washington State / King County / City of Bellevue (none have candidate leads yet,
  see `docs/data-sources.md`)
- Concrete scheduling scripts/configuration for OpenClaw integration (`workflows/` already has a described process, but it has not been verified as actually executable)
- Change-detection notifications (leveraging the existing `content_hash` field)
