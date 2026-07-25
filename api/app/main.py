import os
import json
import logfire
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

load_dotenv()

logfire.configure(
    service_name="compliso-backend",
)

app = FastAPI(title="Compliso.ai Backend", version="0.2.0")

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Vite dev server
        "http://localhost:5173",   # Vite alt port
        "http://localhost:8501",   # Streamlit (legacy)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
            from app.guardrails.integration import wrap_graph_with_guardrails
            _agent = wrap_graph_with_guardrails(rag_agent)
            logfire.info("Guardrails enabled for agent")
        else:
            _agent = rag_agent
    return _agent


# ── Routes ───────────────────────────────────────────────────────────────────


@app.get("/health")
def health():
    return {"status": "ok", "service": "compliso-backend"}


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


# ── Streaming Endpoint ───────────────────────────────────────────────────────


@app.post("/query/stream")
async def query_stream(req: QueryRequest):
    """Stream response via Server-Sent Events."""

    def event_generator():
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

        # Stream status
        yield f"data: {json.dumps({'type': 'status', 'content': 'Analyzing query...'})}\n\n"

        try:
            final_state = agent.invoke(initial_state, config=config)
        except Exception as e:
            logfire.error(f"Agent error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        # Stream thought process
        for step in final_state.get("plan", []):
            yield f"data: {json.dumps({'type': 'thought', 'content': step})}\n\n"

        # Stream answer in chunks for real-time feel
        answer = final_state.get("final_answer", "")
        chunk_size = 4
        for i in range(0, len(answer), chunk_size):
            chunk = answer[i : i + chunk_size]
            yield f"data: {json.dumps({'type': 'answer_chunk', 'content': chunk})}\n\n"

        # Stream sources
        sources = [
            doc.replace("CONTENT: ", "")
            for doc in final_state.get("documents", [])
        ]
        yield f"data: {json.dumps({'type': 'sources', 'content': sources})}\n\n"

        # Stream intent
        intent = "TECHNICAL"
        for step in final_state.get("plan", []):
            if "Conversational" in step:
                intent = "CONVERSATIONAL"
            elif "Out of scope" in step:
                intent = "OUT_OF_SCOPE"
        yield f"data: {json.dumps({'type': 'intent', 'content': intent})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
