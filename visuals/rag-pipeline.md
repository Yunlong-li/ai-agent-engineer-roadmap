# RAG 检索增强生成流程图 / RAG Pipeline

RAG 不是“向量库 + 大模型”这么简单。完整 RAG 至少包含文档处理、索引、检索、重排、生成和评测。

```mermaid
flowchart LR
    RAW["原始文档<br/>Raw Documents<br/>PDF / HTML / Markdown / 表格 Table"] --> PARSE["解析与清洗<br/>Parse & Clean<br/>保留标题、来源、页码<br/>Keep title, source, page"]
    PARSE --> CHUNK["文档切片<br/>Chunking<br/>按标题 / 按段落 / 重叠窗口<br/>Title-aware / Paragraph / Overlap"]
    CHUNK --> EMB["向量化<br/>Embedding<br/>把文本转成向量<br/>Text to Vector"]
    CHUNK --> META["元数据<br/>Metadata<br/>租户 / 角色 / 来源 / 版本<br/>Tenant / Role / Source / Version"]
    EMB --> INDEX["向量索引<br/>Vector Index"]
    META --> INDEX

    Q["用户问题<br/>User Question"] --> REWRITE["查询改写<br/>Query Rewrite<br/>补全指代 / 扩展关键词<br/>Resolve references / Expand keywords"]
    REWRITE --> HYBRID["混合检索<br/>Hybrid Retrieval<br/>向量检索 + BM25<br/>Vector Search + BM25"]
    INDEX --> HYBRID
    HYBRID --> FILTER["权限过滤<br/>Permission Filter<br/>租户 / 角色 / 数据范围<br/>Tenant / Role / Data Scope"]
    FILTER --> RERANK["重排<br/>Rerank<br/>选出最相关证据<br/>Select best evidence"]
    RERANK --> CTX["上下文构造<br/>Context Builder<br/>裁剪 / 引用 / 去重<br/>Trim / Cite / Deduplicate"]
    CTX --> GEN["大模型生成<br/>LLM Generation<br/>只基于证据回答<br/>Answer only from evidence"]
    GEN --> OUT["带引用的答案<br/>Answer with Citations"]

    OUT --> EVAL["评测<br/>Eval<br/>召回率 / 忠实度 / 引用准确率<br/>Recall@k / Faithfulness / Citation Accuracy"]
```

## 面试抓手

当面试官问“如何优化 RAG”，不要直接说“换 embedding 模型”。按这条链路排查：

1. 文档是否解析干净。
2. chunk 是否保留完整语义。
3. query 是否需要改写。
4. 是否需要混合检索。
5. rerank 是否提升证据质量。
6. 权限过滤是否正确。
7. prompt 是否要求引用和资料不足策略。
8. eval 是否能证明指标提升。
