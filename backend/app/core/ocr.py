import logging
from pathlib import Path
from typing import Union, List, Dict, Any, Literal
import pytesseract
from PIL import Image
import numpy as np
import os

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure Tesseract path if provided
if settings.tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_path

# Optional PaddleOCR import
try:
    from paddleocr import PaddleOCR
    paddle_ocr = None  # Initialize on demand
except ImportError:
    logger.warning("PaddleOCR not available. Using Tesseract as fallback.")


class OCRProcessor:
    """Handles OCR processing for scanned documents"""
    
    def __init__(self, engine: Literal["tesseract", "paddleocr"] = None):
        self.engine = engine or settings.ocr_engine
        if self.engine == "paddleocr" and 'paddle_ocr' in globals():
            global paddle_ocr
            if paddle_ocr is None:
                paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
        
    async def process_image(self, image_path: Union[str, Path]) -> str:
        """Process a single image and return extracted text"""
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            if self.engine == "tesseract":
                return self._process_with_tesseract(image_path)
            elif self.engine == "paddleocr":
                return self._process_with_paddleocr(image_path)
            else:
                raise ValueError(f"Unsupported OCR engine: {self.engine}")
        except Exception as e:
            logger.error(f"OCR processing failed for {image_path}: {e}")
            raise
    
    def _process_with_tesseract(self, image_path: Path) -> str:
        """Process with Tesseract OCR"""
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    
    def _process_with_paddleocr(self, image_path: Path) -> str:
        """Process with PaddleOCR"""
        if 'paddle_ocr' not in globals() or paddle_ocr is None:
            raise ImportError("PaddleOCR is not available")
            
        result = paddle_ocr.ocr(str(image_path), cls=True)
        # Extract text from PaddleOCR result format
        text_results = []
        for line in result:
            for item in line:
                text_results.append(item[1][0])  # Extract the text portion
        return "\n".join(text_results)
    
    async def process_pdf_images(self, pdf_path: Union[str, Path], output_dir: Union[str, Path]) -> List[Dict[str, Any]]:
        """Process images extracted from a PDF and return page-wise text"""
        # This would use a PDF to image converter like pdf2image, then process each page
        # Implementation depends on how you're extracting images from PDFs
        # For brevity, this is a placeholder
        return [{"page": 1, "text": "Example OCR text from PDF image"}]