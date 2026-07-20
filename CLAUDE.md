# gov-contract-os

政府/市政采购商机自动化系统。目标：发现商机 → 评估是否值得投标 → 起草提案（LLM 辅助，人工审核）→ 跟踪状态 → 每日生成机会日报。

当前范围：**Port of Seattle 试点**。其他机构（Washington State、King County、City of Seattle、City of Bellevue）尚未开始接入，未来会以同样的目录约定加入 `opportunities/`。

在做任何事之前，先读 `SECURITY.md`——里面的边界（不自动提交提案、不自动外发邮件、不存雇主/客户机密信息等）没有例外。

## 目录约定

| 目录 | 用途 |
|---|---|
| `company/` | 公司资料：简介、创始人简历、能力清单、过往业绩。起草提案前必须先读这里，不得编造资质或业绩。 |
| `opportunities/<agency>/` | 每个机构一份，存放发现的招标/RFP/RFQ 及其评估结果。 |
| `contacts/contacts.csv` | 采购机构联系人。含 PII，处理方式见 `SECURITY.md`。 |
| `proposals/` | 投标提案草稿，与 `opportunities/` 中的机会一一对应。草稿必须经人工审核才能提交。 |
| `demos/` | 面向潜在客户/内部评审的演示材料。 |
| `reports/` | 每日自动生成的机会日报（按日期归档）。 |
| `scripts/` | 确定性的采集/整理脚本，不嵌入 LLM 判断。 |
| `skills/opportunity-review/` | 机会分析流程的定义——评估一个新机会时按此执行。 |
| `workflows/` | OpenClaw 的执行指令（例如每日抓取 → 评估 → 生成日报的自动化流程）。 |

## 工作规则

- 评估新机会时，遵循 `skills/opportunity-review/` 里定义的流程，产出物写回对应 `opportunities/<agency>/` 目录。
- 起草提案前先读 `company/`；不确定的资质/业绩信息标记为待确认，不要自己编。
- `scripts/` 里的代码保持确定性、可复查——判断"值不值得投标"、"怎么打分"这类推理放在 skills/workflows，不要埋进脚本里。
- 涉及 `contacts/contacts.csv` 或客户/机构非公开信息时，遵守 `SECURITY.md` 的处理边界。
- 任何要对外发送/提交的内容（邮件、提案提交）一律先给人审核，不自动执行。
