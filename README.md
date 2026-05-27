# AI Agent Development Engineer Roadmap

这是一套面向“大厂 AI Agent 开发工程师”的 84 天训练营。目标不是泛泛了解大模型，而是把你训练成能做业务落地的 AI 应用/Agent 工程师：会后端工程、会 RAG、会工具调用、会多步任务编排、会评测、会部署、会讲清楚项目。

## 学完你应该具备的能力

1. 能独立实现一个带工具调用、RAG、记忆、评测、观测和部署的 Agent 系统。
2. 能解释 Agent、RAG、Function Calling、MCP、LangGraph、LLMOps 的核心机制。
3. 能设计企业知识库 Agent、数据分析 Agent、Coding Agent 这类大厂常见业务方案。
4. 能在面试中讲清楚系统设计、失败案例、优化思路、安全边界和评测指标。

## 学习方式

每天固定完成四件事：

1. 读当天概念。
2. 写当天代码。
3. 记录当天产出。
4. 用当天面试题自测。

建议每天 2.5 到 4 小时：

- 40 分钟：读概念和画图理解。
- 90 分钟：写代码。
- 40 分钟：调试、补测试、写日志。
- 30 分钟：复盘和面试表达。

## 目录

- [00-prerequisites.md](./00-prerequisites.md)：预备知识和环境。
- [daily-plan.md](./daily-plan.md)：84 天逐日计划。
- [lessons](./lessons/01-agent-mental-model.md)：核心知识教材。
- [labs](./labs/)：可运行代码实验。
- [visuals](./visuals/)：可编辑学习图谱和架构图。
- [notes](./notes/notebook.md)：学习笔记。
- [projects](./projects/)：简历项目方案。
- [interview](./interview/)：面试题库和回答模板。
- [templates](./templates/)：学习日志、项目复盘、简历描述模板。

## 推荐学习顺序

1. 先读 [预备知识和环境](./00-prerequisites.md)，确认 Python、Node、Git、API 调用和基础后端环境都能跑起来。
2. 粗看一遍 [视觉图谱](./visuals/)，先建立全局地图，不需要一开始就看懂每个细节。
3. 把 [84 天逐日计划](./daily-plan.md) 当作主线，每天按它推进当天任务和产出。
4. 按计划穿插学习 [核心教材](./lessons/01-agent-mental-model.md)，顺序是 Agent 心智模型、LLM API 与 Prompt、RAG、Tool Calling/MCP、Agent 模式、评测观测和生产化。
5. 跟核心教材配套完成 [代码实验](./labs/)：LLM API 后做 Lab 01，RAG 后做 Lab 02，Tool Calling/MCP 后做 Lab 03，评测和 Trace 后做 Lab 04。
6. 最后集中打磨 [简历项目](./projects/)，把企业经营数据分析 Agent 或 AI Coding / DevOps Agent 做成能写进简历、能面试讲清楚的项目。
7. 面试前用 [面试题库](./interview/agent-rag-questions.md) 和模板复盘项目表达。

## 推荐主线

第一阶段，后端工程和 LLM API。你要先变成一个能写稳定服务的人。

第二阶段，RAG。你要能把企业文档、业务数据、搜索召回和引用溯源做成可靠系统。

第三阶段，Agent。你要掌握 ReAct、Planner-Executor、Memory、Tool Calling、Human-in-the-loop、Multi-Agent。

第四阶段，生产化。你要补上评测、观测、成本、延迟、安全、部署和面试表达。

## 最终作品

主项目推荐做：企业数据分析 Agent。

它能覆盖大厂 JD 里的高频关键词：RAG、SQL 工具调用、Python 沙箱、任务规划、反思修正、评测、权限、安全、可观测、部署。

备选项目：AI Coding / DevOps Agent。

如果你更想投云平台、研发效能、AI Coding 方向，可以把第二个项目做成主项目。

## 图片和图谱

课程默认使用 Mermaid 图谱来表达架构和流程，因为这些图可编辑、可复制到 README/简历/面试讲稿里，也不会出现图片中文字生成错误的问题。

建议先看：

- [Agent 系统全景图 / Agent System Map](./visuals/agent-system-map.md)
- [RAG 检索增强生成流程图 / RAG Pipeline](./visuals/rag-pipeline.md)
- [工具调用安全链路图 / Tool Calling Safety Flow](./visuals/tool-calling-safety.md)
- [84 天学习路径图 / 84-Day Learning Roadmap](./visuals/learning-roadmap.md)

如果需要做封面、学习海报或概念插画，再使用 imagegen 生成位图素材。
