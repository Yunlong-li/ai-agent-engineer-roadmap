# 项目 1：企业经营数据分析 Agent

## 1. 项目定位

这是最推荐放在简历第一位的项目。它模拟大厂真实业务：运营、销售、商分同学用自然语言提问，Agent 自动查数据库、查业务文档、做统计分析并生成报告。

一句话介绍：

```text
基于 LLM + RAG + SQL Tool + Python Analysis Tool 的企业经营分析 Agent，支持自然语言提问、任务规划、数据查询、业务知识检索、指标归因、报告生成、trace 可观测和离线评测。
```

## 2. 目标用户

- 运营：想知道 GMV、转化率、活动效果。
- 商业分析师：想快速定位指标波动原因。
- 管理者：想要结构化经营报告。

## 3. 核心场景

用户输入：

```text
分析最近 30 天 GMV 下滑原因，并给出可执行建议。
```

Agent 输出：

- 结论摘要。
- GMV 趋势。
- 按渠道、品类、地区拆解。
- 活动和商品规则引用。
- 可能原因排序。
- 建议动作。
- 使用过的 SQL 和引用来源。

## 4. 架构

```text
User
  |
  v
FastAPI
  |
  v
Agent Orchestrator
  |
  +--> Planner
  +--> SQL Tool ----------> SQLite/PostgreSQL
  +--> RAG Tool ----------> Vector Store / BM25
  +--> Python Tool -------> Sandbox
  +--> Report Generator
  +--> Trace Logger
  +--> Eval Runner
```

## 5. 模块设计

### Planner

输入用户目标，输出结构化计划：

```json
{
  "goal": "分析最近 30 天 GMV 下滑原因",
  "steps": [
    {"type": "sql", "task": "查询最近 30 天 GMV 趋势"},
    {"type": "sql", "task": "按渠道、品类、地区拆解 GMV"},
    {"type": "rag", "task": "查询同期活动规则和指标口径"},
    {"type": "python", "task": "计算下滑贡献度"},
    {"type": "report", "task": "生成分析报告"}
  ]
}
```

### SQL Tool

要求：

- 只允许 SELECT。
- 表白名单。
- 自动加 limit。
- 捕获 SQL 错误。
- 返回列名、行数、样例数据。

示例接口：

```python
def run_readonly_sql(query: str, user_id: str) -> ToolResult:
    assert_select_only(query)
    assert_table_whitelist(query, allowed_tables=["orders", "products", "traffic", "campaigns"])
    rows = db.execute(query).fetchmany(200)
    return ToolResult(ok=True, data={"rows": rows})
```

### RAG Tool

检索对象：

- 指标口径文档。
- 活动规则文档。
- 商品分类说明。
- 售后和退款政策。

返回：

```json
{
  "chunks": [
    {
      "chunk_id": "metric_definitions.md#gmv",
      "text": "GMV 指支付成功订单金额...",
      "score": 0.87
    }
  ]
}
```

### Python Analysis Tool

能力：

- 计算环比、同比。
- 找出下降贡献最大的渠道/品类。
- 输出图表数据。

注意：

- 真实生产必须用沙箱隔离。
- 限制执行时间和内存。
- 禁止文件系统和网络危险访问。

### Report Generator

报告结构：

```json
{
  "summary": "...",
  "key_findings": ["..."],
  "evidence": [
    {"type": "sql", "content": "SELECT ..."},
    {"type": "doc", "source": "campaign_policy.md#1"}
  ],
  "recommendations": ["..."],
  "risks": ["..."]
}
```

## 6. 评测设计

准备 30 到 50 条 eval case：

```json
{
  "question": "最近 30 天 GMV 下滑的主要渠道是什么？",
  "expected_tools": ["run_sql", "python_analysis"],
  "expected_tables": ["orders", "traffic"],
  "expected_report_keywords": ["渠道", "GMV", "下滑"]
}
```

指标：

- 任务成功率。
- SQL 正确率。
- 工具选择准确率。
- 报告引用准确率。
- 平均延迟。
- 平均 token 成本。

## 7. 安全设计

- SQL 只读。
- 表白名单。
- 用户权限过滤。
- 敏感字段脱敏。
- 高风险操作审批。
- prompt injection 防护。
- trace 审计。

## 8. 简历写法

```text
企业经营数据分析 Agent：基于 FastAPI + LangGraph 思想实现面向经营分析场景的多工具 Agent，支持自然语言问题拆解、只读 SQL 查询、业务知识 RAG 检索、Python 统计分析和结构化报告生成。

设计 Planner-Executor-Reviser 执行链路，统一 Tool schema 和 ToolResult，加入 SQL 表白名单、参数校验、最大步数限制和人工审批机制，降低越权和危险操作风险。

构建包含 xx 条样本的离线评测集，评估工具选择准确率、SQL 正确率、RAG Recall@3、引用准确率、平均延迟和 token 成本；通过混合检索 + rerank 将 Recall@3 从 xx% 提升至 xx%。

实现 trace 日志记录每个节点的输入输出、耗时、错误和 token 使用，支持问题定位、效果回归和面试演示。
```

没有真实指标时先不要乱写百分比。等你跑完 eval，再替换 `xx`。

## 9. 面试讲解顺序

1. 业务问题：运营分析耗时，数据和规则分散。
2. 技术方案：Agent 编排 SQL、RAG、Python 工具。
3. 难点一：SQL 安全和准确率。
4. 难点二：RAG 证据可靠性。
5. 难点三：Agent 死循环、失败恢复、成本控制。
6. 评测：用 eval case 证明优化有效。
7. 生产化：trace、权限、部署、监控。

