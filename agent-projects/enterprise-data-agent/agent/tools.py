from __future__ import annotations

from collections import Counter
from typing import Any

from agent.data_store import connection, load_docs
from agent.schemas import ToolResult


class MetricTool:
    name = "metric_tool"

    def gmv_summary(self, days: int = 30) -> ToolResult:
        query = """
        with bounds as (
          select max(order_date) as max_date from orders
        ),
        periods as (
          select
            case
              when order_date > date((select max_date from bounds), ?) then 'current'
              when order_date > date((select max_date from bounds), ?) then 'previous'
              else 'older'
            end as period,
            amount
          from orders
          where status = 'paid'
        )
        select period, round(sum(amount), 2) as gmv
        from periods
        where period in ('current', 'previous')
        group by period
        """
        with connection() as conn:
            rows = conn.execute(query, (f"-{days} day", f"-{days * 2} day")).fetchall()

        data = {row["period"]: row["gmv"] for row in rows}
        current = float(data.get("current") or 0)
        previous = float(data.get("previous") or 0)
        delta = round(current - previous, 2)
        delta_pct = round(delta / previous * 100, 2) if previous else 0
        return ToolResult(
            ok=True,
            tool=self.name,
            data={
                "days": days,
                "current_gmv": current,
                "previous_gmv": previous,
                "delta": delta,
                "delta_pct": delta_pct,
                "sql": query.strip(),
            },
            message=f"最近 {days} 天 GMV 环比 {delta_pct}%",
        )


class BreakdownTool:
    name = "breakdown_tool"
    allowed_dimensions = {"channel", "category", "region"}

    def gmv_by_dimension(self, dimension: str, days: int = 30) -> ToolResult:
        if dimension not in self.allowed_dimensions:
            return ToolResult(
                ok=False,
                tool=self.name,
                error_code="invalid_dimension",
                message=f"dimension must be one of {sorted(self.allowed_dimensions)}",
            )

        query = f"""
        with bounds as (
          select max(order_date) as max_date from orders
        ),
        periods as (
          select
            {dimension} as dimension_value,
            case
              when order_date > date((select max_date from bounds), ?) then 'current'
              when order_date > date((select max_date from bounds), ?) then 'previous'
              else 'older'
            end as period,
            amount
          from orders
          where status = 'paid'
        )
        select dimension_value, period, round(sum(amount), 2) as gmv
        from periods
        where period in ('current', 'previous')
        group by dimension_value, period
        """
        with connection() as conn:
            rows = conn.execute(query, (f"-{days} day", f"-{days * 2} day")).fetchall()

        grouped: dict[str, dict[str, float]] = {}
        for row in rows:
            value = row["dimension_value"]
            grouped.setdefault(value, {"current": 0.0, "previous": 0.0})
            grouped[value][row["period"]] = float(row["gmv"])

        breakdown = []
        for value, metrics in grouped.items():
            delta = round(metrics["current"] - metrics["previous"], 2)
            breakdown.append(
                {
                    "dimension": dimension,
                    "value": value,
                    "current_gmv": metrics["current"],
                    "previous_gmv": metrics["previous"],
                    "delta": delta,
                }
            )
        breakdown.sort(key=lambda item: item["delta"])
        return ToolResult(
            ok=True,
            tool=self.name,
            data={"dimension": dimension, "items": breakdown, "sql": query.strip()},
            message=f"已按 {dimension} 拆解 GMV",
        )


class RagTool:
    name = "rag_tool"

    def search(self, query: str, top_k: int = 3) -> ToolResult:
        query_terms = self._terms(query)
        scored_docs = []
        for doc in load_docs():
            doc_terms = self._terms(doc["title"] + doc["text"])
            score = sum((query_terms & doc_terms).values())
            if score > 0:
                scored_docs.append({**doc, "score": score})

        scored_docs.sort(key=lambda item: item["score"], reverse=True)
        return ToolResult(
            ok=True,
            tool=self.name,
            data={"chunks": scored_docs[:top_k]},
            message=f"检索到 {min(len(scored_docs), top_k)} 条业务文档",
        )

    def _terms(self, text: str) -> Counter[str]:
        lowered = text.lower()
        terms: list[str] = []
        for token in ["gmv", "搜索", "广告", "渠道", "电子", "活动", "预算", "退款", "报告", "建议"]:
            if token in lowered:
                terms.append(token)
        return Counter(terms)


class AnalysisTool:
    name = "analysis_tool"

    def explain(
        self,
        summary: ToolResult,
        channel_breakdown: ToolResult,
        category_breakdown: ToolResult,
        docs: ToolResult,
    ) -> ToolResult:
        channel_items = channel_breakdown.data["items"]
        category_items = category_breakdown.data["items"]
        worst_channel = channel_items[0]
        worst_category = category_items[0]
        docs_text = [item["title"] for item in docs.data["chunks"]]

        findings = [
            f"最近 {summary.data['days']} 天 GMV 为 {summary.data['current_gmv']}，环比 {summary.data['delta_pct']}%。",
            f"下滑最明显的渠道是 {worst_channel['value']}，GMV 变化 {worst_channel['delta']}。",
            f"下滑最明显的品类是 {worst_category['value']}，GMV 变化 {worst_category['delta']}。",
        ]
        recommendations = [
            "优先复盘搜索渠道电子品类的活动结束影响，补充替代优惠或优化排序。",
            "对广告渠道检查预算、投放人群和落地页转化，避免只看总 GMV。",
            "报告中保留 SQL 证据和业务文档引用，方便面试时解释分析链路。",
        ]
        return ToolResult(
            ok=True,
            tool=self.name,
            data={
                "findings": findings,
                "recommendations": recommendations,
                "doc_titles": docs_text,
            },
            message="已生成归因分析",
        )
