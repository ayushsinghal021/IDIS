from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    document_ids: List[str]
    top_k: Optional[int] = 5


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Dict[str, Any]] = []