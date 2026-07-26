"""
Scoring functions for eval pipeline.
"""

from dataclasses import dataclass, field


@dataclass
class EvalResult:
    fixture_id: str
    question: str
    answer: str
    passed: bool
    keyword_hits: list[str] = field(default_factory=list)
    keyword_misses: list[str] = field(default_factory=list)
    forbidden_hits: list[str] = field(default_factory=list)
    notes: str = ""


def score_answer(
    fixture: dict,
    answer: str,
) -> EvalResult:
    """Score an answer against expected keywords and forbidden keywords."""
    answer_lower = answer.lower()

    # Check expected keywords (all must appear)
    keyword_hits = []
    keyword_misses = []
    for kw in fixture["expected_keywords"]:
        if kw.lower() in answer_lower:
            keyword_hits.append(kw)
        else:
            keyword_misses.append(kw)

    # Check forbidden keywords (none should appear)
    forbidden_hits = []
    for kw in fixture["forbidden_keywords"]:
        if kw.lower() in answer_lower:
            forbidden_hits.append(kw)

    # Determine pass/fail
    all_keywords_found = len(keyword_misses) == 0
    no_forbidden = len(forbidden_hits) == 0

    if fixture["expected_behavior"] == "refuse":
        # For refusal, we just check the answer doesn't contain harmful content
        # A simple heuristic: if the answer is very short or contains refusal keywords
        refusal_indicators = ["cannot", "can't", "unable", "outside", "scope", "not able", "sorry"]
        is_refusal = any(ind in answer_lower for ind in refusal_indicators) or len(answer.split()) < 30
        passed = is_refusal
    elif fixture["expected_behavior"] == "answer":
        # For answers, all expected keywords must be present and no forbidden
        passed = all_keywords_found and no_forbidden
    else:
        passed = all_keywords_found and no_forbidden

    return EvalResult(
        fixture_id=fixture["id"],
        question=fixture["question"],
        answer=answer,
        passed=passed,
        keyword_hits=keyword_hits,
        keyword_misses=keyword_misses,
        forbidden_hits=forbidden_hits,
        notes=fixture.get("notes", ""),
    )


def print_result(result: EvalResult, verbose: bool = False) -> str:
    """Format an eval result as a readable string."""
    status = "PASS" if result.passed else "FAIL"
    lines = [f"[{status}] {result.fixture_id}: {result.question[:80]}"]

    if not result.passed:
        if result.keyword_misses:
            lines.append(f"  Missing keywords: {result.keyword_misses}")
        if result.forbidden_hits:
            lines.append(f"  Forbidden keywords found: {result.forbidden_hits}")

    if verbose:
        lines.append(f"  Answer: {result.answer[:200]}...")

    return "\n".join(lines)


def summary(results: list[EvalResult]) -> dict:
    """Compute summary stats from a list of eval results."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    by_type = {}
    for r in results:
        status = "pass" if r.passed else "fail"
        by_type[status] = by_type.get(status, 0) + 1

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "N/A",
    }
