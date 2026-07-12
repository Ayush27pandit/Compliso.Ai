import time

import logfire
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings


BATCH_SIZE = 50
_GEMINI_DIM = 3072
_FALLBACK_DIM = 768  # all-mpnet-base-v2

_active_model = None
_model_type: str | None = None  # "gemini" or "fallback"


# ── Model initialization ──────────────────────────────────────────────────────


def _probe_gemini():
    """
    Probe Gemini Embeddings API availability.

    Returns:
        Initialized Gemini embedding model if available,
        otherwise None.
    """

    with logfire.span("🧠 Probing Gemini Embeddings"):
        try:
            model = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-2-preview",
                google_api_key=settings.GEMINI_API_KEY,
            )

            embedding = model.embed_query("probe")

            logfire.info(
                "Gemini embeddings ready",
                model="gemini-embedding-2-preview",
                dimensions=len(embedding),
            )

            return model

        except Exception as error:
            logfire.warning(
                "Gemini probe failed; fallback will be used",
                error=str(error),
            )
            return None


def _load_fallback():
    """
    Load the local all-mpnet-base-v2 embedding model.
    """

    from sentence_transformers import SentenceTransformer

    with logfire.span("🛟 Loading Fallback Embedding Model"):
        model = SentenceTransformer("all-mpnet-base-v2")

        logfire.info(
            "Fallback embedding model loaded",
            model="all-mpnet-base-v2",
            dimensions=_FALLBACK_DIM,
        )

        return model


def _init() -> None:
    """
    Initialize the embedding model once per process.
    """

    global _active_model, _model_type

    if _active_model is not None:
        return

    gemini = _probe_gemini()

    if gemini is not None:
        _active_model = gemini
        _model_type = "gemini"
    else:
        _active_model = _load_fallback()
        _model_type = "fallback"


# ── Public helpers ────────────────────────────────────────────────────────────


def get_embedding_dim() -> int:
    """
    Return the dimensionality of the active embedding model.
    """

    _init()

    if _model_type == "gemini":
        return _GEMINI_DIM

    if _model_type == "fallback":
        return _FALLBACK_DIM

    raise RuntimeError("Embedding model is not initialized")


# ── Batch embedding ───────────────────────────────────────────────────────────


def _embed_batch(batch: list[str]) -> list[list[float]]:
    """
    Embed one batch of text using the active model.
    """

    if not batch:
        return []

    if _active_model is None or _model_type is None:
        raise RuntimeError("Embedding model is not initialized")

    if _model_type == "gemini":
        for attempt in range(4):
            try:
                return _active_model.embed_documents(batch)

            except Exception as error:
                error_message = str(error).lower()

                is_rate_limit = any(
                    keyword in error_message
                    for keyword in (
                        "rate limit",
                        "quota",
                        "429",
                        "resource_exhausted",
                    )
                )

                is_last_attempt = attempt == 3

                if not is_rate_limit or is_last_attempt:
                    logfire.exception(
                        "Gemini embedding failed",
                        attempt=attempt + 1,
                        batch_size=len(batch),
                    )
                    raise

                wait_seconds = 2 ** attempt

                logfire.warning(
                    "Gemini rate limit hit; retrying",
                    attempt=attempt + 1,
                    max_attempts=4,
                    wait_seconds=wait_seconds,
                )

                time.sleep(wait_seconds)

    return _active_model.encode(
        batch,
        show_progress_bar=False,
    ).tolist()


# ── Public API ────────────────────────────────────────────────────────────────


def embed_query(query: str) -> list[float]:
    """
    Embed a single query using the active model.
    """

    _init()

    if not query.strip():
        raise ValueError("Query cannot be empty")

    with logfire.span(
        "🔍 Embedding Query", 
        model=_model_type,
    ):
        if _model_type == "gemini":
            return _active_model.embed_query(query)

        return _active_model.encode(
            query,
            show_progress_bar=False,
        ).tolist()


def embed_texts(
    texts: list[str],
) -> list[list[float]]:
    """
    Embed multiple texts in batches while preserving input order.
    """

    _init()

    if not texts:
        return []

    all_embeddings: list[list[float]] = []

    total_batches = (
        len(texts) + BATCH_SIZE - 1
    ) // BATCH_SIZE

    with logfire.span(
        "🧠 Embedding Documents",
        model=_model_type,
        total_texts=len(texts),
        total_batches=total_batches,
    ):
        for batch_number, start in enumerate(
            range(0, len(texts), BATCH_SIZE),
            start=1,
        ):
            batch = texts[start:start + BATCH_SIZE]

            with logfire.span(
                "📦 Embedding Batch",
                model=_model_type,
                batch_number=batch_number,
                total_batches=total_batches,
                batch_size=len(batch),
            ):
                embeddings = _embed_batch(batch)
                all_embeddings.extend(embeddings)

    return all_embeddings