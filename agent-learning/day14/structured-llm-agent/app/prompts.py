from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    description: str
    template: str

    def render(self, **variables: str) -> str:
        return self.template.format(**variables)


class PromptRegistry:
    def __init__(self, templates: list[PromptTemplate] | None = None) -> None:
        self._templates = {template.name: template for template in templates or []}

    def get(self, name: str) -> PromptTemplate:
        if name not in self._templates:
            available = ", ".join(sorted(self._templates))
            raise KeyError(f"unknown prompt_template={name}; available={available}")
        return self._templates[name]

    def render(self, name: str, **variables: str) -> str:
        return self.get(name).render(**variables)

    def list_templates(self) -> list[PromptTemplate]:
        return list(self._templates.values())


def build_prompt_registry() -> PromptRegistry:
    return PromptRegistry(
        [
            PromptTemplate(
                name="weekly_review",
                description="把学习输入整理成周复盘 JSON。",
                template=(
                    "你是一个 AI Agent 工程学习教练。"
                    "请基于用户最近的学习输入，返回严格 JSON，不要输出 Markdown。"
                    "JSON schema: "
                    '{{"summary":"一句话总结","learned":["已掌握点"],'
                    '"gaps":["薄弱点"],"next_steps":["下一步行动"]}}'
                ),
            ),
            PromptTemplate(
                name="interview_answer",
                description="把输入整理成面试回答 JSON。",
                template=(
                    "你是一个 Agent 工程面试官。"
                    "请把用户输入整理成可复述的面试回答，返回严格 JSON。"
                    "JSON schema: "
                    '{{"summary":"核心回答","learned":["关键论点"],'
                    '"gaps":["容易追问的缺口"],"next_steps":["补强建议"]}}'
                ),
            ),
        ]
    )
