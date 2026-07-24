# 数据来源调研记录

本文档记录每个目标机构的数据来源调研结论，包括已验证可用的公开接口、
仍需验证的线索，以及诚实标注"尚未调研"的情况。所有来源都必须是公开可访问的，
不允许绕过登录/验证码/限流（见 [../SECURITY.md](../SECURITY.md)）。

## Port of Seattle（已验证，唯一真实 connector）

- 门户：`https://hosting.portseattle.org/sops/`（VendorConnect，Ivalua 采购系统）
- **公开 OData v4 API**：`https://hosting.portseattle.org/sopsapi/Solicitations`
  - 门户自带的 "guest"（无需登录）搜索页面本身就是通过这个 API 拉取数据的，
    经浏览器网络面板确认，`robots.txt` 无限制，不存在绕过任何访问控制的情况。
  - 列表查询用 `$filter`/`$select`/`$expand` 精确取字段（`ProcurementNumber`,
    `ProcurementTitle`, `BidDueDateTime`, `Id`, `SolicitationCategory`, `SolicitationStatus`）。
  - 详情查询用 `$filter=Id eq <guid>`，取 `Description`, `PortContact`,
    `PortContactEmail`, `AdvertisementDate`, `BidDueDateTime`,
    `BidDueDateQuestionCutOffDateTime`, `Department.Name` 等字段。
  - 文档下载端点尚未验证（`fetch_documents()` 暂时返回空列表，需要下一轮调研）。
- 优先级分类：`SourceSystemType.OFFICIAL_API`（最高优先级）。
- 代码位置：`src/gov_contract_os/collectors/port_of_seattle.py`。

## City of Seattle（已验证，第二个真实 connector）

- 官方 RSS Feed：`https://thebuyline.seattle.gov/category/bids-and-proposals/feed/`
  - "The Buy Line" 是西雅图市官方采购博客/公告页面，"Bids and Proposals" 分类
    提供标准的公开 RSS 2.0 feed，无需登录/API key，`robots.txt` 无限制。
  - 2026-07-22 已实际抓取并解析真实 feed（约 20 条当前条目），确认字段结构：
    - `<item><title>` 里混合了状态前缀（`CLOSED-`/`ARCHIVED-`/`CANCELED-`/
      `CANCELLED-`）、标题正文、以及招标编号（内部编号如 `TR0-6221`，
      或带标签的编号如 `RFP#6345`/`ITB# CL0-6135`），格式不统一，需要正则清洗。
    - `<item><category>` 常见值包括 "Bids & Proposals"、"Announcements"、
      "History/Archives"，可用于辅助判断是否为纯公告（不含真实招标）。
    - `<item><description>` 是 HTML 转义后的自由文本，包含：
      1. 指向真正招标平台的外链——`https://cityofseattle.bonfirehub.com/...`
         或 `https://procurement.opengov.com/portal/seattle/...`（两者都未验证
         是否有公开 API，目前只抓外链，不解析平台内部详情）；
      2. 自由格式的 "Due Date: ..." 文本，用正则+`dateutil` 模糊解析提取，
         可能提取失败（`due_at=None`）或不精确；截止时间原文是太平洋时区但
         无机器可读时区标记，一律按 UTC 存储（仅适用于日粒度评分，不适合精确提醒）。
    - 纯公告类条目（如月度"Doing Business With The City"研讨会通知）没有
      编号也没有外链，用这两个特征的缺失作为过滤条件跳过，不当作真实商机存入。
  - `fetch_documents()` 未实现（bonfirehub/opengov 均未验证公开文档下载接口）。
- 优先级分类：`SourceSystemType.OFFICIAL_RSS`。
- 代码位置：`src/gov_contract_os/collectors/city_of_seattle.py`，
  测试位于 `tests/test_collectors_city_of_seattle.py`（离线 fixture，不依赖真实网络）。

## Washington State（GovDelivery 邮件已验证，HTML scraper 未实现）

**Step 1 结论：不需要 WEBS 登录自动化**——WA DES 已经提供了一等公民的免登录
公开发现通道，账户只对提交投标/看已中标详情/个性化 watchlist 有意义。

已在 2026-07-24 用只读浏览器验证：

- **WA DES GovDelivery 邮件订阅**（Granicus 平台，政府标准公开通知服务）：
  - Contracts Connection（合同总览）：
    `https://public.govdelivery.com/accounts/WADES/subscriber/new?topic_id=WADES_109`
  - **IT Contracts Focus（IT/AI 采购专题）——本项目最相关的订阅**：
    `https://public.govdelivery.com/accounts/WADES/subscriber/new?topic_id=WADES_4`
  - 订阅后邮件由 `subscriptions.des.wa.gov` / `subscribe.des.wa.gov` /
    `subscriber.govdelivery.com` 域发出，含标题、简介、指向 des.wa.gov 或
    `pr-webs-vendor.des.wa.gov/Search_BidDetails.aspx?ID=<n>` 的详情链接。
  - **实现方式**：不去 govdelivery.com 抓取，而是**用户自行订阅到自己的邮箱**，
    项目通过 IMAP 只读拉取匹配 govdelivery 域的邮件解析。凭据仅存 `.env`（gitignored）。
  - 优先级分类：`SourceSystemType.OFFICIAL_EMAIL_SUBSCRIPTION`。
  - 代码位置：`src/gov_contract_os/collectors/govdelivery_email.py`，
    连接器名 `govdelivery_email`。
  - 已知限制：邮件模板未完全公开、我们只针对 GovDelivery 通用结构写了防御性
    parser；首次收到真实邮件后需要根据实际字段调整（见连接器 docstring 的
    "TODO after first real emails" 段落）。

- **WEBS BidCalendar 公开页面**（未实现，可后续补充）：
  - URL：`https://pr-webs-vendor.des.wa.gov/BidCalendar.aspx`（**完全免登录**，
    2026-07-24 已用只读浏览器确认，可见 Solicitation Close Date / Title /
    Ref # / Contact / Agency 下拉过滤器）。
  - 详情页 URL 模式：`Search_BidDetails.aspx?ID=<int>`。
  - ASP.NET WebForms，用 `__doPostBack` 做分页；抓取比 GovDelivery 邮件复杂但
    可行。GovDelivery 覆盖不足时再补。
  - **绝不要**去 `fortress.wa.gov`——那是 WEBS 认证侧（登录/注册/awarded contracts），
    不属于公开范畴。

- **WA Open Data（Socrata）**（未实现，市场情报用）：
  - 例：`https://data.wa.gov/Procurements-and-Contracts/WEBS-Vendors-by-commodity-code-and-MWBE-V-Small-st/3kwi-7zsj`
  - 用于历史采购/供应商/commodity code 分析，不是实时招标源。未验证具体端点。

- **DES 主页 robots.txt**（`https://des.wa.gov/robots.txt`）：
  - 标准 Drupal robots，禁 `/admin`、`/user/login|register|password`、`/search`、
    `/node/add` 等系统路径；**未禁** `/sell/bid-opportunities` 或
    `pr-webs-vendor.des.wa.gov` / `apps.des.wa.gov` 子域。

## King County（未验证，未实现）

- **候选平台**：LLM 建议为 OpenGov Procurement，本项目**尚未验证**。
- 未验证要点：
  1. 从 `https://kingcounty.gov/` 官方页面反向确认真实的 procurement portal URL
     和 slug（不能凭平台名+机构名猜测 slug）；
  2. OpenGov 门户本身免登录可浏览（已在 Seattle portal 上验证，见下），
     但内部 JSON API 未抓取；
  3. King County 是否也有 GovDelivery 订阅通道（很可能有）——如果有，
     直接复用 `govdelivery_email` connector，无需新写 scraper。
- `health_check()` 如实报告"尚未研究/验证"。

## City of Bellevue（未验证，未实现）

- 与 King County 相同——LLM 建议 OpenGov 平台，未验证。
- 同样应先查 Bellevue 的 GovDelivery 订阅通道，能覆盖就不用 scraper。

## OpenGov 门户平台（部分已验证）

2026-07-24 用只读浏览器打开 `https://procurement.opengov.com/portal/seattle` 验证：

- **门户完全免登录可浏览**：Projects / Calendar / Vendors 三个 tab，
  Project Title / Project ID / Status / Addenda / Release Date / Close Date
  全部可见。详情页可点入。
- **Cloudflare + 内建 bot 检测**：首次访问有 "Just a moment..." 挑战，几秒过关；
  自动化时必须温和（真实 UA、请求间隔 ≥ 3 秒、遇 challenge 放弃而非硬闯）。
- **`procurement.opengov.com/robots.txt` 返回 404**（SPA 无 robots.txt）；
  OpenGov 官网无独立 browsewrap Terms of Use 页，只有 Privacy Policy
  （`https://opengov.com/privacy-policy/`），明确写：门户上层实际使用条款由
  购买 OpenGov 的政府客户（Seattle/King County/Bellevue 等）的公开信息规则约束。
- **未验证**：SPA 加载 Projects 列表调用的内部 JSON API 端点（下一轮任务，
  用浏览器 Network 面板定位后可为多城市共用一个 connector）。

## 通用原则（适用于未来新增来源）

1. 优先级：官方 API > 官方邮件订阅 (GovDelivery) ≈ 官方 RSS/Atom > 官方数据下载
   > 官方公开搜索页 > 纯 HTML 解析 > 浏览器自动化（浏览器自动化仅作最后手段，
   且必须是公开页面，不得绕过任何验证）。
2. 任何一个来源接入前，必须先用只读方式（`fetch_webpage`/浏览器只读检查网络面板）
   确认该端点是"公开、无需登录、非绕过验证码/限流"的，再写抓取代码。
3. **凭据管理**：任何需要账户的通道（例如 IMAP 拉 GovDelivery 邮件），
   凭据只能存本地 `.env`（gitignored），绝不进代码/日志/commit。
4. 无法验证或没有线索的来源，`health_check()` 必须诚实报告状态和原因，
   并给出人工替代方案（如手动下载 PDF 放入 `opportunities/inbox/`），
   不允许编造 URL 或字段结构。
5. LLM 建议可以作为**调研起点**，但每一条 URL / 平台归属 / API 猜测都必须由人
   或本项目的只读工具单独复核后，才能写入代码或 connector 配置。
