"""
Registry Manager Service
Handles document registry operations with centralized configuration
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from app.core.config import config

logger = logging.getLogger(__name__)

class RegistryManager:
    def __init__(self):
        self.registry_file = config.REGISTRY_FILE
        self.auto_backup = config.REGISTRY_AUTO_BACKUP
        self.data_dir = config.DATA_DIR
        logger.debug(f"RegistryManager initialized (auto_backup: {self.auto_backup})")
    
    def get_current_registry(self) -> Dict[str, Any]:
        """Get current registry content"""
        try:
            if not self.registry_file.exists():
                logger.info("Registry file doesn't exist, returning empty registry")
                return {}
            
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            logger.debug(f"Registry loaded: {len(registry)} entries")
            return registry
            
        except Exception as e:
            logger.error(f"Error loading registry: {e}")
            return {}
    
    def save_registry(self, registry_data: Dict[str, Any]) -> bool:
        """
        Save registry to file with optional backup
        """
        try:
            # Create data directory if it doesn't exist
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup current registry if enabled
            if self.auto_backup and self.registry_file.exists():
                self._create_backup()
            
            # Add metadata
            dict_registry = dict(registry_data)
            dict_registry["_metadata"] = {
                "last_updated": datetime.now().isoformat(),
                "total_files": len(dict_registry) - 1,  # Exclude metadata itself
                "cache_strategy": config.FILE_CACHE_STRATEGY,
                "auto_backup_enabled": self.auto_backup
            }
            
            # Save registry
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(dict_registry, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Registry saved: {len(dict_registry)-1} files")
            return True
            
        except Exception as e:
            logger.error(f"Error saving registry: {e}")
            return False
    
    def update_registry(self, scan_results: Dict[str, Any]) -> bool:
        """Update registry with scan results"""
        try:
            current_registry = self.get_current_registry()
            
            # Update with changed files
            for file_path, metadata in scan_results.get("changed_files", {}).items():
                current_registry[file_path] = metadata
            
            # Remove deleted files
            for file_path in scan_results.get("deleted_files", []):
                current_registry.pop(file_path, None)
            
            # Save updated registry
            return self.save_registry(current_registry)
            
        except Exception as e:
            logger.error(f"Error updating registry: {e}")
            return False
    
    def rebuild_registry(self, scan_results: Dict[str, Any]) -> bool:
        """Completely rebuild registry"""
        try:
            new_registry = scan_results.get("all_files", {})
            return self.save_registry(new_registry)
            
        except Exception as e:
            logger.error(f"Error rebuilding registry: {e}")
            return False
    
    def add_file(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """Add single file to registry"""
        try:
            current_registry = self.get_current_registry()
            current_registry[file_path] = metadata
            return self.save_registry(current_registry)
            
        except Exception as e:
            logger.error(f"Error adding file to registry: {e}")
            return False
    
    def remove_file(self, file_path: str) -> bool:
        """Remove single file from registry"""
        try:
            current_registry = self.get_current_registry()
            if file_path in current_registry:
                del current_registry[file_path]
                return self.save_registry(current_registry)
            return True  # File wasn't in registry anyway
            
        except Exception as e:
            logger.error(f"Error removing file from registry: {e}")
            return False
    
    def _create_backup(self) -> None:
        """Create backup of current registry"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.data_dir / f"file_registry_backup_{timestamp}.json"
            
            # Copy current registry to backup
            import shutil
            shutil.copy2(self.registry_file, backup_file)
            
            logger.debug(f"Registry backup created: {backup_file}")
            
            # Clean old backups (keep only last 5)
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.warning(f"Error creating registry backup: {e}")
    
    def _cleanup_old_backups(self) -> None:
        """Keep only the 5 most recent backups"""
        try:
            backup_files = list(self.data_dir.glob("file_registry_backup_*.json"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for old_backup in backup_files[5:]:
                old_backup.unlink()
                logger.debug(f"Old backup removed: {old_backup}")
                
        except Exception as e:
            logger.warning(f"Error cleaning old backups: {e}")