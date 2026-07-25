# Compliso.ai — Project Plan

## Current State

**Working**: Full RAG pipeline (ingestion → embedding → retrieval → reranking → agent → API → UI), landing page, Logfire observability.

**Not working**: No tests, no guardrails, no eval pipeline, no auth, no deployment.

---

## Phase 1: Quality & Trust (Week 1-2)

**Goal**: Ship NeMo Guardrails + test suite + eval pipeline. Make the system trustworthy.

### 1.1 NeMo Guardrails Integration

**Why**: Compliance tool that hallucinates a GST rate is worse than no tool. Need programmatic safety beyond prompt-only guardrails.

**What to build**:
- `guardrails/config/config.yml` — model config, rail definitions
- `guardrails/config/rails/input.co` — jailbreak detection, injection blocking, PII masking
- `guardrails/config/rails/output.co` — fact-check, hallucination detection, citation verification
- `guardrails/actions/custom_actions.py` — source authority check, citation validation
- Modify `app/agents/graph.py` — wrap retriever/responder with `RunnableRails`
- Use `llama-3.1-8b-instant` for rails (fast, cheap) vs `llama-3.3-70b-versatile` for main

**Deliverables**:
- [ ] `pip install nemoguardrails` + config directory
- [ ] Input rails: jailbreak + injection + PII masking
- [ ] Output rails: self-check + citation verify + hallucination detect
- [ ] Custom actions: `verify_citation_exists`, `check_grounding`, `get_retrieved_sources`
- [ ] Integration test: query → rails → response (verify rails fire)
- [ ] Latency benchmark: measure overhead per rail

### 1.2 Test Suite

**Why**: Zero tests today. Every change risks silent regressions.

**What to build**:
- `tests/` directory with pytest
- Unit tests for chunking, embedding, retrieval, agent nodes
- Integration tests for full query pipeline
- Fix `html.py` bug: `from sympy import re` → `import re`

**Deliverables**:
- [ ] `tests/test_chunking.py` — paragraph splitting, edge cases
- [ ] `tests/test_embedding.py` — Gemini/fallback selection, batch processing
- [ ] `tests/test_retrieval.py` — Qdrant search, FlashRank reranking
- [ ] `tests/test_agent.py` — planner classification, responder paths
- [ ] `tests/test_api.py` — FastAPI endpoints, request/response validation
- [ ] `conftest.py` — shared fixtures (mock Qdrant, mock LLM)
- [ ] `pytest.ini` — test configuration
- [ ] Fix `html.py` sympy import bug

### 1.3 Eval Pipeline

**Why**: `noisy_data/` fixtures exist but no script runs them. Need to verify system handles adversarial inputs correctly.

**What to build**:
- `eval/` directory with evaluation scripts
- Regression test suite: true_data questions with expected answers
- Adversarial test suite: noisy_data questions with expected behavior
- Eval metrics: grounding score, citation accuracy, refusal rate

**Deliverables**:
- [ ] `eval/regression.py` — run true_data questions, check answer quality
- [ ] `eval/adversarial.py` — run noisy_data questions, check system behavior
- [ ] `eval/metrics.py` — grounding, citation, refusal calculations
- [ ] `eval/run_all.py` — orchestrator script
- [ ] `docs/noisy_data/README.md` — failure-mode-to-fixture mapping
- [ ] `.env.example` — document all required env vars

**Exit criteria**: 90%+ on regression tests, correct refusal on adversarial inputs, NeMo guardrails firing on unsafe queries.

---

## Phase 2: Retrieval Upgrade (Week 3-4)

**Goal**: Better answers through hybrid search + authority-aware reranking.

### 2.1 Hybrid Retrieval

**Why**: Dense search misses exact circular number lookups (e.g., "Circular 172/03/2024"). Need keyword search alongside vectors.

**What to build**:
- BM25 index in Qdrant (sparse vectors)
- Hybrid search: dense + sparse with RRF (Reciprocal Rank Fusion)
- Query routing: numeric queries → keyword boost, natural language → dense

**Deliverables**:
- [ ] Sparse vector collection in Qdrant
- [ ] Hybrid search function in `qdrant_service.py`
- [ ] Query router: detect circular numbers, section references
- [ ] RRF fusion algorithm
- [ ] A/B test: hybrid vs dense-only accuracy

### 2.2 Source-Authority Reranking

**Why**: `source_type` metadata is stored but unused. Forum posts get same weight as CBIC circulars.

**What to build**:
- Authority scoring: CBIC/state-gazette > official portals > verified content > forums > marketing
- Weighted reranking: multiply FlashRank score by authority weight
- Contradiction detection: flag when sources disagree on same fact

**Deliverables**:
- [ ] Authority scoring model
- [ ] Weighted reranking in `ranking_service.py`
- [ ] Contradiction detector: flag conflicting claims
- [ ] Metadata enrichment: add authority tier during ingestion

### 2.3 Query Expansion

**Why**: Indian CA jargon doesn't always match formal document language.

**What to build**:
- Hindi/regional term mapping
- Acronym expansion (GST → Goods and Services Tax)
- Synonym dictionary for compliance terms

**Deliverables**:
- [ ] `app/services/retrieval/query_expansion.py`
- [ ] Hindi/regional term dictionary
- [ ] Acronym expansion map
- [ ] Integration with planner node

**Exit criteria**: Hybrid search improves recall by 15%+, authority reranking reduces noise answers by 30%+, query expansion handles Hinglish queries.

---

## Phase 3: Production Hardening (Week 5-6)

**Goal**: Deployable, secure, observable.

### 3.1 Auth & Rate Limiting

**What to build**:
- API key management (generate, validate, rotate)
- Per-user rate limits (e.g., 100 queries/day free, 1000/day paid)
- Session tokens for multi-turn conversations

**Deliverables**:
- [ ] API key middleware in `app/main.py`
- [ ] Rate limiter (Redis-backed or in-memory)
- [ ] Session token generation/validation
- [ ] Usage tracking per API key

### 3.2 LLM Gateway

**Why**: Currently hardcoded to Groq. Need model routing, caching, prompt versioning.

**What to build**:
- Model router: Groq for speed, Gemini for complex queries
- Response cache: Redis-backed, TTL-based
- Prompt versioning: track which prompt produced which response

**Deliverables**:
- [ ] `app/services/llm/gateway.py`
- [ ] Model routing logic (query complexity → model selection)
- [ ] Response cache with TTL
- [ ] Prompt version tracking

### 3.3 Docker & Deployment

**What to build**:
- Dockerfile for backend + Qdrant
- docker-compose.yml for local development
- AWS Mumbai deployment (data residency)
- CI/CD pipeline (GitHub Actions)

**Deliverables**:
- [ ] `Dockerfile` — multi-stage build
- [ ] `docker-compose.yml` — backend + Qdrant + Redis
- [ ] `.github/workflows/ci.yml` — lint, test, build, deploy
- [ ] AWS ECS/EKS configuration
- [ ] Environment variable management (AWS SSM)

### 3.4 Streaming Responses

**Why**: Current simulated streaming (char-by-char) feels slow. Need real SSE.

**What to build**:
- SSE (Server-Sent Events) endpoint
- LangGraph streaming support
- Streamlit streaming display

**Deliverables**:
- [ ] `POST /query/stream` endpoint (SSE)
- [ ] LangGraph streaming integration
- [ ] Streamlit SSE display
- [ ] Progress indicators during retrieval

**Exit criteria**: Docker build passes, CI/CD runs tests, streaming works end-to-end, rate limiting enforced.

---

## Phase 4: Product Features (Week 7-10)

**Goal**: Build the features the landing page promises.

### 4.1 Notice Decoder

**Why**: Landing page markets this but it's not built. High-value feature for CAs.

**What to build**:
- PDF upload endpoint
- Notice parsing (DRC-01, GST-3B, income tax notices)
- Action plan generation
- Deadline extraction

**Deliverables**:
- [ ] `POST /decode-notice` endpoint
- [ ] `app/notice/parser.py` — notice structure extraction
- [ ] `app/notice/action_plan.py` — response generation
- [ ] Streamlit upload widget
- [ ] Notice template library

### 4.2 Deadline Radar

**What to build**:
- Calendar integration (Google Calendar, Outlook)
- Automated reminders per GSTIN/TAN
- Deadline tracking dashboard
- WhatsApp/email notifications

**Deliverables**:
- [ ] `app/deadlines/calendar.py` — calendar integration
- [ ] `app/deadlines/reminder.py` — notification scheduler
- [ ] Deadline dashboard in Streamlit
- [ ] Notification templates (WhatsApp, email)

### 4.3 Multi-State Compliance

**What to build**:
- State-specific rules engine
- E-invoicing thresholds by state
- Composition eligibility by state
- State-specific due dates

**Deliverables**:
- [ ] `app/compliance/state_rules.py`
- [ ] State规则 database (JSON/config)
- [ ] Multi-state query handling
- [ ] State comparison tool

### 4.4 ITC Reconciliation

**What to build**:
- 2A vs 2B comparison
- Mismatch flagging
- Vendor follow-up automation
- Recovery tracking

**Deliverables**:
- [ ] `app/reconciliation/itc.py`
- [ ] Mismatch detection algorithm
- [ ] Vendor notification system
- [ ] Recovery dashboard

### 4.5 File Upload in Chat

**What to build**:
- Streamlit file uploader
- On-the-fly document ingestion
- Temporary collection for uploaded docs
- Query against uploaded + existing knowledge

**Deliverables**:
- [ ] Streamlit file upload widget
- [ ] Temporary Qdrant collection
- [ ] Hybrid query (uploaded + permanent)
- [ ] Auto-cleanup after session

**Exit criteria**: Notice decoder works for DRC-01, deadline radar sends reminders, multi-state rules accurate, ITC reconciliation detects mismatches.

---

## Phase 5: Scale (Week 11-12)

**Goal**: Multi-tenant, analytics, enterprise features.

### 5.1 Multi-Tenant

**What to build**:
- Firm-level workspaces
- Role-based access (partner vs junior CA)
- Client isolation
- Shared knowledge base per firm

**Deliverables**:
- [ ] Workspace management
- [ ] RBAC middleware
- [ ] Client-scoped collections
- [ ] Firm admin dashboard

### 5.2 Usage Analytics

**What to build**:
- Query pattern tracking
- Popular topics dashboard
- Error rate monitoring
- User behavior analytics

**Deliverables**:
- [ ] Analytics pipeline (ClickHouse/Postgres)
- [ ] Dashboard in Streamlit
- [ ] Alert rules (error spikes, latency degradation)
- [ ] Weekly digest emails

### 5.3 Webhook Notifications

**What to build**:
- New circular alerts
- Client-specific notifications
- Integration with Slack/WhatsApp

**Deliverables**:
- [ ] Circular monitoring service
- [ ] Notification dispatcher
- [ ] Slack/WhatsApp integration
- [ ] User preference management

**Exit criteria**: Multi-tenant works, analytics dashboard live, webhooks delivering notifications.

---

## Priority Matrix

| Phase | Effort | Impact | Priority |
|-------|--------|--------|----------|
| Phase 1: Quality & Trust | Medium | **Critical** | **P0** |
| Phase 2: Retrieval Upgrade | Medium | High | P1 |
| Phase 3: Production Hardening | High | High | P1 |
| Phase 4: Product Features | High | Medium | P2 |
| Phase 5: Scale | High | Medium | P3 |

**Recommendation**: Start with Phase 1. Without guardrails and tests, everything else is built on sand.

---

## Tech Debt Backlog

- [ ] Fix `html.py` sympy import bug
- [ ] Rename `04_gst_return_types_due_dates copy.txt` → remove " copy"
- [ ] Create `.env.example` with all required vars
- [ ] Create `noisy_data/README.md` with fixture mapping
- [ ] Create `LICENSE` file
- [ ] Add `.streamlit/config.toml` for theme/server settings
- [ ] Add `pyproject.toml` for package management
- [ ] Update README with guardrails documentation

---

## Success Metrics

### Phase 1
- Test coverage > 80%
- Regression test pass rate > 90%
- Adversarial test refusal rate > 95%
- NeMo guardrails latency < 600ms overhead

### Phase 2
- Hybrid search recall improvement > 15%
- Authority reranking noise reduction > 30%
- Query expansion handles Hinglish queries

### Phase 3
- Docker build < 5 minutes
- CI/CD pipeline passes
- Streaming latency < 100ms first token

### Phase 4
- Notice decoder accuracy > 85%
- Deadline reminders delivered on time
- Multi-state rules coverage > 90%

### Phase 5
- Multi-tenant isolation verified
- Analytics dashboard live
- Webhook delivery rate > 99%
