# 简历 Bullet 模板

## 通用公式

```text
做了什么业务系统 + 用了什么技术方案 + 解决了什么难点 + 取得什么指标或工程结果
```

## 数据分析 Agent

```text
基于 FastAPI + Agent 工作流实现企业经营数据分析 Agent，支持自然语言问题拆解、SQL 查询、业务知识 RAG 检索、Python 统计分析和结构化报告生成。
```

```text
设计统一 Tool schema 和 ToolResult，加入 SQL 只读校验、表白名单、参数校验、最大步数限制和 trace 日志，提升多步工具调用的可控性和可排查性。
```

```text
构建 xx 条离线评测样本，覆盖工具选择、SQL 正确性、RAG Recall@3、引用准确率、任务成功率、平均延迟和 token 成本，用数据驱动 RAG 和 Agent 策略优化。
```

## Coding Agent

```text
实现面向 issue 修复的 AI Coding Agent，支持代码库检索、结构化修改计划、patch 生成、测试执行、失败日志反思和 PR 摘要生成。
```

```text
设计命令白名单、patch 人工确认、最大修复轮数和执行 trace，降低自动化代码修改过程中的危险命令和无关变更风险。
```

