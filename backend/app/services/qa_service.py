import logging
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path

from app.config import get_settings
from app.models.query import QueryResponse
from app.core.embedding import EmbeddingGenerator
from app.core.vector_store import VectorStore
from app.core.llm import LLMOrchestrator

logger = logging.getLogger(__name__)
settings = get_settings()


class QAService:
    """Service for document querying and question answering"""
    
    def __init__(self):
        """Initialize QA service with required components"""
        self.embedding_generator = EmbeddingGenerator()
        self.llm = LLMOrchestrator()
    
    async def answer_query(self, 
                          query: str, 
                          document_ids: List[str],
                          k: int = 5) -> QueryResponse:
        """
        Answer a query using the specified documents
        
        Args:
            query: User query
            document_ids: List of document IDs to search
            k: Number of top results to retrieve per document
            
        Returns:
            Query response with answer and sources
        """
        if not query:
            raise ValueError("Query cannot be empty")
            
        if not document_ids:
            raise ValueError("At least one document ID is required")
            
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embeddings([query])[0]
        
        # Search each document's vector store
        all_contexts = []
        
        for doc_id in document_ids:
            try:
                # Load vector store for document
                vector_store = VectorStore(doc_id)
                
                # Search for relevant chunks
                contexts, distances = vector_store.search(
                    query_vector=query_embedding,
                    k=k
                )
                
                # Add to combined contexts
                all_contexts.extend(contexts)
                
            except Exception as e:
                logger.error(f"Error searching document {doc_id}: {e}")
                # Continue with other documents
        
        if not all_contexts:
            return QueryResponse(
                query=query,
                answer="I couldn't find any relevant information in the specified documents.",
                sources=[]
            )
        
        # Sort all contexts by relevance (if we had distances for all)
        # This would require keeping track of distances alongside contexts
        
        # Generate answer using LLM
        result = await self.llm.generate_answer(
            query=query,
            context_docs=all_contexts
        )
        
        # Format sources for response
        sources = []
        for ctx in all_contexts:
            meta = ctx.get("metadata", {})
            if meta:
                source = {
                    "document_id": meta.get("document_id", "unknown"),
                    "source": meta.get("source", "unknown"),
                    "page": meta.get("page_num", None)
                }
                if source not in sources:
                    sources.append(source)
        
        return QueryResponse(
            query=query,
            answer=result["answer"],
            sources=sources
        )
    
    async def chat_with_document(self,
                                document_id: str,
                                message: str,
                                chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Chat with a specific document
        
        Args:
            document_id: Document ID
            message: User message
            chat_history: Previous chat messages
            
        Returns:
            Chat response
        """
        if not chat_history:
            chat_history = []
            
        # First, search for relevant context using the query
        query_embedding = self.embedding_generator.generate_embeddings([message])[0]
        
        try:
            # Load vector store for document
            vector_store = VectorStore(document_id)
            
            # Search for relevant chunks
            contexts, _ = vector_store.search(
                query_vector=query_embedding,
                k=5
            )
            
        except Exception as e:
            logger.error(f"Error searching document {document_id}: {e}")
            return {
                "message": message,
                "response": "I couldn't access the document you're asking about.",
                "document_id": document_id
            }
            
        if not contexts:
            return {
                "message": message,
                "response": "I couldn't find relevant information in this document.",
                "document_id": document_id
            }
            
        # Create a contextualized prompt that includes chat history
        # This would use a more sophisticated prompt than the basic QA
        system_prompt = "You are a helpful assistant answering questions about a specific document. Use only the provided document contexts to answer questions. If you don't know, say so."
        
        # Format chat history
        history_text = ""
        if chat_history:
            for entry in chat_history[-5:]:  # Only use last 5 entries
                if "user" in entry:
                    history_text += f"User: {entry['user']}\n"
                if "assistant" in entry:
                    history_text += f"Assistant: {entry['assistant']}\n"
        
        # Format document contexts
        context_text = "\n\n".join([ctx.get("text", "") for ctx in contexts])
        
        # Generate response
        full_prompt = f"{system_prompt}\n\nDocument context:\n{context_text}\n\nChat history:\n{history_text}\nUser: {message}\nAssistant:"
        
        response = await self.llm.generate_answer(
            query=full_prompt,
            context_docs=contexts,
            max_tokens=1024  # Allow longer responses for chat
        )
        
        return {
            "message": message,
            "response": response["answer"],
            "document_id": document_id
        }