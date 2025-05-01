from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from app.config import Settings, get_settings
from app.core.entity_extraction import EntityExtractor

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/extract")
async def extract_entities(
    text: str,
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Extract entities from text"""
    try:
        extractor = EntityExtractor()
        entities = extractor.extract_entities(text)
        return {"entities": entities}
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract entities")