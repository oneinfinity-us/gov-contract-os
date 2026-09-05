---
name: opportunity-review
description: Assess whether a government/municipal procurement opportunity is worth pursuing for a bid — check fit against company capabilities and past performance, give a go/no-go recommendation and questions requiring human confirmation. Use when reviewing a newly discovered RFP/RFQ.
---

# opportunity-review

## Input

A new or pending-review opportunity under `opportunities/<agency>/` (title, solicitation number, due date, NAICS/UNSPSC codes, budget range, qualification requirements, original link).

## Steps

1. Read the opportunity's original requirements and extract key fields: scope/subject matter, qualification requirements (licenses, insurance, bonding, etc.), due date, budget scale, NAICS/UNSPSC codes.
2. Check against `company/capabilities.md` to judge whether the service scope matches; check against `company/past-performance/` to judge whether there is relevant experience that can be cited.
3. Check whether qualification thresholds (e.g., bonding amount, specific certifications) can currently be met by the company — if uncertain, list as needing human confirmation, do not assume they are met.
4. Check whether the solicitation has any disclosure or restriction requirements regarding AI-assisted drafting of bid documents (see `SECURITY.md`).
5. Give one of three recommendations: go / no-go / need more information, with reasoning.
6. Write the result back into the corresponding opportunity file (append an "Assessment Result" section) — do not modify the original solicitation information.

## Output Format (appended to the end of the opportunity file)

```
## Assessment Result (opportunity-review)
- Fit: High / Medium / Low
- Recommendation: go / no-go / need more information
- Reasoning: ...
- Questions requiring human confirmation:
  - ...
```

## Boundaries

- Does not automatically decide to "bid" or advance to the proposal-drafting stage — go/no-go is a recommendation for a human to see; the final decision rests with a human.
- Does not fabricate company qualifications/past-performance data; anything not in `company/` must be marked as pending confirmation.
