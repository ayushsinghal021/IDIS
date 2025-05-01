from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentResponse(BaseModel):
    document_id: str
    filename: Optional[str]
    status: ProcessingStatus
    message: Optional[str]
    metadata: Optional[dict] = None
