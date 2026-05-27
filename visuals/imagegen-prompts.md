# 生图提示词 / Imagegen Prompts

这些提示词适合生成封面、学习海报或概念插画。注意：包含大量精确文字的架构图不建议用 imagegen，容易出现文字错误；架构图请优先使用本目录下的 Mermaid 文件。

These prompts are for covers, posters, and conceptual illustrations. For architecture diagrams with precise labels, use Mermaid instead of generated images.

## 字段对照 / Field Glossary

- 用途 / Use case：图片类型，例如教学图、海报、产品图。
- 资产类型 / Asset type：图片将用在什么地方，例如课程封面。
- 主要需求 / Primary request：你想生成什么。
- 场景背景 / Scene/backdrop：画面环境。
- 主体 / Subject：画面中心对象。
- 风格媒介 / Style/medium：插画、照片、3D 等风格。
- 构图 / Composition/framing：画面如何排布。
- 光线氛围 / Lighting/mood：视觉情绪。
- 色彩 / Color palette：主色调。
- 文字 / Text：需要出现在图里的精确文字。
- 约束 / Constraints：必须遵守或避免的内容。

## 1. 课程封面

中文理解版：

- 目标：生成一张 AI Agent 工程师学习路线课程封面。
- 画面：现代软件工程工作台，中间是 Agent 编排中心，连接大模型、工具、记忆、RAG、评测和部署。
- 风格：高级、清晰、科技教育感，不要密集小字。

English prompt for imagegen：

```text
Use case: scientific-educational
Asset type: course cover image
Primary request: An educational cover for an AI Agent Development Engineer roadmap course
Scene/backdrop: a modern software engineering workspace with abstract agent workflow panels, code editor, database nodes, retrieval cards, and monitoring traces
Subject: a central AI agent orchestration hub connecting LLM, tools, memory, RAG, evaluation, and deployment
Style/medium: clean high-end editorial illustration, semi-realistic 3D UI elements, professional tech education style
Composition/framing: wide landscape composition, central hub, surrounding modules arranged clearly, no dense text
Lighting/mood: bright, focused, premium, calm
Color palette: balanced blue, green, white, and subtle warm accent; avoid one-note purple gradients
Text (verbatim): "AI Agent Engineer Roadmap"
Constraints: text must be spelled exactly; no logos; no watermark; avoid clutter
```

## 2. RAG 概念插画

中文理解版：

- 目标：用视觉类比解释 RAG。
- 画面：知识库中的文档被转成可检索知识卡片，再输入到 AI 回答引擎。
- 重点：体现“检索证据后再回答”，而不是模型凭空回答。

English prompt for imagegen：

```text
Use case: scientific-educational
Asset type: concept illustration
Primary request: A visual metaphor for Retrieval-Augmented Generation
Scene/backdrop: a knowledge library connected to a reasoning engine
Subject: documents being transformed into searchable knowledge cards, then passed into an AI answer engine with citation markers
Style/medium: polished educational infographic illustration with minimal text
Composition/framing: left-to-right flow, documents on the left, retrieval layer in the center, answer panel on the right
Lighting/mood: clear, trustworthy, analytical
Color palette: white, teal, blue, charcoal, small yellow highlights
Text (verbatim): "RAG"
Constraints: keep labels minimal; no small unreadable text; no watermark
```

## 3. Tool Calling 安全海报

中文理解版：

- 目标：生成一张工具调用安全海报。
- 画面：Agent 的工具请求依次经过参数校验、权限检查、人工审批、工具执行和审计日志。
- 重点：强调模型不能直接操作真实系统，后端工具层才是安全边界。

English prompt for imagegen：

```text
Use case: productivity-visual
Asset type: learning poster
Primary request: A professional learning poster about safe tool calling for AI agents
Scene/backdrop: an AI agent passing a tool request through validation, permission check, approval, execution, and audit logging
Subject: security checkpoints between an AI model and business systems
Style/medium: clean business-tech infographic, crisp icons, high readability
Composition/framing: vertical poster, top-to-bottom process, each checkpoint visually distinct
Lighting/mood: precise, secure, enterprise-grade
Color palette: white, navy, green, amber safety accents
Text (verbatim): "Safe Tool Calling"
Constraints: only use the exact title text; avoid tiny paragraphs; no watermark
```

## 4. Agent 学习路线海报

中文理解版：

- 目标：生成一张 84 天 AI Agent 学习路线海报。
- 画面：从后端工程出发，经过 RAG、工具调用、Agent 工作流、评测和生产部署，最终到达目标岗位。
- 重点：像学习地图，不要放太多小字。

English prompt for imagegen：

```text
Use case: scientific-educational
Asset type: roadmap poster
Primary request: A motivational learning roadmap poster for becoming an AI Agent Development Engineer
Scene/backdrop: a path from backend engineering to RAG, tool calling, agent workflows, evaluation, and production deployment
Subject: a learner moving through technical milestones represented as clean stations
Style/medium: premium educational illustration, modern software engineering aesthetic
Composition/framing: diagonal progress path from bottom-left to top-right, clear milestone cards, spacious layout
Lighting/mood: energetic but focused
Color palette: white, blue, green, graphite, restrained orange accent
Text (verbatim): "84-Day AI Agent Roadmap"
Constraints: title text must be exact; avoid dense labels; no logos; no watermark
```
