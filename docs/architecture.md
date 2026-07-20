# 系统架构（草案）

## 数据流

```
[采购平台 x N]
      │  (定时抓取 / API 拉取)
      ▼
  ingestion/*
      │  原始公告 (HTML/PDF/JSON) → data/raw/
      ▼
  parsing/
      │  结构化字段 (标题、截止日期、NAICS、预算…) → data/parsed/
      ▼
  matching/
      │  按资质/历史业绩打分、筛选
      ▼
  tracking/  ←──────────────┐
      │  记录商机状态             │ 状态更新
      ▼                        │
  proposal/                    │
      │  LLM 生成初稿 → review/ 人工审核 ──┘
      ▼
  notifications/
      提醒相关方（邮件/Slack）
```

## 各平台 ingestion 模块的共同接口（待定）

每个 `src/ingestion/<platform>/` 子模块应暴露统一的抽象，便于 `matching`/`tracking` 不关心具体来源：

- `fetch_new_opportunities(since: date) -> list[RawOpportunity]`
- `RawOpportunity` 至少包含：`source`, `external_id`, `title`, `url`, `published_date`, `due_date`, `raw_content`

具体字段/接口待选定技术栈后细化。

## 未决问题

- 抓取方式：优先确认各平台是否提供官方 API 或开放数据接口，其次才考虑网页抓取（需先确认平台 ToS）。
- 调度：定时任务的执行环境（本地 cron、云函数、workflow 引擎）待定。
- 存储：初期可用本地文件（`data/`），商机量上升后再评估数据库。
