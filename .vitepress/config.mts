import { defineConfig } from "vitepress";

const repoName = process.env.GITHUB_REPOSITORY?.split("/")[1] ?? "";
const isUserOrOrgPage = repoName.endsWith(".github.io");
const defaultGitHubPagesBase =
  process.env.GITHUB_ACTIONS && repoName && !isUserOrOrgPage
    ? `/${repoName}/`
    : "/";
// const base = process.env.VITEPRESS_BASE || defaultGitHubPagesBase
const base = "/ai-agent-engineer-roadmapi/";

export default defineConfig({
  lang: "zh-CN",
  title: "AI Agent 工程师路线",
  description:
    "面向大厂 AI Agent 开发工程师的 84 天学习路线、代码实验、简历项目和面试题库",
  base,
  lastUpdated: true,
  cleanUrls: true,
  head: [
    ["meta", { name: "theme-color", content: "#2563eb" }],
    [
      "meta",
      { name: "apple-mobile-web-app-title", content: "AI Agent Roadmap" },
    ],
  ],
  themeConfig: {
    logo: "/logo.svg",
    siteTitle: "AI Agent Roadmap",
    nav: [
      { text: "首页", link: "/" },
      { text: "每日计划", link: "/daily-plan" },
      { text: "核心教材", link: "/lessons/01-agent-mental-model" },
      { text: "笔记", link: "/notes/notebook" },
      { text: "实战教程", link: "/projects/agent-tutorial/" },
      { text: "项目", link: "/projects/" },
      { text: "面试", link: "/interview/" },
    ],
    sidebar: [
      {
        text: "开始",
        items: [
          { text: "课程首页", link: "/" },
          { text: "预备知识和环境", link: "/00-prerequisites" },
          { text: "84 天逐日计划", link: "/daily-plan" },
        ],
      },
      {
        text: "核心教材",
        collapsed: false,
        items: [
          {
            text: "01. Agent 心智模型",
            link: "/lessons/01-agent-mental-model",
          },
          {
            text: "02. LLM API 与 Prompt",
            link: "/lessons/02-llm-api-and-prompt",
          },
          { text: "03. RAG 从零到可用", link: "/lessons/03-rag-from-zero" },
          {
            text: "04. Tool Calling 与 MCP",
            link: "/lessons/04-tool-calling-and-mcp",
          },
          { text: "05. Agent 核心模式", link: "/lessons/05-agent-patterns" },
          {
            text: "06. 评测、观测和生产化",
            link: "/lessons/06-evaluation-observability-production",
          },
        ],
      },
      {
        text: "代码实验",
        collapsed: true,
        items: [
          { text: "Labs 总览", link: "/labs/" },
          {
            text: "Lab 01：最小 LLM 服务",
            link: "/labs/lab01_minimal_llm_service/",
          },
          { text: "Lab 02：手写 RAG", link: "/labs/lab02_rag_from_scratch/" },
          {
            text: "Lab 03：Tool Calling Agent",
            link: "/labs/lab03_tool_calling_agent/",
          },
          { text: "Lab 04：Eval 和 Trace", link: "/labs/lab04_eval_trace/" },
        ],
      },
      {
        text: "视觉图谱",
        collapsed: true,
        items: [
          { text: "图谱总览", link: "/visuals/" },
          { text: "Agent 系统全景图", link: "/visuals/agent-system-map" },
          { text: "RAG 流程图", link: "/visuals/rag-pipeline" },
          { text: "工具调用安全链路", link: "/visuals/tool-calling-safety" },
          { text: "84 天学习路径", link: "/visuals/learning-roadmap" },
          { text: "生图提示词", link: "/visuals/imagegen-prompts" },
        ],
      },
      {
        text: "学习笔记",
        collapsed: true,
        items: [{ text: "Python 类型标注", link: "/notes/notebook" }],
      },
      {
        text: "实战项目教程",
        collapsed: false,
        items: [
          { text: "教程总览", link: "/projects/agent-tutorial/" },
          {
            text: "01. 起步和目录结构",
            link: "/projects/agent-tutorial/01-start",
          },
          {
            text: "02. Schema 和业务数据",
            link: "/projects/agent-tutorial/02-schema-and-data",
          },
          {
            text: "03. SQL、RAG 和分析工具",
            link: "/projects/agent-tutorial/03-tools",
          },
          {
            text: "04. 编排器和 API",
            link: "/projects/agent-tutorial/04-orchestrator-api",
          },
          {
            text: "05. 运行、测试和扩展",
            link: "/projects/agent-tutorial/05-run-and-test",
          },
        ],
      },
      {
        text: "简历项目",
        collapsed: true,
        items: [
          { text: "项目总览", link: "/projects/" },
          {
            text: "企业经营数据分析 Agent",
            link: "/projects/enterprise-data-analysis-agent",
          },
          {
            text: "AI Coding / DevOps Agent",
            link: "/projects/coding-devops-agent",
          },
        ],
      },
      {
        text: "面试准备",
        collapsed: true,
        items: [
          { text: "面试总览", link: "/interview/" },
          {
            text: "Agent / RAG 高频题",
            link: "/interview/agent-rag-questions",
          },
          { text: "项目深挖", link: "/interview/project-deep-dive" },
          { text: "后端基础", link: "/interview/backend-basics" },
        ],
      },
      {
        text: "模板",
        collapsed: true,
        items: [
          { text: "模板总览", link: "/templates/" },
          { text: "每日学习日志", link: "/templates/daily-log" },
          { text: "项目复盘模板", link: "/templates/project-retrospective" },
          { text: "简历 Bullet 模板", link: "/templates/resume-bullets" },
        ],
      },
    ],
    outline: {
      level: [2, 3],
      label: "本页目录",
    },
    docFooter: {
      prev: "上一页",
      next: "下一页",
    },
    lastUpdated: {
      text: "最后更新",
      formatOptions: {
        dateStyle: "medium",
        timeStyle: "short",
      },
    },
    search: {
      provider: "local",
    },
    footer: {
      message: "Built with VitePress for AI Agent learning.",
      copyright: "Copyright © 2026",
    },
  },
  markdown: {
    lineNumbers: true,
  },
});
