"""
Smart Reload Endpoint
Route: POST /smart_reload
"""
import logging
from app.core.dependencies import dependencies
from app.core.config import config

logger = logging.getLogger(__name__)

def register_smart_reload_route(app):
    @app.post("/smart_reload")
    async def smart_reload():
        """
        Intelligent reload with change detection
        """
        try:
            smart_reload_service = dependencies.get_smart_reload_service()
            logger.info(f"🔄 Starting smart reload (strategy: {config.FILE_CACHE_STRATEGY})")
            
            result = await smart_reload_service.smart_reload()
            
            enriched_result = {
                "success": True,
                "message": "Smart reload completed successfully",
                "details": result,
                "config": {
                    "cache_strategy": config.FILE_CACHE_STRATEGY,
                    "ollama_model": config.OLLAMA_MODEL,
                    "scan_interval": config.FILE_SCAN_INTERVAL
                }
            }
            
            logger.info("✅ Smart reload completed successfully")
            return enriched_result
            
        except Exception as e:
            logger.error(f"Smart reload error: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "config": {
                    "cache_strategy": config.FILE_CACHE_STRATEGY,
                    "ollama_model": config.OLLAMA_MODEL
                }
            }