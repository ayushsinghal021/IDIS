from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List
import os
import logging

from app.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/json/{document_id}")
async def export_json(document_id: str, settings=Depends(get_settings)):
    """Export processed document data as JSON."""
    file_path = os.path.join(settings.processed_folder, f"{document_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")
    return FileResponse(file_path, media_type="application/json", filename=f"{document_id}.json")

@router.get("/csv/{document_id}")
async def export_csv(document_id: str, settings=Depends(get_settings)):
    """Export processed document data as CSV."""
    file_path = os.path.join(settings.processed_folder, f"{document_id}.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")
    return FileResponse(file_path, media_type="text/csv", filename=f"{document_id}.csv")

@router.get("/all")
async def list_exports(settings=Depends(get_settings)) -> List[str]:
    """List all available exports."""
    try:
        files = os.listdir(settings.processed_folder)
        return [file for file in files if file.endswith(".json") or file.endswith(".csv")]
    except Exception as e:
        logger.error(f"Failed to list exports: {e}")
        raise HTTPException(status_code=500, detail="Failed to list exports")