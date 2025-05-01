import logging
from typing import List, Dict, Any, Union, Optional
import re
import nltk
from nltk.tokenize import sent_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Splits documents into semantic chunks for embedding"""
    
    def __init__(self, 
                 chunk_size: int = 512, 
                 chunk_overlap: int = 50,
                 respect_semantics: bool = True):
        """
        Initialize document chunker
        
        Args:
            chunk_size: Target size of chunks in characters
            chunk_overlap: Overlap between chunks in characters
            respect_semantics: Whether to respect semantic boundaries (paragraphs, sentences)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.respect_semantics = respect_semantics
    
    def chunk_document(self, 
                      document: Dict[str, Any], 
                      metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Split document into semantic chunks
        
        Args:
            document: Document dict with text content
            metadata: Additional metadata to include with each chunk
        
        Returns:
            List of chunks with text and metadata
        """
        chunks = []
        
        # Handle different document formats
        if "pages" in document:
            # PDF with pages
            all_text = ""
            for page in document["pages"]:
                page_text = page.get("text", "")
                page_num = page.get("page_num", 0)
                
                # Pre-process: append page number info to help with context
                all_text += f"\n\n[Page {page_num}]\n{page_text}"
        else:
            # Single text document
            all_text = document.get("text", "")
        
        # Split into paragraphs first (respecting document structure)
        paragraphs = re.split(r'\n\s*\n', all_text)
        
        current_chunk = ""
        current_chunk_size = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # If paragraph alone exceeds chunk size, split into sentences
            if len(para) > self.chunk_size:
                sentences = sent_tokenize(para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    sentence_len = len(sentence)
                    
                    if current_chunk_size + sentence_len <= self.chunk_size:
                        # Add sentence to current chunk
                        if current_chunk:
                            current_chunk += " "
                        current_chunk += sentence
                        current_chunk_size += sentence_len
                    else:
                        # Current chunk is full, store it
                        if current_chunk:
                            chunk_metadata = self._prepare_chunk_metadata(document, metadata)
                            chunks.append({
                                "text": current_chunk,
                                "metadata": chunk_metadata,
                                "chunk_id": len(chunks)
                            })
                            
                            # Start new chunk with overlap
                            if self.respect_semantics:
                                # Find a good breaking point for overlap
                                overlap_text = self._get_overlap_text(current_chunk)
                                current_chunk = overlap_text + sentence
                                current_chunk_size = len(current_chunk)
                            else:
                                current_chunk = sentence
                                current_chunk_size = sentence_len
            else:
                # Regular paragraph handling
                para_len = len(para)
                
                if current_chunk_size + para_len <= self.chunk_size:
                    # Add paragraph to current chunk
                    if current_chunk:
                        current_chunk += "\n\n"
                    current_chunk += para
                    current_chunk_size += para_len + 2  # +2 for newlines
                else:
                    # Current chunk is full, store it
                    if current_chunk:
                        chunk_metadata = self._prepare_chunk_metadata(document, metadata)
                        chunks.append({
                            "text": current_chunk,
                            "metadata": chunk_metadata,
                            "chunk_id": len(chunks)
                        })
                        
                        # Start new chunk with this paragraph
                        current_chunk = para
                        current_chunk_size = para_len
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_metadata = self._prepare_chunk_metadata(document, metadata)
            chunks.append({
                "text": current_chunk,
                "metadata": chunk_metadata,
                "chunk_id": len(chunks)
            })
        
        return chunks
    
    def _get_overlap_text(self, text: str, max_overlap: int = None) -> str:
        """Get overlap text from the end of the current chunk"""
        if not max_overlap:
            max_overlap = self.chunk_overlap
            
        if len(text) <= max_overlap:
            return text
            
        # Try to find sentence boundaries for cleaner overlap
        overlap_text = text[-max_overlap:]
        sentences = sent_tokenize(overlap_text)
        
        if len(sentences) > 1:
            # Return only complete sentences
            return " ".join(sentences[1:])
        else:
            # If no sentence boundary found, use character overlap
            return overlap_text
    
    def _prepare_chunk_metadata(self, 
                              document: Dict[str, Any], 
                              additional_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare metadata for a chunk"""
        # Start with document-level metadata
        metadata = {}
        if "metadata" in document:
            metadata.update(document["metadata"])
            
        # Add additional metadata if provided
        if additional_metadata:
            metadata.update(additional_metadata)
            
        return metadata