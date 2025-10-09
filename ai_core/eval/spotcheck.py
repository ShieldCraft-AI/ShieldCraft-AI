from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable, List, Sequence, Tuple


TokenizeFn = Callable[[str], List[str]]


def simple_tokenize(text: str) -> List[str]:
    return [t.lower() for t in text.split()] if text else []


def jaccard_similarity(a: Sequence[str], b: Sequence[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    inter = sa & sb
    union = sa | sb
    return len(inter) / len(union)


@dataclass
class QueryCase:
    query: str
    expected: str


@dataclass
class CaseResult:
    query: str
    expected: str
    retrieved: str
    score: float
    passed: bool


def evaluate_cases(
    cases: Iterable[QueryCase],
    retriever: Callable[[str], str],
    *,
    tokenize: TokenizeFn = simple_tokenize,
    threshold: float = 0.4,
) -> Tuple[List[CaseResult], float]:
    results: List[CaseResult] = []
    passed = 0
    total = 0
    for c in cases:
        total += 1
        retrieved = retriever(c.query)
        score = jaccard_similarity(tokenize(c.expected), tokenize(retrieved))
        ok = score >= threshold
        results.append(
            CaseResult(
                query=c.query,
                expected=c.expected,
                retrieved=retrieved,
                score=round(score, 4),
                passed=ok,
            )
        )
        if ok:
            passed += 1
    pct = (passed / total) if total else 0.0
    return results, pct
