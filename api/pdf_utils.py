import PyPDF2


async def get_pdf_page_count(file_path: str) -> int:
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages)
