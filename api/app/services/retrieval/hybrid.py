"""
Hybrid search: dense + sparse with Reciprocal Rank Fusion (RRF).

Combines semantic (dense) search with keyword (sparse/BM25) search
using RRF to produce a unified ranking.
"""

import logfire
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from app.config import settings
from app.services.retrieval.embeddings import embed_query
from app.services.retrieval.sparse import query_sparse


# ── RRF Fusion ────────────────────────────────────────────────────────────────

def reciprocal_rank_fusion(
    rankings: list[list[str]],
    k: int = 60,
) -> list[str]:
    """
    Fuse multiple ranked lists using Reciprocal Rank Fusion.

    RRF_score(d) = sum(1 / (k + rank_i(d))) across all rankings.
    k=60 is the standard constant from the original RRF paper.

    Args:
        rankings: List of ranked lists (each list is document IDs in rank order).
        k: RRF constant (default 60).

    Returns:
        Fused list of document IDs ranked by RRF score.
    """
    scores: dict[str, float] = {}

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            if doc_id not in scores:
                scores[doc_id] = 0.0
            scores[doc_id] += 1.0 / (k + rank)

    # Sort by RRF score descending
    fused = sorted(scores.keys(), key=lambda d: scores[d], reverse=True)
    return fused


# ── Hybrid Search ─────────────────────────────────────────────────────────────

class HybridSearcher:
    """
    Performs hybrid search combining dense (semantic) and sparse (BM25) vectors.
    Uses Qdrant's native sparse+dense query support with RRF fusion.
    """

    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_CLUSTER_ENDPOINT,
            api_key=settings.QDRANT_API_KEY,
        )

    def search(
        self,
        query: str,
        limit: int = 10,
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4,
        use_hybrid: bool = True,
    ) -> list[dict]:
        """
        Hybrid search: dense + sparse with RRF.

        Args:
            query: Search query text.
            limit: Number of results to return.
            dense_weight: Weight for dense results in RRF (0-1).
            sparse_weight: Weight for sparse results in RRF (0-1).
            use_hybrid: If False, use dense-only search.

        Returns:
            List of {content, source, score, method} dicts.
        """
        with logfire.span("🔍 Hybrid Search", query=query[:80]):
            # ── Dense search ─────────────────────────────────
            dense_vector = embed_query(query)

            dense_response = self.client.query_points(
                collection_name=settings.QDRANT_COLLECTION,
                query=dense_vector,
                limit=limit,
                with_payload=True,
            )

            dense_results = []
            dense_ranking = []
            for pt in dense_response.points:
                doc_id = str(pt.id)
                dense_results.append({
                    "id": doc_id,
                    "content": pt.payload.get("text", ""),
                    "source": pt.payload.get("source", "Unknown"),
                    "dense_score": pt.score,
                })
                dense_ranking.append(doc_id)

            if not use_hybrid:
                return [
                    {
                        "content": r["content"],
                        "source": r["source"],
                        "score": r["dense_score"],
                        "method": "dense",
                    }
                    for r in dense_results
                ]

            # ── Sparse search ────────────────────────────────
            sparse_terms = query_sparse(query, top_k=20)

            if sparse_terms:
                sparse_vector = qdrant_models.SparseVector(
                    indices=[t[0] for t in sparse_terms],
                    values=[t[1] for t in sparse_terms],
                )

                sparse_response = self.client.query_points(
                    collection_name=settings.QDRANT_COLLECTION,
                    query=sparse_vector,
                    limit=limit,
                    with_payload=True,
                )

                sparse_results = {}
                sparse_ranking = []
                for pt in sparse_response.points:
                    doc_id = str(pt.id)
                    sparse_results[doc_id] = {
                        "id": doc_id,
                        "content": pt.payload.get("text", ""),
                        "source": pt.payload.get("source", "Unknown"),
                        "sparse_score": pt.score,
                    }
                    sparse_ranking.append(doc_id)
            else:
                sparse_results = {}
                sparse_ranking = []

            # ── RRF Fusion ──────────────────────────────────
            # Create weighted rankings
            dense_ranking_weighted = [dense_ranking] * int(dense_weight * 10)
            sparse_ranking_weighted = [sparse_ranking] * int(sparse_weight * 10) if sparse_ranking else []

            all_rankings = dense_ranking_weighted + sparse_ranking_weighted

            if all_rankings:
                fused_order = reciprocal_rank_fusion(all_rankings)
            else:
                fused_order = dense_ranking

            # ── Build result list ───────────────────────────
            # Merge dense and sparse results
            all_results = {}
            for r in dense_results:
                all_results[r["id"]] = r
            for r in sparse_results.values():
                if r["id"] in all_results:
                    all_results[r["id"]].update(r)
                else:
                    all_results[r["id"]] = r

            # Return in RRF order, capped at limit
            results = []
            for doc_id in fused_order[:limit]:
                if doc_id in all_results:
                    r = all_results[doc_id]
                    # Combined score: weighted average of dense + sparse
                    dense_s = r.get("dense_score", 0)
                    sparse_s = r.get("sparse_score", 0)
                    combined = dense_weight * dense_s + sparse_weight * sparse_s

                    results.append({
                        "content": r["content"],
                        "source": r["source"],
                        "score": combined,
                        "method": "hybrid",
                    })

            logfire.info(
                "Hybrid search complete",
                dense_results=len(dense_ranking),
                sparse_results=len(sparse_ranking),
                fused_results=len(results),
            )

            return results


# ── Query Analysis ────────────────────────────────────────────────────────────

def analyze_query(query: str) -> dict:
    """
    Analyze a query to determine optimal search strategy.

    Returns:
        {
            "type": "numeric" | "keyword" | "semantic" | "mixed",
            "use_hybrid": bool,
            "dense_weight": float,
            "sparse_weight": float,
        }
    """
    import re

    query_lower = query.lower()

    # Numeric query: circular numbers, section numbers, dates, amounts
    numeric_patterns = [
        r"\b\d+/\d{4}\b",           # circular numbers: 12/2024
        r"\bsection\s+\d+",          # section numbers
        r"\b₹\s*[\d,]+",            # amounts: ₹40 lakh
        r"\b\d+\s*(lakh|crore)\b",   # Indian amounts
        r"\b\d{1,2}\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",  # dates
    ]

    numeric_score = sum(
        1 for p in numeric_patterns
        if re.search(p, query_lower)
    )

    # Keyword-heavy: GSTIN, specific terms, acronyms
    keyword_terms = [
        "gstr-1", "gstr-3b", "gstr-9", "gstr-4",
        "udyam", "msme", "gst", "itc", "hsn",
        "composition", "threshold", "turnover",
        "due date", "filing", "return",
    ]
    keyword_score = sum(1 for t in keyword_terms if t in query_lower)

    # Very short queries (1-3 words) → boost keyword
    short_query = len(query.split()) <= 3

    # Determine strategy
    if numeric_score >= 2 or (numeric_score >= 1 and keyword_score >= 1):
        return {
            "type": "numeric",
            "use_hybrid": True,
            "dense_weight": 0.3,
            "sparse_weight": 0.7,
        }
    elif keyword_score >= 2 or short_query:
        return {
            "type": "keyword",
            "use_hybrid": True,
            "dense_weight": 0.4,
            "sparse_weight": 0.6,
        }
    elif keyword_score >= 1:
        return {
            "type": "mixed",
            "use_hybrid": True,
            "dense_weight": 0.6,
            "sparse_weight": 0.4,
        }
    else:
        return {
            "type": "semantic",
            "use_hybrid": True,
            "dense_weight": 0.7,
            "sparse_weight": 0.3,
        }


# ── Global Instance ───────────────────────────────────────────────────────────

_hybrid_searcher: HybridSearcher | None = None


def get_hybrid_searcher() -> HybridSearcher:
    """Get or create the global hybrid searcher."""
    global _hybrid_searcher
    if _hybrid_searcher is None:
        _hybrid_searcher = HybridSearcher()
    return _hybrid_searcher


def hybrid_search(
    query: str,
    limit: int = 10,
    use_query_analysis: bool = True,
) -> list[dict]:
    """
    Convenience function for hybrid search with automatic query routing.
    """
    searcher = get_hybrid_searcher()

    if use_query_analysis:
        analysis = analyze_query(query)
        return searcher.search(
            query=query,
            limit=limit,
            dense_weight=analysis["dense_weight"],
            sparse_weight=analysis["sparse_weight"],
            use_hybrid=analysis["use_hybrid"],
        )
    else:
        return searcher.search(query=query, limit=limit)
