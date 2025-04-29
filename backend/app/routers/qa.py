from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any, Optional
import logging

from app.config import Settings, get_settings
from app.models.query import QueryRequest, QueryResponse
from app.services.qa_service import QAService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest = Body(...),
    settings: Settings = Depends(get_settings)
):
    """Query documents and get answers"""
    
    try:
        qa_service = QAService()
        response = await qa_service.answer_query(
            query=request.query,
            document_ids=request.document_ids,
            k=request.top_k or 5
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query")


@router.post("/chat/{document_id}")
async def chat_with_document(
    document_id: str,
    message: str = Body(..., embed=True),
    chat_history: Optional[List[Dict[str, str]]] = Body(default=[]),
    settings: Settings = Depends(get_settings)
):
    """Chat with a specific document"""
    
    try:
        qa_service = QAService()
        response = await qa_service.chat_with_document(
            document_id=document_id,
            message=message,
            chat_history=chat_history
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")