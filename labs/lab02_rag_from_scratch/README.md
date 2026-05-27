# Lab 02：手写一个小 RAG

## 学习目标

- 文档切片。
- 简单关键词检索。
- 引用溯源。
- 理解 RAG pipeline。

## 运行

```powershell
python rag_cli.py
```

## 练习

1. 把关键词检索替换成 embedding 检索。
2. 给每个 chunk 增加 `allowed_roles`。
3. 实现 `Recall@3` 评测。

