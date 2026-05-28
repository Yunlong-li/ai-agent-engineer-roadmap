from __future__ import annotations

from agent.schemas import AgentAnswer, ChatRequest, Evidence, PlanStep, TraceStep
from agent.tools import AnalysisTool, BreakdownTool, MetricTool, RagTool


class RulePlanner:
    def plan(self, question: str) -> list[PlanStep]:
        return [
            PlanStep(name="计算 GMV 总览", tool="metric_tool", reason="先确认整体是否下滑"),
            PlanStep(name="按渠道拆解", tool="breakdown_tool", reason="定位渠道贡献"),
            PlanStep(name="按品类拆解", tool="breakdown_tool", reason="定位品类贡献"),
            PlanStep(name="检索业务规则", tool="rag_tool", reason="补充活动和指标口径证据"),
            PlanStep(name="生成归因报告", tool="analysis_tool", reason="把工具结果整理成业务结论"),
        ]


class BusinessAnalysisAgent:
    def __init__(self) -> None:
        self.planner = RulePlanner()
        self.metric_tool = MetricTool()
        self.breakdown_tool = BreakdownTool()
        self.rag_tool = RagTool()
        self.analysis_tool = AnalysisTool()

    def answer(self, req: ChatRequest) -> AgentAnswer:
        plan = self.planner.plan(req.question)
        trace: list[TraceStep] = [
            TraceStep(
                step="plan",
                tool="rule_planner",
                ok=True,
                summary=" -> ".join(step.name for step in plan),
            )
        ]

        summary = self.metric_tool.gmv_summary(days=30)
        trace.append(self._trace("metric", summary.tool, summary.ok, summary.message))

        channel_breakdown = self.breakdown_tool.gmv_by_dimension("channel", days=30)
        trace.append(
            self._trace("channel_breakdown", channel_breakdown.tool, channel_breakdown.ok, channel_breakdown.message)
        )

        category_breakdown = self.breakdown_tool.gmv_by_dimension("category", days=30)
        trace.append(
            self._trace("category_breakdown", category_breakdown.tool, category_breakdown.ok, category_breakdown.message)
        )

        rag_query = f"{req.question} GMV 搜索 广告 电子 活动 预算"
        docs = self.rag_tool.search(rag_query)
        trace.append(self._trace("rag", docs.tool, docs.ok, docs.message))

        analysis = self.analysis_tool.explain(summary, channel_breakdown, category_breakdown, docs)
        trace.append(self._trace("analysis", analysis.tool, analysis.ok, analysis.message))

        findings = analysis.data["findings"]
        recommendations = analysis.data["recommendations"]
        evidence = self._evidence(summary, channel_breakdown, category_breakdown, docs)
        return AgentAnswer(
            question=req.question,
            answer=self._render_answer(findings, recommendations),
            findings=findings,
            recommendations=recommendations,
            evidence=evidence,
            trace=trace,
        )

    def _trace(self, step: str, tool: str, ok: bool, summary: str) -> TraceStep:
        return TraceStep(step=step, tool=tool, ok=ok, summary=summary)

    def _evidence(self, summary, channel_breakdown, category_breakdown, docs) -> list[Evidence]:
        evidence = [
            Evidence(type="sql", source="gmv_summary", content=summary.data["sql"]),
            Evidence(type="sql", source="channel_breakdown", content=channel_breakdown.data["sql"]),
            Evidence(type="sql", source="category_breakdown", content=category_breakdown.data["sql"]),
        ]
        for chunk in docs.data["chunks"]:
            evidence.append(Evidence(type="doc", source=chunk["id"], content=chunk["text"]))
        return evidence

    def _render_answer(self, findings: list[str], recommendations: list[str]) -> str:
        finding_text = "\n".join(f"- {item}" for item in findings)
        recommendation_text = "\n".join(f"- {item}" for item in recommendations)
        return f"## 结论\n{finding_text}\n\n## 建议\n{recommendation_text}"
