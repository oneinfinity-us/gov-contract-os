# Port of Seattle 采购周报 — 2026-07-21

**数据来源**：https://hosting.portseattle.org/sops/#/Solicitations  
**抓取时间**：2026-07-21  
**执行**：port-of-seattle-weekly-review skill  

> ⚠️ **重要限制**：`company/capabilities.md`、`company/company-profile.md`、`company/founder-bio.md` 均为 TODO 未填写，`company/past-performance/` 无任何案例。本次评估仅基于招标内容与评分维度，"能力匹配"和"可引用经验"两项对所有机会均记为 0 分。**强烈建议优先补全公司资料后重新运行评估。**

---

## 摘要

| 项目 | 数量 |
|---|---|
| 平台当前活跃公告数 | 22 |
| 其中 Open（截止日期未到） | 9 |
| 其中 Open（截止日期已过，仍在平台） | 11 |
| Future | 1 |
| Information（无投标截止日） | 2 |
| 本周新增（与本地已跟踪对比） | 22（首次运行，全部为新） |
| 建议跟进（go） | 0 |
| 建议放弃（no-bid） | 7 |
| 待更多信息 | 2 |
| 截止日期已过，监控再发 | 1 |

---

## 一、截止日期未到的机会（按截止日期升序）

### 26-36 — Emergency Elevator Communication System (EECS)

| 字段 | 值 |
|---|---|
| 机构 | Port of Seattle |
| 招标编号 | 26-36 |
| 类别 | Goods and Services |
| 状态 | Open |
| 截止日期 | 2026-07-28 14:00 PT |
| 预算范围 | 未公开 |
| 来源链接 | https://hosting.portseattle.org/sops/#/Solicitations/Detail/4c2970c9-764d-f111-bd3c-005056aa9c71 |

**评估得分：45 / 100**

| 维度 | 得分 | 满分 | 说明 |
|---|---|---|---|
| Microsoft AI / Copilot / Azure / agent fit | 5 | 25 | 通信系统可能含 IoT/云端组件，但不确定 |
| 软件开发与自动化适配 | 10 | 15 | 电梯通信系统含软件/嵌入式组件 |
| Seattle / WA 地理匹配 | 10 | 10 | Port of Seattle，位于西雅图 |
| 合同规模适合小公司 | 7 | 10 | Goods and Services 类，规模未知 |
| 分包潜力 | 5 | 10 | 作为软件集成分包有可能 |
| 可引用相关经验 | 0 | 10 | ⚠️ 公司经验数据缺失 |
| 强制资质要求合理性 | 5 | 10 | 需确认是否要求特定通信/电梯资质 |
| 时间可行性 | 3 | 10 | ⛔ 截止 7 天后（7/28），时间极紧 |

**建议角色**：Sub（如能找到主承包商）  
**建议**：需更多信息  
**理由**：含软件/通信组件，与公司潜在方向有关联；但截止日期仅剩 7 天，且公司能力资料完全缺失，无法在此时间内准备有竞争力的投标。  
**能力差距**：通信系统集成经验未知、电梯行业资质未知、公司资质全部待填  
**立即行动**：
1. 查看详情页确认是否允许纯软件集成商参与，或是否需要实物产品供应资质
2. 补全 `company/capabilities.md` 判断是否有通信/IoT 经验可引用
3. 如确认不适合本次，标记为"监控类型"——未来类似机会提前准备

---

### P-00322887 — Healthcare Navigation Services

| 字段 | 值 |
|---|---|
| 机构 | Port of Seattle |
| 招标编号 | P-00322887 |
| 类别 | Goods and Services |
| 状态 | Open |
| 截止日期 | 2026-07-31 14:00 PT |
| 预算范围 | 未公开 |
| 来源链接 | https://hosting.portseattle.org/sops/#/Solicitations/Detail/fd4de966-dd74-f111-bd41-005056aa9c71 |

**评估得分：30 / 100**

| 维度 | 得分 | 满分 | 说明 |
|---|---|---|---|
| AI / Azure / agent fit | 3 | 25 | 可能涉及数字健康导航工具，但主要是服务 |
| 软件开发与自动化 | 2 | 15 | 服务类为主 |
| Seattle / WA 地理匹配 | 10 | 10 | ✓ |
| 合同规模 | 7 | 10 | 员工福利类，规模适中 |
| 分包潜力 | 3 | 10 | 低 |
| 可引用相关经验 | 0 | 10 | ⚠️ 缺失 |
| 强制资质要求合理性 | 0 | 10 | 很可能要求医疗/保险领域资质 |
| 时间可行性 | 5 | 10 | 10 天，非常紧张 |

**建议**：No Bid  
**理由**：主要是人力资源/医疗服务领域，与软件/AI 公司核心能力不匹配；时间极紧。

---

### 00322873 — Media Buying and Creative Support IDIQ

| 字段 | 值 |
|---|---|
| 机构 | Port of Seattle |
| 招标编号 | 00322873 |
| 类别 | Consulting Services |
| 状态 | Open |
| 截止日期 | 2026-08-04 12:00 PT |
| 预算范围 | 未公开（IDIQ，多次任务订单） |
| 来源链接 | https://hosting.portseattle.org/sops/#/Solicitations/Detail/779b2e76-fe55-f111-bd3f-005056aa9c71 |

**评估得分：48 / 100**

| 维度 | 得分 | 满分 | 说明 |
|---|---|---|---|
| AI / Azure / agent fit | 8 | 25 | 数字媒体采购可结合 AI 创意工具、自动化投放 |
| 软件开发与自动化 | 5 | 15 | 数字营销自动化有一定关联 |
| Seattle / WA 地理匹配 | 10 | 10 | ✓ |
| 合同规模 | 8 | 10 | IDIQ 灵活，小公司可作为候选供应商 |
| 分包潜力 | 7 | 10 | 可作为 AI/技术分包参与主媒体机构的团队 |
| 可引用相关经验 | 0 | 10 | ⚠️ 缺失 |
| 强制资质要求合理性 | 5 | 10 | 需确认是否要求媒体代理资质/最低采购量资质 |
| 时间可行性 | 5 | 10 | 14 天，紧张但可行 |

**建议角色**：Sub / Teaming Partner（与成熟媒体机构联合）  
**建议**：需更多信息  
**理由**：IDIQ 合同结构对小公司友好；如公司有 AI 辅助创意或数字营销自动化能力，可作为技术分包切入。需查看详情页确认是否允许无传统媒体采购资质的技术供应商参与。  
**能力差距**：无传统媒体采购经验（推测）；公司 AI/数字营销能力待确认  
**立即行动**：
1. 打开详情页查看完整 SOW 和强制资质要求
2. 补全 `company/capabilities.md`，确认是否有数字营销/AI 创意工具能力
3. 在 `opportunities/port-of-seattle/` 建立跟踪文件，标记为"评估中"

---

### 00322870 — Main Terminal Improvement Program Emergency Power

| 字段 | 值 |
|---|---|
| 招标编号 | 00322870 |
| 类别 | Consulting Services |
| 截止日期 | 2026-08-06 00:00 PT |
| 来源链接 | https://hosting.portseattle.org/sops/#/Solicitations/Detail/ac7df8af-9748-f111-bd3c-005056aa9c71 |

**评估得分：30 / 100** — 电气工程咨询，需注册工程师资质。**No Bid**。

---

### MC-0321006-2 — SEA South Concourse Evolution, Bid Package 2

| 字段 | 值 |
|---|---|
| 招标编号 | MC-0321006-2 |
| 类别 | Major Construction |
| 截止日期 | 2026-08-11 14:00 PT |
| 来源链接 | https://hosting.portseattle.org/sops/#/Solicitations/Detail/700a8c47-2c81-f111-bd41-005056aa9c71 |

**评估得分：23 / 100** — 大型机场建设，需建筑总承包资质和履约担保。**No Bid**。

---

### 26-72 — Pre-Conditioned Air Modular Bridge Mounted Hose Trolley System

| 字段 | 值 |
|---|---|
| 招标编号 | 26-72 |
| 类别 | Goods and Services |
| 截止日期 | 2026-08-11 14:00 PT |
| 来源链接 | https://hosting.portseattle.org/sops/#/Solicitations/Detail/ab7eaea4-917c-f111-bd41-005056aa9c71 |

**评估得分：30 / 100** — 物理硬件供应（登机桥管道系统），非软件/AI 业务。**No Bid**。

---

### 00322878 — South Concourse Renovation Testing and Special Inspections

| 字段 | 值 |
|---|---|
| 招标编号 | 00322878 |
| 类别 | Consulting Services |
| 截止日期 | 2026-08-14 12:00 PT |
| 来源链接 | https://hosting.portseattle.org/sops/#/Solicitations/Detail/161e8c09-70e8-ee11-9153-005056bd83e7 |

**评估得分：30 / 100** — 建筑材料测试与特种检验，需具备资质的检测机构。**No Bid**。

---

### MC-0322591 — Terminal 25 South Habitat Restoration GC/CM Pre-Construction

| 字段 | 值 |
|---|---|
| 招标编号 | MC-0322591 |
| 类别 | Major Construction |
| 截止日期 | 2026-08-26 14:00 PT |
| 来源链接 | https://hosting.portseattle.org/sops/#/Solicitations/Detail/8f647a52-5fe3-ef11-bd25-005056aa9c71 |

**评估得分：25 / 100** — 生态修复与建设管理，需建筑许可和担保。**No Bid**。

---

### SW-0322908 — Electrical Unit Price Portwide 2026 (Future)

| 字段 | 值 |
|---|---|
| 招标编号 | SW-0322908 |
| 类别 | Small Works |
| 状态 | Future |
| 截止日期 | 2026-08-26 14:00 PT |
| 来源链接 | https://hosting.portseattle.org/sops/#/Solicitations/Detail/e49c2142-cb7f-f111-bd41-005056aa9c71 |

**评估得分：25 / 100** — 电气承包，需持照电气承包商资质。**No Bid**。

---

## 二、截止日期已过但仍显示 Open（监控）

以下机会截止日期已过，目前仍在平台上显示为 Open（可能处于评估阶段或将发布修订版）。

| 招标编号 | 标题 | 原截止日期 | 类别 | 备注 |
|---|---|---|---|---|
| 26-57 | Integrated Engineering Information Management System (IEIMS) | 2026-06-05 | Goods and Services | ⭐ **重点监控**：软件信息管理系统，与公司潜在方向高度相关 |
| 00322809 | Marine Stormwater Utility Services IDIQ | 2026-07-14 | Consulting Services | 环境工程，非软件 |
| 00322826 | Deferred Compensation Retirement Third Party Administrator | 2026-07-02 | Consulting Services | HR/金融，非软件 |
| 25-24 | Port Wide Coffee Service | 2026-06-30 | Goods and Services | 无关 |
| 00322768 | Benefits Account | 2026-06-30 | Consulting Services | HR/福利，非软件 |
| 00322734 | Maritime Clean Energy, Fuels & Technologies IDIQ | 2026-06-05 | Consulting Services | 海事/能源，非软件 |
| 00322814 | Maritime Sustainable Fuels Landscape Assessment IDIQ | 2026-06-05 | Consulting Services | 海事/能源，非软件 |
| P-00322696 | 2026-2027 Tourism Marketing Support Program | 2026-03-10 | Consulting Services | 可能有数字营销组件，但已过期太久 |
| 00322670 | RFI Civil-Environmental Engineering Sponsoring and Mentoring | 2026-02-09 | Consulting Services | RFI（信息征集），非软件 |
| 00322367 | South King and Port Communities Fund Environmental Improvement Program Cycle 5 | 2025-10-31 | Consulting Services | 环境，非软件 |
| 00322359 | 2025 Economic Development City Partnership | 2025-10-10 | Goods and Services | 经济发展，非软件 |

### ⭐ 26-57 IEIMS — 重点说明

**Integrated Engineering Information Management System (IEIMS)** 是本批次与软件/技术公司最相关的机会：
- 性质：信息管理系统（软件平台）
- 截止日期已过（2026-06-05），当前仍在平台  
- **建议**：每周检查是否重新发布或有修订通知；若重新开放，立即启动评估。

---

## 三、Information 类（无投标截止日，仅参考）

| 招标编号 | 标题 | 类别 |
|---|---|---|
| Webinar | Know Your Rights: Immigration Updates for Employers Webinar | Information |
| UMP-Mechanical | SEA - Utility Master Plan - Mechanical Systems ONLY | Information |

---

## 四、行动优先级

| 优先级 | 行动 | 截止 |
|---|---|---|
| 🔴 立即 | 补全 `company/capabilities.md`、`company/company-profile.md`、`company/founder-bio.md` | 本周内 |
| 🔴 立即 | 查看 26-36 EECS 详情页，确认是否允许纯软件/集成商参与（截止 7/28） | 今天 |
| 🟡 本周 | 查看 00322873 Media Buying IDIQ 详情页，确认资质要求（截止 8/4） | 7/25 前 |
| 🟡 持续 | 监控 26-57 IEIMS 是否重新发布 | 每周 |
| 🟢 下次周报前 | 为已确认 No Bid 的机会在 `opportunities/port-of-seattle/` 建立归档文件 | 7/28 前 |

---

## 注意事项

- 本报告为草稿，需人工审阅后方可采取任何行动。
- 评估因公司资料缺失而严重受限，所有评分仅供参考。
- 不得自动提交提案或联系任何外部机构。
- 下次运行建议：2026-07-28（周一）。
