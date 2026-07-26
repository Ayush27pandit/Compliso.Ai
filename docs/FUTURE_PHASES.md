# Compliso.ai — Future Phases

What remains to build, in priority order.

---

## Phase 1: Quality & Trust (In Progress)

**Goal**: Make the system provably trustworthy.

### Done
- [x] Custom guardrails (input/output/retrieval) — `api/app/guardrails/`
- [x] Test suite — 19 tests passing (`api/tests/`)
- [x] `html.py` sympy import bug fixed
- [x] Planner OUT_OF_SCOPE routing added

### Remaining
- [ ] **Eval pipeline** — run `noisy_data/` + `true_data/` fixtures programmatically
  - `api/tests/eval/regression.py` — true_data answer quality checks
  - `api/tests/eval/adversarial.py` — noisy_data refusal/flag checks
  - `api/tests/eval/metrics.py` — grounding, citation accuracy, refusal rate
- [ ] **More unit tests** — chunking, embedding fallback, retrieval, API endpoints
- [ ] **`.env.example`** — document all required env vars
- [ ] **Rename** `04_gst_return_types_due_dates copy.txt` → remove " copy"
- [ ] **`LICENSE` file** — MIT
- [ ] **`pyproject.toml`** — modern Python packaging

**Exit criteria**: 90%+ regression pass, correct refusal on adversarial inputs, >80% test coverage.

---

## Phase 2: Retrieval Upgrade

**Goal**: Better answers through hybrid search + authority-aware reranking.

### 2.1 Hybrid Retrieval
- [ ] BM25 sparse vectors in Qdrant
- [ ] Hybrid search: dense + sparse with RRF (Reciprocal Rank Fusion)
- [ ] Query routing: numeric queries (circular numbers) → keyword boost

### 2.2 Source-Authority Reranking
- [ ] Authority scoring: CBIC > official portals > verified > forums > marketing
- [ ] Weighted reranking: FlashRank score × authority weight
- [ ] Contradiction detection: flag when sources disagree

### 2.3 Query Expansion
- [ ] Hindi/regional term mapping (Hinglish support)
- [ ] Acronym expansion (GST → Goods and Services Tax)
- [ ] Synonym dictionary for compliance jargon

**Exit criteria**: +15% recall, -30% noise answers, Hinglish queries work.

---

## Phase 3: Production Hardening

**Goal**: Deployable, secure, observable.

### 3.1 Auth & Rate Limiting
- [ ] API key management (generate, validate, rotate)
- [ ] Per-user rate limits (Redis-backed)
- [ ] Session tokens for multi-turn conversations

### 3.2 LLM Gateway
- [ ] Model router: Groq (speed) vs Gemini (complex queries)
- [ ] Response cache: Redis-backed, TTL-based
- [ ] Prompt versioning: track which prompt produced which response

### 3.3 Docker & Deployment
- [ ] `Dockerfile` — multi-stage build
- [ ] `docker-compose.yml` — backend + Qdrant + Redis
- [ ] `.github/workflows/ci.yml` — lint, test, build, deploy
- [ ] AWS Mumbai deployment (data residency)
- [ ] Environment variable management (AWS SSM)

### 3.4 Streaming Improvements
- [x] SSE endpoint (`POST /query/stream`)
- [x] React SSE consumer (`useChat` hook)
- [ ] Progress indicators during retrieval
- [ ] LangGraph native streaming (node-by-node)

**Exit criteria**: Docker build passes, CI/CD runs tests, rate limiting enforced.

---

## Phase 4: Product Features

**Goal**: Build the features the landing page promises.

### 4.1 Notice Decoder
- [ ] PDF upload endpoint
- [ ] Notice parsing (DRC-01, GST-3B, income tax notices)
- [ ] Action plan generation
- [ ] Deadline extraction
- [ ] React upload widget

### 4.2 Deadline Radar
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Automated reminders per GSTIN/TAN
- [ ] Deadline tracking dashboard
- [ ] WhatsApp/email notifications

### 4.3 Multi-State Compliance
- [ ] State-specific rules engine
- [ ] E-invoicing thresholds by state
- [ ] Composition eligibility by state
- [ ] State comparison tool

### 4.4 ITC Reconciliation
- [ ] 2A vs 2B comparison
- [ ] Mismatch flagging
- [ ] Vendor follow-up automation
- [ ] Recovery tracking dashboard

### 4.5 File Upload in Chat
- [ ] React file upload component
- [ ] On-the-fly document ingestion
- [ ] Temporary Qdrant collection per session
- [ ] Auto-cleanup after session

**Exit criteria**: Notice decoder works for DRC-01, deadline radar sends reminders.

---

## Phase 5: Scale

**Goal**: Multi-tenant, analytics, enterprise.

### 5.1 Multi-Tenant
- [ ] Firm-level workspaces
- [ ] Role-based access (partner vs junior CA)
- [ ] Client isolation
- [ ] Shared knowledge base per firm

### 5.2 Usage Analytics
- [ ] Query pattern tracking
- [ ] Popular topics dashboard
- [ ] Error rate monitoring
- [ ] Weekly digest emails

### 5.3 Webhook Notifications
- [ ] New circular alerts
- [ ] Client-specific notifications
- [ ] Slack/WhatsApp integration

**Exit criteria**: Multi-tenant works, analytics dashboard live.

---

## Landing Page — Missing Sections

The React landing page currently includes: Nav, Hero, TrustBar, ProblemSolution, FAQ, Footer.

Still to port from `ui/landing.html`:
- [ ] **Features bento grid** — RAG answer, Live rule tracking, ITC recon, Deadline radar, Notice decoder
- [ ] **How It Works** — 4-step timeline (Connect, Sync, Ask, Act)
- [ ] **Pricing** — Solo / Practice / Firm tiers
- [ ] **Testimonials** — 4 customer quotes
- [ ] **Final CTA** — "Stop reading circulars" section

---

## Tech Debt

- [ ] Logfire API key refresh (`logfire auth`)
- [ ] `pnpm install` needed after node_modules cleanup
- [ ] Rename `04_gst_return_types_due_dates copy.txt`
- [ ] Create `.env.example`
- [ ] Create `LICENSE` file
- [ ] Add `pyproject.toml`
- [ ] Add `.oxlintrc.json` to root (currently only in `web/`)

---

## Priority Matrix

| Phase | Effort | Impact | Priority | Status |
|-------|--------|--------|----------|--------|
| Phase 1: Quality & Trust | Medium | **Critical** | **P0** | ~80% done |
| Phase 2: Retrieval Upgrade | Medium | High | P1 | Not started |
| Phase 3: Production Hardening | High | High | P1 | ~30% done (SSE) |
| Phase 4: Product Features | High | Medium | P2 | Not started |
| Phase 5: Scale | High | Medium | P3 | Not started |
