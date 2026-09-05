# Data Source Research Notes

This document records the research findings on data sources for each target agency, including publicly available
interfaces that have been verified, leads that still need verification, and cases honestly marked "not yet researched."
All sources must be publicly accessible — bypassing login/CAPTCHA/rate limits is not allowed (see
[../SECURITY.md](../SECURITY.md)).

## Port of Seattle (verified, the only real connector so far)

- Portal: `https://hosting.portseattle.org/sops/` (VendorConnect, Ivalua procurement system)
- **Public OData v4 API**: `https://hosting.portseattle.org/sopsapi/Solicitations`
  - The portal's own "guest" (no login required) search page pulls its data through this same API — confirmed via
    the browser network panel — and `robots.txt` has no restrictions, so there is no bypassing of any access control.
  - List queries use `$filter`/`$select`/`$expand` to fetch exact fields (`ProcurementNumber`,
    `ProcurementTitle`, `BidDueDateTime`, `Id`, `SolicitationCategory`, `SolicitationStatus`).
  - Detail queries use `$filter=Id eq <guid>`, fetching `Description`, `PortContact`,
    `PortContactEmail`, `AdvertisementDate`, `BidDueDateTime`,
    `BidDueDateQuestionCutOffDateTime`, `Department.Name`, and other fields.
  - The document download endpoint has not yet been verified (`fetch_documents()` currently returns an empty list;
    needs another round of research).
- Priority classification: `SourceSystemType.OFFICIAL_API` (highest priority).
- Code location: `src/gov_contract_os/collectors/port_of_seattle.py`.

## City of Seattle (verified, second real connector)

- Official RSS feed: `https://thebuyline.seattle.gov/category/bids-and-proposals/feed/`
  - "The Buy Line" is the City of Seattle's official procurement blog/announcement page. Its "Bids and Proposals"
    category provides a standard public RSS 2.0 feed, requiring no login/API key, and `robots.txt` has no restrictions.
  - The real feed was actually fetched and parsed on 2026-07-22 (roughly 20 current items), confirming the field structure:
    - `<item><title>` mixes a status prefix (`CLOSED-`/`ARCHIVED-`/`CANCELED-`/
      `CANCELLED-`), the title body, and a solicitation number (internal numbers like `TR0-6221`,
      or labeled numbers like `RFP#6345`/`ITB# CL0-6135`) — the format is inconsistent and needs regex cleanup.
    - `<item><category>` common values include "Bids & Proposals", "Announcements",
      "History/Archives" — useful for helping determine whether an item is a pure announcement (containing no real solicitation).
    - `<item><description>` is HTML-escaped free text containing:
      1. An outbound link to the actual bidding platform — `https://cityofseattle.bonfirehub.com/...`
         or `https://procurement.opengov.com/portal/seattle/...` (neither platform's public API has been verified;
         currently only the outbound link is captured, without parsing platform-internal details);
      2. Free-form "Due Date: ..." text, extracted via regex + `dateutil` fuzzy parsing,
         which may fail to extract (`due_at=None`) or be imprecise; the due-date text is in Pacific time but has
         no machine-readable timezone marker, so it is always stored as UTC (suitable only for day-granularity scoring,
         not for precise reminders).
    - Pure announcement items (such as monthly "Doing Business With The City" workshop notices) have no
      solicitation number and no outbound link — the absence of both features is used as a filter to skip them,
      so they are not stored as real opportunities.
  - `fetch_documents()` is not implemented (neither bonfirehub's nor opengov's public document download interface has been verified).
- Priority classification: `SourceSystemType.OFFICIAL_RSS`.
- Code location: `src/gov_contract_os/collectors/city_of_seattle.py`,
  tests in `tests/test_collectors_city_of_seattle.py` (offline fixtures, no dependency on real network access).

## Washington State (GovDelivery email verified, HTML scraper not implemented)

**Step 1 conclusion: WEBS login automation is not needed** — WA DES already provides a first-class, login-free
public discovery channel; an account is only meaningful for submitting bids/viewing awarded-contract details/a
personalized watchlist.

Verified with a read-only browser on 2026-07-24:

- **WA DES GovDelivery email subscription** (Granicus platform, a standard government public notification service):
  - Contracts Connection (contract overview):
    `https://public.govdelivery.com/accounts/WADES/subscriber/new?topic_id=WADES_109`
  - **IT Contracts Focus (IT/AI procurement topic) — the subscription most relevant to this project**:
    `https://public.govdelivery.com/accounts/WADES/subscriber/new?topic_id=WADES_4`
  - After subscribing, emails are sent from the `subscriptions.des.wa.gov` / `subscribe.des.wa.gov` /
    `subscriber.govdelivery.com` domains and contain a title, summary, and a detail link pointing to des.wa.gov or
    `pr-webs-vendor.des.wa.gov/Search_BidDetails.aspx?ID=<n>`.
  - **Implementation approach**: instead of scraping govdelivery.com, **the user subscribes their own mailbox**,
    and the project pulls matching govdelivery-domain emails read-only via IMAP for parsing. Credentials are stored
    only in `.env` (gitignored).
  - Priority classification: `SourceSystemType.OFFICIAL_EMAIL_SUBSCRIPTION`.
  - Code location: `src/gov_contract_os/collectors/govdelivery_email.py`,
    connector name `govdelivery_email`.
  - Known limitation: the email template is not fully public documentation, so only a defensive parser against the
    generic GovDelivery structure has been written; it will need adjustment based on actual fields once the first
    real emails are received (see the "TODO after first real emails" section in the connector docstring).

- **WEBS BidCalendar public page** (not implemented, can be added later):
  - URL: `https://pr-webs-vendor.des.wa.gov/BidCalendar.aspx` (**completely login-free**,
    confirmed with a read-only browser on 2026-07-24; shows Solicitation Close Date / Title /
    Ref # / Contact / Agency dropdown filters).
  - Detail page URL pattern: `Search_BidDetails.aspx?ID=<int>`.
  - ASP.NET WebForms, using `__doPostBack` for pagination; harder to scrape than GovDelivery email but
    feasible. Add if GovDelivery coverage turns out to be insufficient.
  - **Never** go to `fortress.wa.gov` — that is the WEBS authenticated side (login/registration/awarded contracts)
    and is not within the public scope.

- **WA Open Data (Socrata)** (not implemented, for market intelligence use):
  - Example: `https://data.wa.gov/Procurements-and-Contracts/WEBS-Vendors-by-commodity-code-and-MWBE-V-Small-st/3kwi-7zsj`
  - Used for historical procurement/vendor/commodity-code analysis, not a real-time solicitation source. Specific endpoints not yet verified.

- **DES homepage robots.txt** (`https://des.wa.gov/robots.txt`):
  - Standard Drupal robots, disallowing `/admin`, `/user/login|register|password`, `/search`, `/node/add` and other
    system paths; it does **not** disallow `/sell/bid-opportunities` or the
    `pr-webs-vendor.des.wa.gov` / `apps.des.wa.gov` subdomains.

## King County (not verified, not implemented)

- **Candidate platform**: LLM suggests OpenGov Procurement; **not yet verified** for this project.
- Unverified points:
  1. Confirm the real procurement portal URL and slug from the official `https://kingcounty.gov/` page
     (the slug cannot be guessed from platform name + agency name);
  2. The OpenGov portal itself is browsable without login (already verified on the Seattle portal, see below),
     but the internal JSON API has not been captured;
  3. Whether King County also has a GovDelivery subscription channel (quite likely) — if so,
     reuse the `govdelivery_email` connector directly instead of writing a new scraper.
- `health_check()` honestly reports "not yet researched/verified."

## City of Bellevue (not verified, not implemented)

- Same as King County — LLM suggests an OpenGov platform, not verified.
- Should likewise check Bellevue's GovDelivery subscription channel first; if it covers this, no scraper is needed.

## OpenGov Portal Platform (partially verified)

Verified by opening `https://procurement.opengov.com/portal/seattle` with a read-only browser on 2026-07-24:

- **The portal is completely browsable without login**: three tabs — Projects / Calendar / Vendors —
  with Project Title / Project ID / Status / Addenda / Release Date / Close Date
  all visible. Detail pages can be clicked into.
- **Cloudflare + built-in bot detection**: a "Just a moment..." challenge appears on first visit and clears in a
  few seconds; automation must be gentle (real UA, ≥3 second request intervals, back off rather than force through
  when a challenge appears).
- **`procurement.opengov.com/robots.txt` returns 404** (SPA has no robots.txt);
  OpenGov's own site has no separate browsewrap Terms of Use page, only a Privacy Policy
  (`https://opengov.com/privacy-policy/`), which explicitly states that the actual terms of use on top of the
  portal are governed by the public information rules of the government customer that purchased OpenGov
  (Seattle/King County/Bellevue, etc.).
- **Not verified**: the internal JSON API endpoint the SPA calls to load the Projects list (a task for next round;
  once located via the browser Network panel, a single connector could serve multiple cities).

## General Principles (applicable to any newly added source)

1. Priority order: official API > official email subscription (GovDelivery) ≈ official RSS/Atom > official data
   download > official public search page > plain HTML parsing > browser automation (browser automation is a last
   resort only, and must be against a public page — never bypassing any verification).
2. Before integrating any source, it must first be confirmed read-only (via `fetch_webpage`/a read-only browser
   checking the network panel) that the endpoint is "public, no login required, not bypassing CAPTCHA/rate limits,"
   before any scraping code is written.
3. **Credential management**: any channel requiring an account (e.g., IMAP pulling GovDelivery email) must have its
   credentials stored only in the local `.env` (gitignored), and must never go into code/logs/commits.
4. For sources that cannot be verified or have no leads, `health_check()` must honestly report the status and reason,
   and provide a manual alternative (such as manually downloading the PDF into `opportunities/inbox/`) —
   fabricating URLs or field structures is not allowed.
5. LLM suggestions can serve as a **research starting point**, but every URL / platform attribution / API guess must
   be independently re-verified by a human or this project's read-only tools before it can be written into code or
   connector configuration.
