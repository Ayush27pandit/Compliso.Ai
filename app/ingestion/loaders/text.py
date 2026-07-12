import logfire

def parse_text(file_path: str) -> str:
    """
    Read and return the contents of a plain text file.

    Args:
        file_path: Path to the text file.

    Returns:
        Contents of the text file.
    """

    with logfire.span("📄 Text Parsing", filename=file_path):
        try:
            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore",
            ) as file:
                text = file.read()

            logfire.info(
                "✅ Text file parsed successfully",
                filename=file_path,
                characters=len(text),
            )

            return text

        except Exception:
            logfire.exception(
                "💥 Text Parse Failed: ",
                filename=file_path,
            )
            raise