---
name: grant-review
description: 评估一份 grant 机会是否值得申请——先跑硬性资格 pass/fail，再对通过资格的评分与出建议（Apply / Apply with Partner / Seek Fiscal Sponsor / Request Clarification / Monitor / Do Not Apply）。评审新发现或手工导入的 NOFO/RFA 时使用。
---

# grant-review

## 输入

- 一条 `GrantOpportunity`（手工导入的 `opportunities/grants/inbox/<slug>/manifest.yaml` 或 collector 抓来的）
- 目标非盈利的 `organizations/<slug>/organization-profile.yaml`

## 前置条件

- 只对 `type: nonprofit` 的组织运行本流程。见 `SECURITY.md` 的组织身份隔离条款。
- 起草任何叙述/预算前必须先读 `organizations/<slug>/` 里的 mission / programs / capacity 文件；不得引用 `company/` 或 consulting-business 的过往业绩。

## 步骤

1. **Eligibility pass/fail**（`gov_contract_os.grants.eligibility.check_grant_eligibility`）
   - 501(c)(3) 状态、eligible applicant type、geographic scope、invitation-only、SAM.gov 注册、deadline 可行性、cost share 上限
   - 硬失败 → `INELIGIBLE`，直接跳到"归档"步骤，不评分
   - 缺信息 → `CONDITIONAL` 或 `UNKNOWN`，记入 `missing_information` / `conditional_actions`
2. **Level-1 打分**（仅对 `ELIGIBLE` / `CONDITIONAL`，`gov_contract_os.grants.scoring.score_grant`，config: `config/scoring/grant-scoring.yaml`）
   - 11 个维度：mission / program / population / geography / entity / funding amount / cost / capacity / outcomes / effort / deadline
   - 权重外部化，不写死在代码里
3. **建议**
   - Apply / Apply with Partner / Seek Fiscal Sponsor / Request Clarification / Monitor / Do Not Apply
   - 分数 ≥ 70 → `requires_advanced_model=True`，等 Level-2 LLM 分析
4. **生成分析 artifact**（Phase 2 起）
   写入 `reports/grants/<grant-id>/`：
   - opportunity-summary.md
   - eligibility-matrix.csv
   - application-checklist.md
   - narrative-outline.md
   - budget-framework.csv
   - questions-for-funder.md
   - risk-register.md
   - decision-memo.md
5. **人工审核**——所有 artifact 是草稿，最终决定权在人。

## 输出

一条 `GrantAnalysis`（存 `grant_analyses` 表），带：

- `eligibility.status`、`hard_failures`、`missing_information`、`conditional_actions`
- `fit_score`（ineligible 时为 `None`）、`fit_level`、`recommendation`
- `matched_criteria`、`gaps`、`next_actions`
- `requires_human_review=True`（永远）

## 边界

- **不自动决定申请**——`recommendation` 是给人看的建议。
- **不代表非盈利与 funder 通信**、**不代签授权代表签名**、**不自动提交申请**。
- **不编造** organizational capacity、program outcomes、财务数据、合作伙伴承诺、董事会成员。缺失一律 `[HUMAN INPUT REQUIRED]`。
- **不复用** `company/` / consulting-business 的 past performance 到 grant 申请里。
