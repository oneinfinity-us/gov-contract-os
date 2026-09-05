# gov-contract-os

Government/municipal procurement opportunity automation system: discover opportunities → assess whether they're worth bidding on → draft proposals (human review) → track status → daily opportunity digest.

## Safety Statement

- **Does not auto-submit government proposals**, **does not send outbound email automatically**, **does not bypass login/CAPTCHA/access control/rate limits/paywalls**.
- Only uses publicly available government procurement information; does not download unrelated attachments; only processes publicly accessible solicitation information.
- Real API keys are not committed to the Git repository (see `.env.example`). Any content going out officially must be approved by a human first.
- See [SECURITY.md](SECURITY.md) for the full boundaries; see [CLAUDE.md](CLAUDE.md) for overall repo conventions.

## Current Status (Round 1 MVP)

The Python skeleton has been implemented: data models, SQLite storage, a unified connector interface, scorer, CLI, and tests.
**Port of Seattle** (public OData API) and **City of Seattle** (official RSS feed) are the two sources that can
currently be scraped for real; the other three target agencies (Washington State / King County / City of Bellevue)
currently only have placeholder connectors — `health_check()` explicitly reports the reason it isn't implemented and
the alternative (see "Supported Sources" / "Not Yet Supported Sources" below).

## Installation

Requires Python 3.12+.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Configuration

```powershell
cp .env.example .env
# Fill in ANTHROPIC_API_KEY / OPENCLAW_GATEWAY_TOKEN as needed (this round does not yet actually call any paid AI API)
```

The SQLite database is written to `runtime/gov_contract_os.sqlite3` by default (already excluded via `.gitignore`, not committed).

## CLI Commands

```powershell
# Collect from all sources (unimplemented sources are skipped with a printed reason, without affecting other sources)
python -m gov_contract_os collect --all

# Collect from a single source
python -m gov_contract_os collect --source port_of_seattle
python -m gov_contract_os collect --source city_of_seattle

# Run Level-1 deterministic scoring on opportunities that haven't been scored yet
python -m gov_contract_os analyze --new

# Generate the daily opportunity digest into reports/generated/
python -m gov_contract_os report daily

# Export all opportunities as JSON/CSV
python -m gov_contract_os export --output-dir runtime/export

# The following two commands are placeholders only in this round (they print "not implemented" and exit with a non-zero code)
python -m gov_contract_os rfp analyze opportunities/inbox/example.pdf
python -m gov_contract_os demo
```

## Tests

```powershell
python -m pytest
```

All tests run offline: connector tests use `respx` to mock HTTP responses (`tests/fixtures/`) and do not access real government websites.

## How to Start the Demo

Not yet implemented (Streamlit or FastAPI is planned; see the "Not Yet Implemented" section of `docs/architecture.md`).

## How OpenClaw Runs

OpenClaw should only invoke the deterministic CLI commands listed above; for behavioral boundaries (push/sending email/submitting proposals/deleting source files, etc. are not allowed),
see [SECURITY.md](SECURITY.md) and `workflows/`. For detailed integration instructions see `docs/openclaw-integration.md`
(a placeholder, to be filled in in a later round).

## Supported Sources

| Source | Status | Method |
|---|---|---|
| Port of Seattle | ✅ Working | VendorConnect public OData API (guest, no login required) |
| City of Seattle | ✅ Working | Official public RSS feed (`thebuyline.seattle.gov`), see `docs/data-sources.md` for details |

## Not Yet Supported Sources and Reasons

| Source | Status | Reason | Known Leads |
|---|---|---|---|
| Washington State | Not implemented | Have not yet researched/verified whether WEBS offers a public API/RSS/export | Need to research des.wa.gov |
| King County | Not implemented | Have not yet researched/verified its procurement platform | To be researched |
| City of Bellevue | Not implemented | Have not yet researched/verified its procurement platform | To be researched |

Manual fallback process for unimplemented sources: download the public RFP/RFQ PDF and place it in `opportunities/inbox/`;
the `rfp analyze` command (not yet implemented) will later be used to analyze it.

See [docs/data-sources.md](docs/data-sources.md) and [docs/architecture.md](docs/architecture.md) for more detail.
