from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import textwrap
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]", re.UNICODE)
SUPPORTED_FALLBACK_SUFFIXES = {".md", ".markdown", ".txt", ".csv", ".json"}


@dataclass(frozen=True)
class Document:
    source: str
    markdown: str


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source: str
    index: int
    text: str


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float


def tokenize(text: str) -> list[str]:
    tokens = [token.lower() for token in TOKEN_PATTERN.findall(text)]
    chinese_chars = [token for token in tokens if re.fullmatch(r"[\u4e00-\u9fff]", token)]
    bigrams = [
        "".join(chinese_chars[index : index + 2])
        for index in range(len(chinese_chars) - 1)
    ]
    return tokens + bigrams


def vectorize(text: str) -> Counter[str]:
    return Counter(tokenize(text))


def cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0

    dot = sum(weight * right.get(term, 0) for term, weight in left.items())
    left_norm = math.sqrt(sum(weight * weight for weight in left.values()))
    right_norm = math.sqrt(sum(weight * weight for weight in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def convert_with_markitdown(path: Path) -> str | None:
    try:
        from markitdown import MarkItDown
    except ImportError:
        return None

    result = MarkItDown(enable_plugins=False).convert(str(path))
    markdown = getattr(result, "text_content", None) or getattr(result, "markdown", "")
    return str(markdown).strip()


def fallback_convert(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown", ".txt"}:
        return path.read_text(encoding="utf-8")

    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        if not rows:
            return ""
        lines: list[str] = [f"# {path.stem}", ""]
        for row_index, row in enumerate(rows, start=1):
            lines.append(f"## Row {row_index}")
            for key, value in row.items():
                label = {"question": "问题", "answer": "答案", "owner": "负责人"}.get(key, key)
                lines.append(f"- {label}: {value}")
            lines.append("")
        return "\n".join(lines)

    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return f"# {path.stem}\n\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```"

    raise ValueError(
        f"{path} needs MarkItDown. Install dependencies with: python -m pip install -r requirements.txt"
    )


def convert_file(path: Path) -> Document:
    markdown = convert_with_markitdown(path)
    if markdown is None:
        if path.suffix.lower() not in SUPPORTED_FALLBACK_SUFFIXES:
            raise ValueError(
                f"MarkItDown is not installed, and no fallback converter exists for {path.suffix}."
            )
        markdown = fallback_convert(path)

    return Document(source=path.name, markdown=markdown.strip())


def iter_input_files(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
        return

    for item in sorted(path.rglob("*")):
        if item.is_file() and not item.name.startswith("."):
            yield item


def load_documents(input_path: Path) -> list[Document]:
    documents: list[Document] = []
    for file_path in iter_input_files(input_path):
        try:
            document = convert_file(file_path)
        except ValueError as exc:
            print(f"[skip] {exc}")
            continue

        if document.markdown:
            documents.append(document)

    return documents


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    clean = re.sub(r"\n{3,}", "\n\n", text.strip())
    if not clean:
        return []

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", clean) if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        is_heading = paragraph.startswith("#")
        if is_heading and current:
            chunks.append(current)
            current = paragraph
            continue

        if len(current) + len(paragraph) + 2 <= chunk_size:
            current = f"{current}\n\n{paragraph}".strip()
            continue

        if current:
            chunks.append(current)
        current = paragraph

        while len(current) > chunk_size:
            chunks.append(current[:chunk_size].strip())
            current = current[max(0, chunk_size - overlap) :].strip()

    if current:
        chunks.append(current)

    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    overlapped: list[str] = []
    previous_tail = ""
    for chunk in chunks:
        combined = f"{previous_tail}\n{chunk}".strip() if previous_tail else chunk
        overlapped.append(combined)
        previous_tail = chunk[-overlap:]
    return overlapped


def build_chunks(documents: list[Document], chunk_size: int, overlap: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        for index, text in enumerate(split_text(document.markdown, chunk_size, overlap), start=1):
            digest = hashlib.sha1(f"{document.source}:{index}:{text}".encode("utf-8")).hexdigest()[:8]
            chunks.append(
                Chunk(
                    chunk_id=f"{Path(document.source).stem}-{index}-{digest}",
                    source=document.source,
                    index=index,
                    text=text,
                )
            )
    return chunks


def search(chunks: list[Chunk], query: str, top_k: int) -> list[SearchHit]:
    query_vector = vectorize(query)
    hits = [
        SearchHit(chunk=chunk, score=cosine_similarity(query_vector, vectorize(chunk.text)))
        for chunk in chunks
    ]
    hits = [hit for hit in hits if hit.score > 0]
    return sorted(hits, key=lambda hit: hit.score, reverse=True)[:top_k]


def make_answer(query: str, hits: list[SearchHit]) -> str:
    if not hits:
        return "没有在当前文档中检索到足够相关的内容。请补充文档，或换一个更具体的问题。"

    answer_hits = select_answer_hits(hits)
    evidence = "\n".join(
        f"[{number}] {hit.chunk.source} chunk {hit.chunk.index}: {summarize(hit.chunk.text)}"
        for number, hit in enumerate(answer_hits, start=1)
    )
    return (
        f"问题：{query}\n\n"
        "基于检索结果，可以这样回答：\n"
        f"{compose_extractive_summary(query, answer_hits)}\n\n"
        "引用：\n"
        f"{evidence}"
    )


def select_answer_hits(hits: list[SearchHit]) -> list[SearchHit]:
    best_score = hits[0].score
    strong_hits = [hit for hit in hits if hit.score >= best_score * 0.72]
    return strong_hits or hits[:1]


def summarize(text: str, max_length: int = 180) -> str:
    one_line = re.sub(r"\s+", " ", text).strip()
    if len(one_line) <= max_length:
        return one_line
    return f"{one_line[:max_length].rstrip()}..."


def compose_extractive_summary(query: str, hits: list[SearchHit]) -> str:
    query_vector = vectorize(query)
    sentences: list[str] = []
    for hit in hits:
        candidates = re.split(r"(?<=[。！？.!?])\s+|\n+", hit.chunk.text)
        candidates = [
            candidate.strip("-:： \t")
            for candidate in candidates
            if 20 <= len(candidate.strip("-:： \t")) <= 220
        ]
        if candidates:
            best = max(candidates, key=lambda candidate: candidate_score(query_vector, candidate))
            sentences.append(clean_candidate(best))

    if not sentences:
        sentences = [summarize(hit.chunk.text, 160) for hit in hits]

    cited_sentences = [f"{sentence} [{index}]" for index, sentence in enumerate(sentences, start=1)]
    return "\n".join(cited_sentences)


def candidate_score(query_vector: Counter[str], candidate: str) -> float:
    score = cosine_similarity(query_vector, vectorize(candidate))
    normalized = candidate.lower().lstrip("- ")
    if normalized.startswith(("答案:", "答案：", "answer:", "answer：")):
        score += 0.2
    if normalized.startswith(("问题:", "问题：", "question:", "question：")):
        score -= 0.08
    return score


def clean_candidate(candidate: str) -> str:
    return re.sub(r"^(答案|answer)\s*[:：]\s*", "", candidate, flags=re.IGNORECASE)


def write_markdown_outputs(documents: list[Document], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for document in documents:
        output_path = output_dir / f"{Path(document.source).stem}.md"
        output_path.write_text(document.markdown + "\n", encoding="utf-8")
        print(f"[write] {output_path}")


def run_convert(args: argparse.Namespace) -> None:
    documents = load_documents(args.input)
    write_markdown_outputs(documents, args.output)
    print(f"converted {len(documents)} document(s)")


def run_ask(args: argparse.Namespace) -> None:
    documents = load_documents(args.docs)
    chunks = build_chunks(documents, chunk_size=args.chunk_size, overlap=args.overlap)
    hits = search(chunks, args.query, top_k=args.top_k)

    print(f"loaded {len(documents)} document(s), built {len(chunks)} chunk(s)")
    print()
    print(make_answer(args.query, hits))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Day 21 minimal RAG CLI with MarkItDown document conversion."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="Convert files to Markdown.")
    convert_parser.add_argument("input", type=Path, help="Input file or directory.")
    convert_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("build/markdown"),
        help="Output directory for converted Markdown files.",
    )
    convert_parser.set_defaults(func=run_convert)

    ask_parser = subparsers.add_parser("ask", help="Ask a question against local documents.")
    ask_parser.add_argument("query", help="Question to answer.")
    ask_parser.add_argument(
        "--docs",
        type=Path,
        default=Path("sample_docs"),
        help="Document file or directory.",
    )
    ask_parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve.")
    ask_parser.add_argument("--chunk-size", type=int, default=500, help="Target chunk size.")
    ask_parser.add_argument("--overlap", type=int, default=0, help="Character overlap between chunks.")
    ask_parser.set_defaults(func=run_ask)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
