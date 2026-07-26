"""
Source authority scoring for document ranking.

Assigns authority weights to document sources based on their type and filename patterns.
Higher authority = more trustworthy = gets a boost in reranking.
"""

import re
import logfire


# ── Authority Tiers ───────────────────────────────────────────────────────────

# Tier 1: Government/Regulatory (highest authority)
_GOVERNMENT_PATTERNS = [
    r"cbic", r"gst\.gov", r"msme\.gov", r"udyam",
    r"ministry", r"gazette", r"notification",
    r"official", r"regulatory", r"act\b", r"rule",
]

# Tier 2: Verified professional sources
_VERIFIED_PATTERNS = [
    r"guide", r"handbook", r"manual", r"reference",
    r"compliance", r"tax", r"gst.*guide", r"msme.*guide",
    r"accountune", r"ca.*firm", r"professional",
]

# Tier 3: Professional forums / Q&A
_FORUM_PATTERNS = [
    r"forum", r"qna", r"q&a", r"stack", r"quora",
    r"reddit", r"linkedin", r"blog",
]

# Tier 4: Marketing / sales pages
_MARKETING_PATTERNS = [
    r"marketing", r"sales", r"promo", r"advert",
    r"consultancy", r"agency", r"landing",
]

# Tier 5: Unconfirmed / speculative (lowest authority)
_UNCONFIRMED_PATTERNS = [
    r"unconfirmed", r"speculative", r"rumor", r"whatsapp",
    r"social", r"viral", r"fake", r"spam",
    r"outdated", r"old", r"archive",
]


# ── Source Type Authority ─────────────────────────────────────────────────────

def get_source_authority(source_name: str) -> float:
    """
    Assign an authority score (0.0 - 1.0) to a source based on filename patterns.

    Scoring:
        1.0 = Government/Regulatory
        0.8 = Verified professional
        0.6 = Professional forums
        0.4 = Marketing/sales
        0.2 = Unconfirmed/speculative
        0.5 = Unknown (default)
    """
    name_lower = source_name.lower()

    # Check patterns in order (highest authority first)
    for pattern in _GOVERNMENT_PATTERNS:
        if re.search(pattern, name_lower):
            return 1.0

    for pattern in _VERIFIED_PATTERNS:
        if re.search(pattern, name_lower):
            return 0.8

    for pattern in _FORUM_PATTERNS:
        if re.search(pattern, name_lower):
            return 0.6

    for pattern in _MARKETING_PATTERNS:
        if re.search(pattern, name_lower):
            return 0.4

    for pattern in _UNCONFIRMED_PATTERNS:
        if re.search(pattern, name_lower):
            return 0.2

    # Check source_type field (from ingestion)
    if source_name in ("true",):
        return 0.9
    if source_name in ("noisy",):
        return 0.3

    # Default: moderate authority
    return 0.5


def get_source_tier(source_name: str) -> str:
    """Return a human-readable tier label for a source."""
    authority = get_source_authority(source_name)
    if authority >= 0.9:
        return "government"
    elif authority >= 0.7:
        return "verified"
    elif authority >= 0.5:
        return "professional"
    elif authority >= 0.3:
        return "marketing"
    else:
        return "unconfirmed"


# ── Authority-Weighted Reranking ──────────────────────────────────────────────

def authority_rerank(
    results: list[dict],
    authority_weight: float = 0.3,
    relevance_weight: float = 0.7,
) -> list[dict]:
    """
    Rerank results using a combination of relevance score and source authority.

    Args:
        results: List of dicts with 'score', 'source' keys.
        authority_weight: How much to weight authority (0-1).
        relevance_weight: How much to weight relevance (0-1).

    Returns:
        Reranked list with added 'authority_score' and 'combined_score' fields.
    """
    if not results:
        return []

    for r in results:
        source = r.get("source", "unknown")
        authority = get_source_authority(source)
        r["authority_score"] = authority
        r["authority_tier"] = get_source_tier(source)
        r["combined_score"] = (
            relevance_weight * r.get("score", 0)
            + authority_weight * authority
        )

    # Sort by combined score
    reranked = sorted(results, key=lambda x: x["combined_score"], reverse=True)

    logfire.info(
        "Authority reranking applied",
        total=len(reranked),
        authority_weight=authority_weight,
        top_source=reranked[0].get("source", "?") if reranked else None,
        top_authority=reranked[0].get("authority_score", 0) if reranked else None,
    )

    return reranked


# ── Contradiction Detection ───────────────────────────────────────────────────

def detect_contradictions(results: list[dict]) -> list[dict]:
    """
    Detect when source chunks contain contradictory information.

    Simple approach: look for chunks that contain negation patterns
    for similar topics (e.g., "X is mandatory" vs "X is voluntary").
    """
    if len(results) < 2:
        return results

    contradictions = []

    # Check for key factual contradictions
    contradiction_pairs = [
        ("mandatory", "voluntary"),
        ("cannot", "can"),
        ("eligible", "ineligible"),
        ("required", "not required"),
        ("true", "false"),
        ("valid", "invalid"),
    ]

    for i, r1 in enumerate(results):
        text1 = r1.get("content", "").lower()
        for j, r2 in enumerate(results):
            if j <= i:
                continue
            text2 = r2.get("content", "").lower()

            for pos, neg in contradiction_pairs:
                if (pos in text1 and neg in text2) or (neg in text1 and pos in text2):
                    # Check if they're about similar topics
                    # Simple: check if they share key terms
                    words1 = set(text1.split())
                    words2 = set(text2.split())
                    overlap = words1 & words2
                    # If significant overlap, likely a contradiction
                    if len(overlap) > 5:
                        contradictions.append({
                            "source1": r1.get("source", "?"),
                            "source2": r2.get("source", "?"),
                            "term": f"{pos}/{neg}",
                            "overlap_terms": list(overlap)[:10],
                        })

    if contradictions:
        logfire.warning(
            "Contradictions detected between sources",
            count=len(contradictions),
            pairs=[(c["source1"], c["source2"]) for c in contradictions[:3]],
        )

        # Mark contradictory chunks with lower authority
        for c in contradictions:
            for r in results:
                if r.get("source") in (c["source1"], c["source2"]):
                    r["contradiction_flag"] = True

    return results
