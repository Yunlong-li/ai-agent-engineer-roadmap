# 06. 评测、观测和生产化

## 1. 为什么 Agent 必须评测

Agent 的输出不稳定，只靠人工体验会有三个问题：

- 今天好，明天改 prompt 后坏了。
- 一个样例好，不代表整体好。
- 面试时说不出效果指标。

所以你必须建立 eval。

## 2. Agent 评测指标

任务级：

- Task success rate：任务是否完成。
- Step count：平均执行步数。
- Completion latency：完成耗时。

工具级：

- Tool selection accuracy：工具选得对不对。
- Argument accuracy：参数是否正确。
- Tool failure rate：工具失败率。

RAG 级：

- Recall@k。
- Citation accuracy。
- Faithfulness。

成本级：

- input_tokens。
- output_tokens。
- cost_per_task。

安全级：

- 越权调用次数。
- prompt injection 成功率。
- 高风险动作审批覆盖率。

## 3. Trace 设计

每一步都要记录：

```json
{
  "trace_id": "t_001",
  "step_id": 1,
  "node": "sql_tool",
  "input": {"query": "select ..."},
  "output": {"rows": 10},
  "latency_ms": 120,
  "tokens": 0,
  "error": null
}
```

Trace 的价值：

- 调试。
- 评测。
- 审计。
- 面试演示。

## 4. 线上监控

至少监控：

- 请求量。
- 错误率。
- 平均延迟和 P95 延迟。
- token 成本。
- 工具失败率。
- 用户差评率。
- fallback 次数。

## 5. 安全和权限

Agent 安全不是 prompt 一句话能解决的。

要做：

- API 鉴权。
- 数据权限过滤。
- 工具白名单。
- 参数校验。
- SQL 只读。
- 高风险操作审批。
- 敏感字段脱敏。
- 审计日志。

## 6. 部署

生产化项目至少应该有：

- Dockerfile。
- `.env.example`。
- README 启动命令。
- 健康检查接口。
- 日志配置。
- 简单 eval 脚本。

## 7. 面试表达

```text
我不会只看 Agent 的主观效果，会把它拆成任务级、工具级、RAG 级、成本级和安全级指标。每次执行都会记录 trace，包括节点输入输出、延迟、token 和错误。离线用 eval case 做回归，线上看成功率、P95 延迟、成本和工具失败率。这样才能定位问题是出在检索、规划、工具参数还是生成阶段。
```

