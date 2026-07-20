# parsing

将 `ingestion/*` 落地的原始公告（HTML/PDF/JSON）解析为结构化字段，写入 `data/parsed/`。

统一输出字段（草案，待细化）：

- `source`（平台名）
- `external_id`（平台内的公告编号）
- `title`
- `published_date` / `due_date`
- `naics_codes` / `unspsc_codes`
- `estimated_value`
- `contact`
- `qualification_requirements`
- `url`
- `raw_ref`（指向原始文件的引用）
