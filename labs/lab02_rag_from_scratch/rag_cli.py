import re
from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source: str


DOCUMENTS = {
    "member_policy.md": """
    黄金会员权益

    黄金会员每月可以领取 2 张优惠券。优惠券当月有效，不能转让。

    退款规则

    会员服务开通后 7 天内，如果没有使用会员权益，可以申请退款。
    """,
    "campaign_policy.md": """
    促销活动规则

    满减活动和折扣活动不能叠加。大促期间，部分商品会限制优惠券使用。
    """,
}


def split_into_chunks(source: str, text: str, max_chars: int = 120) -> list[Chunk]:
    chunks: list[Chunk] = []
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    current = ""
    index = 1
    for paragraph in paragraphs:
        if len(current) + len(paragraph) > max_chars and current:
            chunks.append(Chunk(f"{source}#{index}", current.strip(), source))
            current = paragraph
            index += 1
        else:
            current += "\n\n" + paragraph
    if current.strip():
        chunks.append(Chunk(f"{source}#{index}", current.strip(), source))
    return chunks


def build_index() -> list[Chunk]:
    chunks: list[Chunk] = []
    for source, text in DOCUMENTS.items():
        chunks.extend(split_into_chunks(source, text))
    return chunks


def tokenize_query(query: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", query.lower()).strip()
    words = re.findall(r"[a-z0-9_]+", normalized)
    cjk_chars = re.findall(r"[\u4e00-\u9fff]", normalized)
    cjk_bigrams = ["".join(cjk_chars[index:index + 2]) for index in range(len(cjk_chars) - 1)]
    return words + cjk_chars + cjk_bigrams


def keyword_score(query: str, text: str) -> int:
    query_tokens = tokenize_query(query)
    lowered_text = text.lower()
    return sum(1 for token in query_tokens if token in lowered_text)


def search(query: str, chunks: list[Chunk], top_k: int = 3) -> list[Chunk]:
    scored = [(keyword_score(query, chunk.text), chunk) for chunk in chunks]
    scored = [item for item in scored if item[0] > 0]
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def answer(query: str, chunks: list[Chunk]) -> str:
    hits = search(query, chunks)
    if not hits:
        return "资料不足，无法回答。"

    context = "\n\n".join(f"[{hit.chunk_id}]\n{hit.text}" for hit in hits)
    return (
        "这是一个教学版 RAG。真实系统会把以下上下文交给 LLM 生成答案。\n\n"
        f"用户问题：{query}\n\n"
        f"检索上下文：\n{context}\n\n"
        "回答要求：只基于上下文回答，并在关键结论后标注引用。"
    )


def main() -> None:
    chunks = build_index()
    print("RAG CLI started. 输入问题，输入 exit 退出。")
    while True:
        query = input("\nQuestion> ").strip()
        if query == "exit":
            break
        print(answer(query, chunks))


if __name__ == "__main__":
    main()
