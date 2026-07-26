# Security Boundaries

- Do not store Microsoft internal source code.
- Do not store employer confidential information.
- Do not store customer data.
- Do not store API keys in Git.
- Do not automatically send external email.
- Do not automatically submit government proposals.
- Do not automatically submit grant applications, letters of inquiry, or preapplications.
- All public-facing content requires human approval.

## Organization identity isolation

The system may act on behalf of MORE THAN ONE legal entity (a consulting business AND a 501(c)(3) nonprofit). These identities MUST NOT be mixed:

- Grant operations only run under a nonprofit organization context. Enforced by `gov_contract_os.organizations.ensure_grant_context` — the CLI raises `InvalidOrganizationContextError` if a grant command is invoked with a consulting-business slug.
- Never reuse consulting-business past performance, staff bios, client references, insurance certificates, or certifications as if they were the nonprofit's own.
- Never reuse nonprofit volunteers, board members, program impact data, or beneficiary demographics as if they were the consulting business's.
- Individual founder experience may appear in a Founder/Leadership Bio section when relevant, but must be clearly labeled as personal history, NOT as organizational past performance.
- Financial data, EIN, banking, and SAM/UEI registrations belong to exactly one entity — do not conflate.

## Scraping & data sourcing

- Before automating collection from any procurement platform (Port of Seattle, and later WA State/King County/Seattle/Bellevue), confirm the platform's Terms of Service / robots.txt permit automated access. Prefer an official API/open-data feed over scraping when one exists.
- Same rule applies to grant sources: prefer Grants.gov Search2 API and official RSS/GovDelivery feeds over scraping foundation websites. Do NOT bypass logins or paywalls on grant databases (Candid, Instrumentl, GrantStation, etc.).
- Respect rate limits; do not hammer a platform with retries.

## AI-assisted proposal / application drafting

- Some solicitations require disclosure of AI-assisted content, or restrict how much of a proposal may be AI-generated. Check the specific RFP/RFQ terms in `opportunities/<agency>/` before drafting.
- LLM output in `proposals/` and (Phase 2+) `grant-proposals/` is a draft only. Pricing, certifications/qualification claims, and legal terms must be verified by a human before submission (see "Do not automatically submit …" above).
- For grant applications, never invent program participant counts, outcomes, financial data, board members, partner commitments, endorsements, or 501(c)(3) determination dates. Missing content must be marked `[HUMAN INPUT REQUIRED]`.

## Nonprofit-specific sensitive data

- **Do not commit** real EIN, banking details, private beneficiary data, individual donor records, or board-member PII beyond names publicly listed by the nonprofit. The `OrganizationProfile` schema uses `has_...` booleans for this reason: attest "we have this on file elsewhere" without storing the value.
- Live organization profiles (`organizations/*/organization-profile.yaml`) are gitignored; only `*.example.yaml` templates are committed.
- Do not automatically register / update SAM.gov, UEI, or Grants.gov accounts on behalf of the nonprofit — those steps involve legal identity attestations and are human-only.
- Do not represent the nonprofit in communications with funders. The tool produces drafts; humans send.

## Contacts & PII

- `contacts/contacts.csv` may contain personal contact information for agency staff. Treat it as sensitive — do not paste its contents into external tools/services beyond what's needed for this project.
- The same rule applies to any funder program-officer contact information collected from grant announcements.

