from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.routers import documents, qa, entities, export
from app.config import Settings, get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Interactive Document Intelligence System",
    description="API for document processing, analysis, and Q&A",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(qa.router, prefix="/api/qa", tags=["qa"])
app.include_router(entities.router, prefix="/api/entities", tags=["entities"])
app.include_router(export.router, prefix="/api/export", tags=["export"])

@app.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": app.version,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)