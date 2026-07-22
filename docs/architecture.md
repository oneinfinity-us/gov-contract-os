# 架构说明

## 分层设计

```
models/       Pydantic 数据模型 (Opportunity, Analysis) - 全系统唯一的数据契约
storage/      SQLAlchemy ORM + SQLite，围绕 Opportunity.id 做去重 upsert
collectors/   每个采购机构一个 connector，实现统一的 Connector 抽象接口
normalizers/  机构名/日期/金额等字段的清洗与标准化工具函数
scoring/      Level-1 确定性关键词评分规则 + 评分入口
reports/      每日机会日报生成（Markdown）
cli.py        Typer CLI，串联以上各层
```

依赖方向：`collectors` 产出 `Opportunity`（用到 `normalizers`）→ `storage` 落库
→ `scoring` 读取未评分的机会产出 `Analysis` → `storage` 落库 → `reports` 汇总生成日报。
`cli.py` 是唯一的编排层，OpenClaw 只应调用 CLI 命令，不直接导入内部模块。

## 去重策略

`Opportunity.build_id()` 是主键来源：

1. 优先用 `f"{normalize_agency_name(source_agency)}::{solicitation_number}"`。
2. 若没有编号，退回 `f"{agency}::{source_url}::{normalized_title}::{due_at_iso}"`。
3. 对上述字符串取 `sha256` 前 32 位十六进制作为 `id`。

同一个机会被多次抓取时 `id` 不变，`storage.db.upsert_opportunity` 据此原地更新而非重复插入。
另外维护 `content_hash`（标题/描述/状态/截止日期/金额的哈希）用于未来检测"内容是否发生实质变化"，
本轮尚未接入变更通知逻辑。

## 两级评分（Level 1 已实现，Level 2 未实现）

- **Level 1（本轮实现）**：`scoring/rules.py` + `scoring/scorer.py`，纯关键词/规则打分，
  0-100 分，5 类能力关键词（AI/Agent/Copilot/Azure 权重最高 25 分）+ 小公司体量匹配 +
  强制性要求匹配（暂时恒定 50%，因为 Level 1 无法真正解析强制性要求条款）+ 时间可行性。
  确定性、可单测、不调用任何外部 API。
- **Level 2（未实现）**：计划让 LLM 读取机会全文，结合 `company/` 目录判断真实契合度、
  提炼 `capability_gaps`/`mandatory_requirement_risks`，仅对 `requires_advanced_model=True`
  （即 Level 1 分数 ≥ 75）的机会调用，控制付费 API 成本。本轮 `requires_advanced_model`
  字段已计算并写入 `Analysis`，但没有任何代码真正调用付费模型。

`Analysis.requires_human_review` 恒为 `True` —— 系统任何输出都不能被当作自动决策依据。

## Connector 统一接口

`collectors/base.py` 定义 `Connector` 抽象基类：`discover()` / `fetch_details()` /
`fetch_documents()` / `health_check()`。任何一个来源抓取失败都必须通过
`ConnectorHealth`（状态 + 原因 + 替代方案 + 人工 inbox 提示）汇报，不能抛出未处理异常
中断其他来源的抓取（`cli.py` 的 `collect --all` 对每个来源单独 try/except）。

已实现：
- `PortOfSeattleConnector`：唯一真实可用的 connector，调用公开 OData API。
- 其余 4 个（Washington State / King County / City of Seattle / City of Bellevue）
  均为 stub：`discover()` 直接 `raise NotImplementedError`，`health_check()` 返回
  `NOT_IMPLEMENTED` 状态并给出研究线索/人工替代方案。

## 已实现功能

- 数据模型（`Opportunity`/`Analysis`）+ 去重/内容哈希
- SQLite 存储 + upsert 语义
- Connector 统一接口 + 1 个真实 connector（Port of Seattle）+ 4 个诚实的 stub
- 字段标准化（机构名/日期/金额）
- Level-1 确定性评分
- 每日 Markdown 报告生成
- CLI：`collect` / `analyze --new` / `report daily` / `export`
- 单元测试（52 个，覆盖模型/标准化/评分/存储/connector/CLI），全部离线运行
- ruff lint + format 通过

## 尚未实现（留给下一轮）

- Level-2 LLM 分析（真正调用 Anthropic API）
- RFP 全文解析与合规矩阵（`rfp analyze` 目前只是打印"未实现"并退出码 2）
- 提案起草辅助
- Demo（Streamlit/FastAPI），`demo` 命令目前只是占位
- Washington State / King County / City of Seattle / City of Bellevue 的真实 connector
  （City of Seattle 已有两条线索，见 `docs/data-sources.md`）
- OpenClaw 集成的具体调度脚本/配置（`workflows/` 中已有流程描述，但尚未验证真实可执行）
- 变更检测通知（利用已有的 `content_hash` 字段）
