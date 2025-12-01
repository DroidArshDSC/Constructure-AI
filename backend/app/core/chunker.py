import pdfplumber
from uuid import uuid4
from typing import List, Dict


# ---------------------------------------------------------
# Split text into safe sub-chunks (1500 chars ≈ 250–300 tokens)
# ---------------------------------------------------------
def split_text(text: str, max_len: int = 1500) -> List[str]:
    """
    Splits large OCR-heavy page text into safe chunks.
    Ensures embedding token limits are never exceeded.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + max_len
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end

    return chunks


# ---------------------------------------------------------
# Extract PDF text + generate sub-chunks
# ---------------------------------------------------------
def extract_text_and_chunks(upload_file) -> (str, List[Dict]):
    """
    Returns:
      full_text: raw concatenated text from entire PDF
      chunks: list of chunk dicts with (id, text, page, file_name, part)
    """
    chunks = []
    full_text = ""

    with pdfplumber.open(upload_file.file) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):

            # Extract text from page
            text = page.extract_text() or ""
            full_text += text + "\n\n"

            # Split text into safe-length chunks
            sub_chunks = split_text(text, max_len=1500)

            # Convert sub-chunks into chunk objects
            for i, sub_text in enumerate(sub_chunks):
                chunk = {
                    "id": str(uuid4()),
                    "text": sub_text,
                    "page": page_num,
                    "file_name": upload_file.filename,
                    "part": i  # helpful for debugging long pages
                }
                chunks.append(chunk)

    # Reset file pointer for re-use
    upload_file.file.seek(0)

    return full_text, chunks
