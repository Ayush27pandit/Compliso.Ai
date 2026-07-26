import logfire
from app.agents.state import AgentState
from app.services.retrieval.qdrant_service import search_enterprise_knowledge
from app.config import settings
from app.services.retrieval.ranking_service import rerank_documents
from app.services.retrieval.hybrid import analyze_query
from app.services.retrieval.query_expansion import expand_for_retrieval

def retrieve_node(state: AgentState):
    """
    Performs hybrid search (dense + sparse with RRF) and semantic reranking for technical queries.
    Includes query expansion for Hinglish, acronyms, and synonyms.
    """
    query = state["current_query"]

    # Expand query for better retrieval
    expansion = expand_for_retrieval(query)
    search_query = expansion["expanded"]

    # Analyze query to determine search strategy
    analysis = analyze_query(search_query)

    with logfire.span("🔍 Knowledge Retrieval"):
        logfire.info(
            f"Searching Qdrant",
            original_query=query[:80],
            expanded=query != search_query,
            query_type=analysis["type"],
        )
        raw_results = search_enterprise_knowledge(search_query, limit=15)
        logfire.info(f"Retrieved {len(raw_results)} candidates from Vector DB")

        # Pair content with source metadata for reranking
        doc_contents = [doc['content'] for doc in raw_results]
        doc_sources = [doc.get('source', 'unknown') for doc in raw_results]

        with logfire.span("⚖️ Semantic Reranking"):
            # Prepend source to content so LLM sees provenance after reranking
            tagged_contents = [
                f"[Source: {src}]\n{content}"
                for content, src in zip(doc_contents, doc_sources)
            ]
            reranked_docs = rerank_documents(search_query, tagged_contents, top_n=5)
            logfire.info("Reranking complete. Kept top 5 most relevant chunks.")

    plan_step = f"Context Retrieved ({analysis['type']}"
    if expansion["was_expanded"]:
        plan_step += ", expanded"
    plan_step += ")"

    return {
        "documents": reranked_docs,
        "status": f"Found technical context (query type: {analysis['type']}).",
        "plan": state["plan"] + [plan_step]
    }