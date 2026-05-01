import fitz
from docx import Document
import re
import os


def clean_text(text: str) -> str:
    """
    Clean raw extracted text.
    - Strip leading/trailing whitespace
    - Collapse multiple newlines into one
    - Collapse multiple spaces into one
    """
    text = text.strip()
    text = re.sub(r'\n+', '\n', text)      # multiple newlines → single newline
    text = re.sub(r'[ \t]+', ' ', text)    # multiple spaces/tabs → single space
    return text


def extract_text_from_pdf(file) -> str:
    """
    Extract text from PDF using pymupdf (Python 3.14 compatible)
    """
    # Read file bytes
    if hasattr(file, 'read'):
        file_bytes = file.read()
    else:
        with open(file, 'rb') as f:
            file_bytes = f.read()

    pages_text = []

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        text = page.get_text()
        if text.strip():
            pages_text.append(text)
    doc.close()

    if not pages_text:
        return ""

    return clean_text("\n".join(pages_text))

def extract_text_from_docx(file) -> str:
    """
    Extract text from a .docx file object using python-docx.

    Args:
        file: A file-like object (from Streamlit uploader or open())

    Returns:
        Cleaned extracted text as a single string.
        Returns empty string if no text could be extracted.
    """
    doc = Document(file)

    paragraphs_text = []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:                            # skip empty/spacing paragraphs
            paragraphs_text.append(text)

    if not paragraphs_text:
        return ""

    full_text = "\n".join(paragraphs_text)
    return clean_text(full_text)


def parse_resume(file) -> str:
    """
    Main wrapper function. Detects file type and calls the right extractor.

    Args:
        file: A file-like object with a .name attribute (Streamlit UploadedFile
              or a regular file opened with open())

    Returns:
        Cleaned extracted text as a string.

    Raises:
        ValueError: If the file type is not .pdf or .docx
    """
    filename = file.name.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file)

    elif filename.endswith(".docx"):
        return extract_text_from_docx(file)

    else:
        raise ValueError(
            f"Unsupported file type: '{file.name}'. "
            "Please upload a PDF or DOCX file."
        )


# ──────────────────────────────────────────────
# Quick local test — run: python parser.py
# Place a sample resume PDF and DOCX in the
# same folder before running this.
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import os

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # ── Test PDF ──────────────────────────────
    pdf_path = os.path.join(BASE_DIR, "sample_resume.pdf")
    try:
        text = extract_text_from_pdf(pdf_path)   # pass path string directly
        print("===== PDF OUTPUT =====")
        print(text[:500])
        print(f"\nTotal characters: {len(text)}")
    except FileNotFoundError:
        print("sample_resume.pdf not found")

    # ── Test DOCX ─────────────────────────────
    docx_path = os.path.join(BASE_DIR, "sample_resume.docx")
    try:
        text = extract_text_from_docx(docx_path)  # pass path string directly
        print("\n===== DOCX OUTPUT =====")
        print(text[:500])
        print(f"\nTotal characters: {len(text)}")
    except FileNotFoundError:
        print("sample_resume.docx not found")