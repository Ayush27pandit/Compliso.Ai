import logfire
from app.agents.state import AgentState
from app.services.retrieval.qdrant_service import search_enterprise_knowledge
from app.config import settings
from app.services.retrieval.ranking_service import rerank_documents

def retrieve_node(state: AgentState):
    """
    Performs vector search and semantic reranking for technical queries.
    """
    query = state["current_query"]

    with logfire.span("🔍 Knowledge Retrieval"):
        logfire.info(f"Searching Qdrant for: {query}")
        raw_results = search_enterprise_knowledge(query, limit=15)
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
            reranked_docs = rerank_documents(query, tagged_contents, top_n=5)
            logfire.info("Reranking complete. Kept top 5 most relevant chunks.")

    return {
        "documents": reranked_docs,
        "status": f"Found technical context.",
        "plan": state["plan"] + ["Context Retrieved"]
    }