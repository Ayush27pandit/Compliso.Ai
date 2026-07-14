# Compliso.ai — System Architecture

## Overview

Compliso.ai is a production-shaped RAG system for Indian GST and MSME compliance. It consists of four layers: **Ingestion**, **Retrieval**, **Agent**, and **Interface**.

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI (ui/app.py)                 │
│              Compliso-branded chat interface                 │
└──────────────────────────┬──────────────────────────────────┘
                           │ POST /query
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (app/main.py)               │
│            Request validation, session routing               │
└──────────────────────────┬──────────────────────────────────┘
                           │ LangGraph invoke
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               LangGraph Agent (app/agents/graph.py)          │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ Planner  │───▶│Retriever │───▶│Responder │──▶ END       │
│  └────┬─────┘    └──────────┘    └──────────┘              │
│       │                                                       │
│       └── CONVERSATIONAL / OUT_OF_SCOPE ──▶ Responder        │
└─────────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Qdrant  │ │  Gemini  │ │  Groq    │
        │  (vector │ │ (embeds) │ │  (LLM)   │
        │   DB)    │ │          │ │          │
        └──────────┘ └──────────┘ └──────────┘
```

---

## 1. Ingestion Pipeline

Entry point: `python -m app.ingestion.processor <data_dir> [source_type] [--wipe]`

```
Scan directory
     │
     ▼
Extension check (.pdf .txt .md .html .docx .pptx)
     │ unsupported → SKIP
     ▼
SHA-256 content hash → Document ID
     │
     ▼
Parse document (extension-specific parser)
     │ empty text → SKIP
     ▼
Chunk text (paragraph-aware, ~1500 chars)
     │ no chunks → SKIP
     ▼
Save processed JSON locally (processed_data/)
     │
     ▼
Embed chunks (Gemini API, fallback: sentence-transformers)
     │
     ▼
Create Qdrant points (deterministic UUID = doc_id:index:chunk)
     │
     ▼
Batch upsert to Qdrant (batches ≤ 100)
```

### Supported Parsers

| Extension | Parser | Library |
|-----------|--------|---------|
| `.pdf` | `parse_pdf` | pypdf + pdfplumber fallback |
| `.txt` | `parse_text` | Python open() |
| `.md` | `parse_markdown` | Regex syntax stripping |
| `.html` | `parse_html` | BeautifulSoup |
| `.docx` | `parse_office` | unstructured |
| `.pptx` | `parse_office` | unstructured |

### Key Design Decisions

- **Content-hash document IDs**: Re-ingesting the same file produces the same ID. Changed content → new ID.
- **Deterministic point IDs**: `SHA-256(doc_id:chunk_index:chunk_text)` → UUID. Prevents duplicate vectors.
- **Paragraph-aware chunking**: Splits on `\n\n` boundaries, not fixed token count. Preserves document structure.
- **Dual PDF extraction**: pypdf first, pdfplumber fallback for blank/scanned pages.

---

## 2. Embedding Layer

**File**: `app/services/retrieval/embeddings.py`

```
Embed Request
     │
     ▼
Probe Gemini API (models/gemini-embedding-2-preview)
     │ available → use Gemini (3072 dim)
     │ unavailable → fallback
     ▼
Load sentence-transformers/all-mpnet-base-v2 (768 dim)
```

| Model | Dimensions | Source | When Used |
|-------|-----------|--------|-----------|
| `gemini-embedding-2-preview` | 3072 | Google API | Default (if API available) |
| `all-mpnet-base-v2` | 768 | Local | Fallback when Gemini fails |

**Batch processing**: 50 texts per batch, exponential backoff on rate limits (4 retries).

**Important**: If you switch between Gemini and fallback, you must re-create the Qdrant collection (different vector dimensions). Use `--wipe` flag.

---

## 3. Agent System (LangGraph)

### State

**File**: `app/agents/state.py`

```python
class AgentState(TypedDict):
    messages: Annotated[List[dict], operator.add]  # conversation history
    current_query: str                               # planner decision
    documents: List[str]                             # retrieved chunks
    plan: List[str]                                  # reasoning trace
    status: str                                      # current status
    final_answer: str                                # LLM response
```

### Graph Flow

**File**: `app/agents/graph.py`

```
                    ┌──────────────┐
                    │   Planner    │
                    │ (intent      │
                    │  classify)   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        CONVERSATIONAL  OUT_OF_SCOPE  TECHNICAL
              │            │            │
              ▼            ▼            ▼
         ┌─────────┐  ┌─────────┐  ┌──────────┐
         │Responder│  │Responder│  │Retriever │
         │(memory  │  │(refusal │  │(Qdrant   │
         │ only)   │  │ message)│  │ search + │
         └────┬────┘  └────┬────┘  │ rerank)  │
              │            │        └────┬─────┘
              │            │             │
              │            │             ▼
              │            │      ┌──────────┐
              │            │      │Responder │
              │            │      │(grounded │
              │            │      │ RAG)     │
              │            │      └────┬─────┘
              ▼            ▼           ▼
              └────────────┴───────────┘
                         │
                         ▼
                        END
```

### Nodes

| Node | File | Role |
|------|------|------|
| **Planner** | `app/agents/nodes/planner.py` | Classifies intent: CONVERSATIONAL / OUT_OF_SCOPE / TECHNICAL (search query) |
| **Retriever** | `app/agents/nodes/retriever.py` | Searches Qdrant (15 candidates), reranks to top 5 via FlashRank |
| **Responder** | `app/agents/nodes/responder.py` | Synthesizes answer via Groq LLM (llama-3.3-70b-versatile) |

### Planner Classification

| Intent | Condition | Action |
|--------|-----------|--------|
| `CONVERSATIONAL` | Greetings, general knowledge, follow-ups | Answer from memory/LLM knowledge |
| `TECHNICAL` | Compliance questions needing regulatory docs | Retrieve → rerank → grounded RAG answer |
| `OUT_OF_SCOPE` | Completely unrelated (poems, code, jokes) | Polite refusal with topic list |

### Memory

`MemorySaver` (LangGraph checkpointer) stores full `AgentState` snapshots per `thread_id`. The Streamlit UI generates a UUID per session and passes it as `thread_id`. This enables multi-turn conversations where the agent remembers prior context.

**Production note**: `MemorySaver` is in-memory and single-process. For production, swap to a `PostgresSaver` or `RedisSaver`.

---

## 4. Retrieval Pipeline

**Files**: `app/services/retrieval/qdrant_service.py`, `app/services/retrieval/ranking_service.py`

```
User Query
     │
     ▼
Embed query (same model as ingestion)
     │
     ▼
Qdrant query_points (cosine similarity, top 15)
     │
     ▼
FlashRank reranking (ms-marco-MiniLM-L-6-v2 cross-encoder)
     │
     ▼
Top 5 documents → Responder
```

### Qdrant Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Deterministic from `SHA-256(doc_id:index:chunk)` |
| `vector` | float[3072] or float[768] | Gemini or fallback embedding |
| `payload.text` | string | Chunk text content |
| `payload.document_id` | string | SHA-256 hash of source file |
| `payload.chunk_index` | int | Position within document |
| `payload.source` | string | Original filename |
| `payload.source_type` | string | `true` or `noisy` |

---

## 5. Interface Layer

### Backend (FastAPI)

**File**: `app/main.py`

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/health` | GET | — | `{"status": "ok"}` |
| `/query` | POST | `{"q": str, "thread_id": str}` | `{"answer", "thought_process", "sources", "intent"}` |

### Frontend (Streamlit)

**File**: `ui/app.py`

- Compliso-branded chat interface
- Quick prompts for common compliance questions
- Topic sidebar with domain coverage
- Source/reference expanders
- Compliance disclaimer
- Session management via UUID thread_id

---

## 6. Observability

**Stack**: Pydantic Logfire

Every layer is instrumented with `logfire.span()` and `logfire.info()`:
- Ingestion: file parsing, chunking, embedding, Qdrant upsert
- Agent: planner decisions, retrieval, reranking, LLM synthesis
- UI: user interactions, backend calls, errors

Dashboard: [logfire-us.pydantic.dev/ayush27p/compliso-rag](https://logfire-us.pydantic.dev/ayush27p/compliso-rag)

---

## 7. Environment Variables

| Variable | Purpose |
|----------|---------|
| `GROQ_API_KEY` | Groq API key for LLM |
| `GROQ_MODEL` | LLM model ID (e.g., `llama-3.3-70b-versatile`) |
| `GROQ_FALLBACK_API_KEY` | Backup Groq key |
| `QDRANT_API_KEY` | Qdrant Cloud auth token |
| `QDRANT_CLUSTER_ENDPOINT` | Qdrant Cloud cluster URL |
| `QDRANT_COLLECTION_NAME` | Collection name (default: `compliso`) |
| `GEMINI_API_KEY` | Google Gemini API key for embeddings |
| `LOGFIRE_API_KEY` | Pydantic Logfire token |
| `BACKEND_URL` | FastAPI server URL (default: `http://localhost:8000`) |

---

## 8. Running

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env  # fill in API keys
logfire auth          # configure tracing

# 3. Ingest documents
python -m app.ingestion.processor data/true_data true
python -m app.ingestion.processor data/ noisy_data noisy --wipe

# 4. Start backend
python -m app.main

# 5. Start frontend (new terminal)
streamlit run ui/app.py
```
