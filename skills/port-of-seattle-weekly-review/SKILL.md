---
name: port-of-seattle-weekly-review
description: Weekly, fetch the current solicitation list from the Port of Seattle procurement platform, compare it against already-tracked opportunities, run the opportunity-review assessment on newly discovered opportunities, and generate a weekly report saved into reports/generated/. Execution rigor: apply the decision tree to new opportunities (timeline < 5 days → No Bid; weighted scoring; Go/Watch/No Bid decision); note ⚠️ when company data is missing; the report includes workflow metadata and weekly trends.
---

# port-of-seattle-weekly-review

## Purpose

Once a week (recommended: **Monday 06:00 UTC**), systematically check the Port of Seattle procurement platform, discover new solicitations and assess whether they're worth bidding on, and generate a structured weekly report for human review and decision-making.

**Core features**:
- ⏱️ **Timeline priority**: < 5 days to due date is eliminated outright; 5-7 days is flagged as Watch
- 📊 **Weighted scoring**: core capability (AI/software) weighted 3×; business fit weighted 1.5×; execution risk weighted 1×
- 🎯 **Clear decision tree**: Go / Watch / No Bid, no ambiguity left
- ⚠️ **Transparent gaps**: clearly flag when company data is incomplete, never overstate capabilities
- 🔄 **Workflow maintainability**: each weekly report includes metadata, trend statistics, and expectations for next week

## Data Sources

- **Solicitation list**: https://hosting.portseattle.org/sops/#/Solicitations
- **Tracked opportunities directory**: `opportunities/port-of-seattle/`
- **Assessment criteria**: `workflows/opportunity-review.md` (includes the hard timeline filter and weighted scoring)
- **Company data**: `company/capabilities.md`, `company/company-profile.md`, `company/past-performance/`

## Execution Steps

### 1. Fetch current solicitations

Open https://hosting.portseattle.org/sops/#/Solicitations, extract all currently active solicitations, and record for each:

- Solicitation number (Solicitation #)
- Title
- Issue Date
- Due Date
- Type (RFP / RFQ / IFB / other)
- Budget range (if obtainable)
- Direct link (if obtainable)

### 2. Compare against tracked opportunities

Scan all files under `opportunities/port-of-seattle/` and extract the list of already-tracked solicitation numbers.

Find the **new** solicitations (present on the platform but with no corresponding file in the local directory).

### 3. Apply the decision tree, assess new opportunities

For each new solicitation, follow the process in `workflows/opportunity-review.md`:

#### Step 1: Hard timeline filter
| Days remaining | Decision | Note |
|---|---|---|
| < 5 | **No Bid** | Insufficient time, eliminated outright |
| 5-7 | **Watch** | Monitor, only consider if score > 70 |
| ≥ 8 | Continue to Step 2 | Enough time, proceed to full assessment |

#### Step 2: Weighted scoring (if it passes the timeline filter)
Following the scoring dimensions in `workflows/opportunity-review.md`, compute a weighted score (0–100):
- Core capability fit (AI/Azure + software development) weighted 3×
- Business/market fit (geography, contract size, subcontracting potential) weighted 1.5×
- Execution risk (relevant experience, qualification requirements) weighted 1×

**Special notes**:
- If `company/capabilities.md` etc. are incomplete → the "relevant experience" score is 0
- Explicitly flag ⚠️ "company data missing" in the report — **never overstate capabilities**

#### Step 3: Decision
| Normalized score | Decision | Follow-up |
|---|---|---|
| ≥ 70 | **Go** | Assign to a Prime/Sub lead; set 3 immediate action items + deadlines |
| 40-69 | **Watch** | Add to tracking list; monitor for reissue/scope changes |
| < 40 | **No Bid** | Archive, with the elimination reason noted |

**Do not use "need more information"**. Every decision must be one of the above three.

### 4. Generate the weekly report

Write the weekly report to `reports/generated/port-of-seattle-weekly-<YYYY-MM-DD>.md`.

## Weekly Report Format

```markdown
# Port of Seattle Procurement Weekly Report — <YYYY-MM-DD>

**Data source**: https://hosting.portseattle.org/sops/#/Solicitations
**Fetched at**: <YYYY-MM-DD HH:MM UTC>
**Run by**: port-of-seattle-weekly-review skill

---

## Summary Statistics

| Metric | Value |
|---|---|
| Currently active solicitations on the platform | <n> |
| New this week | <n> |
| Recommended to pursue (Go) | <n> |
| Recommended to monitor (Watch) | <n> |
| Recommended to drop (No Bid) | <n> |
| ⚠️ Assessments affected by missing company data | <n> |

---

## Go (Recommended to Pursue)

### <solicitation number> — <title>

| Field | Value |
|---|---|
| Agency | Port of Seattle |
| Solicitation number | |
| Due date | |
| Budget range | |
| Source link | |

**Weighted score**: <0–100>  
**Recommended role**: Prime / Sub / Teaming Partner  
**Reasoning**: <brief explanation of why the score is ≥ 70>  
**Capability gaps**: <write "none" if none; otherwise list them>  

**Immediate actions (in priority order, with assignee + deadline)**:
1. [Name] by <due date> — <specific action>
2. [Name] by <due date> — <specific action>
3. [Name] by <due date> — <specific action>

---

## Watch (Recommended to Monitor, Not Pursuing for Now)

### <solicitation number> — <title>

| Field | Value |
|---|---|
| Agency | Port of Seattle |
| Solicitation number | |
| Due date | |
| Budget range | |
| Source link | |

**Weighted score**: <40-69>  
**Current decision**: Watch  
**Reasoning**: <explain why the score is 40-69; or note if it's due to a short timeline (5-7 days)>  
**Monitoring plan**:
- Monitor for reissue/scope changes
- Reassess next week (if new information becomes available)
- Watch for related follow-on procurement from the same agency

---

## No Bid (Eliminated)

<n> opportunities in total, elimination reasons by category:

| Elimination reason | Count | Solicitation numbers |
|---|---|---|
| Insufficient time (< 5 days) | | |
| Core capability mismatch (score < 40) | | |
| Unrelated to electrical/construction/HR domain | | |
| Mandatory qualification requirement unreachable | | |

---

## Company Data Completeness Notes

⚠️ **Current status**:
- `company/capabilities.md` — <TODO / complete>
- `company/company-profile.md` — <TODO / complete>
- `company/past-performance/` — <TODO / has n case studies>

**Impact**: In this assessment, <n> opportunities had their "relevant experience" dimension recorded as 0 (to be reassessed once company data is updated).

**Priority action**:
🔴 **This week** — [Name] to complete `company/capabilities.md` (including AI/Azure, software development, and case studies from the past 3 years); once done, notify [lead reviewer] to run a batch reassessment.

---

## Workflow Metadata

| Field | Value |
|---|---|
| Skill file | `skills/port-of-seattle-weekly-review/SKILL.md` |
| Workflow file | `workflows/port-of-seattle-weekly-review.md` |
| Assessment criteria | `workflows/opportunity-review.md` |
| Next run | 2026-07-28 06:00 UTC (Monday) |
| Maintainer | Jeff Tian |
| Execution tool | OpenClaw (GCP) |

---

## Weekly Report Trends (historical comparison)

| Week | Open count | New | Go | Watch | No Bid | Updated |
|---|---|---|---|---|---|---|
| 2026-07-21 | 9 | 22 | 0 | 0 | 7 | 2026-07-21 |
| 2026-07-28 | ? | ? | ? | ? | ? | 2026-07-28 |

---

## Notes

- This report is a draft; all decisions require human review before any action is taken
- Does not automatically submit proposals or contact external agencies
- Scores are for reference only; the final decision rests with the team lead
- If the platform is unreachable, this report will note the failure reason
- Every "immediate action" item includes an assignee, otherwise it is treated as an orphaned task

---

**Generated by**: port-of-seattle-weekly-review (OpenClaw)  
**Generated at**: <timestamp>
```

## Boundaries and Safety Constraints

- Does not automatically contact any external agency or procurement officer
- Does not automatically submit proposals
- Does not fabricate company qualifications, past performance, or pricing information
- All outputs are marked as drafts; the final decision is made by a human
- Complies with all boundary requirements in `SECURITY.md`
- If the platform is unreachable, note it in the weekly report — do not skip or fail silently
