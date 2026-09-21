from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument


def load_pdf(file_path: str) -> list[dict]:
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        text = text.strip()

        if text:
            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

    return pages


def load_docx(file_path: str) -> list[dict]:
    document = DocxDocument(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    if not paragraphs:
        return []

    return [
        {
            "page_number": 1,
            "text": "\n".join(paragraphs),
        }
    ]


def load_document(file_path: str) -> list[dict]:
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        return load_pdf(file_path)

    if path.suffix.lower() == ".docx":
        return load_docx(file_path)

    raise ValueError(
        f"Unsupported file type: {path.suffix}"
    )