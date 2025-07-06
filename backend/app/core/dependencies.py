"""
Centralized dependency manager
"""
import logging
from typing import Optional, Any
from app.core.config import config

logger = logging.getLogger(__name__)

class DependencyContainer:
    """Container for dependency injection"""
    
    def __init__(self):
        self._smart_reload_service: Optional[Any] = None
        self._registry_manager: Optional[Any] = None
        self._file_scanner: Optional[Any] = None
        self._metadata_manager: Optional[Any] = None
        logger.info(f"🔧 Container initialized - Cache strategy: {config.FILE_CACHE_STRATEGY}")
    
    def get_smart_reload_service(self):
        """Lazy loading of SmartReloadService"""
        if self._smart_reload_service is None:
            from app.services.smart_reload_service import SmartReloadService
            self._smart_reload_service = SmartReloadService()
            logger.debug(f"✅ SmartReloadService initialized (strategy: {config.FILE_CACHE_STRATEGY})")
        return self._smart_reload_service
    
    def get_registry_manager(self):
        """Lazy loading of RegistryManager"""
        if self._registry_manager is None:
            from app.services.documents.registry import RegistryManager
            self._registry_manager = RegistryManager()
            logger.debug("✅ RegistryManager initialized")
        return self._registry_manager
    
    def get_file_scanner(self):
        """Lazy loading of FileScanner"""
        if self._file_scanner is None:
            from app.services.documents.scanner import FileScanner
            self._file_scanner = FileScanner()
            logger.debug(f"✅ FileScanner initialized (extensions: {config.SUPPORTED_EXTENSIONS})")
        return self._file_scanner
    
    def get_metadata_manager(self):
        """Lazy loading of MetadataManager"""
        if self._metadata_manager is None:
            from app.services.documents.metadata import MetadataManager
            self._metadata_manager = MetadataManager()
            logger.debug(f"✅ MetadataManager initialized (strict: {config.METADATA_VALIDATION_STRICT})")
        return self._metadata_manager
    
    def health_check(self) -> dict:
        """Health check for dependencies"""
        health_status = {
            "dependencies_status": "healthy",
            "services_loaded": [],
            "configuration": config.get_configuration_summary()
        }
        
        if self._smart_reload_service:
            health_status["services_loaded"].append("SmartReloadService")
        if self._registry_manager:
            health_status["services_loaded"].append("RegistryManager")
        if self._file_scanner:
            health_status["services_loaded"].append("FileScanner")
        if self._metadata_manager:
            health_status["services_loaded"].append("MetadataManager")
            
        return health_status

# Global instance
dependencies = DependencyContainer()