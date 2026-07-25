import re

import logfire


def parse_markdown(file_path: str) -> str:
    """
    Read a markdown file and strip markdown syntax,
    returning plain text suitable for chunking.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Plain text content of the markdown file.
    """

    with logfire.span("📄 Markdown Parsing", filename=file_path):
        try:
            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore",
            ) as file:
                text = file.read()

            # Remove HTML tags
            text = re.sub(r"<[^>]+>", "", text)

            # Remove heading markers (e.g., ## Heading -> Heading)
            text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

            # Remove bold/italic markers
            text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
            text = re.sub(r"_{1,3}(.+?)_{1,3}", r"\1", text)

            # Remove inline code backticks
            text = re.sub(r"`(.+?)`", r"\1", text)

            # Remove links, keep text only: [text](url) -> text
            text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)

            # Remove images: ![alt](url) -> alt
            text = re.sub(r"!\[(.+?)\]\(.+?\)", r"\1", text)

            # Remove horizontal rules
            text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)

            # Collapse multiple blank lines
            text = re.sub(r"\n{3,}", "\n\n", text)

            text = text.strip()

            logfire.info(
                "✅ Markdown file parsed successfully",
                filename=file_path,
                characters=len(text),
            )

            return text

        except Exception:
            logfire.exception(
                "💥 Markdown Parse Failed: ",
                filename=file_path,
            )
            raise
