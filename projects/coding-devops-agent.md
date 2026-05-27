# 项目 2：AI Coding / DevOps Agent

## 1. 项目定位

这个项目适合投 AI Coding、云平台、研发效能、开发者工具方向。它展示你不仅懂 LLM，也懂代码库、测试、补丁和工程交付。

一句话介绍：

```text
面向研发流程的 Coding Agent，支持读取 issue、检索代码库、生成修改计划、产出 patch、执行测试、基于失败日志自修复，并生成 PR 摘要。
```

## 2. 核心流程

```text
Issue
  -> Repo Scanner
  -> Code Retriever
  -> Planner
  -> Patch Generator
  -> Test Runner
  -> Reflection
  -> PR Summary
```

## 3. 模块设计

### Repo Scanner

收集：

- 文件树。
- README。
- 配置文件。
- 测试命令。
- 依赖信息。

### Code Retriever

检索策略：

- 文件名关键词。
- `rg` 文本搜索。
- 函数/类名搜索。
- embedding 语义检索。

### Planner

输出：

```json
{
  "files_to_change": ["src/service.py"],
  "reason": "bug occurs when user_id is empty",
  "steps": [
    "add input validation",
    "add unit test",
    "run pytest"
  ],
  "risks": ["may change API error message"]
}
```

### Patch Generator

要求：

- 输出 unified diff。
- 小步修改。
- 避免无关重构。
- 改前备份或依赖 Git。

### Test Runner

运行：

- 单元测试。
- lint。
- 类型检查。

把失败日志摘要给 Reflection。

### Reflection

限制最多 2 轮：

```text
测试失败 -> 摘要错误 -> 修改计划 -> 生成 patch -> 再测
```

避免无限循环。

## 4. 安全设计

- 命令白名单。
- 禁止删除仓库外文件。
- 高风险命令人工确认。
- patch 人工确认后再应用。
- 每轮修改保存 trace。

## 5. 评测设计

样本：

- 10 个小 bug。
- 10 个文档修改。
- 10 个测试补全。

指标：

- 一次通过率。
- 平均修复轮数。
- 测试通过率。
- patch 最小性。
- 人工审查通过率。

## 6. 简历写法

```text
AI Coding Agent：实现面向 issue 修复的研发效能 Agent，支持代码库扫描、相关文件检索、结构化修改计划、patch 生成、测试执行、失败日志反思和 PR 摘要生成。

设计命令白名单、patch 人工确认、最大修复轮数和 trace 机制，降低自动改代码带来的误修改和危险命令风险。

构建 xx 个真实/模拟 issue 的评测集，统计一次通过率、平均修复轮数、测试通过率和 patch 最小性，并根据失败日志优化代码检索和计划生成策略。
```

## 7. 适合强调的面试点

- 大仓库上下文如何检索。
- 如何避免 Agent 乱改代码。
- 如何用测试反馈驱动修复。
- 如何设计沙箱和命令白名单。
- 如何评估 Coding Agent 的质量。

