import os
import PyPDF2
from docx import Document as DocxDocument
import markdown

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return '\n\n'.join(text)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = DocxDocument(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n\n'.join(text)
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading TXT file: {e}")
        return ""

def extract_text_from_file(file_path, file_type):
    """Extract text from various file types"""
    if file_type == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_type == 'docx':
        return extract_text_from_docx(file_path)
    elif file_type in ['txt', 'md']:
        return extract_text_from_txt(file_path)
    else:
        return ""

def markdown_to_html(text):
    """Convert markdown to HTML"""
    return markdown.markdown(text, extensions=['fenced_code', 'tables'])

def save_uploaded_file(file, upload_folder):
    """Save uploaded file and return file path"""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Generate unique filename
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_folder, filename)
    
    file.save(file_path)
    return file_path
