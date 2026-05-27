import sqlite3
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolResult:
    ok: bool
    data: Any = None
    error_code: str | None = None
    message: str = ""


@dataclass
class Tool:
    name: str
    description: str
    parse_args: Callable[[dict[str, Any]], Any]
    func: Callable[[Any], ToolResult]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def run(self, name: str, raw_args: dict[str, Any]) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(ok=False, error_code="tool_not_found", message=name)
        try:
            args = tool.parse_args(raw_args)
        except ValueError as exc:
            return ToolResult(ok=False, error_code="invalid_args", message=str(exc))
        return tool.func(args)


@dataclass
class CalculatorArgs:
    expression: str


def parse_calculator_args(raw_args: dict[str, Any]) -> CalculatorArgs:
    expression = raw_args.get("expression")
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("expression must be a non-empty string")
    return CalculatorArgs(expression=expression)


def calculator(args: CalculatorArgs) -> ToolResult:
    allowed = set("0123456789+-*/(). ")
    if any(char not in allowed for char in args.expression):
        return ToolResult(ok=False, error_code="unsafe_expression", message="Only arithmetic is allowed")
    try:
        value = eval(args.expression, {"__builtins__": {}}, {})
        return ToolResult(ok=True, data={"value": value})
    except Exception as exc:
        return ToolResult(ok=False, error_code="calculation_error", message=str(exc))


@dataclass
class SqlArgs:
    query: str


def parse_sql_args(raw_args: dict[str, Any]) -> SqlArgs:
    query = raw_args.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    return SqlArgs(query=query)


def init_database() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE orders(id INTEGER, user_id TEXT, amount REAL, status TEXT)")
    conn.executemany(
        "INSERT INTO orders(id, user_id, amount, status) VALUES (?, ?, ?, ?)",
        [
            (1, "u1", 99.0, "paid"),
            (2, "u1", 199.0, "paid"),
            (3, "u2", 39.0, "refunded"),
        ],
    )
    return conn


DB = init_database()


def assert_readonly_sql(query: str) -> None:
    lowered = query.strip().lower()
    if not lowered.startswith("select"):
        raise ValueError("Only SELECT is allowed")
    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate"]
    if any(word in lowered for word in forbidden):
        raise ValueError("Unsafe SQL")


def run_sql(args: SqlArgs) -> ToolResult:
    try:
        assert_readonly_sql(args.query)
        rows = DB.execute(args.query).fetchmany(20)
        return ToolResult(ok=True, data={"rows": rows})
    except Exception as exc:
        return ToolResult(ok=False, error_code="sql_error", message=str(exc))


class FakePlanner:
    def decide(self, goal: str, observations: list[ToolResult]) -> dict[str, Any]:
        if observations:
            latest = observations[-1]
            return {"type": "final", "answer": f"Tool returned: {latest.data or latest.message}"}
        if "order" in goal.lower() or "u1" in goal.lower():
            return {
                "type": "tool",
                "tool": "run_sql",
                "arguments": {"query": "SELECT * FROM orders WHERE user_id = 'u1'"},
            }
        return {"type": "tool", "tool": "calculator", "arguments": {"expression": "1 + 2 * 3"}}


def run_agent(goal: str, registry: ToolRegistry, max_steps: int = 3) -> str:
    planner = FakePlanner()
    observations: list[ToolResult] = []
    trace: list[dict[str, Any]] = []

    for step in range(1, max_steps + 1):
        action = planner.decide(goal, observations)
        trace.append({"step": step, "action": action})

        if action["type"] == "final":
            print("TRACE:", trace)
            return action["answer"]

        result = registry.run(action["tool"], action["arguments"])
        observations.append(result)
        trace[-1]["observation"] = result

    print("TRACE:", trace)
    return "Task failed: max steps reached"


def main() -> None:
    registry = ToolRegistry()
    registry.register(Tool("calculator", "Run safe arithmetic calculation", parse_calculator_args, calculator))
    registry.register(Tool("run_sql", "Run read-only SQL query", parse_sql_args, run_sql))

    print(run_agent("Find orders for u1", registry))
    print(run_agent("Calculate 1 + 2 * 3", registry))


if __name__ == "__main__":
    main()
