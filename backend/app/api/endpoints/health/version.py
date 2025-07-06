"""
System version information endpoint
Route: GET /version
"""
import logging
from .base import health_base
from app.core.config import config

logger = logging.getLogger(__name__)

def register_version_route(app):
    @app.get("/version")
    async def get_version():
        """
        System version information
        """
        # ✅ EXACTLY your version return + centralized config
        version_info = config.get_version_info()
        version_info["timestamp"] = health_base.get_current_timestamp()
        
        logger.debug("✅ Version information returned")
        return version_info