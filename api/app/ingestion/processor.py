import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import logfire
from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import settings
from app.ingestion.chunking.splitter import chunk_text
from app.ingestion.loaders.html import parse_html
from app.ingestion.loaders.markdown import parse_markdown
from app.ingestion.loaders.pdf import parse_pdf
from app.ingestion.loaders.text import parse_text
from app.services.retrieval.embeddings import (
    embed_texts,
    get_embedding_dim,
)
from app.services.retrieval.sparse import BM25Encoder


# ── Configuration ─────────────────────────────────────────────────────────────

PROCESSED_DATA_DIR = Path("processed_data")

QDRANT_UPSERT_BATCH_SIZE = 100

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".html",
    ".htm",
    ".txt",
    ".docx",
    ".pptx",
    ".md",
}


# ── Clients ───────────────────────────────────────────────────────────────────

logfire.configure(
    service_name="enterprise-ingestion-service",
)

qdrant_client = QdrantClient(
    url=settings.QDRANT_CLUSTER_ENDPOINT,
    api_key=settings.QDRANT_API_KEY,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_source_type(name: str) -> str:
    """
    Determine source type from a directory name.

    Examples:
        true_data  -> true
        noisy_data -> noisy
        contracts  -> contracts
    """

    normalized = name.lower()

    if normalized == "true_data":
        return "true"

    if normalized == "noisy_data":
        return "noisy"

    return normalized


def generate_document_id(
    file_path: str,
) -> str:
    """
    Generate a stable ID from the complete file content.

    Same file content -> same document ID.
    Changed file content -> different document ID.
    """

    hasher = hashlib.sha256()

    with open(file_path, "rb") as file:
        while block := file.read(1024 * 1024):
            hasher.update(block)

    return hasher.hexdigest()


def generate_point_id(
    document_id: str,
    chunk_index: int,
    chunk: str,
) -> str:
    """
    Generate a deterministic UUID-compatible Qdrant point ID.

    Same document + same chunk position + same chunk content
    always produces the same ID.
    """

    identity = (
        f"{document_id}:{chunk_index}:{chunk}"
    )

    digest = hashlib.sha256(
        identity.encode("utf-8")
    ).hexdigest()

    # Convert part of SHA-256 into a UUID-compatible string.
    return (
        f"{digest[0:8]}-"
        f"{digest[8:12]}-"
        f"{digest[12:16]}-"
        f"{digest[16:20]}-"
        f"{digest[20:32]}"
    )


def save_processed_locally(
    data: dict[str, Any],
    source_type: str,
    filename: str,
) -> str:
    """
    Save parsed and chunked metadata locally as JSON.
    """

    folder = PROCESSED_DATA_DIR / source_type
    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    stem = Path(filename).stem

    destination = folder / f"{stem}.json"

    with destination.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return str(destination)


def parse_document(
    file_path: str,
) -> str:
    """
    Route a file to the correct parser based on extension.
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return parse_pdf(file_path)

    if extension in {".html", ".htm"}:
        return parse_html(file_path)

    if extension == ".txt":
        return parse_text(file_path)

    if extension == ".md":
        return parse_markdown(file_path)

    if extension in {".docx", ".pptx"}:
        from app.ingestion.loaders.office import parse_office

        return parse_office(file_path)

    raise ValueError(
        f"Unsupported file extension: {extension}"
    )


def upsert_points_in_batches(
    points: list[models.PointStruct],
) -> None:
    """
    Upsert Qdrant points in bounded batches.
    """

    total_points = len(points)

    for start in range(
        0,
        total_points,
        QDRANT_UPSERT_BATCH_SIZE,
    ):
        batch = points[
            start:start + QDRANT_UPSERT_BATCH_SIZE
        ]

        batch_number = (
            start // QDRANT_UPSERT_BATCH_SIZE
        ) + 1

        with logfire.span(
            "📤 Qdrant Batch Upsert",
            batch_number=batch_number,
            batch_size=len(batch),
        ):
            qdrant_client.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=batch,
                wait=True,
            )


# ── File Processing ───────────────────────────────────────────────────────────

def process_file(
    file_path: str,
    filename: str,
    source_type: str,
) -> dict[str, Any]:
    """
    Process one file through the complete ingestion pipeline.

    Flow:
        Parse
        -> Chunk
        -> Save processed metadata
        -> Embed
        -> Create Qdrant points
        -> Upsert
    """

    with logfire.span(
        f"📄 Processing {filename[:40]}",
        file=filename,
        source_type=source_type,
    ):
        try:
            extension = Path(filename).suffix.lower()

            if extension not in SUPPORTED_EXTENSIONS:
                logfire.warning(
                    "Skipping unsupported file",
                    filename=filename,
                    extension=extension,
                )

                return {
                    "status": "skipped",
                    "filename": filename,
                    "reason": "unsupported_extension",
                }

            # ── 1. Generate stable document identity ───────────────

            document_id = generate_document_id(file_path)

            logfire.info(
                "Document identity generated",
                filename=filename,
                document_id=document_id,
            )

            # ── 2. Parse ──────────────────────────────────────────

            with logfire.span(
                f"📖 Parsing {filename[:40]}",
                filename=filename,
            ):
                full_text = parse_document(file_path)

            if not full_text or not full_text.strip():
                logfire.warning(
                    "No text extracted; skipping document",
                    filename=filename,
                )

                return {
                    "status": "skipped",
                    "filename": filename,
                    "reason": "empty_text",
                }

            # ── 3. Chunk ──────────────────────────────────────────

            chunks = chunk_text(full_text)

            if not chunks:
                logfire.warning(
                    "No chunks generated; skipping document",
                    filename=filename,
                )

                return {
                    "status": "skipped",
                    "filename": filename,
                    "reason": "no_chunks",
                }

            logfire.info(
                "Document chunked",
                filename=filename,
                chunks_generated=len(chunks),
            )

            # ── 4. Save intermediate processed data ───────────────

            processed_data = {
                "document_id": document_id,
                "filename": filename,
                "source_type": source_type,
                "chunk_count": len(chunks),
                "chunks": chunks,
            }

            local_path = save_processed_locally(
                processed_data,
                source_type,
                filename,
            )

            logfire.info(
                "Processed data saved locally",
                filename=filename,
                path=local_path,
            )

            # ── 5. Generate embeddings ────────────────────────────

            with logfire.span(
                f"🧠 Embedding {filename[:40]}",
                filename=filename,
                chunks=len(chunks),
            ):
                embeddings = embed_texts(chunks)

            # Never trust silent zip truncation.
            if len(chunks) != len(embeddings):
                raise RuntimeError(
                    "Embedding count mismatch: "
                    f"{len(chunks)} chunks but "
                    f"{len(embeddings)} embeddings"
                )

            # ── 5b. Generate BM25 sparse vectors ──────────────

            bm25 = BM25Encoder()
            bm25.fit(chunks)
            sparse_vectors = bm25.encode_batch(chunks)

            logfire.info(
                "BM25 sparse vectors generated",
                filename=filename,
                vocab_size=len(bm25.vocab),
            )

            # ── 6. Create deterministic Qdrant points ─────────────

            points: list[models.PointStruct] = []

            for chunk_index, (
                chunk,
                vector,
                sparse_vec,
            ) in enumerate(
                zip(chunks, embeddings, sparse_vectors)
            ):
                point_id = generate_point_id(
                    document_id=document_id,
                    chunk_index=chunk_index,
                    chunk=chunk,
                )

                # Convert sparse dict {dim: weight} to Qdrant SparseVector format
                sparse_indices = list(sparse_vec.keys())
                sparse_values = list(sparse_vec.values())

                point = models.PointStruct(
                    id=point_id,
                    vector={
                        "dense": vector,
                        "bm25": models.SparseVector(
                            indices=sparse_indices,
                            values=sparse_values,
                        ),
                    },
                    payload={
                        "text": chunk,
                        "document_id": document_id,
                        "chunk_index": chunk_index,
                        "source": filename,
                        "source_type": source_type,
                    },
                )

                points.append(point)

            # ── 7. Upsert into Qdrant ─────────────────────────────

            with logfire.span(
                f"📦 Indexing {filename[:40]}",
                filename=filename,
                total_points=len(points),
            ):
                upsert_points_in_batches(points)

            logfire.info(
                "Document successfully indexed",
                filename=filename,
                points_indexed=len(points),
            )

            return {
                "status": "success",
                "filename": filename,
                "document_id": document_id,
                "chunks": len(chunks),
                "points_indexed": len(points),
            }

        except Exception:
            logfire.exception(
                "File processing failed",
                filename=filename,
                source_type=source_type,
            )

            return {
                "status": "failed",
                "filename": filename,
            }


# ── Directory Processing ──────────────────────────────────────────────────────

def process_directory(
    dir_path: str,
    source_type: str,
) -> dict[str, int]:
    """
    Process every regular file in one directory.
    """

    summary = {
        "success": 0,
        "failed": 0,
        "skipped": 0,
    }

    with logfire.span(
        "📂 Scanning Directory",
        path=dir_path,
        source_type=source_type,
    ):
        files = sorted(
            filename
            for filename in os.listdir(dir_path)
            if os.path.isfile(
                os.path.join(dir_path, filename)
            )
        )

        logfire.info(
            "Directory scan completed",
            directory=dir_path,
            files_found=len(files),
        )

        for filename in files:
            file_path = os.path.join(
                dir_path,
                filename,
            )

            result = process_file(
                file_path=file_path,
                filename=filename,
                source_type=source_type,
            )

            status = result["status"]

            if status in summary:
                summary[status] += 1

    return summary


# ── Collection Management ─────────────────────────────────────────────────────

def ensure_collection(
    wipe: bool = False,
) -> None:
    """
    Ensure the Qdrant collection exists with dense + sparse vector configs.

    If wipe=True, delete the existing collection first.
    """

    collection_name = settings.QDRANT_COLLECTION

    exists = qdrant_client.collection_exists(
        collection_name
    )

    if wipe and exists:
        with logfire.span(
            "🗑️ Wiping Qdrant Collection",
            collection=collection_name,
        ):
            qdrant_client.delete_collection(
                collection_name
            )

            logfire.warning(
                "Qdrant collection deleted",
                collection=collection_name,
            )

            exists = False

    if exists:
        return

    dimension = get_embedding_dim()

    with logfire.span(
        "🗄️ Creating Qdrant Collection (dense + sparse)",
        collection=collection_name,
        vector_dimension=dimension,
    ):
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": models.VectorParams(
                    size=dimension,
                    distance=models.Distance.COSINE,
                ),
            },
            sparse_vectors_config={
                "bm25": models.SparseVectorParams(
                    modifier=models.Modifier.IDF,
                ),
            },
        )

    logfire.info(
        "Qdrant collection created (dense + sparse)",
        collection=collection_name,
        vector_dimension=dimension,
        distance="cosine",
        sparse="bm25 with IDF",
    )


# ── Main Orchestrator ─────────────────────────────────────────────────────────

def run_universal_ingestion(
    base_dir: str,
    explicit_source_type: str | None = None,
    wipe: bool = False,
) -> dict[str, int]:
    """
    Discover directories and run the complete ingestion pipeline.
    """

    total_summary = {
        "success": 0,
        "failed": 0,
        "skipped": 0,
    }

    with logfire.span(
        "🚀 Universal Ingestion",
        base_directory=base_dir,
        wipe=wipe,
    ):
        ensure_collection(wipe=wipe)

        subdirectories = sorted(
            directory
            for directory in os.listdir(base_dir)
            if os.path.isdir(
                os.path.join(base_dir, directory)
            )
        )

        # No subdirectories:
        # process the base directory itself.

        if not subdirectories:
            source_type = (
                explicit_source_type
                or get_source_type(
                    os.path.basename(
                        os.path.normpath(base_dir)
                    )
                )
            )

            summary = process_directory(
                dir_path=base_dir,
                source_type=source_type,
            )

            for status, count in summary.items():
                total_summary[status] += count

        # Process every immediate subdirectory.

        else:
            for subdirectory in subdirectories:
                source_type = get_source_type(
                    subdirectory
                )

                directory_path = os.path.join(
                    base_dir,
                    subdirectory,
                )

                summary = process_directory(
                    dir_path=directory_path,
                    source_type=source_type,
                )

                for status, count in summary.items():
                    total_summary[status] += count

        logfire.info(
            "Ingestion completed",
            successful=total_summary["success"],
            failed=total_summary["failed"],
            skipped=total_summary["skipped"],
        )

    return total_summary


# ── CLI Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":

    wipe_requested = "--wipe" in sys.argv

    clean_args = [
        argument
        for argument in sys.argv
        if argument != "--wipe"
    ]

    target_dir = (
        clean_args[1]
        if len(clean_args) > 1
        else "DATA"
    )

    explicit_type = (
        clean_args[2]
        if len(clean_args) > 2
        else None
    )

    if not os.path.isdir(target_dir):
        print(
            f"Error: directory '{target_dir}' "
            "does not exist."
        )
        sys.exit(1)

    summary = run_universal_ingestion(
        base_dir=target_dir,
        explicit_source_type=explicit_type,
        wipe=wipe_requested,
    )

    print(
        "\nIngestion summary:"
        f"\n  Successful: {summary['success']}"
        f"\n  Failed:     {summary['failed']}"
        f"\n  Skipped:    {summary['skipped']}"
    )

    # Non-zero exit code if any documents failed.
    if summary["failed"] > 0:
        sys.exit(1)