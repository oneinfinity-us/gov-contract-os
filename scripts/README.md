# scripts

确定性的采集与整理脚本（例如：抓取 Port of Seattle 采购平台的公开列表、把原始公告规范化写入 `opportunities/<agency>/`、清理缓存等）。

## 原则

- 只做确定性的数据获取/整理，不在脚本里嵌入 LLM 判断（哪个机会值得跟进、如何打分等推理交给 `skills/opportunity-review` 和 `workflows/`）。
- 抓取前确认对应平台的 ToS/robots.txt 是否允许自动化访问。
- 认证信息（API token 等）一律从环境变量读取（见 `.env.example`），不写入脚本或提交到仓库。

