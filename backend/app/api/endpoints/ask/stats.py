"""
Document statistics endpoint (from Ask)
Route: GET /documents/stats
"""
import logging
from .base import ask_base

logger = logging.getLogger(__name__)

def register_stats_route(app):
    """
    Register the GET /documents/stats route from Ask
    """
    
    @app.get("/documents/stats")
    async def get_document_stats():
        """
        Document statistics
        """
        try:
            # ✅ EXACTLY your code - using existing service
            from app.services.documents import document_service
            
            return document_service.get_document_stats()
            
        except Exception as e:
            # ✅ EXACTLY your error handling
            logger.error(f"Stats error: {e}")
            
            from fastapi import HTTPException
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving stats: {str(e)}"
            )