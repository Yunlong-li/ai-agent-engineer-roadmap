# 企业经营数据分析 Agent 实战教程

这部分不再只是项目方案，而是一个可以跟着敲、跟着跑、跟着理解的完整 Agent 项目教程。

参考黑马优购那类项目教程的组织方式：先告诉你最终要做什么，再按功能模块拆成小章节，每一章都有目标、文件、代码和验证方式。

## 最终效果

你会搭出一个“企业经营数据分析 Agent”：

```text
用户问题
  -> Planner 生成执行计划
  -> Metric Tool 查询 GMV 总览
  -> Breakdown Tool 按渠道/品类拆解
  -> RAG Tool 检索业务规则
  -> Analysis Tool 生成归因结论
  -> FastAPI 返回结构化报告、证据和 trace
```

示例问题：

```text
最近 30 天 GMV 为什么下滑？
```

示例输出包含：

- 结论摘要。
- 下滑渠道和品类。
- SQL 证据。
- 业务文档引用。
- 建议动作。
- 每一步工具调用 trace。

## 代码目录

完整代码在：

```text
agent-projects/enterprise-data-agent/
```

核心结构：

```text
enterprise-data-agent/
  app.py
  requirements.txt
  agent/
    schemas.py
    data_store.py
    tools.py
    orchestrator.py
  scripts/
    seed_data.py
  tests/
    test_agent.py
```

## 学习顺序

1. [起步：项目目标和目录结构](./01-start)
2. [Schema 和模拟业务数据](./02-schema-and-data)
3. [工具层：SQL、RAG 和分析工具](./03-tools)
4. [Agent 编排和 FastAPI 接口](./04-orchestrator-api)
5. [运行、测试和下一步扩展](./05-run-and-test)

## 先跑起来

进入项目目录：

```powershell
cd agent-projects/enterprise-data-agent
```

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

运行测试：

```powershell
python -m unittest discover -s tests
```

启动服务：

```powershell
uvicorn app:app --reload
```

打开接口文档：

```text
http://127.0.0.1:8000/docs
```

## 为什么先用规则 Planner

这个实战项目第一版先不用真实 LLM，而是用 `RulePlanner` 模拟大模型规划。

原因很简单：你现在最需要先看清 Agent 工程链路，而不是一开始就被 API Key、模型不稳定、Prompt 细节卡住。

等你理解完整链路后，再把 `RulePlanner` 换成真实 LLM Planner：

```text
RulePlanner
  -> OpenAI / Qwen / DeepSeek Planner
  -> JSON Schema 结构化计划
  -> 同一套 Tool Executor
```

