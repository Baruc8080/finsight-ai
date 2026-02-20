from pypdf import PdfReader
from io import BytesIO

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extrae texto de un PDF recibido en bytes.
    """
    pdf_file_like = BytesIO(file_bytes)  # <--- envolver los bytes en BytesIO
    reader = PdfReader(pdf_file_like)

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

