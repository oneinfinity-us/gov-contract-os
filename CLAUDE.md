# gov-contract-os

政府/市政采购商机 + 非盈利 grant 商机自动化系统。目标：发现商机 → 评估是否值得投标/申请 → 起草提案/申请（LLM 辅助，人工审核）→ 跟踪状态 → 定期生成机会日报。

当前范围：
- **采购（合同）线**：Port of Seattle 试点已运行；WA State / King County / City of Seattle / City of Bellevue 后续接入。产品名 "Government Contract Opportunity Copilot"。
- **Grant 线**（Phase 1 完成，2026-07）：非盈利 grant 机会 —— 手工 PDF 导入闭环 + 硬性资格 pass/fail + Level-1 打分 + 组织身份隔离守卫。Grants.gov API / WA GovDelivery grant 分流是 Phase 3。

在做任何事之前，先读 `SECURITY.md`——里面的边界（不自动提交提案/申请、不自动外发邮件、不存雇主/客户机密信息、组织身份隔离等）没有例外。

## 目录约定

| 目录 | 用途 |
|---|---|
| `company/` | 咨询公司的人类可读资料：简介、创始人简历、能力清单、过往业绩。起草采购提案前必须先读这里，不得编造资质或业绩。**不得用于 grant 申请**。 |
| `organizations/` | 组织身份 manifest（YAML）。`consulting-business/` 对应 `company/` 内容；`nonprofit/` 是 501(c)(3) 非盈利。CLI 的 `--nonprofit/--organization` 参数从这里读。 |
| `opportunities/<agency>/` | 采购机会。每个机构一份。 |
| `opportunities/grants/inbox/<slug>/` | 手工投递的 grant 公告 —— 每个 grant 一个文件夹，含 `manifest.yaml` + 原始 PDF。 |
| `opportunities/grants/archive/` | 已归档的 grant（closed / awarded / do_not_apply）。 |
| `contacts/contacts.csv` | 采购机构联系人。含 PII，处理方式见 `SECURITY.md`。 |
| `proposals/` | 采购投标提案草稿。人工审核才能提交。 |
| `templates/grants/` | Grant application 段落模板（LOI、statement of need、budget narrative 等）。Phase 2 起提供真实内容。 |
| `reports/` | 采购每日机会日报。 |
| `reports/grants/<grant-id>/` | 每个 grant 的分析产物（eligibility matrix、decision memo 等）。Phase 2 起自动生成。 |
| `config/scoring/*.yaml` | 评分权重配置（externalized，不写死在代码里）。 |
| `scripts/` | 确定性的采集/整理脚本，不嵌入 LLM 判断。 |
| `skills/opportunity-review/` | 采购机会分析流程。 |
| `skills/grant-review/` | Grant 机会分析流程（eligibility → 评分 → recommendation）。 |
| `workflows/` | OpenClaw 的执行指令。 |

## 工作规则

- 采购机会评估遵循 `skills/opportunity-review/`；Grant 机会评估遵循 `skills/grant-review/`。
- 起草采购提案前读 `company/`；起草 grant 申请前读 `organizations/<nonprofit-slug>/`。**永远不跨用**。
- 不确定的资质/业绩/项目结果标为 `[HUMAN INPUT REQUIRED]`，不要自己编。
- Grant 分析必须先跑硬性 eligibility pass/fail，`INELIGIBLE` 的不参与评分排名。
- `scripts/` 里的代码保持确定性、可复查——判断"值不值得投"、"怎么打分"这类推理放在 skills/workflows/scoring config，不要埋进脚本里。
- 涉及 `contacts/contacts.csv`、非盈利 EIN/银行/董事会 PII、或客户/机构非公开信息时，遵守 `SECURITY.md`。
- 任何要对外发送/提交的内容（邮件、采购提案提交、grant 申请提交、SAM.gov/UEI 注册更新）一律先给人审核，不自动执行。

## Grant 阶段路线图

- **Phase 1（完成）**：领域模型、eligibility checker、Level-1 打分、YAML 权重、手工导入、CLI (`grants import` / `grants screen` / `grants list`)、组织身份隔离、tests。
- **Phase 2**：手工 grant PDF → LLM 抽字段填 manifest、完整分析产物（8 个 markdown/csv 文件）、grant-review LLM Level-2。
- **Phase 3**：Grants.gov Search2 API connector + 复用现有 GovDelivery connector 处理 WA 州 grant 邮件的解析分流。
- **Phase 4**：Grant application workspace（LOI / narrative / budget 起草 + budget validation）。
- **Phase 5**：基金会 / 企业 CSR connector（大部分只做 stub，走 manual inbox）。

