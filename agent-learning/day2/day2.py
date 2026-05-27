from dataclasses import dataclass


@dataclass
class ToolResult:
    ok: bool
    content: str
    error: str | None = None


def divide(a: float, b: float) -> ToolResult:
    try:
        return ToolResult(ok=True, content=str(a / b))
    except ZeroDivisionError as exc:
        return ToolResult(ok=False, content="", error=str(exc))


print(divide(10, 2))
print(divide(10, 0))