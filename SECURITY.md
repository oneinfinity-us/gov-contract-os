# Security Boundaries

- Do not store Microsoft internal source code.
- Do not store employer confidential information.
- Do not store customer data.
- Do not store API keys in Git.
- Do not automatically send external email.
- Do not automatically submit government proposals.
- All public-facing content requires human approval.

## Scraping & data sourcing

- Before automating collection from any procurement platform (Port of Seattle, and later WA State/King County/Seattle/Bellevue), confirm the platform's Terms of Service / robots.txt permit automated access. Prefer an official API/open-data feed over scraping when one exists.
- Respect rate limits; do not hammer a platform with retries.

## AI-assisted proposal drafting

- Some solicitations require disclosure of AI-assisted content, or restrict how much of a proposal may be AI-generated. Check the specific RFP/RFQ terms in `opportunities/<agency>/` before drafting.
- LLM output in `proposals/` is a draft only. Pricing, certifications/qualification claims, and legal terms must be verified by a human before submission (see "Do not automatically submit government proposals" above).

## Contacts & PII

- `contacts/contacts.csv` may contain personal contact information for agency staff. Treat it as sensitive — do not paste its contents into external tools/services beyond what's needed for this project.
