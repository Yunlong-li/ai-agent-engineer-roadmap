# 3. 工具层：SQL、RAG 和分析工具

## 3.1 这一章要做什么

Agent 的核心不是“会聊天”，而是会调用工具完成任务。

这一章实现四个工具：

1. `MetricTool`：查询 GMV 总览。
2. `BreakdownTool`：按渠道、品类、地区拆解。
3. `RagTool`：检索业务文档。
4. `AnalysisTool`：把工具结果整理成结论和建议。

## 3.2 MetricTool：先看整体指标

`MetricTool.gmv_summary()` 的职责是回答：

```text
最近 30 天 GMV 是否下滑？
```

关键代码：

```python
current = float(data.get("current") or 0)
previous = float(data.get("previous") or 0)
delta = round(current - previous, 2)
delta_pct = round(delta / previous * 100, 2) if previous else 0
```

工具返回：

```python
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
```

注意这里把 SQL 也放进了 `data`。

原因是最终报告要能解释证据，面试时也要能讲清楚“结论从哪里来”。

## 3.3 BreakdownTool：定位下滑来源

只知道 GMV 下滑还不够，必须继续拆解。

`BreakdownTool` 支持三个维度：

```python
allowed_dimensions = {"channel", "category", "region"}
```

调用示例：

```python
channel_breakdown = breakdown_tool.gmv_by_dimension("channel", days=30)
category_breakdown = breakdown_tool.gmv_by_dimension("category", days=30)
```

为什么要做维度白名单？

- 防止用户输入任意字段。
- 防止拼接 SQL 失控。
- 让工具能力边界清晰。

教程里为了让你看懂 SQL，先用字符串插入维度名；但维度名必须来自白名单。

## 3.4 RagTool：补充业务规则证据

经营分析不能只看数字，还要知道业务发生了什么。

比如：

- 活动是不是结束了？
- 广告预算有没有调整？
- 指标口径是不是变了？

`RagTool.search()` 会从业务文档中检索相关内容：

```python
docs = self.rag_tool.search(req.question)
```

第一版使用简单关键词打分：

```python
for token in ["gmv", "搜索", "广告", "渠道", "电子", "活动", "预算", "退款", "报告", "建议"]:
    if token in lowered:
        terms.append(token)
```

后续可以替换成：

- BM25。
- 向量检索。
- 混合检索。
- rerank。

但工具输入输出不变。

## 3.5 AnalysisTool：生成归因结论

分析工具不再查数据，而是综合其它工具结果。

它会找出：

```python
worst_channel = channel_items[0]
worst_category = category_items[0]
```

然后生成结构化结论：

```python
findings = [
    f"最近 {summary.data['days']} 天 GMV 为 {summary.data['current_gmv']}，环比 {summary.data['delta_pct']}%。",
    f"下滑最明显的渠道是 {worst_channel['value']}，GMV 变化 {worst_channel['delta']}。",
    f"下滑最明显的品类是 {worst_category['value']}，GMV 变化 {worst_category['delta']}。",
]
```

再生成建议：

```python
recommendations = [
    "优先复盘搜索渠道电子品类的活动结束影响，补充替代优惠或优化排序。",
    "对广告渠道检查预算、投放人群和落地页转化，避免只看总 GMV。",
    "报告中保留 SQL 证据和业务文档引用，方便面试时解释分析链路。",
]
```

## 3.6 本章理解重点

工具层要做到四件事：

1. 输入边界清楚。
2. 输出结构稳定。
3. 失败时返回 `ToolResult`，不要让异常直接炸穿 Agent。
4. 每个工具只做一类事情，不要把查询、检索、分析混在一起。

