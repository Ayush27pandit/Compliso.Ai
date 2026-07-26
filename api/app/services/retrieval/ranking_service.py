import time
import logfire
from flashrank import Ranker, RerankRequest
from app.services.retrieval.authority import authority_rerank, detect_contradictions

# Lazy initialization - Ranker is loaded on first use to ensure logfire.configure() has run
_ranker = None


def _get_ranker() -> Ranker:
    """
    Initializes the FlashRank engine lazily. 
    FlashRank uses a local ONNX model (ms-marco-MiniLM-L-6-v2) for ultra-fast reranking.
    """
    global _ranker
    if _ranker is None:
        logfire.info("🧠 Initializing FlashRank Model (TinyBERT) locally...")
        try:
            # We use a specific cache directory to avoid permission issues in production
            _ranker = Ranker(cache_dir="/tmp/flashrank")
        except Exception:
            _ranker = Ranker()
    return _ranker



def rerank_documents(query: str, documents: list[str], top_n: int = 5) -> list[str]:
    """
    Refines retrieval results using semantic reranking + authority scoring.
    
    Flow:
        1. FlashRank semantic reranking (relevance)
        2. Authority scoring (source trustworthiness)
        3. Contradiction detection
        4. Combined ranking
    """
    if not documents:
        return []

    start_time = time.time()
    logfire.info(f"📡 [Reranker] Sending {len(documents)} docs to FlashRank Cross-Encoder...")

    try:
        ranker = _get_ranker()
        
        # FlashRank expects a list of dictionaries with 'id' and 'text'
        passages = [
            {"id": i, "text": doc}
            for i, doc in enumerate(documents)
        ]

        request = RerankRequest(query=query, passages=passages)
        results = ranker.rerank(request)
        
        # Build result list with scores
        reranked = []
        for res in results[:top_n * 2]:  # Get more candidates for authority reranking
            idx = res['id']
            # Extract source from tagged content (format: "[Source: filename]\ncontent")
            content = res['text']
            source = "unknown"
            if content.startswith("[Source: "):
                end = content.index("]")
                source = content[9:end]
                content = content[end + 2:]

            reranked.append({
                "content": content,
                "source": source,
                "score": res['score'],
                "tagged_content": res['text'],  # Keep original for LLM
            })

        duration = time.time() - start_time
        top_score = results[0]['score'] if results else 'N/A'
        logfire.info(f"✅ [Reranker] Semantic reranking done in {duration:.2f}s. Top score: {top_score}")

        # Apply authority scoring
        reranked = authority_rerank(
            reranked,
            authority_weight=0.25,
            relevance_weight=0.75,
        )

        # Detect contradictions
        reranked = detect_contradictions(reranked)

        # Return top_n results (already sorted by combined_score)
        final = reranked[:top_n]

        logfire.info(
            "✅ [Reranker] Final ranking applied",
            total=len(final),
            sources=[r.get("source", "?") for r in final[:3]],
            scores=[f"{r.get('combined_score', 0):.3f}" for r in final[:3]],
        )

        # Return tagged content for LLM context
        return [r.get("tagged_content", r["content"]) for r in final]

    except Exception as e:
        logfire.error(f"❌ [Reranker] Reranking Failed: {e}")
        # Fallback to the original order
        return documents[:top_n]