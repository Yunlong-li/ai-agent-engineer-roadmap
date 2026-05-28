# 5. 运行、测试和下一步扩展

## 5.1 安装依赖

```powershell
cd agent-projects/enterprise-data-agent
python -m pip install -r requirements.txt
```

## 5.2 初始化数据

```powershell
python scripts/seed_data.py
```

如果你不手动运行也没关系，代码会在第一次连接数据库时自动初始化。

## 5.3 运行测试

```powershell
python -m unittest discover -s tests
```

测试覆盖的核心链路：

- Agent 能返回结论。
- Agent 能返回建议。
- evidence 里有 SQL 证据。
- evidence 里有文档证据。
- trace 能记录多个步骤。

测试代码：

```python
class BusinessAnalysisAgentTest(unittest.TestCase):
    def test_agent_returns_findings_evidence_and_trace(self) -> None:
        agent = BusinessAnalysisAgent()
        answer = agent.answer(ChatRequest(question="最近 30 天 GMV 为什么下滑？"))

        self.assertGreaterEqual(len(answer.findings), 3)
        self.assertGreaterEqual(len(answer.recommendations), 3)
        self.assertTrue(any(item.type == "sql" for item in answer.evidence))
        self.assertTrue(any(item.type == "doc" for item in answer.evidence))
        self.assertGreaterEqual(len(answer.trace), 5)
```

## 5.4 启动服务

```powershell
uvicorn app:app --reload
```

浏览器打开：

```text
http://127.0.0.1:8000/docs
```

## 5.5 用 PowerShell 调接口

```powershell
$body = @{
  question = "最近 30 天 GMV 为什么下滑？"
  user_id = "demo-user"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/chat `
  -ContentType "application/json" `
  -Body $body
```

## 5.6 你应该观察什么

不要只看最终答案，要重点看三个字段：

### findings

它告诉你 Agent 的结论。

### evidence

它告诉你结论来自哪些 SQL 和业务文档。

### trace

它告诉你 Agent 每一步调用了哪个工具，是否成功，摘要是什么。

## 5.7 下一步扩展路线

这个项目第一版已经是完整闭环，但还可以继续升级：

1. 把 `RulePlanner` 换成真实 LLM Planner。
2. 把 SQLite 换成 PostgreSQL。
3. 把关键词 RAG 换成 BM25 + 向量检索。
4. 加入权限过滤，比如不同 `user_id` 只能查自己的业务线。
5. 加入 eval case，统计工具选择准确率、SQL 证据完整率、回答可用率。
6. 加入前端页面，把 `answer/evidence/trace` 分栏展示。

## 5.8 面试讲法

这个项目可以这样讲：

```text
我做了一个企业经营数据分析 Agent。用户用自然语言提问后，Agent 会先规划任务，再调用 GMV 指标工具、维度拆解工具、业务文档 RAG 工具和分析工具，最后返回结构化报告。

为了避免 Agent 胡说，我把 SQL 证据、业务文档引用和每一步 trace 都返回出来。工具层统一使用 ToolResult，失败时不会直接中断，而是可以进入重试、降级或追问用户的流程。
```

