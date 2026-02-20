from io import BytesIO
from pypdf import PdfReader

def read_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Lee un PDF desde bytes y devuelve el texto completo como string.
    """
    pdf_text = ""
    pdf_stream = BytesIO(pdf_bytes)
    reader = PdfReader(pdf_stream)
    
    for page in reader.pages:
        pdf_text += page.extract_text() + "\n"
    
    return pdf_text
