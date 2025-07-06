"""
Smart Reload Service
Handles intelligent document reloading with change detection
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from app.core.config import config

logger = logging.getLogger(__name__)

class SmartReloadService:
    """Smart reload service with configurable cache strategy"""
    
    def __init__(self):
        self.cache_strategy = config.FILE_CACHE_STRATEGY
        self.scan_interval = config.FILE_SCAN_INTERVAL
        logger.info(f"SmartReloadService initialized with strategy: {self.cache_strategy}")
    
    async def smart_reload(self) -> Dict[str, Any]:
        logger.info(f"Starting smart reload with strategy: {self.cache_strategy}")
        
        try:
            if self.cache_strategy == "smart":
                result = await self._smart_strategy_reload()
            elif self.cache_strategy == "full":
                result = await self._full_strategy_reload()
            elif self.cache_strategy == "incremental":
                result = await self._incremental_strategy_reload()
            elif self.cache_strategy == "disabled":
                result = await self._disabled_strategy_reload()
            else:
                logger.warning(f"Unknown cache strategy: {self.cache_strategy}, using smart")
                result = await self._smart_strategy_reload()
            
            logger.info(f"Smart reload completed: {result.get('strategy')} strategy")
            return result
                
        except Exception as e:
            logger.error(f"Smart reload failed: {e}")
            raise
    
    async def _smart_strategy_reload(self) -> Dict[str, Any]:
        """Smart strategy: Only reload changed files"""
        try:
            from app.services.documents.registry import RegistryManager
            from app.services.documents.scanner import FileScanner
            
            registry_manager = RegistryManager()
            file_scanner = FileScanner()
            
            # Get current registry
            current_registry = registry_manager.get_current_registry()
            
            # Scan for changes
            scan_results = await file_scanner.scan_for_changes()
            
            # Process only changed files
            changed_files = scan_results.get("changed_files", {})
            deleted_files = scan_results.get("deleted_files", [])
            
            # Update registry
            if changed_files or deleted_files:
                registry_manager.update_registry(scan_results)
            
            return {
                "strategy": "smart",
                "files_processed": len(changed_files),
                "files_changed": list(changed_files.keys()),
                "files_deleted": deleted_files,
                "total_files_in_registry": len(current_registry),
                "timestamp": datetime.now().isoformat(),
                "cache_strategy_config": self.cache_strategy
            }
        except Exception as e:
            logger.error(f"Smart strategy reload failed: {e}")
            raise
    
    async def _full_strategy_reload(self) -> Dict[str, Any]:
        """Full strategy: Reload all files"""
        try:
            from app.services.documents.registry import RegistryManager
            from app.services.documents.scanner import FileScanner
            
            registry_manager = RegistryManager()
            file_scanner = FileScanner()
            
            # Full scan
            scan_results = await file_scanner.full_scan()
            
            # Rebuild entire registry
            registry_manager.rebuild_registry(scan_results)
            
            return {
                "strategy": "full",
                "files_processed": len(scan_results.get("all_files", {})),
                "registry_rebuilt": True,
                "timestamp": datetime.now().isoformat(),
                "cache_strategy_config": self.cache_strategy
            }
        except Exception as e:
            logger.error(f"Full strategy reload failed: {e}")
            raise
    
    async def _incremental_strategy_reload(self) -> Dict[str, Any]:
        """Incremental strategy: Add only new files"""
        try:
            from app.services.documents.registry import RegistryManager
            from app.services.documents.scanner import FileScanner
            
            registry_manager = RegistryManager()
            file_scanner = FileScanner()
            
            # Scan for new files only
            scan_results = await file_scanner.scan_new_files()
            
            # Add new files to registry
            new_files = scan_results.get("new_files", {})
            for file_path, metadata in new_files.items():
                registry_manager.add_file(file_path, metadata)
            
            return {
                "strategy": "incremental",
                "files_added": len(new_files),
                "new_files": list(new_files.keys()),
                "timestamp": datetime.now().isoformat(),
                "cache_strategy_config": self.cache_strategy
            }
        except Exception as e:
            logger.error(f"Incremental strategy reload failed: {e}")
            raise
    
    async def _disabled_strategy_reload(self) -> Dict[str, Any]:
        """Disabled strategy: No reload"""
        logger.info("Cache strategy disabled - no reload performed")
        
        return {
            "strategy": "disabled",
            "files_processed": 0,
            "message": "Reload disabled by configuration",
            "timestamp": datetime.now().isoformat(),
            "cache_strategy_config": self.cache_strategy
        }