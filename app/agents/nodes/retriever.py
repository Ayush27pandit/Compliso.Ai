import logfire
from app.agents.state import AgentState
from app.services.retrieval import search_compliance_knowledge

def retrieve_node(state: AgentState):
    """
    Performs vector search for technical queries.
    Reranking arrives in a later stage — for now we use Qdrant's top results directly.
    """
    query = state["current_query"]

    with logfire.span("🔍 Knowledge Retrieval"):
        logfire.info(f"Searching Qdrant for: {query}")
        raw_results = search_compliance_knowledge(query, limit=5)
        logfire.info(f"Retrieved {len(raw_results)} candidates from Vector DB")

        formatted_docs = [f"CONTENT: {doc['content']}" for doc in raw_results]

    return {
        "documents": formatted_docs,
        "status": f"Found technical context.",
        "plan": state["plan"] + ["Context Retrieved"]
    }

    # Defensive guard for future : this node should only run for technical/search queries.
    # If routing ever misfires and this runs for CONVERSATIONAL/OUT_OF_SCOPE,
    # skip the search rather than hitting Qdrant with a meaningless query.