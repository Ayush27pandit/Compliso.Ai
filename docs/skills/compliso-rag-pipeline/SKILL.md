---
name: compliso-rag-pipeline
description: "Compliso RAG ingestion, embedding, and retrieval pipeline. Use when modifying ingestion flow, chunking, Qdrant schema, retrieval logic, or adding new parsers."
---

# Compliso RAG Pipeline

## Architecture

```
Scan → Parse → Chunk → Embed → Qdrant Upsert
                ↓
        Query → Embed → Qdrant Search (top 15) → FlashRank Rerank (top 5)
```

## File Locations

| Component | File |
|-----------|------|
| Ingestion entry | `app/ingestion/processor.py` |
| PDF parser | `app/ingestion/loaders/pdf.py` |
| Markdown parser | `app/ingestion/loaders/markdown.py` |
| HTML parser | `app/ingestion/loaders/html.py` |
| Text parser | `app/ingestion/loaders/text.py` |
| Office parser | `app/ingestion/loaders/office.py` |
| Chunking | `app/ingestion/chunking/splitter.py` |
| Embeddings | `app/services/retrieval/embeddings.py` |
| Qdrant service | `app/services/retrieval/qdrant_service.py` |
| Reranking | `app/services/retrieval/ranking_service.py` |

## Key Rules

### Document IDs
- Content-hash based (SHA-256 of file content)
- Re-ingesting same file = same ID; changed content = new ID
- Implementation: `processor.py` → `_compute_doc_id(content: bytes) -> str`

### Chunking
- Paragraph-aware splitting on `\n\n` boundaries
- Target chunk size: ~1500 characters
- Overlap: 200 characters
- Metadata: `doc_id`, `chunk_index`, `source`, `source_type` (`true` or `noisy`)

### Embedding Model
- **Primary**: `gemini-embedding-2-preview` (3072 dimensions)
- **Fallback**: `sentence-transformers/all-mpnet-base-v2` (768 dimensions)
- Defined in: `app/services/retrieval/embeddings.py`
- Batch size: 50 texts, exponential backoff (4 retries)
- ⚠️ Switching models requires Qdrant collection wipe (`--wipe` flag)

### Qdrant Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Deterministic: `SHA-256(doc_id:index:chunk_text)` |
| `vector` | float[3072] or float[768] | Embedding vector |
| `payload.text` | string | Chunk text |
| `payload.document_id` | string | Source document hash |
| `payload.chunk_index` | int | Position in document |
| `payload.source` | string | Original filename |
| `payload.source_type` | string | `true` or `noisy` |

### Retrieval Flow
1. Embed user query (same model as ingestion)
2. Qdrant `query_points` — cosine similarity, top 15
3. FlashRank reranking (`ms-marco-MiniLM-L-6-v2` cross-encoder) → top 5
4. Pass chunks to Responder node

## Adding a New Parser

1. Create `app/ingestion/loaders/<format>.py`
2. Implement `parse_<format>(file_path: str) -> str`
3. Register in `processor.py` extension map:
   ```python
   PARSERS = {
       ".pdf": parse_pdf,
       ".<ext>": parse_<format>,  # add here
   }
   ```
4. Update `requirements.txt` if new dependency needed
5. Test with: `python -m app.ingestion.processor data/test_data true`

## Changing Chunk Size

Edit `app/ingestion/chunking/splitter.py`:
- `CHUNK_SIZE = 1500` (target characters)
- `CHUNK_OVERLAP = 200` (overlap between chunks)
- After changing: `--wipe` and re-ingest

## Common Commands

```bash
# Ingest true data
python -m app.ingestion.processor data/true_data true

# Ingest noisy data (wipes previous)
python -m app.ingestion.processor data/noisy_data noisy --wipe

# Check Qdrant collection stats
python -c "from app.services.retrieval.qdrant_service import get_collection_info; print(get_collection_info())"
```
