# 05. Agent 核心模式

## 1. ReAct

ReAct 的核心循环：

```text
Thought -> Action -> Observation -> Thought -> ...
```

工程实现中，你不一定要把 Thought 暴露给用户，但要记录 trace。

简化代码：

```python
def run_react(goal: str, max_steps: int = 5) -> str:
    state = {"goal": goal, "steps": []}
    for _ in range(max_steps):
        action = decide_next_action(state)
        observation = run_tool(action)
        state["steps"].append({"action": action, "observation": observation})
        if action["type"] == "final":
            return action["answer"]
    return "任务未在步数限制内完成"
```

## 2. Planner-Executor

Planner-Executor 把“想”和“做”拆开：

```text
Planner：把目标拆成步骤。
Executor：逐步执行。
Reviewer：检查是否完成。
```

适合数据分析、代码修复、复杂办公任务。

## 3. Reflection

Reflection 是失败后的检查和修正：

```text
执行失败 -> 分析原因 -> 修改参数或计划 -> 重试
```

注意：

- 必须限制重试次数。
- 必须基于错误信息修正。
- 不要让模型无限自我反思。

## 4. Memory

短期记忆：

- 当前会话消息。
- 当前任务步骤。
- 最近工具结果。

长期记忆：

- 用户偏好。
- 稳定事实。
- 历史任务摘要。

记忆写入策略：

```python
def should_persist_memory(text: str) -> bool:
    stable_markers = ["我偏好", "以后", "我的团队", "我的公司"]
    return any(marker in text for marker in stable_markers)
```

## 5. Multi-Agent

多智能体适合角色差异明显的任务：

```text
Planner：拆任务。
Researcher：找资料。
Coder：写代码。
Reviewer：审查结果。
```

但它有明显代价：

- token 成本高。
- 延迟高。
- 容易循环讨论。
- 责任边界不清。

大厂面试中，不要一上来就说“用多智能体”。先说明为什么单 Agent 不够。

## 6. Agent 失败原因

常见失败：

- 目标不清。
- 工具描述不清。
- 工具返回太长。
- 没有步数限制。
- 没有状态持久化。
- 没有评测。
- 权限边界缺失。

## 7. 面试表达

```text
复杂 Agent 我一般先用 Planner-Executor 拆任务，再在执行阶段使用 ReAct 选择工具和处理 observation。如果工具失败，会进入 Reflection，但限制最大重试次数。整个执行过程会写入 AgentState 和 trace，支持 checkpoint 恢复。Memory 会区分短期会话和长期偏好，长期记忆需要满足稳定性和用户授权，避免污染。
```

