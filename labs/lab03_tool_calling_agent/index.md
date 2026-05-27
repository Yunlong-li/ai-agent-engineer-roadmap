# Lab 03：Tool Calling Agent

## 学习目标

- 定义工具 schema。
- 注册工具。
- 校验参数。
- 实现一个可观察的 Agent loop。

## 运行

```powershell
python agent.py
```

## 练习

1. 增加一个 `search_kb` 工具。
2. 给 `run_sql` 增加表白名单。
3. 把当前标准库参数校验替换成 Pydantic schema。
4. 把 `FakePlanner` 换成真实 LLM function calling。

