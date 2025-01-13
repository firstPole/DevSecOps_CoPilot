from docx import Document

def extract_text_from_docx(docx_file):
    """Extracts text from a Word document."""
    try:
        document = Document(docx_file)
        return "\n".join([paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()])
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""
