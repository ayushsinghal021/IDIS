import logging
from pathlib import Path
from typing import Union, List, Dict, Any, BinaryIO
import pdfplumber
import docx
import io
import os

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parses various document formats into text"""
    
    async def parse_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse a file and return text content with metadata"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            ext = file_path.suffix.lower()
            
            if ext == '.pdf':
                return await self.parse_pdf(file_path)
            elif ext in ['.docx', '.doc']:
                return await self.parse_docx(file_path)
            elif ext in ['.txt']:
                return await self.parse_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            logger.error(f"Parsing failed for {file_path}: {e}")
            raise
    
    async def parse_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract text and metadata from PDF files"""
        result = {
            "pages": [],
            "metadata": {},
            "is_scanned": False
        }
        
        with pdfplumber.open(file_path) as pdf:
            # Extract metadata
            result["metadata"] = pdf.metadata
            
            # Check if PDF is likely scanned (low text content)
            text_content = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_content += page_text
                result["pages"].append({
                    "page_num": page.page_number,
                    "text": page_text,
                    "width": page.width,
                    "height": page.height
                })
            
            # Heuristic: if average text per page is very low, likely scanned
            avg_chars_per_page = len(text_content) / len(pdf.pages) if pdf.pages else 0
            result["is_scanned"] = avg_chars_per_page < 50
            
        return result
    
    async def parse_docx(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from Word documents"""
        doc = docx.Document(file_path)
        
        # Extract full text
        full_text = "\n".join([para.text for para in doc.paragraphs])
        
        # Extract metadata from document properties
        metadata = {
            "title": doc.core_properties.title,
            "author": doc.core_properties.author,
            "created": doc.core_properties.created,
            "modified": doc.core_properties.modified,
        }
        
        return {
            "text": full_text,
            "metadata": metadata,
            "is_scanned": False
        }
    
    async def parse_text(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from plain text files"""
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        
        return {
            "text": text,
            "metadata": {
                "filename": file_path.name,
                "size": os.path.getsize(file_path)
            },
            "is_scanned": False
        }