import json

result = {
    "role": "ai_agent_engineer",
    "skills": ["backend", "rag", "tool_calling", "evaluation"],
    "goal": "build production-ready agent systems",
}

print(json.dumps(result, ensure_ascii=False, indent=2))