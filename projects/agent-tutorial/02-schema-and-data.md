# 2. Schema 和模拟业务数据

## 2.1 这一章要做什么

Agent 工程里最容易混乱的是数据结构。

所以先定义 Schema，再写工具和编排。

这一章会建立：

- 用户请求 `ChatRequest`
- 工具返回 `ToolResult`
- 最终回答 `AgentAnswer`
- trace 记录 `TraceStep`
- SQLite 模拟业务数据
- RAG 用的业务文档

## 2.2 请求 Schema

`agent/schemas.py`：

```python
class ChatRequest(BaseModel):
    question: str = Field(min_length=2, examples=["最近 30 天 GMV 为什么下滑？"])
    user_id: str = "demo-user"
```

重点：

- `question` 是用户问题。
- `user_id` 后续可以用于权限、个性化、审计。
- `Field(min_length=2)` 是最基本的入口校验。

## 2.3 ToolResult

```python
class ToolResult(BaseModel):
    ok: bool
    tool: str
    data: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    message: str = ""
```

为什么不用直接抛异常？

- Agent 需要理解“工具失败”这个业务状态。
- 失败后可能重试、降级、换工具、追问用户。
- `ToolResult` 能把成功、失败、错误码、可读说明统一起来。

## 2.4 最终回答 Schema

```python
class AgentAnswer(BaseModel):
    question: str
    answer: str
    findings: list[str]
    recommendations: list[str]
    evidence: list[Evidence]
    trace: list[TraceStep]
```

这个结构是为了让回答既能给用户看，也能给开发者排查。

- `answer`：最终自然语言报告。
- `findings`：结构化结论。
- `recommendations`：建议动作。
- `evidence`：SQL 和文档证据。
- `trace`：每一步工具调用过程。

## 2.5 SQLite 模拟业务表

`agent/data_store.py` 会自动创建 SQLite 数据库：

```python
DB_PATH = DATA_DIR / "business.db"
```

核心表是 `orders`：

```sql
create table if not exists orders (
  id integer primary key,
  order_date text not null,
  channel text not null,
  category text not null,
  region text not null,
  amount real not null,
  status text not null
);
```

这个表能支撑经营分析里最常见的问题：

- 最近 30 天 GMV 是多少？
- 比上一个 30 天涨了还是跌了？
- 哪个渠道贡献了下滑？
- 哪个品类下滑最明显？

## 2.6 模拟一个真实波动

种子数据里故意制造了两个业务变化：

```python
if is_recent_window and channel == "search" and category == "electronics":
    amount *= 0.58
if is_recent_window and channel == "ads":
    amount *= 0.82
```

这样 Agent 分析时就能发现：

- 搜索渠道电子品类明显下滑。
- 广告渠道也有下滑。
- 这些下滑可以和活动规则、预算变化互相印证。

## 2.7 RAG 业务文档

同一个数据文件里还会写入业务文档：

```python
{
  "id": "campaign-search-coupon",
  "title": "搜索渠道电子品类活动",
  "text": "搜索渠道电子品类满减券在 2026-05-10 结束，活动结束后搜索渠道转化可能下降。"
}
```

这些文档用于模拟 RAG：

- 指标口径。
- 活动规则。
- 广告预算变化。
- 报告要求。

## 2.8 本章验证

重置模拟数据：

```powershell
python scripts/seed_data.py
```

预期输出：

```text
seeded database: ...\business.db
```

如果你看到这个文件生成了，说明数据层已经准备好。

