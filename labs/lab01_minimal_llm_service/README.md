# Lab 01：最小 LLM 服务

## 学习目标

- 用 FastAPI 暴露 `/chat`。
- 用统一 `LLMClient` 抽象模型。
- 保存消息历史。
- 记录延迟。

## 运行

```powershell
pip install -r requirements.txt
uvicorn app:app --reload --port 8001
```

打开：

```text
http://127.0.0.1:8001/docs
```

## 练习

1. 给 `ChatRequest` 增加 `session_id`。
2. 把 FakeLLM 换成真实模型 API。
3. 在响应中返回 `latency_ms`。

