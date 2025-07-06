"""
Common utilities for ask endpoints
"""
import logging
from datetime import datetime
from app.core.config import config

logger = logging.getLogger(__name__)

class AskBase:
    """Utility class for ask endpoints"""
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Standardized timestamp"""
        return datetime.now().isoformat()
    
    @staticmethod
    def get_service_context() -> dict:
        """Service context for responses"""
        return {
            "service": config.APP_NAME,
            "version": config.APP_VERSION,
            "ollama_model": config.OLLAMA_MODEL,
            "ollama_data_version": config.OLLAMA_DATA_VERSION,
            "cache_strategy": config.FILE_CACHE_STRATEGY
        }
    
    @staticmethod
    def format_error_response(error: Exception) -> dict:
        """Standardized error format"""
        return {
            "success": False,
            "error": str(error),
            "timestamp": AskBase.get_current_timestamp(),
            "service_info": AskBase.get_service_context()
        }

# Shared instance
ask_base = AskBase()