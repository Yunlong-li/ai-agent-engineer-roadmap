# 00. 预备知识和环境

## 你需要先会什么

最低要求：

- Python 基础：函数、类、异常、类型标注、虚拟环境。
- Web 基础：HTTP、JSON、REST API。
- 数据库基础：SQL、索引、事务的基本概念。
- Git 基础：commit、branch、pull request。

如果 Java/Go 更熟，也可以继续用它们做后端。但本课程代码用 Python，因为 Python 是 LLM 应用和 Agent 生态最顺手的主语言。

## 推荐环境

- Python 3.11+
- Git
- VS Code 或 JetBrains
- Docker Desktop
- 一个大模型 API Key，优先顺序：
  - OpenAI / Azure OpenAI
  - DashScope Qwen
  - DeepSeek
  - 本地 Ollama

## 建议安装

```powershell
python --version
git --version
docker --version
```

如果你先不想接真实 API，也可以用课程里的 `FakeLLM` 完成核心架构练习。真正重要的是理解工程结构：消息、工具、状态、检索、评测和观测。

## 学习时的硬标准

每个功能都要问自己 5 个问题：

1. 失败时怎么办？
2. 输出能不能被程序稳定解析？
3. 如何限制权限和风险？
4. 如何评估效果？
5. 如何降低延迟和成本？

这 5 个问题，就是从 Demo 作者走向大厂工程师的分界线。

