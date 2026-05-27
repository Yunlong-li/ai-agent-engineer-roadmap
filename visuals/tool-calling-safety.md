# 工具调用安全链路图 / Tool Calling Safety Flow

工具调用（Tool Calling）的本质是把模型意图转成真实系统动作。安全边界一定在后端工具层，而不是只靠提示词。

```mermaid
sequenceDiagram
    participant U as 用户 User
    participant A as Agent 编排器 Orchestrator
    participant M as 大模型 LLM
    participant V as 校验与权限层 Validator
    participant T as 工具服务 Tool
    participant L as 审计日志 Audit Log

    U->>A: 提交任务目标 Submit goal
    A->>M: 带工具说明，请模型选择下一步动作 Ask next action with tool schema
    M-->>A: 返回工具名和参数 tool_name + arguments
    A->>V: 校验参数结构和权限 Validate schema and permissions

    alt 参数不合法 Invalid arguments
        V-->>A: 返回参数错误观察结果 invalid_args observation
        A->>M: 带错误信息请求修正 Ask for correction with error
    else 高风险动作 Risky action
        V-->>U: 请求人工审批 Request human approval
        U-->>V: 批准或拒绝 Approve or reject
    else 安全动作 Safe action
        V->>T: 带超时限制执行工具 Execute with timeout
        T-->>A: 返回结构化观察结果 Structured observation
        A->>L: 保存执行轨迹和工具结果 Save trace and tool result
        A->>M: 总结结果或决定下一步 Summarize or decide next step
    end

    A-->>U: 返回最终答案 Final answer
```

## 必须记住

- 模型只提出动作，不直接执行动作。
- 参数必须校验。
- 权限必须在工具层做。
- 高风险动作必须人工确认。
- 每次工具调用都要记录执行轨迹（trace）和审计日志（audit log）。
