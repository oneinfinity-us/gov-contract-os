---
name: port-of-seattle-weekly-review
description: 每周抓取 Port of Seattle 采购平台的当前公告列表，与已跟踪的机会对比，对新发现的机会运行 opportunity-review 评估，并生成周报存入 reports/generated/。每周执行一次，触发词包括"port of seattle 周报"、"weekly port of seattle review"、"刷新 port of seattle 机会"。
---

# port-of-seattle-weekly-review

## 目的

每周一次，系统性地检查 Port of Seattle 采购平台，发现新公告并评估是否值得投标，生成周报供人工审阅。

## 数据来源

- **采购公告列表**：https://hosting.portseattle.org/sops/#/Solicitations
- **已跟踪机会目录**：`opportunities/port-of-seattle/`

## 执行步骤

### 1. 抓取当前公告

打开 https://hosting.portseattle.org/sops/#/Solicitations，提取所有当前活跃的公告，记录每条的：

- 招标编号（Solicitation #）
- 标题（Title）
- 发布日期（Issue Date）
- 截止日期（Due Date）
- 类型（RFP / RFQ / IFB / 其他）
- 直接链接（如可获取）

### 2. 比对已跟踪机会

扫描 `opportunities/port-of-seattle/` 下的所有文件，提取已有的招标编号列表。

找出**新增**的公告（平台上有、本地目录中没有对应文件的）。

### 3. 评估新机会

对每条新公告，按照 `skills/opportunity-review/SKILL.md` 定义的流程执行完整评估：

- 提取关键字段
- 对照 `company/capabilities.md` 和 `company/past-performance/`
- 检查资质门槛
- 检查 AI 披露限制（`SECURITY.md`）
- 给出 go / no-go / 需更多信息 建议

将评估结果写入 `opportunities/port-of-seattle/<solicitation-id>-<slug>.md`（新建文件）。

### 4. 生成周报

将周报写入 `reports/generated/port-of-seattle-weekly-<YYYY-MM-DD>.md`，格式见下方。

## 周报格式

```markdown
# Port of Seattle 采购周报 — <YYYY-MM-DD>

**数据来源**：https://hosting.portseattle.org/sops/#/Solicitations
**抓取时间**：<datetime>
**执行人**：port-of-seattle-weekly-review skill

---

## 摘要

- 平台当前活跃公告数：<n>
- 本周新增：<n>
- 建议跟进（go）：<n>
- 建议放弃（no-go）：<n>
- 待更多信息：<n>

---

## 新增机会

### <招标编号> — <标题>

| 字段 | 值 |
|---|---|
| 机构 | Port of Seattle |
| 招标编号 | |
| 发布日期 | |
| 截止日期 | |
| 类型 | |
| 预算范围 | |
| 来源链接 | |

**评估得分**：<0–100>
**建议角色**：Prime / Sub / Teaming Partner / No Bid
**建议**：go / no-go / 需更多信息
**理由**：...
**能力差距**：...
**立即行动（3 项）**：
1. ...
2. ...
3. ...

---

## 已跟踪机会状态更新

（如已跟踪机会截止日期变化、状态变化，在此列出。）

---

## 注意事项

- 本报告为草稿，需人工审阅后方可采取任何行动。
- 不得自动提交提案或联系外部机构。
```

## 边界与安全约束

- 不自动联系任何外部机构或采购官员。
- 不自动提交提案。
- 不编造公司资质、业绩、价格信息。
- 所有产出物标注为草稿，最终决定由人工做出。
- 遵守 `SECURITY.md` 中所有边界要求。
- 如平台无法访问，在周报中注明，不跳过或静默失败。
