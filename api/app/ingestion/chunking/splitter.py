import logfire


def chunk_text(
    text: str,
    chunk_size: int = 1500,
) -> list[str]:
    """
    Split text into chunks while preserving paragraph boundaries
    whenever possible.

    Paragraphs larger than chunk_size are split into smaller pieces.

    Args:
        text: The input text to chunk.
        chunk_size: Maximum number of characters per chunk.

    Returns:
        List of text chunks.
    """

    with logfire.span(
        "✂️ Text Chunking",
        text_length=len(text),
        chunk_size=chunk_size,
    ):
        if not text.strip():
            return []

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n\n")
            if paragraph.strip()
        ]

        chunks: list[str] = []
        current_parts: list[str] = []
        current_length = 0

        for paragraph in paragraphs:

            # Handle oversized paragraphs separately
            if len(paragraph) > chunk_size:

                # Flush the existing chunk first
                if current_parts:
                    chunks.append("\n\n".join(current_parts))
                    current_parts = []
                    current_length = 0

                # Split oversized paragraph into fixed-size pieces
                for start in range(0, len(paragraph), chunk_size):
                    piece = paragraph[start:start + chunk_size]

                    if piece:
                        chunks.append(piece)

                continue

            # Account for separator only when chunk already has content
            separator_length = 2 if current_parts else 0

            projected_length = (
                current_length
                + separator_length
                + len(paragraph)
            )

            if projected_length <= chunk_size:
                current_parts.append(paragraph)
                current_length = projected_length

            else:
                # Save current chunk
                chunks.append("\n\n".join(current_parts))

                # Start new chunk
                current_parts = [paragraph]
                current_length = len(paragraph)

        # Flush remaining content
        if current_parts:
            chunks.append("\n\n".join(current_parts))

        logfire.info(
            "Text chunking completed",
            chunks_generated=len(chunks),
            text_length=len(text),
            chunk_size=chunk_size,
        )

        return chunks