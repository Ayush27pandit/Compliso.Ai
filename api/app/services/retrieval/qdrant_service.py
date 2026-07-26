import logfire
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.config import settings
from app.services.retrieval.embeddings import embed_query
from app.services.retrieval.hybrid import hybrid_search, analyze_query


# Initialize Qdrant Client
client = QdrantClient(
    url=settings.QDRANT_CLUSTER_ENDPOINT,
    api_key=settings.QDRANT_API_KEY
)


def search_enterprise_knowledge(query: str, limit: int = 8):
    """
    Performs hybrid search (dense + sparse with RRF) in the enterprise knowledge base.
    Falls back to dense-only if sparse vectors are not available.
    """
    try:
        # Analyze query to determine search strategy
        analysis = analyze_query(query)
        logfire.info(
            "Query analyzed",
            query_type=analysis["type"],
            dense_weight=analysis["dense_weight"],
            sparse_weight=analysis["sparse_weight"],
        )

        # Try hybrid search first
        results = hybrid_search(
            query=query,
            limit=limit,
            use_query_analysis=True,
        )

        # If hybrid returned results, use them
        if results:
            return results

        # Fallback to dense-only
        logfire.warning("Hybrid search returned empty, falling back to dense-only")
        return _dense_search(query, limit)

    except Exception as e:
        logfire.warning(f"Hybrid search failed ({e}), falling back to dense-only")
        return _dense_search(query, limit)


def _dense_search(query: str, limit: int = 8):
    """Fallback dense-only search for backward compatibility."""
    try:
        query_vector = embed_query(query)

        response = client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )

        results = []
        for res in response.points:
            results.append({
                "content": res.payload.get("text", ""),
                "source": res.payload.get("source", "Unknown"),
                "score": res.score,
            })

        return results
    except Exception as e:
        logfire.error(f"❌ Qdrant Search Failed: {e}")
        return []
