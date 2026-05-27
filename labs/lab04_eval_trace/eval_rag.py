from dataclasses import dataclass


@dataclass
class EvalCase:
    question: str
    expected_sources: list[str]


CASES = [
    EvalCase("黄金会员每月几张优惠券？", ["member_policy.md#1"]),
    EvalCase("会员开通后几天内能退款？", ["member_policy.md#2"]),
    EvalCase("满减和折扣能叠加吗？", ["campaign_policy.md#1"]),
]


RETRIEVAL_RESULTS = {
    "黄金会员每月几张优惠券？": ["member_policy.md#1", "campaign_policy.md#1"],
    "会员开通后几天内能退款？": ["member_policy.md#2"],
    "满减和折扣能叠加吗？": ["campaign_policy.md#1"],
}


def recall_at_k(retrieved: list[str], expected: list[str], k: int) -> float:
    if not expected:
        return 1.0
    return len(set(retrieved[:k]) & set(expected)) / len(set(expected))


def main() -> None:
    scores = []
    trace = []
    for case in CASES:
        retrieved = RETRIEVAL_RESULTS.get(case.question, [])
        score = recall_at_k(retrieved, case.expected_sources, k=3)
        scores.append(score)
        trace.append(
            {
                "question": case.question,
                "expected_sources": case.expected_sources,
                "retrieved": retrieved,
                "recall_at_3": score,
            }
        )

    print("Trace:")
    for item in trace:
        print(item)

    print(f"\nRecall@3: {sum(scores) / len(scores):.2f}")


if __name__ == "__main__":
    main()

