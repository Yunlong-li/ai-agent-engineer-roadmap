# 04. Tool Calling、权限和 MCP

## 1. 为什么需要工具

LLM 不能直接知道实时数据，也不应该凭空执行真实操作。工具调用让模型把意图转成结构化动作：

```json
{
  "tool": "search_orders",
  "arguments": {
    "user_id": "u_123",
    "status": "paid"
  }
}
```

后端负责校验和执行。

## 2. 工具设计原则

一个好工具有 5 个特点：

1. 名字清楚。
2. 描述明确。
3. 参数 schema 严格。
4. 返回结构稳定。
5. 权限边界清晰。

示例：

```python
from pydantic import BaseModel, Field


class SearchOrdersArgs(BaseModel):
    user_id: str = Field(description="Current user id")
    status: str | None = Field(default=None, description="Order status filter")
    limit: int = Field(default=10, ge=1, le=50)
```

## 3. 不要相信模型参数

模型可能生成危险 SQL：

```sql
DROP TABLE orders;
```

工具层必须拦截：

```python
def assert_readonly_sql(sql: str) -> None:
    lowered = sql.strip().lower()
    if not lowered.startswith("select"):
        raise ValueError("Only SELECT is allowed")
    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate"]
    if any(word in lowered for word in forbidden):
        raise ValueError("Unsafe SQL")
```

## 4. 工具返回结构

不要返回一大段随意文本。推荐：

```python
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    ok: bool
    data: Any = None
    error_code: str | None = None
    message: str = ""
```

错误也要可理解：

```json
{
  "ok": false,
  "error_code": "permission_denied",
  "message": "User cannot access this order"
}
```

## 5. Human-in-the-loop

高风险动作要人工确认：

- 发邮件。
- 退款。
- 删除数据。
- 修改配置。
- 执行写 SQL。

工作流：

```text
Agent 提出动作 -> 后端判断风险 -> 暂停 -> 用户审批 -> 继续执行
```

## 6. MCP 的理解

MCP 可以理解为 Agent 连接工具和数据源的标准协议。它的意义不是“又一个 API”，而是统一了工具暴露方式，让不同 Agent 客户端可以复用同一套工具服务。

你面试时至少要能说清：

- MCP Server：提供工具或资源。
- MCP Client：Agent 侧调用工具的客户端。
- Tool：可执行动作。
- Resource：可读取上下文。

例子：

```text
订单 MCP Server
  tools:
    - search_orders
    - get_order_detail
    - check_refund_policy
  resources:
    - order_schema
    - refund_policy_doc
```

## 7. 面试表达

```text
我会把工具调用看作 LLM 和真实系统之间的权限边界。模型只负责选择意图和生成参数，后端必须做 schema 校验、权限校验、超时控制、幂等设计和审计日志。对高风险工具，我会加入 human-in-the-loop。MCP 的价值是把工具以标准方式暴露出来，便于多个 Agent 或客户端复用。
```

