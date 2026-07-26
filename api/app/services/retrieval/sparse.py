"""
BM25 sparse vector generation for hybrid retrieval.

Converts text into sparse vectors compatible with Qdrant's sparse vector format.
Uses TF-IDF weighting with BM25-style normalization.
"""

import math
import re
from collections import Counter

import logfire


# ── Tokenizer ─────────────────────────────────────────────────────────────────

_STOP_WORDS = frozenset(
    "a an the is are was were be been being have has had do does did "
    "will would shall should may might can could of in to for on with "
    "at by from as into through during before after above below between "
    "out off over under again further then once here there when where why "
    "how all each every both few more most other some such no nor not "
    "only own same so than too very that this these those it its i me my "
    "we our you your he his she her they them their what which who whom "
    "if or because although while about up".split()
)


def tokenize(text: str) -> list[str]:
    """
    Tokenize text into lowercase terms for BM25.
    Preserves numeric tokens (important for GST/circular numbers).
    """
    text = text.lower()
    # Keep alphanumeric tokens, split on punctuation/spaces
    tokens = re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text)
    return [t for t in tokens if len(t) > 1 and t not in _STOP_WORDS]


# ── IDF Computation ───────────────────────────────────────────────────────────

def compute_idf(documents: list[list[str]]) -> dict[str, float]:
    """
    Compute inverse document frequency for a corpus.
    IDF(t) = log((N - df(t) + 0.5) / (df(t) + 0.5) + 1)
    """
    n = len(documents)
    df: Counter[str] = Counter()

    for doc_tokens in documents:
        unique_terms = set(doc_tokens)
        for term in unique_terms:
            df[term] += 1

    idf = {}
    for term, freq in df.items():
        idf[term] = math.log((n - freq + 0.5) / (freq + 0.5) + 1)

    return idf


# ── Sparse Vector Builder ─────────────────────────────────────────────────────

class BM25Encoder:
    """
    Encodes text into sparse vectors using BM25 weighting.
    Maintains a vocabulary mapping for Qdrant sparse vector indices.
    """

    def __init__(self):
        self.vocab: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self._fitted = False

    def fit(self, documents: list[str]) -> "BM25Encoder":
        """
        Build vocabulary and compute IDF from a corpus.
        """
        with logfire.span("🔤 Building BM25 Vocabulary", n_docs=len(documents)):
            tokenized = [tokenize(doc) for doc in documents]
            self.idf = compute_idf(tokenized)

            # Build vocabulary: term -> index
            sorted_terms = sorted(self.idf.keys())
            self.vocab = {term: idx for idx, term in enumerate(sorted_terms)}
            self._fitted = True

            logfire.info(
                "BM25 vocabulary built",
                vocab_size=len(self.vocab),
                idf_computed=len(self.idf),
            )

        return self

    def encode(self, text: str) -> dict[int, float]:
        """
        Encode a single text into a sparse vector.
        Returns {dimension_index: tf_idf_weight}.
        """
        tokens = tokenize(text)
        if not tokens:
            return {}

        tf = Counter(tokens)
        max_tf = max(tf.values())

        sparse = {}
        for term, count in tf.items():
            if term not in self.vocab:
                continue
            # BM25-style TF normalization: tf * (k1 + 1) / (tf + k1)
            # Simplified: count / (count + k1) where k1=1.5
            tf_norm = count / (count + 1.5)
            idf_val = self.idf.get(term, 0.0)
            weight = tf_norm * idf_val
            if weight > 0:
                sparse[self.vocab[term]] = weight

        return sparse

    def encode_batch(self, texts: list[str]) -> list[dict[int, float]]:
        """
        Encode multiple texts into sparse vectors.
        """
        return [self.encode(text) for text in texts]

    def query(self, query_text: str, top_k: int = 20) -> list[tuple[int, float]]:
        """
        Encode a query and return top-k terms as (dimension_index, weight).
        """
        sparse = self.encode(query_text)
        # Sort by weight descending, return top_k
        sorted_items = sorted(sparse.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:top_k]


# ── Global Instance ───────────────────────────────────────────────────────────

_bm25_encoder: BM25Encoder | None = None


def get_bm25_encoder() -> BM25Encoder:
    """Get or create the global BM25 encoder."""
    global _bm25_encoder
    if _bm25_encoder is None:
        _bm25_encoder = BM25Encoder()
    return _bm25_encoder


def fit_bm25(documents: list[str]) -> BM25Encoder:
    """Fit the global BM25 encoder on a corpus."""
    encoder = get_bm25_encoder()
    encoder.fit(documents)
    return encoder


def encode_sparse(text: str) -> dict[int, float]:
    """Encode a single text using the global BM25 encoder."""
    return get_bm25_encoder().encode(text)


def query_sparse(query: str, top_k: int = 20) -> list[tuple[int, float]]:
    """Encode a query into sparse dimensions."""
    return get_bm25_encoder().query(query, top_k=top_k)
