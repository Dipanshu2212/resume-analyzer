import re
import os


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text


def extract_text_from_pdf(file) -> str:
    import pdfplumber

    pages_text = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

    if not pages_text:
        return ""

    return clean_text("\n".join(pages_text))


def extract_text_from_docx(file) -> str:
    from docx import Document

    doc = Document(file)
    paragraphs_text = []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs_text.append(text)

    if not paragraphs_text:
        return ""

    return clean_text("\n".join(paragraphs_text))


def parse_resume(file) -> str:
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


if __name__ == "__main__":
    import sys
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT     = os.path.abspath(os.path.join(BASE_DIR, ".."))
    sys.path.insert(0, ROOT)

    pdf_path = os.path.join(ROOT, "sample_resume.pdf")
    text     = extract_text_from_pdf(pdf_path)
    print(text[:500])
    print(f"\nTotal characters: {len(text)}")