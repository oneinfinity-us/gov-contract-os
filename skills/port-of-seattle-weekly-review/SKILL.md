---
name: port-of-seattle-weekly-review
description: 每周抓取 Port of Seattle 采购平台的当前公告列表，与已跟踪的机会对比，对新发现的机会运行 opportunity-review 评估，并生成周报存入 reports/generated/。执行力度：新增机会应用决策树（时间 < 5 天 → No Bid；加权评分；Go/Watch/No Bid 决策）；缺失公司资料则注明 ⚠️；报告包含工作流元数据与周报趋势。
---

# port-of-seattle-weekly-review

## 目的

每周一次（推荐：**周一 06:00 UTC**），系统性地检查 Port of Seattle 采购平台，发现新公告并评估是否值得投标，生成结构化周报供人工审阅和决策。

**核心特色**：
- ⏱️ **时间优先级**：< 5 天截止直接淘汰，5-7 天标记为 Watch
- 📊 **加权评分**：核心能力 (AI/软件) 权重 3×；业务拟合权重 1.5×；执行风险权重 1×
- 🎯 **决策树清晰**：Go / Watch / No Bid，不留模糊
- ⚠️ **透明的缺陷**：公司资料不全则明确标注，不虚报能力
- 🔄 **工作流可维护性**：每周报告含元数据、趋势统计、下周预期

## 数据来源

- **采购公告列表**：https://hosting.portseattle.org/sops/#/Solicitations
- **已跟踪机会目录**：`opportunities/port-of-seattle/`
- **评估标准**：`workflows/opportunity-review.md`（含时间线硬过滤和加权评分）
- **公司资料**：`company/capabilities.md`、`company/company-profile.md`、`company/past-performance/`

## 执行步骤

### 1. 抓取当前公告

打开 https://hosting.portseattle.org/sops/#/Solicitations，提取所有当前活跃的公告，记录每条的：

- 招标编号（Solicitation #）
- 标题（Title）
- 发布日期（Issue Date）
- 截止日期（Due Date）
- 类型（RFP / RFQ / IFB / 其他）
- 预算范围（如可获取）
- 直接链接（如可获取）

### 2. 比对已跟踪机会

扫描 `opportunities/port-of-seattle/` 下的所有文件，提取已有的招标编号列表。

找出**新增**的公告（平台上有、本地目录中没有对应文件的）。

### 3. 应用决策树，评估新机会

对每条新公告，按 `workflows/opportunity-review.md` 的流程执行：

#### 第一步：时间线硬过滤
| 剩余天数 | 决定 | 说明 |
|---|---|---|
| < 5 | **No Bid** | 时间不足，直接淘汰 |
| 5-7 | **Watch** | 监控，仅在得分 > 70 时考虑 |
| ≥ 8 | 继续第二步 | 时间充足，进入完整评估 |

#### 第二步：加权评分（如通过时间过滤）
按照 `workflows/opportunity-review.md` 的评分维度，计算加权得分（0–100）：
- 核心能力匹配（AI/Azure + 软件开发）权重 3×
- 业务/市场拟合（地理、合约规模、分包潜力）权重 1.5×
- 执行风险（相关经验、资质要求）权重 1×

**特别说明**：
- 如 `company/capabilities.md` 等不完整 → 「相关经验」得分为 0
- 在报告中明确标注 ⚠️ "公司资料缺失"，**不虚报能力**

#### 第三步：决策
| 归一化得分 | 决定 | 后续 |
|---|---|---|
| ≥ 70 | **Go** | 分配给 Prime/Sub lead；设置 3 个立即行动项 + 截止日期 |
| 40-69 | **Watch** | 加入跟踪列表；监控重新发布/范围变化 |
| < 40 | **No Bid** | 归档，说明淘汰理由 |

**不使用"需更多信息"**。所有决定必须是上述三种之一。

### 4. 生成周报

将周报写入 `reports/generated/port-of-seattle-weekly-<YYYY-MM-DD>.md`。

## 周报格式

```markdown
# Port of Seattle 采购周报 — <YYYY-MM-DD>

**数据来源**：https://hosting.portseattle.org/sops/#/Solicitations
**抓取时间**：<YYYY-MM-DD HH:MM UTC>
**执行**：port-of-seattle-weekly-review skill

---

## 摘要统计

| 指标 | 数值 |
|---|---|
| 平台当前活跃公告 | <n> |
| 本周新增 | <n> |
| 建议跟进（Go） | <n> |
| 建议监控（Watch） | <n> |
| 建议放弃（No Bid） | <n> |
| ⚠️ 公司资料缺失影响的评估数 | <n> |

---

## Go（建议跟进）

### <招标编号> — <标题>

| 字段 | 值 |
|---|---|
| 机构 | Port of Seattle |
| 招标编号 | |
| 截止日期 | |
| 预算范围 | |
| 来源链接 | |

**加权得分**：<0–100>  
**建议角色**：Prime / Sub / Teaming Partner  
**理由**：<简洁说明为何得分 ≥ 70>  
**能力差距**：<如无，写"无"；如有，列出>  

**立即行动（优先级顺序，含分配人员 + 截止）**：
1. [姓名] 在 <截止日期> 前 —— <具体行动>
2. [姓名] 在 <截止日期> 前 —— <具体行动>
3. [姓名] 在 <截止日期> 前 —— <具体行动>

---

## Watch（建议监控，暂不跟进）

### <招标编号> — <标题>

| 字段 | 值 |
|---|---|
| 机构 | Port of Seattle |
| 招标编号 | |
| 截止日期 | |
| 预算范围 | |
| 来源链接 | |

**加权得分**：<40-69>  
**当前决定**：Watch  
**理由**：<说明为何得分 40-69；或因时间过短（5-7 天）>  
**监控计划**：
- 监控重新发布/范围变化
- 下周重新评估（如有新信息）
- 关注是否有相关机构的后续采购

---

## No Bid（已淘汰）

共 <n> 个机会，淘汰理由分类：

| 淘汰理由 | 数量 | 招标编号 |
|---|---|---|
| 时间不足（< 5 天） | | |
| 核心能力不匹配（得分 < 40） | | |
| 电气/建筑/HR 领域无关 | | |
| 强制资质要求不可达 | | |

---

## 公司资料完整性说明

⚠️ **当前状态**：
- `company/capabilities.md` — <TODO / 完整>
- `company/company-profile.md` — <TODO / 完整>
- `company/past-performance/` — <TODO / 有 n 个案例>

**影响**：本次评估中，<n> 个机会的「相关经验」维度记为 0 分（待公司资料更新后重新评估）。

**优先行动**：
🔴 **本周内** — 由 [姓名] 补全 `company/capabilities.md`（含 AI/Azure、软件开发、近3年案例）；完成后通知 [主评估人] 进行批量重新评估。

---

## 工作流元数据

| 字段 | 值 |
|---|---|
| Skill 文件 | `skills/port-of-seattle-weekly-review/SKILL.md` |
| Workflow 文件 | `workflows/port-of-seattle-weekly-review.md` |
| 评估标准 | `workflows/opportunity-review.md` |
| 下次运行 | 2026-07-28 06:00 UTC（周一）|
| 维护者 | Jeff Tian |
| 执行工具 | OpenClaw (GCP) |

---

## 周报趋势（历史对比）

| 周次 | Open 数 | 新增 | Go | Watch | No Bid | 更新日期 |
|---|---|---|---|---|---|---|
| 2026-07-21 | 9 | 22 | 0 | 0 | 7 | 2026-07-21 |
| 2026-07-28 | ? | ? | ? | ? | ? | 2026-07-28 |

---

## 注意事项

- 本报告为草稿，所有决定需人工审阅后方可采取行动
- 不自动提交提案或联系外部机构
- 评分仅供参考；最终决定权由团队负责人掌握
- 如平台无法访问，此报告会标注失败原因
- 所有"立即行动"项包含分配人员，否则视为悬空任务

---

**生成工具**：port-of-seattle-weekly-review (OpenClaw)  
**生成时间**：<timestamp>
```

## 边界与安全约束

- 不自动联系任何外部机构或采购官员
- 不自动提交提案
- 不编造公司资质、业绩、价格信息
- 所有产出物标注为草稿，最终决定由人工做出
- 遵守 `SECURITY.md` 中所有边界要求
- 如平台无法访问，在周报中注明，不跳过或静默失败
