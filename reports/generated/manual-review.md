# 机会评估报告（Manual Review）

- 执行流程：`workflows/opportunity-review.md`
- 生成时间：2026-07-21（UTC）
- 输入文件：`opportunities/inbox/Presentation - 2026.06.17 ICT First Look.pdf`（38 页，Port of Seattle "PortGen First Look: Information and Communication Technology Contracts"，2026-06-17 宣讲）
- 说明：该文件是**信息宣讲材料（First Look），非正式招标**。其中金额、日期、要求均为"预估、可能变动"，正式条款以后续实际招标文件为准（见 PDF 第 2 页免责声明）。本报告对文件中可识别的每个机会分别评估。

> **重要前置约束**：`company/` 下的公司简介、能力清单、创始人简历目前**全部为 TODO 占位**，`past-performance/` 无案例。按 `SECURITY.md` 与 workflow 边界，**不得编造资质/业绩**。因此下列所有"能力匹配、业绩可证明性、强制资质是否满足"均标记为**待人工确认**，评分为在"公司具备通用软件/AI/Azure 交付能力"这一假设下的**初步倾向性打分**，最终以补齐 `company/` 真实信息后为准。

---

## 汇总表

| # | 机会 | 类型 | 预估金额 | WMBE 目标 | 预计发布 | 建议角色 | 初步评分 |
|---|---|---|---|---|---|---|---|
| 1 | AI Consulting Services IDIQ | IDIQ | $400K–$500K | TBD | Q3 2026 | Prime / Sub（待定） | 72 |
| 2 | Azure Consulting Services IDIQ | IDIQ | $1.8M | TBD | Q3 2026 | Sub / Teaming | 70 |
| 3 | Technology Services IDIQ（人力增援）| IDIQ | $4.5M–$5M | TBD | Q4 2026 | Sub / Teaming | 63 |
| 4 | HubSpot Consulting Services IDIQ | IDIQ | NTE $500K | No Goal | 6–7/2026（最近）| Sub / Teaming | 55 |
| 5 | PeopleSoft Technical Services | Project/IDIQ | NTE $1.9M | 6% | 7/2026（最近）| No Bid / Sub | 40 |
| 6 | Virtualization Consulting IDIQ | IDIQ | $150K–$200K | TBD | Q1 2027 | Sub / No Bid | 42 |
| 7 | Property Management System Refresh | 采购 | $800K–$1.2M | N/A | Q3 2026 | No Bid | 25 |
| 8 | Fire Alarm Monitoring System Refresh | 采购 | $250K–$350K | N/A | Q2 2027 | No Bid | 12 |

优先级建议：**#1 AI IDIQ 与 #2 Azure IDIQ 为主攻方向**（命中微软 AI/Azure 最高权重，且 Q3 2026 即将发布，时间上最紧）。

---

## 1. AI Consulting Services IDIQ

1. **机会名称**：AI Consulting Services IDIQ
2. **机构**：Port of Seattle — ICT Department
3. **招标编号**：未公布（First Look 阶段，尚未正式广告）
4. **截止日期**：未定；预计发布 Q3 2026，惯例为广告后约 2 周预投标会、约 30 天提交（依 PDF 内 HubSpot/PeopleSoft 时间表推断）
5. **预估价值**：$400K–$500K
6. **强制要求**：文件未列明；WMBE 目标 TBD。→ **待人工确认**（发布后看正式 RFP）
7. **建议角色**：Prime 或 Sub —— **待定**（取决于公司 AI 交付业绩与产能，见 `company/` 补齐后）
8. **评分**：**72 / 100**
   - MS AI/Copilot/Azure/agent 契合：**25/25**（正是 Port 对 AI 使用与落地的咨询需求）
   - 软件开发/自动化契合：12/15
   - Seattle/WA 地理契合：10/10
   - 合同规模适配小企业：10/10（$400–500K，IDIQ 对小企业友好）
   - 分包潜力：8/10
   - 相关经验可证明：**?/10 → 待确认**（暂计 0，`company/` 无数据）
   - 强制要求合理：7/10（未知，暂中性）
   - 时间可行性：**待确认**（Q3 2026，最紧迫之一）→ 暂计 0
9. **能力缺口**：需确认公司是否有可引用的 AI 咨询/落地案例、是否具备任何 WMBE/SBE 认证（Port 五年目标 16% WMBE，认证是加分/门槛）。
10. **接下来三步**：
    1. 在 **VendorConnect** 注册并加入 Diversity in Contracting 邮件列表，确保能收到该 IDIQ 的正式广告通知（PDF 第 5 页）。
    2. 补齐 `company/capabilities.md` + `past-performance/` 中的 AI 相关能力与案例，评估自身以 Prime 还是 Sub 定位。
    3. 联系人跟进：Harold Federow（Contract & Compliance Advisor, ICT，Federow.h@portseattle.org）确认该 IDIQ 时间表与认证要求——**外发前需人工审核**。
11. **来源**：`Presentation - 2026.06.17 ICT First Look.pdf` 第 28 页（"Future Consulting Opportunity — AI Consulting Services IDIQ"）

---

## 2. Azure Consulting Services IDIQ

1. **机会名称**：Azure Consulting Services IDIQ
2. **机构**：Port of Seattle — ICT Department
3. **招标编号**：未公布（First Look 阶段）
4. **截止日期**：未定；预计发布 Q3 2026
5. **预估价值**：$1.8M
6. **强制要求**：文件未列明；预期需要 Azure/云架构、安全、韧性相关资质与业绩。→ **待人工确认**
7. **建议角色**：Sub / Teaming Partner（$1.8M 规模较大，若公司体量小，建议以分包或组队方式；PDF 第 34 页明确 Microsoft 认证对 IT 合同有帮助）
8. **评分**：**70 / 100**
   - MS AI/Copilot/Azure/agent 契合：**25/25**（纯 Azure 云采纳/现代化/优化）
   - 软件开发/自动化契合：10/15
   - Seattle/WA 地理契合：10/10
   - 合同规模适配小企业：6/10（$1.8M 偏大，独立 Prime 有产能风险）
   - 分包潜力：9/10
   - 相关经验可证明：**?/10 → 待确认**（暂计 0）
   - 强制要求合理：7/10（未知，暂中性）
   - 时间可行性：**待确认**（Q3 2026）→ 暂计 0
9. **能力缺口**：Azure 架构评估/安全态势/韧性方面的可引用业绩；是否持有 Microsoft 合作伙伴认证（Azure）；小企业独立承接 $1.8M 的产能与担保能力。
10. **接下来三步**：
    1. VendorConnect 注册 + 邮件列表（同 #1，一次完成覆盖所有 Port 机会）。
    2. 评估组队策略：物色可做 Prime 的 Azure 合作伙伴，公司以专长分包切入（`contacts/contacts.csv` 建库）。
    3. 盘点/确认公司 Azure 认证与案例，写入 `company/` 与 `past-performance/`。
11. **来源**：`Presentation - 2026.06.17 ICT First Look.pdf` 第 29 页

---

## 3. Technology Services IDIQ（人员增援）

1. **机会名称**：Technology Services IDIQ（Staff Augmentation：开发、PM、QA 等）
2. **机构**：Port of Seattle — ICT Department
3. **招标编号**：未公布
4. **截止日期**：未定；预计发布 Q4 2026
5. **预估价值**：$4.5M–$5M
6. **强制要求**：未列明；范围极广（按具体任务派单）。→ **待人工确认**
7. **建议角色**：Sub / Teaming Partner（总额大，适合以人力资源分包进入）
8. **评分**：**63 / 100**
   - MS AI/Azure 契合：12/25（范围泛，非 AI 专向，但可包含）
   - 软件开发/自动化契合：13/15（开发/QA/PM 增援正是软件交付）
   - 地理契合：10/10
   - 合同规模适配小企业：5/10（$4.5–5M 大，但 IDIQ 按任务派单，可小额切入）
   - 分包潜力：9/10
   - 相关经验可证明：**待确认** → 暂计 0
   - 强制要求合理：7/10
   - 时间可行性：**待确认**（Q4 2026，较宽裕）→ 暂计 0
9. **能力缺口**：可调配的开发/QA/PM 产能与人员简历库；过往人力增援类业绩。
10. **接下来三步**：
    1. VendorConnect 注册 + 邮件列表。
    2. 建立可派遣人员/子承包商能力矩阵（技能、可用性、费率）。
    3. Q4 前锁定 1–2 家可组队的 Prime。
11. **来源**：`Presentation - 2026.06.17 ICT First Look.pdf` 第 30 页

---

## 4. HubSpot Consulting Services IDIQ

1. **机会名称**：HubSpot Consulting Services IDIQ
2. **机构**：Port of Seattle — ICT Department
3. **招标编号**：未公布
4. **截止日期**：未定；PDF 第 20 页时间表：广告 6–7/2026，广告后约 2 周预投标会，约 30 天提交 → **最临近的机会之一，时间紧**
5. **预估价值**：Not to Exceed $500K
6. **强制要求**：Category=Consulting Services；WMBE Goal=**No Goal**；Certifications=**TBD**；范围含 HubSpot 需求梳理、数据模型/流程设计、自定义开发与集成、自动化工作流、培训、系统支持、项目管理。→ 需 HubSpot 平台专长
7. **建议角色**：Sub / Teaming Partner（除非公司有 HubSpot 专长，否则以组队为主；PDF 第 34 页把 HubSpot 列为 WMBE 参与机会点）
8. **评分**：**55 / 100**
   - MS AI/Azure 契合：3/25（HubSpot 非微软栈，仅弱相关）
   - 软件开发/自动化契合：13/15（自定义开发、集成、自动化工作流契合度高）
   - 地理契合：10/10
   - 合同规模适配小企业：10/10（NTE $500K，IDIQ）
   - 分包潜力：8/10
   - 相关经验可证明：**待确认** → 暂计 0
   - 强制要求合理：8/10（No WMBE goal，门槛相对低）
   - 时间可行性：3/10（发布最早、窗口最短，若现在无 HubSpot 现成能力，准备时间不足）
9. **能力缺口**：HubSpot 平台实施/开发的专门经验与可引用案例；是否需要 HubSpot 认证（TBD）。
10. **接下来三步**：
    1. **立即** VendorConnect 注册（此项最快发布，别错过广告）。
    2. 评估公司是否有 HubSpot 实操能力/认证——无则决定 No Bid 或快速找 HubSpot 分包伙伴。
    3. 关注广告发布，及时成为 Plan Holder 并参加预投标会。
11. **来源**：`Presentation - 2026.06.17 ICT First Look.pdf` 第 18–20 页

---

## 5. PeopleSoft Technical Services

1. **机会名称**：PeopleSoft Technical Services（支持 PeopleSoft HCM/Financials 9.2 与 Oracle Taleo）
2. **机构**：Port of Seattle — ICT Department
3. **招标编号**：未公布
4. **截止日期**：未定；PDF 第 25 页：广告 7/2026，广告后约 2 周预投标会，约 30 天提交 → **临近**
5. **预估价值**：Not to Exceed $1.9M
6. **强制要求**：**Certification: Oracle at vendor level（供应商级 Oracle 认证）**；WMBE Goal 6%；需 PeopleSoft 开发/管理/功能分析/PM 等角色，评估看 PeopleSoft 深度技术能力（SQR、App Engine、PeopleCode、Integration Broker、Fluid、AWE 等）。→ 门槛高且专用
7. **建议角色**：**No Bid**（除非公司恰有 PeopleSoft/Oracle 专长）/ 否则 Sub
8. **评分**：**40 / 100**
   - MS AI/Azure 契合：0/25（Oracle PeopleSoft 生态，与微软栈无关）
   - 软件开发/自动化契合：8/15（是开发工作，但为 PeopleSoft 专用技能）
   - 地理契合：10/10
   - 合同规模适配小企业：6/10（NTE $1.9M）
   - 分包潜力：6/10
   - 相关经验可证明：**待确认** → 暂计 0
   - 强制要求合理：**2/10**（供应商级 Oracle 认证是硬门槛，小企业通常不满足）
   - 时间可行性：**待确认**（7/2026 临近）→ 暂计 0（若无现成 PeopleSoft 团队，实际不可行）
9. **能力缺口**：供应商级 Oracle 认证、PeopleSoft/Taleo 专业顾问团队与业绩——这是明确的强制门槛。
10. **接下来三步**：
    1. 确认公司是否持有供应商级 Oracle 认证与 PeopleSoft 团队——**不满足则明确 No Bid**。
    2. 若不 Bid，可考虑作为分包向具备资质的 Prime 提供边缘能力（如 PM）。
    3. 记录决策，避免后续重复评估。
11. **来源**：`Presentation - 2026.06.17 ICT First Look.pdf` 第 22–25 页

---

## 6. Virtualization Consulting IDIQ

1. **机会名称**：Virtualization Consulting IDIQ（虚拟化平台评估/优化路线图）
2. **机构**：Port of Seattle — ICT Department
3. **招标编号**：未公布
4. **截止日期**：未定；预计发布 Q1 2027（较远）
5. **预估价值**：$150K–$200K
6. **强制要求**：未列明；需虚拟化平台（健康度/性能/安全/架构）评估能力。→ **待人工确认**
7. **建议角色**：Sub / No Bid（视公司是否有虚拟化/基础设施专长）
8. **评分**：**42 / 100**
   - MS AI/Azure 契合：5/25（可能涉及 Hyper-V/Azure，但主体是虚拟化平台评估）
   - 软件开发/自动化契合：4/15
   - 地理契合：10/10
   - 合同规模适配小企业：10/10（$150–200K，小额友好）
   - 分包潜力：6/10
   - 相关经验可证明：**待确认** → 0
   - 强制要求合理：7/10
   - 时间可行性：**待确认**（Q1 2027，很宽裕）→ 0
9. **能力缺口**：虚拟化平台（VMware/Hyper-V 等）评估与安全态势专业经验。
10. **接下来三步**：
    1. 归档观察，Q1 2027 前无需紧急动作。
    2. 若公司有基础设施/虚拟化能力再评估是否投。
    3. VendorConnect 邮件列表已覆盖通知。
11. **来源**：`Presentation - 2026.06.17 ICT First Look.pdf` 第 31 页

---

## 7. Property Management System Refresh（采购）

1. **机会名称**：Property Management System Refresh
2. **机构**：Port of Seattle
3. **招标编号**：未公布
4. **截止日期**：未定；预计发布 Q3 2026
5. **预估价值**：$800K–$1.2M
6. **强制要求**：未列明；本质是**物业管理系统（软件产品）采购**，非咨询/开发服务。→ 需具备成品 PMS 解决方案
7. **建议角色**：**No Bid**（除非公司是 PMS 产品供应商/转售商）
8. **评分**：**25 / 100**
   - MS AI/Azure：2/25；开发/自动化：2/15；地理：10/10；规模：6/10；分包：3/10；业绩：0；要求合理：2/10（需产品）；时间：0
9. **能力缺口**：需要现成的物业管理系统产品与实施能力——与 AI/软件咨询定位不符。
10. **接下来三步**：（1）标记 No Bid；（2）如有合作的 PMS 厂商可考虑转介/组队；（3）归档。
11. **来源**：`Presentation - 2026.06.17 ICT First Look.pdf` 第 32 页

---

## 8. Fire Alarm Monitoring System Refresh（采购）

1. **机会名称**：Fire Alarm Monitoring System Refresh（SEA 机场火警监控系统更换）
2. **机构**：Port of Seattle
3. **招标编号**：未公布
4. **截止日期**：未定；预计发布 Q2 2027
5. **预估价值**：$250K–$350K
6. **强制要求**：未列明；属**消防/楼宇安全系统**专业工程，需相关行业资质。→ 与公司 IT/AI 定位无关
7. **建议角色**：**No Bid**
8. **评分**：**12 / 100**（几乎不契合任何评分维度：AI/Azure 0、开发 0、地理 10、其余低）
9. **能力缺口**：消防报警系统集成资质与业绩——超出公司业务范围。
10. **接下来三步**：（1）标记 No Bid；（2）无需动作；（3）归档。
11. **来源**：`Presentation - 2026.06.17 ICT First Look.pdf` 第 33 页

---

## 跨机会说明与人工确认清单

**AI 辅助披露检查（依 SECURITY.md 第 4 步）**：本输入为宣讲材料，未包含任何招标条款，因此**无法确认**各 IDIQ 是否对 AI 辅助撰写投标文件有披露/限制要求。→ **待每个机会正式发布后，在其 RFP 中逐一核对。**

**必须由人工确认的事项：**
1. `company/` 三份文件（简介、能力、创始人简历）与 `past-performance/` 案例——补齐前所有"业绩可证明性/时间可行性"项按 0 计，评分会明显偏低；补齐后需重算。
2. 公司是否持有任何 **WMBE / SBE / DBE 认证**（Port 五年目标 16% WMBE，多数机会有 WMBE 目标或视为加分）。
3. 针对 #5：是否持有**供应商级 Oracle 认证**（硬门槛）。
4. 针对 #4：是否有 **HubSpot** 实操能力/认证（发布最早，窗口最短）。
5. 针对 #1/#2：是否持有 **Microsoft 合作伙伴认证（Azure）** 及可引用的 AI/Azure 案例。
6. VendorConnect 平台入口 URL / 是否有官方 API（用于自动化后续机会采集；采集前须核对 ToS/robots，见 SECURITY.md）。

**统一的第一步（覆盖全部机会）**：在 Port of Seattle **VendorConnect** 注册，并订阅 Diversity in Contracting 邮件列表，以便正式广告发布时第一时间收到通知。

**关键联系人（来自 PDF）**：
- Harold Federow — Contract & Compliance Advisor, ICT — Federow.h@portseattle.org
- Kelvin Dankwa — Community Engagement & Training Program Specialist — dankwa.k@portseattle.org

> 以上所有内容均为**草稿，需人工审核**。未发送任何邮件、未联系任何外部方、未提交任何提案、未修改输入文件、未执行 git push。
