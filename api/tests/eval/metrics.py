"""
Scoring functions for eval pipeline.

v2: Context-aware forbidden keywords, paraphrase-tolerant matching.
"""

import re
from dataclasses import dataclass, field


# Words that signal a forbidden keyword is mentioned as historical context, not current fact
_HISTORICAL_CONTEXT = re.compile(
    r"(previously|reduced from|reduction from|was|old|earlier|formerly|used to be|prior to|before|down from|dropped from|changed from|cut from|not\s|was\s|isn't|wasn't|rumor|incorrect|wrong|false|no\s|don't|doesn't|didn't|alleged|claimed|supposedly)",
    re.IGNORECASE,
)

# Alias map: expected keyword → acceptable paraphrases
_ALIASES = {
    "cannot": ["can't", "not able", "not eligible", "not available", "not covered", "not applicable", "inaccessible", "prohibited", "disallowed"],
    "not covered": ["not available", "not eligible", "not applicable", "excluded", "does not cover", "does not apply"],
    "excluded": ["not counted", "exempt", "not included", "outside", "left out", "disregarded", "not considered"],
    "free": ["no charge", "zero cost", "complimentary", "at no cost", "without charge", "rupees zero"],
    "voluntary": ["not mandatory", "optional", "not compulsory", "elective"],
    "1.5 crore": ["1,50,00,000", "15 million", "rs 1.5 crore", "rs. 1.5 crore", "₹1.5 crore"],
    "40 lakh": ["40,00,000", "4 million", "rs 40 lakh", "rs. 40 lakh", "₹40 lakh"],
    "20th": ["20", "20th of"],
    "31 December": ["december 31", "31st december", "31 dec", "dec 31"],
    "2 crore": ["2,00,00,000", "20 million", "rs 2 crore", "₹2 crore"],
    "NIL": ["nil", "0%", "zero", "zero-rated", "not rated", "no tax"],
    "1%": ["1 percent", "one percent"],
    "18%": ["18 percent", "eighteen percent"],
    "45 days": ["45", "forty-five days", "forty five days"],
    "43B(h)": ["43b(h)", "section 43b(h)", "43b h"],
    "deductible": ["allowable", "claimable", "admissible"],
    "expenses": ["expense", "expenditure", "costs", "deductions"],
    "trading": ["trader", "retail", "reseller"],
    "e-commerce": ["ecommerce", "e-commerce", "online marketplace"],
    "ineligible": ["not eligible", "not allowed", "barred", "prohibited", "not permitted", "excluded"],
    "PAN": ["pan", "permanent account number"],
    "refuse": ["cannot help", "unable to", "outside my scope", "not related", "beyond my"],
    "5%": ["5 percent", "five percent", "0.05"],
    "125 crore": ["125", "1,25,00,00,000"],
    "100 crore": ["100", "1,00,00,00,000"],
    "500 crore": ["500", "5,00,00,00,000"],
    "10 crore": ["10", "1,00,00,000"],
    "2.5 crore": ["2.5", "25 million", "2,50,00,000"],
    "25 crore": ["25", "250 million", "25,00,00,000"],
}


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


def _is_historical_context(answer_lower: str, keyword_lower: str) -> bool:
    """Check if a forbidden keyword appears in historical context, not as a current fact."""
    # Find all occurrences of the keyword
    idx = 0
    while True:
        pos = answer_lower.find(keyword_lower, idx)
        if pos == -1:
            return False

        # Look at the 60 characters before the keyword
        start = max(0, pos - 60)
        preceding = answer_lower[start:pos]

        if _HISTORICAL_CONTEXT.search(preceding):
            return True

        idx = pos + len(keyword_lower)


def _check_keyword_match(answer_lower: str, keyword_lower: str) -> bool:
    """Check if a keyword matches in the answer, with alias support."""
    # Direct match
    if keyword_lower in answer_lower:
        return True

    # Check aliases — both directions
    # 1. keyword is the key, check if any alias value matches
    for alias_key, alias_values in _ALIASES.items():
        if alias_key.lower() == keyword_lower:
            for alias in alias_values:
                if alias.lower() in answer_lower:
                    return True

    # 2. keyword is an alias value, check if the key matches
    for alias_key, alias_values in _ALIASES.items():
        for alias in alias_values:
            if alias.lower() == keyword_lower and alias_key.lower() in answer_lower:
                return True

    return False


def score_answer(
    fixture: dict,
    answer: str,
) -> EvalResult:
    """Score an answer against expected keywords and forbidden keywords."""
    answer_lower = answer.lower()

    # Check expected keywords (all must appear, with alias support)
    keyword_hits = []
    keyword_misses = []
    for kw in fixture["expected_keywords"]:
        if _check_keyword_match(answer_lower, kw.lower()):
            keyword_hits.append(kw)
        else:
            keyword_misses.append(kw)

    # Check forbidden keywords (none should appear unless in historical context)
    forbidden_hits = []
    for kw in fixture["forbidden_keywords"]:
        kw_lower = kw.lower()
        if kw_lower in answer_lower:
            if not _is_historical_context(answer_lower, kw_lower):
                forbidden_hits.append(kw)

    # Determine pass/fail
    all_keywords_found = len(keyword_misses) == 0
    no_forbidden = len(forbidden_hits) == 0

    if fixture["expected_behavior"] == "refuse":
        refusal_indicators = [
            "cannot", "can't", "unable", "outside", "scope",
            "not able", "sorry", "not related", "beyond my",
            "not related to", "not compliance",
        ]
        is_refusal = any(ind in answer_lower for ind in refusal_indicators) or len(answer.split()) < 30
        passed = is_refusal
    elif fixture["expected_behavior"] == "answer":
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

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "N/A",
    }
