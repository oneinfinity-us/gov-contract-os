# gov-contract-os

政府/市政采购商机自动化系统：发现商机 → 评估是否值得投标 → 起草提案（人工审核）→ 跟踪状态 → 每日机会日报。

## 安全声明

- **不自动提交政府提案**、**不自动发送外部邮件**、**不绕过登录/CAPTCHA/访问控制/限流/付费墙**。
- 只使用公开的政府采购信息；不下载无关附件；只处理公开可访问的招标信息。
- 真实 API Key 不写入 Git 仓库（见 `.env.example`）。任何正式对外内容必须经人工审批。
- 完整边界见 [SECURITY.md](SECURITY.md)；仓库整体约定见 [CLAUDE.md](CLAUDE.md)。

## 现状（第一轮 MVP）

已实现 Python 骨架：数据模型、SQLite 存储、connector 统一接口、评分器、CLI、测试。
**Port of Seattle**（公开 OData API）和 **City of Seattle**（官方 RSS feed）是目前两个
可真实抓取的来源；其余三个目标机构（Washington State / King County / City of Bellevue）
目前只有占位 connector，`health_check()` 会明确报告未实现原因与替代方案（见下方
"已支持/暂不支持来源"）。

## 安装

需要 Python 3.12+。

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## 配置

```powershell
cp .env.example .env
# 按需填写 ANTHROPIC_API_KEY / OPENCLAW_GATEWAY_TOKEN（本轮尚未实际调用付费 AI API）
```

SQLite 数据库默认写在 `runtime/gov_contract_os.sqlite3`（已在 `.gitignore` 中排除，不提交）。

## CLI 命令

```powershell
# 抓取所有来源（未实现的来源会被跳过并打印原因，不影响其他来源）
python -m gov_contract_os collect --all

# 抓取单个来源
python -m gov_contract_os collect --source port_of_seattle
python -m gov_contract_os collect --source city_of_seattle

# 对尚未评分的机会跑 Level-1 确定性评分
python -m gov_contract_os analyze --new

# 生成每日机会日报到 reports/generated/
python -m gov_contract_os report daily

# 导出全部机会为 JSON/CSV
python -m gov_contract_os export --output-dir runtime/export

# 以下两个命令本轮只是占位（会打印"未实现"并以非零码退出）
python -m gov_contract_os rfp analyze opportunities/inbox/example.pdf
python -m gov_contract_os demo
```

## 测试

```powershell
python -m pytest
```

测试全部离线运行：connector 测试用 `respx` 模拟 HTTP 响应（`tests/fixtures/`），不会访问真实政府网站。

## Demo 启动方式

尚未实现（计划 Streamlit 或 FastAPI，见 `docs/architecture.md` 的"尚未实现"部分）。

## OpenClaw 运行方式

OpenClaw 应只调用上面列出的确定性 CLI 命令；行为边界（不允许 push/发邮件/提交提案/删除源文件等）
见 [SECURITY.md](SECURITY.md) 与 `workflows/`。详细集成方式见 `docs/openclaw-integration.md`
（占位，待后续轮次补充）。

## 已支持来源

| 来源 | 状态 | 方式 |
|---|---|---|
| Port of Seattle | ✅ 可运行 | VendorConnect 公开 OData API（guest，无需登录） |
| City of Seattle | ✅ 可运行 | 官方公开 RSS feed（`thebuyline.seattle.gov`），详见 `docs/data-sources.md` |

## 暂不支持来源及原因

| 来源 | 状态 | 原因 | 已知线索 |
|---|---|---|---|
| Washington State | 未实现 | 尚未研究/验证 WEBS 是否提供公开 API/RSS/导出 | 需调研 des.wa.gov |
| King County | 未实现 | 尚未研究/验证其采购平台 | 待调研 |
| City of Bellevue | 未实现 | 尚未研究/验证其采购平台 | 待调研 |

未实现来源的手动替代流程：将公开 RFP/RFQ PDF 下载后放入 `opportunities/inbox/`，
后续 `rfp analyze` 命令（尚未实现）将用于分析。

更多细节见 [docs/data-sources.md](docs/data-sources.md) 与 [docs/architecture.md](docs/architecture.md)。
