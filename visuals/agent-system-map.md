# Agent 系统全景图 / Agent System Map

这张图帮你建立“大厂 AI Agent 开发工程师”的整体架构感。面试时，很多问题都可以落回这张图：模型调用、工具权限、RAG、记忆、评测、观测和部署。

```mermaid
flowchart TD
    U["用户 / 业务方<br/>User / Business User"] --> API["接口服务<br/>API Server<br/>鉴权 / 限流 / 请求校验<br/>Auth / Rate Limit / Request Validation"]
    API --> ORCH["Agent 编排器<br/>Agent Orchestrator<br/>状态机 / 规划器 / 执行器<br/>State Machine / Planner / Executor"]

    ORCH --> LLM["大模型网关<br/>LLM Gateway<br/>提示词 / 结构化输出 / 模型路由<br/>Prompt / JSON Schema / Model Routing"]
    ORCH --> TOOLS["工具执行器<br/>Tool Executor<br/>超时 / 重试 / 权限<br/>Timeout / Retry / Permission"]
    ORCH --> MEM["记忆模块<br/>Memory<br/>短期记忆 / 长期记忆<br/>Short-term / Long-term"]
    ORCH --> TRACE["轨迹日志<br/>Trace Logger<br/>步骤 / 延迟 / Token / 错误<br/>Step / Latency / Token / Error"]

    TOOLS --> SQL["SQL 查询工具<br/>SQL Tool<br/>只读 / 表白名单<br/>Read-only / Table Whitelist"]
    TOOLS --> RAG["RAG 检索工具<br/>RAG Tool<br/>混合检索 / 重排 / 引用<br/>Hybrid Search / Rerank / Citation"]
    TOOLS --> PY["Python 沙箱<br/>Python Sandbox<br/>统计分析 / 图表数据<br/>Stats / Chart Data"]
    TOOLS --> API2["业务接口<br/>Business APIs<br/>订单 / 工单 / 客户系统<br/>Orders / Tickets / CRM"]

    RAG --> VS["向量库<br/>Vector Store<br/>Embedding / 元数据过滤<br/>Embedding / Metadata Filter"]
    RAG --> DOC["文档库<br/>Document Store<br/>PDF / Markdown / 网页<br/>PDF / Markdown / Web Pages"]
    SQL --> DB["业务数据库<br/>Database<br/>订单 / 流量 / 活动<br/>Orders / Traffic / Campaigns"]

    TRACE --> EVAL["评测系统<br/>Eval System<br/>任务成功率 / 工具准确率 / Recall@k<br/>Task Success / Tool Accuracy / Recall@k"]
    TRACE --> MON["监控系统<br/>Monitoring<br/>P95 延迟 / 成本 / 错误率<br/>P95 Latency / Cost / Error Rate"]

    ORCH --> FINAL["最终输出<br/>Final Answer<br/>结构化报告 / 引用 / 建议动作<br/>Structured Report / Citations / Actions"]
    FINAL --> U
```

## 读图方法

1. 用户请求先进入 API Server，做鉴权、限流和参数校验。
2. Orchestrator 是 Agent 的大脑，负责维护状态和决定下一步。
3. LLM 不直接操作真实系统，只通过 Tool Executor 间接调用工具。
4. RAG、SQL、Python、业务 API 都是工具。
5. Trace 是生产化关键，没有 trace 就很难排查 Agent 为什么错。
6. Eval 用来证明优化有效，而不是靠主观感觉调 prompt。
