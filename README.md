# gov-contract-os

政府/市政采购商机自动化系统：抓取多个采购平台的招标信息，解析、匹配商机，并用 LLM 辅助生成投标提案。

## 目标

1. **抓取（Ingestion）** — 定期从以下采购平台获取新发布的招标/RFP/RFQ：
   - **Washington State** — 州级采购平台
   - **King County** — 金县采购平台
   - **City of Seattle** — 西雅图市采购平台
   - **City of Bellevue** — 贝尔维尤市采购平台
   - **Port of Seattle** — 西雅图港务局采购平台
   - （可扩展：SAM.gov 联邦级，其他周边市级平台）

   > 各平台的具体入口 URL、认证方式、是否提供 API 见 `config/settings.example.yaml`，需要逐一确认后填入 —— 避免在文档里写未经核实的链接。

2. **解析（Parsing）** — 从抓取到的公告/文档（PDF、HTML）中提取结构化字段：标题、发布/截止日期、NAICS/UNSPSC 代码、预算范围、联系人、资质要求等。

3. **匹配（Matching）** — 根据公司资质、历史业绩、NAICS 代码等条件筛选出值得跟进的商机。

4. **提案生成（Proposal Generation）** — 基于招标要求 + 公司资料库（过往业绩、资质证明、标准条款），用 LLM 辅助起草投标文件初稿，并保留人工审核环节。

5. **跟踪（Tracking）** — 记录每个商机的状态（发现/评估/投标中/已提交/中标/未中标），提醒关键截止日期。

6. **通知（Notifications）** — 新商机、即将截止、状态变更等提醒（邮件/Slack）。

## 目录结构

```
gov-contract-os/
├── README.md
├── .gitignore
├── docs/
│   ├── architecture.md       # 系统架构与数据流
│   └── compliance.md         # 合规注意事项（各州/市采购规则、AI 生成内容披露等）
├── src/
│   ├── ingestion/             # 各采购平台的抓取模块，一个平台一个子目录
│   │   ├── wa_state/
│   │   ├── king_county/
│   │   ├── seattle/
│   │   ├── bellevue/
│   │   └── port_of_seattle/
│   ├── parsing/                # 公告/文档解析，提取结构化字段
│   ├── matching/               # 商机筛选与打分逻辑
│   ├── proposal/               # LLM 辅助提案生成
│   │   ├── templates/          # 提案模板、标准条款、公司资料片段
│   │   ├── generator/          # 调用 LLM 生成初稿的逻辑
│   │   └── review/             # 人工审核 / 合规检查流程
│   ├── tracking/                # 商机状态与截止日期跟踪
│   └── notifications/          # 邮件/Slack 通知
├── config/
│   └── settings.example.yaml   # 各平台入口配置模板（不含真实密钥）
├── tests/
├── scripts/                     # 一次性/运维脚本
└── data/                        # 本地缓存数据（已加入 .gitignore，不入库）
```

## 当前状态

骨架阶段：目录结构已搭建，尚未选定具体技术栈（语言/框架）与各采购平台的抓取方式（API vs 网页抓取）。

## 待决策事项

- [ ] 技术栈：语言（Python / Node / 其他）、任务调度方式（cron / Airflow / 云函数）
- [ ] 各平台数据获取方式：是否有官方 API，还是需要网页抓取（需确认各平台 ToS 是否允许自动化抓取）
- [ ] 数据存储：文件 vs 数据库（体量增长后是否需要 Postgres/SQLite）
- [ ] LLM 提案生成的合规要求：是否需要在投标文件中披露 AI 辅助生成，参见 `docs/compliance.md`
