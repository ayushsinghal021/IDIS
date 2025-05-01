import logging
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
import os
import faiss
import json
from pathlib import Path
import pickle

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStore:
    """Vector database for storing and retrieving document embeddings"""
    
    def __init__(self, 
                 index_name: str,
                 dimension: int = None,
                 vector_dir: str = None):
        """
        Initialize vector store
        
        Args:
            index_name: Name of the index to use
            dimension: Dimension of embedding vectors
            vector_dir: Directory to store vector indexes
        """
        self.index_name = index_name
        self.dimension = dimension or settings.vector_dimension
        self.vector_dir = Path(vector_dir or settings.vector_folder)
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_path = self.vector_dir / f"{index_name}.faiss"
        self.metadata_path = self.vector_dir / f"{index_name}_metadata.pkl"
        
        # Initialize index
        self.index = None
        self.metadata = []
        
        # Load or create index
        self._load_or_create_index()
        
    def _load_or_create_index(self):
        """Load existing index or create a new one"""
        if self.index_path.exists() and self.metadata_path.exists():
            # Load existing index
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded existing index '{self.index_name}' with {len(self.metadata)} vectors")
            except Exception as e:
                logger.error(f"Failed to load index: {e}")
                self._create_new_index()
        else:
            # Create new index
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        logger.info(f"Created new index '{self.index_name}' with dimension {self.dimension}")
    
    def add_vectors(self, vectors: np.ndarray, metadata_list: List[Dict[str, Any]]) -> List[int]:
        """
        Add vectors to the index
        
        Args:
            vectors: Numpy array of vectors with shape (n, dimension)
            metadata_list: List of metadata dictionaries for each vector
            
        Returns:
            List of assigned IDs
        """
        if vectors.shape[0] != len(metadata_list):
            raise ValueError("Number of vectors and metadata entries must match")
            
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {vectors.shape[1]}")
        
        # Convert to float32 if needed
        if vectors.dtype != np.float32:
            vectors = vectors.astype(np.float32)
        
        # Get current count for ID assignment
        start_id = len(self.metadata)
        
        # Add vectors to index
        self.index.add(vectors)
        
        # Store metadata
        assigned_ids = list(range(start_id, start_id + len(metadata_list)))
        for meta in metadata_list:
            self.metadata.append(meta)
            
        # Save updated index
        self._save_index()
        
        return assigned_ids
    
    def search(self, 
              query_vector: np.ndarray, 
              k: int = 5) -> Tuple[List[Dict[str, Any]], List[float]]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query vector
            k: Number of results to return
            
        Returns:
            Tuple of (list of metadata, list of distances)
        """
        if not self.index or self.index.ntotal == 0:
            return [], []
            
        # Ensure vector is correctly shaped
        if len(query_vector.shape) == 1:
            query_vector = np.expand_dims(query_vector, axis=0)
            
        if query_vector.dtype != np.float32:
            query_vector = query_vector.astype(np.float32)
            
        # Search index
        distances, indices = self.index.search(query_vector, k)
        
        # Get metadata for results
        result_metadata = []
        result_distances = []
        
        for idx, dist in zip(indices[0], distances[0]):
            if idx != -1 and 0 <= idx < len(self.metadata):
                result_metadata.append(self.metadata[idx])
                result_distances.append(float(dist))
                
        return result_metadata, result_distances
    
    def _save_index(self):
        """Save the index and metadata to disk"""
        try:
            faiss.write_index(self.index, str(self.index_path))
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            logger.info(f"Saved index '{self.index_name}' with {len(self.metadata)} vectors")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            
    def clear(self):
        """Clear the index and metadata"""
        self._create_new_index()
        if self.index_path.exists():
            self.index_path.unlink()
        if self.metadata_path.exists():
            self.metadata_path.unlink()
        logger.info(f"Cleared index '{self.index_name}'")