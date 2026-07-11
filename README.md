# Compliso.ai

**AI-powered compliance copilot for Indian MSMEs — GST, Udyam registration, and regulatory filing, answered in plain language.**

Compliso.ai is a production-shaped Retrieval-Augmented Generation (RAG) system that answers questions about GST compliance, MSME classification, Udyam registration, and payment protection law for India's ~7.5 crore MSMEs — a segment that is massively underserved by generic AI tools and drowning in outdated or contradictory advice scattered across blogs, forums, and WhatsApp forwards.

> This is not a demo wrapped around `pdf → chunk → embed → prompt`. It's built with the same async, durable, and eval-gated architecture patterns used in production agentic systems — because a compliance tool that confidently hallucinates a GST rate is worse than no tool at all.

---

## Why this exists

Ask five different sources what the GST composition scheme turnover limit is, and you'll get three different numbers — one outdated, one correct, one a rumor from a WhatsApp forward. Multiply that across GST rate slabs, MSME classification thresholds, and payment-delay law, and the average small business owner in India has no reliable way to get a straight, current answer without paying a CA for a five-minute question.

Compliso.ai is built to solve exactly that: **grounded, source-cited, conflict-aware answers** to the compliance questions Indian MSMEs actually ask — not a general-purpose chatbot with a GST skin on top.

---

## What it does

- Answers questions on MSME classification, Udyam registration, GST registration thresholds, GST rate slabs (post GST 2.0 reform), GST return filing & due dates, the composition scheme, and MSME delayed-payment protection (Section 15 MSMED Act / Section 43B(h) Income Tax Act).
- Cites the source document behind every factual claim — no answer ships without a traceable reference.
- Detects and flags conflicting or stale information instead of silently picking one number when sources disagree.
- Refuses to state unconfirmed/speculative policy changes as fact, even when the source material is phrased confidently.
- Ignores promotional/marketing content and forum noise when a verified regulatory source is available.

---

## Architecture

Compliso.ai follows a production RAG pattern, not a linear notebook pipeline:

```
User Query
   │
   ▼
API Gateway (auth, rate limiting)
   │
   ▼
Orchestrator ── Guardrails (input) ── Retriever (hybrid: dense + keyword)
   │                                        │
   │                                        ▼
   │                              Vector Store (embeddings + metadata)
   │                                        │
   ▼                                        │
LLM Gateway (model routing, caching) ◄──────┘
   │
   ▼
Guardrails (output: fact-check, conflict flag, citation enforcement)
   │
   ▼
Response + Sources
```

Every layer below is deliberately named to match how it would be discussed in a system design review — not marketing language.

| Layer | Responsibility |
|---|---|
| **Ingestion** | Chunking by semantic heading (not fixed token count), metadata tagging (source authority, date verified, doc type) |
| **Embedding** | Domain-benchmarked embedding model (see [Embedding Model Selection](#embedding-model-selection)) |
| **Retrieval** | Hybrid dense + sparse retrieval with source-authority-aware re-ranking |
| **Guardrails** | Input validation, output fact-checking, conflict detection, speculation flagging, promotional-bias filtering |
| **LLM Gateway** | Model routing, prompt versioning, response caching |
| **Eval Pipeline** | Offline regression suite + adversarial fixtures (see [Data & Eval](#data--eval)) gating every deploy |

---

## Data & Eval

Compliso.ai's knowledge base is split into two intentionally separate sets:

### `true_data/` — verified ground truth
Structured, source-dated, cross-checked regulatory documents covering:
- MSME classification & Udyam registration
- GST registration thresholds
- GST rate slabs (post GST 2.0 reform, effective 22 Sept 2025)
- GST return types & due dates
- GST composition scheme
- MSME delayed-payment protection (Samadhaan, Section 43B(h))

Every file carries a "last verified" date and flags known points of confusion (e.g., old vs. new composition limits) so retrieval and generation can be tested against them explicitly.

### `noisy_data/` — adversarial eval fixtures
Realistic low-quality content mirroring what a real ingestion pipeline actually encounters: outdated blog posts, forum threads with mixed-accuracy answers, promotional consultancy pages, contradictory sources on the same fact, OCR-garbled scanned circulars, unconfirmed policy speculation, and off-topic distractors.

These aren't excluded from the index — they're indexed *alongside* `true_data/` specifically to stress-test whether retrieval and generation correctly prioritize authoritative sources over noise. See `noisy_data/README.md` for the full failure-mode-to-fixture mapping and paired eval questions.


---

## Disclaimer

Compliso.ai provides informational guidance based on publicly available regulatory sources and is **not a substitute for a qualified Chartered Accountant, GST practitioner, or legal advisor**. Tax and compliance rules change by government notification — always verify time-sensitive figures against the official GST portal (gst.gov.in) or Udyam portal (udyamregistration.gov.in) before acting on them.

---

## License

[MIT](LICENSE) — or update to match your intended license.

---

*Built by [Ayush](https://github.com/<your-handle>) as part of a broader effort in production-grade agentic AI systems.*
