"""
Health Check Endpoint
Route: GET /health
"""
import logging
from .base import health_base

logger = logging.getLogger(__name__)

def register_health_route(app):
    """Register the GET /health route"""
    
    @app.get("/health")
    async def health_check():
        try:
            # Basic information
            base_info = health_base.get_service_info()
            
            # COMPLETE system information
            detailed_health = health_base.get_detailed_system_health()
            
            # COMPLETE combination - No information lost
            health_response = {
                "status": "healthy",
                "timestamp": health_base.get_current_timestamp(),
                **base_info,
                **detailed_health
            }
            
            logger.debug("✅ Complete health check performed successfully")
            return health_response
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            from app.core.config import config
            return {
                "status": "degraded",
                "timestamp": health_base.get_current_timestamp(),
                "service": "Backend RAG",
                "error": str(e),
                "configuration": {
                    "cache_strategy": config.FILE_CACHE_STRATEGY,
                    "ollama_model": config.OLLAMA_MODEL,
                    "ollama_data_version": config.OLLAMA_DATA_VERSION
                }
            }