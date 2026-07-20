# ingestion

各采购平台的抓取模块，一个平台一个子目录。每个子目录职责一致：拉取新发布的招标/RFP/RFQ 原始数据，落地到 `data/raw/<platform>/`，不做字段解析（解析交给 `src/parsing/`）。

子目录：

- `wa_state/` — Washington State 州级采购平台
- `king_county/` — King County 采购平台
- `seattle/` — City of Seattle 采购平台
- `bellevue/` — City of Bellevue 采购平台
- `port_of_seattle/` — Port of Seattle 采购平台

每个子目录内的具体入口 URL、是否有 API、抓取频率待确认后填入 `config/settings.example.yaml` 对应条目。
