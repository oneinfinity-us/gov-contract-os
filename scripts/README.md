# scripts

Deterministic collection and organization scripts (e.g., fetching the public listing from the Port of Seattle procurement platform, normalizing raw solicitations and writing them into `opportunities/<agency>/`, clearing caches, etc.).

## Principles

- Only do deterministic data fetching/organizing — do not embed LLM judgment in scripts (reasoning like which opportunity is worth pursuing or how to score it belongs in `skills/opportunity-review` and `workflows/`).
- Before scraping, confirm that the platform's ToS/robots.txt permits automated access.
- Credentials (API tokens, etc.) must always be read from environment variables (see `.env.example`), never written into scripts or committed to the repository.
