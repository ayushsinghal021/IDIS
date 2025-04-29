import logging
import json
from typing import Dict, Any, List, Optional, Union
import os
import requests
import openai

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure OpenAI if API key is available
if settings.openai_api_key:
    openai.api_key = settings.openai_api_key


class LLMOrchestrator:
    """Orchestrates interactions with LLMs for document Q&A"""
    
    def __init__(self, provider: str = None):
        """
        Initialize LLM orchestrator
        
        Args:
            provider: LLM provider to use (openai, ollama, huggingface)
        """
        self.provider = provider or settings.llm_provider
        
        # Validate setup
        if self.provider == "openai" and not settings.openai_api_key:
            logger.warning("OpenAI API key not set. Set OPENAI_API_KEY in environment variables.")
        
    async def generate_answer(self, 
                             query: str, 
                             context_docs: List[Dict[str, Any]],
                             max_tokens: int = 512) -> Dict[str, Any]:
        """
        Generate an answer based on the query and context documents
        
        Args:
            query: User query
            context_docs: List of relevant document chunks with metadata
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            Dictionary with answer and metadata
        """
        # Format context for the LLM
        formatted_context = self._format_context(context_docs)
        
        # Create prompt
        prompt = self._create_qa_prompt(query, formatted_context)
        
        # Generate answer using selected provider
        try:
            if self.provider == "openai":
                response = await self._query_openai(prompt, max_tokens)
            elif self.provider == "ollama":
                response = await self._query_ollama(prompt, max_tokens)
            elif self.provider == "huggingface":
                response = await self._query_huggingface(prompt, max_tokens)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
                
            # Format response
            return {
                "answer": response,
                "sources": [doc.get("metadata", {}) for doc in context_docs],
                "query": query
            }
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def _format_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """Format context documents for the prompt"""
        formatted_chunks = []
        
        for i, doc in enumerate(context_docs):
            text = doc.get("text", "")
            meta = doc.get("metadata", {})
            source = meta.get("source", f"Document {i+1}")
            
            # Format the chunk with source information
            formatted_chunk = f"[DOCUMENT {i+1}: {source}]\n{text}\n"
            formatted_chunks.append(formatted_chunk)
            
        return "\n".join(formatted_chunks)
    
    def _create_qa_prompt(self, query: str, context: str) -> str:
        """Create a prompt for Q&A"""
        return f"""Answer the question based on the provided context. If the answer cannot be determined from the context, say "I don't have enough information to answer that."

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""
    
    async def _query_openai(self, prompt: str, max_tokens: int) -> str:
        """Query OpenAI API"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided document contexts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _query_ollama(self, prompt: str, max_tokens: int) -> str:
        """Query Ollama API"""
        try:
            url = f"{settings.ollama_url}/api/generate"
            data = {
                "model": settings.ollama_model,
                "prompt": prompt,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.3
                }
            }
            
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            # Extract text from Ollama response
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def _query_huggingface(self, prompt: str, max_tokens: int) -> str:
        """Query HuggingFace model (implementation placeholder)"""
        # This would use a HuggingFace client or API
        # For brevity, returning mock response
        logger.warning("HuggingFace integration not fully implemented")
        return "This is a placeholder response from the HuggingFace model integration."