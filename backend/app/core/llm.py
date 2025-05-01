import logging
import json
from typing import Dict, Any, List, Optional, Union
import os
import requests
import openai
import groq
from groq import Groq

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure OpenAI if API key is available
if settings.openai_api_key:
    openai.api_key = settings.openai_api_key

# Configure Groq client properly
groq_client = None
if settings.groq_api_key:
    groq_client = Groq(api_key=settings.groq_api_key)

# List of available Groq models to try (in order of preference)
GROQ_MODELS = [
    "llama3-8b-8192",     # Smaller but widely available
    "llama3-70b-8192",    # Larger but may require more resources
    "gemma-7b-it",        # Another widely available option
    "mixtral-8x7b-32768"  # Alternative option
]

class LLMOrchestrator:
    """Orchestrates interactions with LLMs for document Q&A"""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM orchestrator
        
        Args:
            provider: LLM provider to use (groq, openai)
        """
        self.provider = provider or settings.llm_provider

        # Validate setup
        if self.provider == "groq" and not settings.groq_api_key:
            logger.warning("Groq API key not set. Set GROQ_API_KEY in environment variables.")
        elif self.provider == "openai" and not settings.openai_api_key:
            logger.warning("OpenAI API key not set. Set OPENAI_API_KEY in environment variables.")

    async def generate_answer(self, query: str, context_docs: List[Dict[str, Any]], max_tokens: int = 512) -> Dict[str, Any]:
        """
        Generate an answer based on the query and context documents
        
        Args:
            query: User query
            context_docs: List of relevant document chunks with metadata
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Format the context and create the prompt
            formatted_context = self._format_context(context_docs)
            prompt = self._create_qa_prompt(query, formatted_context)

            # Call the appropriate LLM provider
            if self.provider == "groq":
                return await self._query_groq(prompt, max_tokens)
            elif self.provider == "openai":
                return await self._query_openai(prompt, max_tokens)
            elif self.provider == "ollama":
                response = await self._query_ollama(prompt, max_tokens)
                return {
                    "answer": response,
                    "sources": [],
                    "query": prompt
                }
            elif self.provider == "huggingface":
                response = await self._query_huggingface(prompt, max_tokens)
                return {
                    "answer": response,
                    "sources": [],
                    "query": prompt
                }
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"LLM generation failed with {self.provider}: {e}")
            
            # Try different models for Groq if there's an error
            if self.provider == "groq":
                return await self._try_groq_models(prompt, max_tokens)
            
            # If all else fails, try other providers or raise error
            if settings.openai_api_key:
                logger.info("Falling back to OpenAI...")
                try:
                    return await self._query_openai(prompt, max_tokens)
                except Exception as openai_error:
                    logger.error(f"OpenAI fallback failed: {openai_error}")
            
            try:
                logger.info("Falling back to Ollama...")
                response = await self._query_ollama(prompt, max_tokens)
                return {
                    "answer": response,
                    "sources": [],
                    "query": prompt
                }
            except Exception as ollama_error:
                logger.error(f"Ollama fallback failed: {ollama_error}")
            
            # If all fallbacks fail, raise the original error
            raise

    async def _try_groq_models(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Try multiple Groq models until one works"""
        last_error = None
        
        # Try each model in the list
        for model in GROQ_MODELS:
            if model == settings.groq_model:
                continue  # Skip the one that already failed
                
            logger.info(f"Trying Groq model: {model}")
            try:
                completion = groq_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.3
                )
                
                answer = completion.choices[0].message.content
                logger.info(f"Successfully used Groq model: {model}")
                
                return {
                    "answer": answer,
                    "sources": [],
                    "query": prompt
                }
            except Exception as e:
                logger.warning(f"Failed with Groq model {model}: {e}")
                last_error = e
        
        # If we've tried all models and none worked, raise the last error
        if last_error:
            raise last_error
        else:
            raise ValueError("No Groq models worked and no errors were captured")

    async def _query_groq(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Query Groq API using the correct client method"""
        try:
            if not groq_client:
                raise ValueError("Groq client not initialized. Check if GROQ_API_KEY is set correctly.")
                
            # Create a completion using the Groq client
            completion = groq_client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            # Extract the response text from the completion
            answer = completion.choices[0].message.content
            
            return {
                "answer": answer,
                "sources": [],
                "query": prompt
            }
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

    async def _query_openai(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Query OpenAI API"""
        try:
            # Check if API key is available
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not set. Set OPENAI_API_KEY in environment variables.")
                
            response = openai.ChatCompletion.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return {
                "answer": response.choices[0].message.content.strip(),
                "sources": [],
                "query": prompt
            }
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

    def _format_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """Format context documents for the prompt"""
        formatted_chunks = []
        for i, doc in enumerate(context_docs):
            text = doc.get("text", "")
            meta = doc.get("metadata", {})
            source = meta.get("source", f"Document {i+1}")
            formatted_chunks.append(f"[DOCUMENT {i+1}: {source}]\n{text}\n")
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