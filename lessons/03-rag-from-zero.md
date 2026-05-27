# 03. RAG 从零到可用

## 1. RAG 是什么

RAG 的全称是 Retrieval-Augmented Generation，检索增强生成。

它解决的问题是：模型本身不知道或不可靠的信息，通过外部知识库检索后再回答。

典型链路：

```text
用户问题
  -> 查询改写
  -> 文档检索
  -> 结果重排
  -> 构造上下文
  -> 模型生成
  -> 引用溯源
```

## 2. RAG 的数据结构

一个 chunk 不应该只有文本：

```python
from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source: str
    title: str
    page: int | None
    metadata: dict
```

metadata 可以包含：

- tenant_id：租户。
- allowed_roles：权限。
- created_at：时间。
- doc_type：文档类型。
- version：版本。

## 3. Chunk 策略

不要机械地每 500 字切一刀。更好的顺序：

1. 优先按标题层级切。
2. 再按段落切。
3. 太长时用滑动窗口。
4. 保留标题作为上下文。

示例：

```python
def chunk_markdown(title: str, text: str, max_chars: int = 800) -> list[str]:
    chunks = []
    current = f"# {title}\n\n"
    for paragraph in text.split("\n\n"):
        if len(current) + len(paragraph) > max_chars and current.strip():
            chunks.append(current.strip())
            current = f"# {title}\n\n{paragraph}"
        else:
            current += "\n\n" + paragraph
    if current.strip():
        chunks.append(current.strip())
    return chunks
```

## 4. 检索不只是向量

向量检索适合语义相似：

```text
问：怎么取消订单？
文档：用户可以在待发货状态申请退款。
```

关键词检索适合精确匹配：

```text
问：错误码 E1024 是什么？
文档：E1024 表示库存锁定失败。
```

生产 RAG 常用混合检索：

```python
final_score = 0.7 * vector_score + 0.3 * keyword_score
```

## 5. 引用溯源

回答不能只说“根据资料”。应该给出证据：

```text
黄金会员每月可领取 2 张优惠券。[member_policy.md#coupon]
```

如果没有证据，就应该回答资料不足。

## 6. RAG 评测

检索侧：

- Recall@k：正确文档是否出现在前 k 个。
- MRR：正确文档排得是否靠前。

生成侧：

- Faithfulness：回答是否忠于资料。
- Answer relevance：是否回答了问题。
- Citation accuracy：引用是否支持结论。

一个 eval case：

```json
{
  "question": "黄金会员每月几张优惠券？",
  "expected_sources": ["member_policy.md#coupon"],
  "expected_answer_keywords": ["2", "优惠券"]
}
```

## 7. 常见优化路径

问题：检索不到。

排查：

- query 是否需要改写。
- chunk 是否切碎了语义。
- embedding 模型是否适合中文/业务语料。
- 权限过滤是否误过滤。
- top-k 是否太小。

问题：检索到了但回答错。

排查：

- prompt 是否允许模型使用外部常识。
- 上下文是否太长导致模型忽略重点。
- rerank 是否把关键证据排后面。
- 输出是否要求引用。

## 8. 面试表达

```text
我会把 RAG 优化拆成检索侧和生成侧。检索侧看 Recall@k、MRR，重点调文档解析、chunk、query rewrite、混合检索和 rerank；生成侧看忠实度、引用准确率和答案相关性，重点调 prompt、上下文裁剪和结构化输出。线上还要加权限过滤、trace、评测集和回归测试，避免靠主观感觉调参。
```

