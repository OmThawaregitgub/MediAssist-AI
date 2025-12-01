import os
import logging
from typing import List, Dict, Any
import PyPDF2
import docx
import pandas as pd
from PIL import Image
import pytesseract
import io

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process various document types (PDF, DOCX, CSV, images)"""
    
    def __init__(self):
        # Check if Tesseract is available for OCR
        try:
            pytesseract.get_tesseract_version()
            self.ocr_available = True
        except:
            self.ocr_available = False
            logger.warning("Tesseract OCR not available. Image text extraction will be limited.")
    
    def process_file(self, file_path: str, file_type: str = None) -> List[Dict[str, Any]]:
        """
        Process a file and extract text content
        
        Args:
            file_path: Path to the file
            file_type: File type (pdf, docx, txt, csv, jpg, png)
            
        Returns:
            List of documents with text and metadata
        """
        if not file_type:
            file_type = os.path.splitext(file_path)[1].lower().lstrip('.')
        
        processors = {
            'pdf': self._process_pdf,
            'docx': self._process_docx,
            'txt': self._process_text,
            'csv': self._process_csv,
            'jpg': self._process_image,
            'jpeg': self._process_image,
            'png': self._process_image,
        }
        
        if file_type not in processors:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        try:
            documents = processors[file_type](file_path)
            logger.info(f"✅ Processed {file_path}: {len(documents)} documents extracted")
            return documents
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            raise e
    
    def _process_pdf(self, file_path: str) -> List[Dict]:
        """Extract text from PDF file"""
        documents = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    documents.append({
                        'text': text,
                        'metadata': {
                            'source': file_path,
                            'page': page_num,
                            'total_pages': len(pdf_reader.pages),
                            'file_type': 'pdf'
                        }
                    })
        
        return documents
    
    def _process_docx(self, file_path: str) -> List[Dict]:
        """Extract text from DOCX file"""
        documents = []
        
        doc = docx.Document(file_path)
        full_text = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        
        if full_text:
            documents.append({
                'text': '\n'.join(full_text),
                'metadata': {
                    'source': file_path,
                    'file_type': 'docx',
                    'paragraphs': len(full_text)
                }
            })
        
        return documents
    
    def _process_text(self, file_path: str) -> List[Dict]:
        """Read text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        return [{
            'text': text,
            'metadata': {
                'source': file_path,
                'file_type': 'txt'
            }
        }]
    
    def _process_csv(self, file_path: str) -> List[Dict]:
        """Extract text from CSV file"""
        documents = []
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except:
                    continue
            
            # Convert dataframe to text
            text = df.to_string(index=False)
            
            documents.append({
                'text': text,
                'metadata': {
                    'source': file_path,
                    'file_type': 'csv',
                    'rows': len(df),
                    'columns': list(df.columns)
                }
            })
            
        except Exception as e:
            # Fallback: read as plain text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
            
            documents.append({
                'text': text,
                'metadata': {
                    'source': file_path,
                    'file_type': 'csv',
                    'error': 'Parsed as plain text'
                }
            })
        
        return documents
    
    def _process_image(self, file_path: str) -> List[Dict]:
        """Extract text from image using OCR"""
        documents = []
        
        if not self.ocr_available:
            return [{
                'text': f"Image file: {os.path.basename(file_path)} (OCR not available)",
                'metadata': {
                    'source': file_path,
                    'file_type': 'image',
                    'warning': 'OCR not available'
                }
            }]
        
        try:
            # Open and process image
            image = Image.open(file_path)
            
            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            if text.strip():
                documents.append({
                    'text': text,
                    'metadata': {
                        'source': file_path,
                        'file_type': 'image',
                        'dimensions': image.size,
                        'mode': image.mode
                    }
                })
            else:
                documents.append({
                    'text': f"No text detected in image: {os.path.basename(file_path)}",
                    'metadata': {
                        'source': file_path,
                        'file_type': 'image',
                        'warning': 'No text detected'
                    }
                })
        
        except Exception as e:
            documents.append({
                'text': f"Error processing image: {str(e)}",
                'metadata': {
                    'source': file_path,
                    'file_type': 'image',
                    'error': str(e)
                }
            })
        
        return documents
    
    def process_multiple_files(self, file_paths: List[str]) -> List[Dict]:
        """Process multiple files"""
        all_documents = []
        
        for file_path in file_paths:
            try:
                documents = self.process_file(file_path)
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                continue
        
        return all_documents