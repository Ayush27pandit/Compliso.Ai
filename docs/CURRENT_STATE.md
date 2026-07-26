# Compliso.ai — Current State

Last updated: 2026-07-26

---

## What Works

### Backend (`api/`)

| Component | Status | Details |
|-----------|--------|---------|
| **FastAPI server** | ✅ Running | `uvicorn app.main:app --port 8000` |
| **POST /query** | ✅ Working | Synchronous query → answer with sources |
| **POST /query/stream** | ✅ Working | SSE streaming with real-time tokens |
| **GET /health** | ✅ Working | Health check endpoint |
| **CORS** | ✅ Configured | Allows localhost:3000, :5173, :8501 |
| **LangGraph agent** | ✅ Running | planner → retriever → responder |
| **Planner node** | ✅ 3 intents | TECHNICAL, CONVERSATIONAL, OUT_OF_SCOPE |
| **Retriever node** | ✅ Working | Qdrant search + FlashRank reranking |
| **Responder node** | ✅ Working | Groq llama-3.3-70b-versatile |
| **Gemini embeddings** | ✅ Working | Falls back to sentence-transformers |
| **Qdrant vector DB** | ✅ Connected | Cloud cluster |
| **Logfire observability** | ⚠️ API key expired | Needs `logfire auth` to refresh |

### Guardrails (`api/app/guardrails/`)

| Rail | Stage | Checks | Status |
|------|-------|--------|--------|
| **Input** | Before planner | Jailbreak, injection, extraction, PII masking | ✅ Built |
| **Retrieval** | After retrieval | Source authority, outdated rejection | ✅ Built |
| **Output** | After responder | Safety, citation verify, hallucination detect | ✅ Built |

Enable with `ENABLE_GUARDRAILS=true`. ~20ms overhead, pure regex (no NeMo — version conflict with LangGraph).

### Frontend (`web/`)

| Component | Status | Details |
|-----------|--------|---------|
| **Vite + React + TypeScript** | ✅ Built | pnpm, Tailwind CSS v4 |
| **Hash routing** | ✅ Working | `/` = landing, `#chat` = chat |
| **Landing page** | ✅ Built | Nav, Hero (video bg), TrustBar, ProblemSolution, FAQ, Footer |
| **Chat UI** | ✅ Built | ChatMessage, ChatInput, QuickPrompts, Sidebar |
| **SSE streaming** | ✅ Working | useChat hook + chatStore (Zustand) |
| **Thought process display** | ✅ Built | Collapsible reasoning in messages |
| **Source citations** | ✅ Built | Shown per message |
| **Build** | ✅ Passing | `pnpm build` succeeds |

### Tests (`api/tests/`)

| File | Tests | Status |
|------|-------|--------|
| `test_planner.py` | 4 | ✅ Passing |
| `test_guardrails.py` | 15 | ✅ Passing |
| **Total** | **19** | **✅ All Passing** |

### Documentation (`docs/`)

| File | Status |
|------|--------|
| `docs/architecture.md` | ✅ Updated with custom guardrails |
| `docs/plan.md` | ✅ 5-phase roadmap |
| `docs/skills/` | ✅ 4 agent skills created |

### Data (`api/data/`)

| Directory | Contents |
|-----------|----------|
| `true_data/` | 6 verified regulatory documents (MSME, GST, payments) |
| `noisy_data/` | 7 adversarial test fixtures (outdated, contradictory, spam) |

---

## Project Structure

```
RAG/
├── api/                  # Python backend
│   ├── app/
│   │   ├── agents/       # LangGraph (planner, retriever, responder)
│   │   ├── guardrails/   # Custom input/output/retrieval rails
│   │   ├── ingestion/    # Document processing pipeline
│   │   ├── services/     # Embeddings, Qdrant, reranking
│   │   ├── config.py     # Settings
│   │   └── main.py       # FastAPI + SSE
│   ├── data/             # Source documents
│   ├── tests/            # 19 pytest tests
│   └── requirements.txt
├── web/                  # React frontend
│   ├── src/
│   │   ├── components/   # chat/, landing/, layout/
│   │   ├── hooks/        # useChat (SSE)
│   │   ├── store/        # Zustand chatStore
│   │   └── pages/        # LandingPage
│   └── vite.config.ts
├── docs/                 # Architecture, plan, skills
├── .env                  # Secrets (gitignored)
└── venv/                 # Python venv (gitignored)
```

---

## How to Run

```bash
# Backend
cd /Users/Ayush/RAG
source venv/bin/activate
cd api
uvicorn app.main:app --port 8000 --reload

# Frontend (new terminal)
cd /Users/Ayush/RAG/web
pnpm install  # first time only
pnpm dev
```

- Landing: `http://localhost:3000`
- Chat: `http://localhost:3000/#chat`
- API docs: `http://localhost:8000/docs`

---

## Known Issues

1. **Logfire API key expired** — 401 errors on requests. Run `logfire auth` to refresh.
2. **`pnpm install` required** — `node_modules` was cleaned. Must reinstall before `pnpm dev`.
3. **No eval pipeline** — `noisy_data/` fixtures exist but no script runs them.
4. **No .env.example** — required env vars not documented in a template file.
5. **File naming** — `04_gst_return_types_due_dates copy.txt` has " copy" in name.
