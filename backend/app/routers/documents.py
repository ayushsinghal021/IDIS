from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import shutil
import os
import uuid
from pathlib import Path
import logging

from app.config import Settings, get_settings
from app.models.document import DocumentResponse, ProcessingStatus
from app.services.document_service import DocumentService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    process_now: bool = Form(True),
    settings: Settings = Depends(get_settings)
):
    """Upload a document and optionally process it immediately"""
    
    # Validate file type
    allowed_extensions = [".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create document ID and save path
    document_id = str(uuid.uuid4())
    upload_dir = Path(settings.upload_folder)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename
    safe_filename = f"{document_id}{file_ext}"
    file_path = upload_dir / safe_filename
    
    # Save the uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")
    
    # Initialize document service
    document_service = DocumentService()
    
    # Process document in background or just register it
    if process_now:
        background_tasks.add_task(
            document_service.process_document,
            str(file_path),
            document_id,
            original_filename=file.filename
        )
        status = ProcessingStatus.PROCESSING
    else:
        status = ProcessingStatus.PENDING
    
    return DocumentResponse(
        document_id=document_id,
        filename=file.filename,
        status=status,
        message="Document uploaded successfully" + 
                (". Processing started in background." if process_now else "")
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_status(
    document_id: str,
    settings: Settings = Depends(get_settings)
):
    """Get document processing status"""
    document_service = DocumentService()
    status = await document_service.get_document_status(document_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return status


@router.post("/{document_id}/process")
async def process_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings)
):
    """Process a previously uploaded document"""
    document_service = DocumentService()
    
    # Check if document exists
    status = await document_service.get_document_status(document_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get file path
    upload_dir = Path(settings.upload_folder)
    files = list(upload_dir.glob(f"{document_id}.*"))
    
    if not files:
        raise HTTPException(status_code=404, detail="Document file not found")
    
    # Start processing in background
    background_tasks.add_task(
        document_service.process_document,
        str(files[0]),
        document_id,
        original_filename=status.filename
    )
    
    return {"document_id": document_id, "status": "Processing started"}


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    settings: Settings = Depends(get_settings)
):
    """Delete a document and its processed data"""
    document_service = DocumentService()
    
    try:
        await document_service.delete_document(document_id)
        return {"document_id": document_id, "status": "deleted"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")