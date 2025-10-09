from ai_core.eval.spotcheck import QueryCase, evaluate_cases


def test_evaluate_cases_basic_pass():
    def retriever(q: str) -> str:
        return "port scan detected" if "port" in q else ""

    cases = [QueryCase(query="guardduty port scan", expected="port scan detected")]
    results, pct = evaluate_cases(cases, retriever, threshold=0.3)
    assert len(results) == 1
    assert results[0].passed is True
    assert pct == 1.0


def test_evaluate_cases_empty_sets():
    def retriever(q: str) -> str:  # pragma: no cover - trivial stub
        return "" if q == "" else "irrelevant"

    cases = [QueryCase(query="", expected="")]
    results, pct = evaluate_cases(cases, retriever)
    assert results[0].score == 1.0  # empty vs empty -> perfect similarity
    assert results[0].passed is True
    assert pct == 1.0
