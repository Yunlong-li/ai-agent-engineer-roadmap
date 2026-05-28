# 4. Agent 编排和 FastAPI 接口

## 4.1 这一章要做什么

工具本身不会自动协作。

Agent Orchestrator 的职责是：

1. 接收用户问题。
2. 生成执行计划。
3. 按顺序调用工具。
4. 收集证据和 trace。
5. 输出最终报告。

## 4.2 RulePlanner

第一版 Planner 写成规则：

```python
class RulePlanner:
    def plan(self, question: str) -> list[PlanStep]:
        return [
            PlanStep(name="计算 GMV 总览", tool="metric_tool", reason="先确认整体是否下滑"),
            PlanStep(name="按渠道拆解", tool="breakdown_tool", reason="定位渠道贡献"),
            PlanStep(name="按品类拆解", tool="breakdown_tool", reason="定位品类贡献"),
            PlanStep(name="检索业务规则", tool="rag_tool", reason="补充活动和指标口径证据"),
            PlanStep(name="生成归因报告", tool="analysis_tool", reason="把工具结果整理成业务结论"),
        ]
```

这里不是为了“写死业务逻辑”，而是为了让你先看清楚标准 Agent 链路。

后续替换真实大模型 Planner 时，计划仍然应该输出类似结构：

```json
[
  {"name": "计算 GMV 总览", "tool": "metric_tool", "reason": "先确认整体是否下滑"},
  {"name": "按渠道拆解", "tool": "breakdown_tool", "reason": "定位渠道贡献"}
]
```

## 4.3 BusinessAnalysisAgent

编排器初始化所有工具：

```python
class BusinessAnalysisAgent:
    def __init__(self) -> None:
        self.planner = RulePlanner()
        self.metric_tool = MetricTool()
        self.breakdown_tool = BreakdownTool()
        self.rag_tool = RagTool()
        self.analysis_tool = AnalysisTool()
```

## 4.4 执行链路

`answer()` 是主流程：

```python
summary = self.metric_tool.gmv_summary(days=30)
channel_breakdown = self.breakdown_tool.gmv_by_dimension("channel", days=30)
category_breakdown = self.breakdown_tool.gmv_by_dimension("category", days=30)
docs = self.rag_tool.search(req.question)
analysis = self.analysis_tool.explain(summary, channel_breakdown, category_breakdown, docs)
```

这就是最小可用的 Agent 执行链路。

它已经具备：

- 计划。
- 工具调用。
- RAG 证据。
- 分析报告。
- trace。

## 4.5 Trace

每一步都记录 trace：

```python
trace.append(self._trace("metric", summary.tool, summary.ok, summary.message))
trace.append(self._trace("rag", docs.tool, docs.ok, docs.message))
trace.append(self._trace("analysis", analysis.tool, analysis.ok, analysis.message))
```

为什么 trace 很关键？

- Agent 经常不是“完全错”，而是中间某一步错。
- 没有 trace，你不知道是 SQL 错、RAG 错、分析错，还是 Planner 错。
- 面试讲项目时，trace 是最能体现工程化能力的部分。

## 4.6 Evidence

最终回答不只返回结论，还返回证据：

```python
Evidence(type="sql", source="gmv_summary", content=summary.data["sql"])
Evidence(type="doc", source=chunk["id"], content=chunk["text"])
```

这能解决两个问题：

1. 用户知道结论从哪里来。
2. 你能在面试里讲清楚“如何防止 Agent 胡说”。

## 4.7 FastAPI 接口

`app.py` 暴露 `/chat`：

```python
@app.post("/chat", response_model=AgentAnswer)
def chat(req: ChatRequest) -> AgentAnswer:
    return agent.answer(req)
```

启动后访问：

```text
http://127.0.0.1:8000/docs
```

在 Swagger UI 里请求：

```json
{
  "question": "最近 30 天 GMV 为什么下滑？",
  "user_id": "demo-user"
}
```

你应该能看到结构化返回。

