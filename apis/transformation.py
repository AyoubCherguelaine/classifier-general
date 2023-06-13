import pytesseract
from PIL import Image
import textract
from pathlib import Path

def extract_text(filename: str, file_path: str) -> str:
    file_extension = Path(filename).suffix.lower()
    
    if file_extension in ['.pdf', '.docx', '.xlsx', '.doc', '.rtf', '.odt']:
        try:
            # Use textract library to extract text from PDF, DOCX, or XLSX files
            text = textract.process(file_path, method='tesseract', encoding='utf-8', pages='all')
            text = text.decode('utf-8')
            return text
        except Exception as e:
            # Handle any exceptions that may occur during text extraction
            print(f"Exception: {e}")
    
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
        try:
            # Convert other file types (images) to text using Tesseract OCR
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            # Handle any exceptions that may occur during text extraction
            print(f"Exception: {e}")
    
    return None
