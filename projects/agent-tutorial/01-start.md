# 1. 起步：项目目标和目录结构

## 1.1 这一章要做什么

这一章先把项目跑通需要的目录、依赖和入口文件建立起来。

你要理解三件事：

1. Agent 项目不是一个单文件脚本，而是一个“服务 + 工具 + 编排 + 数据 + 测试”的工程。
2. FastAPI 只是入口，真正的 Agent 逻辑放在 `agent/` 目录。
3. 每一步都要能测试，否则后面工具一多就很难排错。

## 1.2 项目目录

代码目录：

```text
agent-projects/enterprise-data-agent/
```

目录结构：

```text
enterprise-data-agent/
  app.py                  # FastAPI 入口
  requirements.txt        # 依赖
  agent/
    schemas.py            # 请求、响应、ToolResult、trace
    data_store.py         # SQLite 数据和业务文档
    tools.py              # SQL/RAG/分析工具
    orchestrator.py       # Agent 编排器
  scripts/
    seed_data.py          # 重置模拟数据
  tests/
    test_agent.py         # 最小回归测试
```

## 1.3 安装依赖

`requirements.txt`：

```txt
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.7.0
```

安装：

```powershell
cd agent-projects/enterprise-data-agent
python -m pip install -r requirements.txt
```

## 1.4 FastAPI 入口

入口文件是 `app.py`：

```python
from __future__ import annotations

from fastapi import FastAPI

from agent.orchestrator import BusinessAnalysisAgent
from agent.schemas import AgentAnswer, ChatRequest

app = FastAPI(title="Enterprise Data Analysis Agent")
agent = BusinessAnalysisAgent()
```

这里先创建一个全局 `BusinessAnalysisAgent`。

在教程项目里这样写足够清晰；生产环境可以再考虑依赖注入、连接池、配置中心。

## 1.5 健康检查接口

```python
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

先写健康检查的原因：

- 确认服务能启动。
- 部署或调试时快速判断进程是否正常。
- 不依赖 Agent 业务逻辑，排错更清楚。

## 1.6 Agent 对话接口

```python
@app.post("/chat", response_model=AgentAnswer)
def chat(req: ChatRequest) -> AgentAnswer:
    return agent.answer(req)
```

这个接口只做一件事：把请求交给 Agent。

不要把 SQL、RAG、分析逻辑写在 `app.py` 里，否则项目很快会变成不可维护的“大脚本”。

## 1.7 本章验证

启动服务：

```powershell
uvicorn app:app --reload
```

访问：

```text
http://127.0.0.1:8000/health
```

预期结果：

```json
{"status":"ok"}
```

