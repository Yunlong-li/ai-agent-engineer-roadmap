# Python 类型标注（Type Hints）完全讲解

Python 是动态类型语言（变量类型无需声明，运行时才确定），而**类型标注**（Type Hints）是 Python 3.5+ 引入的特性，核心作用是「静态声明变量/函数的类型」——既不影响代码运行（解释器会忽略标注），又能提升代码可读性、支持静态类型检查（如 `mypy`）、增强 IDE 智能提示，是工程化开发（尤其是 Agent 这类复杂系统）的必备实践。

## 一、核心价值（为什么要用？）

1. **提升可读性**：一眼看出变量/函数的类型，不用读代码逻辑猜（比如 Agent 工具的入参是 `str` 还是 `dict`）；
2. **IDE 智能提示**：PyCharm、VS Code 能基于标注给出精准的补全、报错提示；
3. **静态类型检查**：用 `mypy` 提前发现类型错误（如把 `int` 传给需要 `str` 的参数），避免运行时踩坑；
4. **工程化协作**：多人开发 Agent 服务时，类型标注是「隐性接口文档」，减少沟通成本；
5. **适配 Schema 校验**：和 Agent 的请求/响应 Schema 呼应，便于结构化数据解析。

## 二、基础语法：变量/函数的类型标注

### 1. 变量标注（最基础）

格式：`变量名: 类型 = 值`，支持基础类型、复杂类型、可选类型。

```python
# 基础类型
name: str = "Agent"  # 字符串
age: int = 18        # 整数
is_running: bool = True  # 布尔值
score: float = 95.5  # 浮点数

# 可选类型（可能为 None）
email: str | None = None  # Python 3.10+ 写法（推荐）
# 3.10 以下需导入：from typing import Optional
# email: Optional[str] = None

# 容器类型（列表、字典、元组）
# 列表：List[元素类型]（3.9+ 可直接用 list）
tools: list[str] = ["codegraph", "mcp", "function_call"]  # 字符串列表
# 字典：Dict[键类型, 值类型]（3.9+ 可直接用 dict）
config: dict[str, int] = {"timeout": 60, "retry": 3}  # 键是字符串，值是整数
# 元组（固定长度+固定类型）
position: tuple[int, int] = (100, 200)  # 两个整数组成的元组
```

### 2. 函数标注（核心：入参+返回值）

格式：`def 函数名(参数名: 类型, ...) -> 返回值类型:`

```python
# 基础函数标注
def call_tool(tool_name: str, params: dict[str, any]) -> dict[str, any]:
    """
    调用 Agent 工具的函数
    :param tool_name: 工具名称（字符串）
    :param params: 工具入参（字典）
    :return: 工具返回结果（字典）
    """
    # 业务逻辑
    return {"success": True, "data": params}

# 无返回值（返回 None）
def log_error(msg: str) -> None:
    print(f"Error: {msg}")

# 可选参数 + 默认值
def query_data(keyword: str, page: int = 1, size: int | None = None) -> list[dict]:
    """page 有默认值，size 可选（可为 None）"""
    return [{"id": 1, "content": "test"}]
```

## 三、进阶：复杂类型标注（Agent 开发高频用）

Agent 开发中常遇到「嵌套结构、任意类型、回调函数」等场景，需用到进阶类型：

### 1. 任意类型（Any）

表示「不限制类型」，适合无法确定类型的场景（尽量少用，会失去类型检查价值）：

```python
from typing import Any

def process_result(data: Any) -> Any:
    """处理任意类型的工具返回结果"""
    return data
```

### 2. 嵌套容器（Agent 响应/请求 Schema 常用）

比如 Agent 的 `ToolResult` 结构化数据：

```python
# 嵌套字典+列表（模拟 ToolResult）
ToolResult = dict[str, bool | dict[str, str] | str]  # 类型别名（见下文）

def build_tool_result(success: bool, error: dict[str, str], suggestion: str) -> ToolResult:
    return {
        "success": success,
        "error": error,
        "suggestion": suggestion
    }
```

### 3. 类型别名（Type Aliases）

给复杂类型起「别名」，简化标注（Agent 中定义 Schema 时超实用）：

```python
from typing import TypeAlias

# 定义别名：Agent 请求参数类型
AgentRequest: TypeAlias = dict[str, str | int | list[str]]
# 定义别名：工具调用结果类型
ToolCallResult: TypeAlias = tuple[bool, dict | None, str]

# 使用别名
def handle_agent_request(req: AgentRequest) -> ToolCallResult:
    return (True, {"data": "ok"}, "success")
```

### 4. 泛型（Generics）

针对「容器类型不固定」的场景（比如通用的缓存工具）：

```python
from typing import Generic, TypeVar

T = TypeVar("T")  # 定义类型变量

class AgentCache(Generic[T]):
    """通用缓存类，支持任意类型的缓存值"""
    def __init__(self):
        self.cache: dict[str, T] = {}

    def set(self, key: str, value: T) -> None:
        self.cache[key] = value

    def get(self, key: str) -> T | None:
        return self.cache.get(key)

# 使用泛型：缓存字符串
str_cache = AgentCache[str]()
str_cache.set("tool_name", "codegraph")
# 使用泛型：缓存字典
dict_cache = AgentCache[dict]()
dict_cache.set("config", {"timeout": 60})
```

### 5. 函数类型（Callable）

标注「回调函数/函数参数」（Agent 工具编排时常用）：

```python
from typing import Callable

# 标注：参数是「函数」，该函数接收 str 返回 bool
def validate_tool(validator: Callable[[str], bool], tool_name: str) -> bool:
    return validator(tool_name)

# 定义符合类型的验证函数
def check_tool(tool: str) -> bool:
    return tool in ["codegraph", "mcp"]

# 调用
validate_tool(check_tool, "codegraph")  # 返回 True
```

## 四、实战：Agent 工具层的类型标注示例

结合之前聊的 `ToolResult`，用类型标注规范 Agent 工具调用：

```python
from typing import TypedDict, Optional  # TypedDict 用于结构化字典

# 定义 ToolResult 结构化类型（比普通 dict 更规范）
class ToolError(TypedDict):
    type: str
    code: int
    msg: str

class ToolResult(TypedDict):
    success: bool
    data: Optional[dict]  # 可选字典
    error: Optional[ToolError]  # 可选错误结构
    suggestion: Optional[str]  # 可选建议

# 工具调用函数（完整标注）
def call_codegraph_tool(params: dict[str, str]) -> ToolResult:
    """调用 CodeGraph 工具"""
    try:
        # 模拟工具调用成功
        return {
            "success": True,
            "data": {"result": "code index ok"},
            "error": None,
            "suggestion": None
        }
    except Exception as e:
        # 模拟工具调用失败
        return {
            "success": False,
            "data": None,
            "error": {"type": "system_error", "code": 500, "msg": str(e)},
            "suggestion": "请重启 CodeGraph 服务后重试"
        }
```

## 五、类型检查工具：mypy

类型标注本身不影响运行，需用 `mypy` 做静态检查，提前发现类型错误：

### 1. 安装

```bash
pip install mypy
```

### 2. 使用

```bash
# 检查单个文件
mypy agent_tool.py
# 检查整个项目
mypy your_agent_project/
```

### 示例：错误检测

如果写了这样的代码：

```python
# 错误：把 int 传给需要 str 的参数
call_codegraph_tool(params={"path": 123})
```

运行 `mypy` 会直接报错：

```
error: Argument "params" to "call_codegraph_tool" has incompatible type "dict[str, int]"; expected "dict[str, str]"
```

## 六、关键注意事项

1. **兼容性**：Python 3.5+ 支持基础标注，3.9+ 支持 `list[str]`（替代 `List[str]`），3.10+ 支持 `str | None`（替代 `Optional[str]`）；
2. **运行时忽略**：解释器不会校验类型，比如 `name: str = 18` 能运行，但 `mypy` 会报错；
3. **不要过度标注**：简单脚本可不用，复杂 Agent 服务、工具库必须标注；
4. **结合 Schema**：类型标注和 Agent 的请求/响应 Schema 一一对应，便于结构化数据校验。

## 总结

Python 类型标注是「动态语言的静态化补充」，核心价值是**提升代码可读性、工程化能力、提前发现错误**。在 Agent 开发中，标注请求/响应、工具入参/出参的类型，能和 Schema 形成闭环，让复杂的工具调用、多模块协作更稳定，是从「脚本开发」到「工程化开发」的关键一步。
