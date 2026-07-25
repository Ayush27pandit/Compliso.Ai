---
name: compliso-agent-graph
description: "Compliso LangGraph agent architecture. Use when modifying planner, retriever, responder nodes, AgentState, graph routing, or conversation memory."
---

# Compliso Agent Graph

## Architecture

```
Planner → Retriever → Responder → END
   │
   └── CONVERSATIONAL / OUT_OF_SCOPE → Responder → END
```

## File Locations

| Component | File |
|-----------|------|
| Graph definition | `app/agents/graph.py` |
| Agent state | `app/agents/state.py` |
| Planner node | `app/agents/nodes/planner.py` |
| Retriever node | `app/agents/nodes/retriever.py` |
| Responder node | `app/agents/nodes/responder.py` |

## AgentState

```python
class AgentState(TypedDict):
    messages: Annotated[List[dict], operator.add]  # conversation history (append-only)
    current_query: str                              # planner decision or search query
    documents: List[str]                            # retrieved chunks
    plan: List[str]                                 # reasoning trace
    status: str                                     # current status message
    final_answer: str                               # LLM response
```

**Key**: `messages` uses `operator.add` — always appends, never replaces.

## Node Behavior

### Planner Node (`planner.py`)

**Input**: Full conversation history + latest user message
**Output**: One of:
- `"CONVERSATIONAL"` → greetings, general knowledge, follow-ups
- `"OUT_OF_SCOPE"` → completely unrelated (poems, code, jokes)
- `"<search query>"` → technical compliance question needing retrieval

**Prompt rules**:
- When in doubt, prefer `CONVERSATIONAL` (not `OUT_OF_SCOPE`)
- Even borderline finance/business questions → `CONVERSATIONAL`
- `OUT_OF_SCOPE` only for completely unrelated requests

**LLM**: `ChatGroq(model="llama-3.3-70b-versatile", temperature=0)`

### Retriever Node (`retriever.py`)

**Input**: `current_query` from planner
**Output**: Updates `documents` with top 5 chunks

**Flow**:
1. Embed query via `app.services.retrieval.embeddings`
2. Qdrant search (top 15, cosine similarity)
3. FlashRank rerank (top 5)
4. Store in `state["documents"]`

### Responder Node (`responder.py`)

**Input**: `current_query`, `documents`, `messages`
**Output**: Updates `final_answer` and appends to `messages`

**Behavior by intent**:
- `CONVERSATIONAL`: Answer from LLM knowledge (no retrieval)
- `OUT_OF_SCOPE`: Polite refusal with topic list
- `TECHNICAL`: Grounded RAG response using retrieved chunks

**LLM**: `ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)`

## Graph Construction

```python
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("planner", planner_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("responder", responder_node)

# Entry point
workflow.set_entry_point("planner")

# Edges
workflow.add_conditional_edges(
    "planner",
    route_decision,  # CONVERSATIONAL/OUT_OF_SCOPE → responder, else → retriever
    {
        "CONVERSATIONAL": "responder",
        "OUT_OF_SCOPE": "responder",
        "TECHNICAL": "retriever",
    }
)
workflow.add_edge("retriever", "responder")
workflow.add_edge("responder", END)

# Compile with MemorySaver checkpointer
app = workflow.compile(checkpointer=MemorySaver())
```

## Memory

- **Checkpointer**: `MemorySaver` (LangGraph built-in)
- **Thread ID**: UUID generated per Streamlit session
- **Storage**: In-memory snapshots of full `AgentState`
- ⚠️ `MemorySaver` is single-process — for production use `PostgresSaver` or `RedisSaver`

## Modifying the Planner

To add a new intent category:

1. Update planner prompt in `planner.py` with new category description
2. Update `route_decision()` in `graph.py`:
   ```python
   def route_decision(state: AgentState) -> str:
       decision = state["current_query"]
       if decision == "CONVERSATIONAL":
           return "CONVERSATIONAL"
       elif decision == "OUT_OF_SCOPE":
           return "OUT_OF_SCOPE"
       elif decision == "NEW_CATEGORY":
           return "NEW_CATEGORY"
       return "TECHNICAL"
   ```
3. Add edge in graph construction:
   ```python
   workflow.add_conditional_edges("planner", route_decision, {
       ...,
       "NEW_CATEGORY": "new_node",
   })
   ```

## Observability

All nodes use `logfire.span()` and `logfire.info()`:
```python
with logfire.span("🧠 Planner Decision"):
    decision = llm.invoke(prompt).content.strip()
    logfire.info(f"Intent identified: {decision}")
```

Dashboard: https://logfire-us.pydantic.dev/ayush27p/compliso-rag
