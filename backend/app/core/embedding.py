import logging
from typing import List, Dict, Any, Union
import numpy as np
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingGenerator:
    """Generates vector embeddings for document chunks"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding generator
        
        Args:
            model_name: Name of the SentenceTransformer model to use
        """
        self.model_name = model_name or settings.embedding_model
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
            
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of text chunks
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Array of embeddings with shape (len(texts), embedding_dim)
        """
        try:
            embeddings = self.model.encode(texts, show_progress_bar=len(texts) > 10)
            return embeddings
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
            
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks and add them to chunk objects
        
        Args:
            chunks: List of chunk dictionaries with 'text' key
            
        Returns:
            Updated chunks with embeddings added
        """
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.generate_embeddings(texts)
        
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()
            
        return chunks