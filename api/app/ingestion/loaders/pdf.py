import logfire
import pdfplumber
from pypdf import PdfReader


def parse_pdf(file_path: str) -> str:
    """
    Extract text from a PDF using pypdf.

    Falls back to pdfplumber for pages where pypdf
    fails to extract meaningful text.

    Note:
        This does not perform OCR on image-only pages.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text with original page order preserved.
    """

    with logfire.span("parse_pdf 📄", filename=file_path):
        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)

            logfire.info(
                "📄 PDF opened",
                filename=file_path,
                total_pages=total_pages,
            )

            # One slot per page preserves document order
            page_texts: list[str] = [""] * total_pages
            fallback_pages: list[int] = []

            # Primary extraction with pypdf
            for page_index, page in enumerate(reader.pages):
                text = page.extract_text() or ""

                if text.strip():
                    page_texts[page_index] = text.strip()
                else:
                    fallback_pages.append(page_index)

            # Fallback extraction with pdfplumber
            if fallback_pages:
                logfire.info(
                    "🔁 Retrying blank pages with pdfplumber",
                    pages=[index + 1 for index in fallback_pages],
                )

                try:
                    with pdfplumber.open(file_path) as pdf:
                        for page_index in fallback_pages:
                            fallback_text = (
                                pdf.pages[page_index].extract_text() or ""
                            )

                            if fallback_text.strip():
                                page_texts[page_index] = fallback_text.strip()

                except Exception:
                    logfire.exception(
                        "❌ pdfplumber fallback failed",
                        filename=file_path,
                    )

            # Identify pages still blank after fallback
            unresolved_pages = [
                index + 1
                for index, text in enumerate(page_texts)
                if not text.strip()
            ]

            if unresolved_pages:
                logfire.warning(
                    "⚠️ Some pages contain no extractable text",
                    filename=file_path,
                    pages=unresolved_pages,
                )

            # Preserve page boundaries
            full_text = "\n\n".join(
                text for text in page_texts if text.strip()
            )

            if not full_text:
                logfire.warning(
                    "⚠️ No text extracted from PDF",
                    filename=file_path,
                )
            else:
                logfire.info(
                    "✅ PDF extraction completed",
                    filename=file_path,
                    characters=len(full_text),
                    total_pages=total_pages,
                    unresolved_pages=len(unresolved_pages),
                )

            return full_text
        except Exception as e:
            logfire.error(f"💥 PDF Parse Failed for {file_path}: {e}")
            raise
        

