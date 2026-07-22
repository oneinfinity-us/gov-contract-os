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

## City of Seattle（有线索，未验证，未实现）

两条候选线索（通过 `fetch_webpage` 调研得到，尚未写解析代码验证结构）：

1. **OpenGov 采购门户**：`https://procurement.opengov.com/portal/seattle`
   - 城市可能把招标发布迁移到了第三方 OpenGov 平台；未确认是否有公开 API 或
     只能网页浏览，未确认列表/详情字段结构。
2. **官方 RSS Feed**：`https://thebuyline.seattle.gov/category/bids-and-proposals/feed/`
   - "The Buy Line" 是西雅图市官方采购博客/公告页面，其"Bids and Proposals"分类
     提供标准 RSS/Atom feed。**如果内容结构稳定，这可能是 4 个未实现来源中最快能
     落地的一个**（RSS 优先级高于网页爬取，见 SECURITY.md 的来源优先级顺序），
     但尚未解析过真实 feed 条目，字段映射未知，下一轮需要先抓样本验证。

`health_check()` 的 `reason`/`recommended_alternative` 已经写入了以上两条线索，
方便下一轮直接按图索骥。

## Washington State（未验证，未实现）

候选：WEBS（Washington's Electronic Business Solution，由 DES 运营）可能提供
公开数据源，但本轮没有时间验证是否存在公开 API/RSS/批量导出、是否需要注册账号
才能查看列表（如需登录查看，则不符合"仅使用公开可访问信息"的边界，需要另找
替代方案，例如手动 inbox 流程）。`health_check()` 如实报告"尚未研究/验证"。

## King County（未验证，未实现）

没有找到任何候选线索。`health_check()` 如实报告"尚未研究/验证"，未编造任何
候选 URL 或 API。下一轮需要从头调研其采购平台。

## City of Bellevue（未验证，未实现）

同 King County，没有找到任何候选线索，`health_check()` 如实报告"尚未研究/验证"。

## 通用原则（适用于未来新增来源）

1. 优先级：官方 API > 官方 RSS/Atom > 官方数据下载 > 官方公开搜索页 > 纯 HTML 解析
   > 浏览器自动化（浏览器自动化仅作最后手段，且必须是公开页面，不得绕过任何验证）。
2. 任何一个来源接入前，必须先用只读方式（`fetch_webpage`/浏览器只读检查网络面板）
   确认该端点是"公开、无需登录、非绕过验证码/限流"的，再写抓取代码。
3. 无法验证或没有线索的来源，`health_check()` 必须诚实报告状态和原因，
   并给出人工替代方案（如手动下载 PDF 放入 `opportunities/inbox/`），
   不允许编造 URL 或字段结构。
