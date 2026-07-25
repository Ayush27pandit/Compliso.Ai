import os
import logfire
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

load_dotenv()

logfire.configure(
    service_name="compliso-backend",
)

app = FastAPI(title="Compliso.ai Backend", version="0.1.0")


# ── Request / Response Models ────────────────────────────────────────────────


class QueryRequest(BaseModel):
    q: str
    thread_id: str


class QueryResponse(BaseModel):
    answer: str
    thought_process: list[str]
    sources: list[str]
    intent: str


# ── Lazy-load the compiled agent ─────────────────────────────────────────────

_agent = None
_guardrails_enabled = os.getenv("ENABLE_GUARDRAILS", "false").lower() == "true"


def get_agent():
    global _agent
    if _agent is None:
        from app.agents.graph import rag_agent
        if _guardrails_enabled:
            from guardrails.integration import wrap_graph_with_guardrails
            _agent = wrap_graph_with_guardrails(rag_agent)
            logfire.info("Guardrails enabled for agent")
        else:
            _agent = rag_agent
    return _agent


# ── Routes ───────────────────────────────────────────────────────────────────


@app.get("/health")
def health():
    return {"status": "ok", "service": "compliso-backend"}


@app.get("/", response_class=FileResponse)
def serve_landing():
    landing_page = Path(__file__).parent.parent / "ui" / "landing.html"
    return FileResponse(landing_page, media_type="text/html")


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    logfire.info(
        "Incoming query",
        query=req.q,
        thread_id=req.thread_id,
    )

    agent = get_agent()

    initial_state = {
        "messages": [{"role": "user", "content": req.q}],
        "current_query": "",
        "documents": [],
        "plan": [],
        "status": "",
        "final_answer": "",
    }

    config = {"configurable": {"thread_id": req.thread_id}}

    final_state = agent.invoke(initial_state, config=config)

    # Extract intent from plan
    intent = "TECHNICAL"
    plan_steps = final_state.get("plan", [])
    for step in plan_steps:
        if "Conversational" in step:
            intent = "CONVERSATIONAL"
        elif "Out of scope" in step:
            intent = "OUT_OF_SCOPE"

    # Extract source filenames from documents
    sources = []
    for doc in final_state.get("documents", []):
        # Documents are formatted as "CONTENT: <text>" — just pass through
        text = doc.replace("CONTENT: ", "")
        sources.append(text)

    thought_process = final_state.get("plan", [])
    answer = final_state.get("final_answer", "No response generated.")

    logfire.info(
        "Query resolved",
        intent=intent,
        sources_count=len(sources),
    )

    return QueryResponse(
        answer=answer,
        thought_process=thought_process,
        sources=sources,
        intent=intent,
    )


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
