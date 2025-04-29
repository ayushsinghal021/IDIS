import logging
from typing import Dict, Any, List, Optional, Union
import os
import json
import asyncio
from pathlib import Path
import uuid

from app.config import get_settings
from app.models.document import DocumentResponse, ProcessingStatus
from app.core.ocr import OCRProcessor
from app.core.parser import DocumentParser
from app.core.chunking import DocumentChunker
from app.core.embedding import EmbeddingGenerator
from app.core.vector_store import VectorStore
from app.core.entity_extraction import EntityExtractor

logger = logging.getLogger(__name__)
settings = get_settings()


class DocumentService:
    """Service for document processing workflows"""
    
    def __init__(self):
        """Initialize document service with required processors"""
        self.ocr = OCRProcessor()
        self.parser = DocumentParser()
        self.chunker = DocumentChunker()
        self.embedding_generator = EmbeddingGenerator()
        self.entity_extractor = EntityExtractor()
        
        # Ensure directories exist
        Path(settings.upload_folder).mkdir(parents=True, exist_ok=True)
        Path(settings.processed_folder).mkdir(parents=True, exist_ok=True)
        Path(settings.vector_folder).mkdir(parents=True, exist_ok=True)
    
    async def process_document(self, 
                              file_path: str, 
                              document_id: str,
                              original_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a document through the full pipeline
        
        Args:
            file_path: Path to the document file
            document_id: Unique document identifier
            original_filename: Original filename (for metadata)
            
        Returns:
            Processing result summary
        """
        try:
            # Update status to processing
            await self._update_document_status(
                document_id, 
                ProcessingStatus.PROCESSING,
                message="Document processing started"
            )
            
            # Step 1: Parse or OCR the document
            file_path = Path(file_path)
            ext = file_path.suffix.lower()
            
            if ext in ['.png', '.jpg', '.jpeg']:
                # Process image with OCR
                text = await self.ocr.process_image(file_path)
                parsed_doc = {
                    "text": text,
                    "metadata": {
                        "source": original_filename or file_path.name,
                        "document_id": document_id,
                        "type": "image"
                    }
                }
            else:
                # Parse document
                parsed_doc = await self.parser.parse_file(file_path)
                
                # Add metadata
                if "metadata" not in parsed_doc:
                    parsed_doc["metadata"] = {}
                parsed_doc["metadata"]["source"] = original_filename or file_path.name
                parsed_doc["metadata"]["document_id"] = document_id
                
                # If PDF is scanned, perform OCR
                if ext == '.pdf' and parsed_doc.get("is_scanned", False):
                    # This would extract images from PDF and process them
                    logger.info(f"Document {document_id} appears to be scanned, performing OCR")
                    # Implementation depends on how you're extracting PDF images
            
            # Step 2: Extract entities
            entities = {}
            if "text" in parsed_doc:
                entities = self.entity_extractor.extract_entities(parsed_doc["text"])
            elif "pages" in parsed_doc:
                # Process each page for entities
                all_text = "\n".join([p.get("text", "") for p in parsed_doc["pages"]])
                entities = self.entity_extractor.extract_entities(all_text)
            
            # Step 3: Chunk the document
            chunks = self.chunker.chunk_document(parsed_doc)
            logger.info(f"Document {document_id} chunked into {len(chunks)} parts")
            
            # Step 4: Generate embeddings
            chunks_with_embeddings = self.embedding_generator.embed_chunks(chunks)
            
            # Step 5: Store in vector database
            vector_store = VectorStore(document_id)
            vectors = [chunk["embedding"] for chunk in chunks_with_embeddings]
            metadata_list = [
                {
                    "text": chunk["text"],
                    "metadata": chunk["metadata"],
                    "chunk_id": chunk["chunk_id"]
                }
                for chunk in chunks_with_embeddings
            ]
            vector_store.add_vectors(vectors=vectors, metadata_list=metadata_list)
            
            # Save processing results
            result = {
                "document_id": document_id,
                "original_filename": original_filename or file_path.name,
                "chunks": len(chunks),
                "entities": entities,
                "metadata": parsed_doc.get("metadata", {}),
                "processed_at": str(date.today())
            }
            
            processed_path = Path(settings.processed_folder) / f"{document_id}.json"
            with open(processed_path, 'w') as f:
                json.dump(result, f)
            
            # Update status to completed
            await self._update_document_status(
                document_id, 
                ProcessingStatus.COMPLETED,
                message="Document processing completed",
                metadata=result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            await self._update_document_status(
                document_id, 
                ProcessingStatus.FAILED,
                message=f"Processing failed: {str(e)}"
            )
            raise
    
    async def get_document_status(self, document_id: str) -> Optional[DocumentResponse]:
        """Get document processing status"""
        status_path = Path(settings.processed_folder) / f"{document_id}_status.json"
        
        if not status_path.exists():
            return None
            
        try:
            with open(status_path, 'r') as f:
                status_data = json.load(f)
                
            return DocumentResponse(**status_data)
        except Exception as e:
            logger.error(f"Failed to get document status: {e}")
            return None
    
    async def _update_document_status(self, 
                                    document_id: str, 
                                    status: ProcessingStatus,
                                    message: str = "",
                                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update and save document processing status"""
        status_path = Path(settings.processed_folder) / f"{document_id}_status.json"
        
        status_data = {
            "document_id": document_id,
            "status": status.value,
            "message": message,
            "updated_at": str(date.today()),
            # Get original filename from existing status if available
            "filename": None,
            "metadata": metadata or {}
        }
        
        # Update existing status if it exists
        if status_path.exists():
            try:
                with open(status_path, 'r') as f:
                    existing_data = json.load(f)
                status_data["filename"] = existing_data.get("filename")
            except Exception:
                pass
        
        with open(status_path, 'w') as f:
            json.dump(status_data, f)
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its processed data"""
        # Check if document exists
        upload_dir = Path(settings.upload_folder)
        processed_dir = Path(settings.processed_folder)
        vector_dir = Path(settings.vector_folder)
        
        # Find document file
        files = list(upload_dir.glob(f"{document_id}.*"))
        if not files:
            raise FileNotFoundError(f"Document {document_id} not found")
            
        # Delete original file
        for file in files:
            file.unlink()
            
        # Delete processed data
        status_file = processed_dir / f"{document_id}_status.json"
        if status_file.exists():
            status_file.unlink()
            
        result_file = processed_dir / f"{document_id}.json"
        if result_file.exists():
            result_file.unlink()
            
        # Delete vector index
        index_file = vector_dir / f"{document_id}.faiss"
        if index_file.exists():
            index_file.unlink()
            
        metadata_file = vector_dir / f"{document_id}_metadata.pkl"
        if metadata_file.exists():
            metadata_file.unlink()
            
        return True