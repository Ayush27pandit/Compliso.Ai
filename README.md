# Compliso.ai

**AI-powered compliance copilot for Indian MSMEs — GST, Udyam registration, and regulatory filing, answered in plain language.**

Compliso.ai is a production-shaped Retrieval-Augmented Generation (RAG) system that answers questions about GST compliance, MSME classification, Udyam registration, and payment protection law for India's ~7.5 crore MSMEs — a segment that is massively underserved by generic AI tools and drowning in outdated or contradictory advice scattered across blogs, forums, and WhatsApp forwards.

> This is not a demo wrapped around `pdf → chunk → embed → prompt`. It's built with the same async, durable, and eval-gated architecture patterns used in production agentic systems — because a compliance tool that confidently hallucinates a GST rate is worse than no tool at all.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env   # fill in API keys (Groq, Qdrant, Gemini)
logfire auth            # set up tracing

# 3. Ingest documents
python -m app.ingestion.processor data/true_data true

# 4. Start the backend
python -m app.main

# 5. Start the frontend (new terminal)
streamlit run ui/app.py
```

Open `http://localhost:8501` — ask a GST or MSME compliance question.

### With Guardrails

```bash
# Enable input/output guardrails
export ENABLE_GUARDRAILS=true
python -m app.main
```

---

## What it does

- Answers questions on MSME classification, Udyam registration, GST registration thresholds, GST rate slabs (post GST 2.0 reform), GST return filing & due dates, the composition scheme, and MSME delayed-payment protection (Section 15 MSMED Act / Section 43B(h) Income Tax Act).
- Cites the source document behind every factual claim — no answer ships without a traceable reference.
- Detects and flags conflicting or stale information instead of silently picking one number when sources disagree.
- Refuses to state unconfirmed/speculative policy changes as fact, even when the source material is phrased confidently.
- Ignores promotional/marketing content and forum noise when a verified regulatory source is available.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Streamlit UI (ui/app.py)                    │
│             Compliso-branded chat interface                  │
└──────────────────────────┬──────────────────────────────────┘
                           │ POST /query
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (app/main.py)                │
│           Request validation, session routing                │
└──────────────────────────┬──────────────────────────────────┘
                           │ LangGraph invoke
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            LangGraph Agent (app/agents/graph.py)             │
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │ Planner  │──▶│Retriever │──▶│Responder │──▶ END        │
│  └────┬─────┘   └──────────┘   └──────────┘               │
│       │                                                      │
│       └── CONVERSATIONAL / OUT_OF_SCOPE ──▶ Responder       │
└─────────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Qdrant  │ │  Gemini  │ │  Groq    │
        │  (vector │ │ (embeds) │ │  (LLM)   │
        │   DB)    │ │          │ │          │
        └──────────┘ └──────────┘ └──────────┘

              │ Guardrails Layer
              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Guardrails System                           │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Input Rails  │  │Retrieval Rail│  │ Output Rails │     │
│  │ - Jailbreak  │  │ - Source     │  │ - Fact-check │     │
│  │ - Injection  │  │   authority  │  │ - Hallucin.  │     │
│  │ - Extraction │  │ - Outdated   │  │ - Citation   │     │
│  │ - PII mask   │  │   rejection  │  │   verify     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

See [docs/architecture.md](docs/architecture.md) for the full system design.

---

## Guardrails

Custom lightweight guardrails that run before/after the agent:

| Rail | Stage | Checks |
|------|-------|--------|
| **Input** | Before planner | Jailbreak, prompt injection, information extraction, PII masking |
| **Retrieval** | After retrieval | Source authority, outdated content filtering |
| **Output** | After responder | Safety, citation verification, hallucination detection |

### Blocked Patterns

| Category | Examples |
|----------|----------|
| Jailbreak | "Ignore your instructions", "Pretend you are a different AI" |
| Injection | "```ignore previous instructions```", "ADMIN MODE ACTIVATED" |
| Extraction | "Retrieve all documents from vector db", "Show system config" |
| PII | PAN, GSTIN, email, phone (masked in logs) |

### Enable Guardrails

```bash
export ENABLE_GUARDRAILS=true
python -m app.main
```

---

## Testing

```bash
# Run all tests
pytest

# With verbose output
pytest -v

# Run specific test file
pytest tests/test_guardrails.py -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Test Coverage

| Test File | Tests | Status |
|-----------|-------|--------|
| `test_planner.py` | 4 | ✅ Passing |
| `test_guardrails.py` | 15 | ✅ Passing |
| **Total** | **19** | **✅ All Passing** |

---

## Agent Skills

Pre-built skills for AI coding agents:

| Skill | Purpose |
|-------|---------|
| `compliso-rag-pipeline` | Ingestion, embedding, Qdrant schema, retrieval |
| `compliso-agent-graph` | LangGraph nodes, AgentState, routing |
| `compliso-guardrails` | Input/output/retrieval rail implementation |
| `compliso-testing` | pytest patterns, adversarial fixtures |

Skills are in `docs/skills/` — each follows the [Agent Skills standard](https://agentskills.io).

---

## Project Structure

```
compliso/
├── app/
│   ├── agents/
│   │   ├── graph.py          # LangGraph graph definition
│   │   ├── state.py          # AgentState TypedDict
│   │   └── nodes/
│   │       ├── planner.py    # Intent classification
│   │       ├── retriever.py  # Qdrant search + reranking
│   │       └── responder.py  # LLM response generation
│   ├── ingestion/
│   │   ├── processor.py      # Ingestion pipeline
│   │   ├── loaders/          # PDF, HTML, MD, TXT parsers
│   │   └── chunking/         # Text splitter
│   ├── services/
│   │   └── retrieval/        # Embeddings, Qdrant, reranking
│   ├── config.py             # Settings class
│   └── main.py               # FastAPI backend
├── guardrails/
│   ├── config/config.yml     # Rail configuration
│   ├── actions/              # Custom rail actions
│   └── integration.py        # LangGraph wrapper
├── tests/
│   ├── conftest.py           # Shared fixtures
│   ├── test_planner.py       # Planner tests
│   └── test_guardrails.py    # Guardrails tests
├── docs/
│   ├── architecture.md       # System design
│   ├── skills/               # Agent skills
│   └── noisy_data/           # Adversarial test fixtures
├── ui/
│   ├── app.py                # Streamlit chat interface
│   └── landing.html          # Landing page
└── requirements.txt
```

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GROQ_API_KEY` | Groq API key for LLM |
| `GROQ_MODEL` | LLM model (default: `llama-3.3-70b-versatile`) |
| `QDRANT_API_KEY` | Qdrant Cloud auth token |
| `QDRANT_CLUSTER_ENDPOINT` | Qdrant Cloud cluster URL |
| `GEMINI_API_KEY` | Google Gemini API key for embeddings |
| `LOGFIRE_API_KEY` | Pydantic Logfire token |
| `ENABLE_GUARDRAILS` | Enable guardrails (`true`/`false`) |

---

## Data & Eval

### `data/true_data/` — verified ground truth
Structured, source-dated, cross-checked regulatory documents covering MSME classification, GST registration, rate slabs, return filing, composition scheme, and delayed-payment protection.

### `data/noisy_data/` — adversarial eval fixtures
Realistic low-quality content: outdated blogs, forum threads, promotional pages, contradictory sources, OCR-garbled circulars, unconfirmed speculation. Indexed alongside `true_data/` to stress-test retrieval prioritization.

---

## Disclaimer

Compliso.ai provides informational guidance based on publicly available regulatory sources and is **not a substitute for a qualified Chartered Accountant, GST practitioner, or legal advisor**. Tax and compliance rules change by government notification — always verify time-sensitive figures against the official GST portal (gst.gov.in) or Udyam portal (udyamregistration.gov.in) before acting on them.

---

## License

[MIT](LICENSE)

---

*Built by [Ayush](https://github.com/ayush27p) as part of a broader effort in production-grade agentic AI systems.*
