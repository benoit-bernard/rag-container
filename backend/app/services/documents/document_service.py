"""
Document Service
Handles document statistics and operations
This is the service used in your stats.py endpoint
"""
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from app.core.config import config

logger = logging.getLogger(__name__)

class DocumentService:
    """Document service for statistics and operations"""
    
    def __init__(self):
        self.data_dir = config.DATA_DIR
        self.documents_dir = config.DOCUMENTS_DIR
        self.registry_file = config.REGISTRY_FILE
        self.supported_extensions = config.SUPPORTED_EXTENSIONS
        logger.debug("DocumentService initialized")
    
    def get_document_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive document statistics
        This is the method called by your stats.py endpoint
        """
        try:
            logger.info("Collecting document statistics")
            
            # Basic file system stats
            registry_stats = self._get_registry_stats()
            file_system_stats = self._get_file_system_stats()
            extension_stats = self._get_extension_stats()
            
            # Combine all statistics
            stats = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "registry": registry_stats,
                "file_system": file_system_stats,
                "extensions": extension_stats,
                "configuration": {
                    "cache_strategy": config.FILE_CACHE_STRATEGY,
                    "supported_extensions": config.SUPPORTED_EXTENSIONS,
                    "data_directory": str(config.DATA_DIR),
                    "documents_directory": str(config.DOCUMENTS_DIR)
                }
            }
            
            logger.info(f"Document stats collected: {registry_stats['total_files']} files in registry")
            return stats
            
        except Exception as e:
            logger.error(f"Error collecting document stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "configuration": {
                    "cache_strategy": config.FILE_CACHE_STRATEGY
                }
            }
    
    def _get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics from registry file"""
        try:
            if not self.registry_file.exists():
                return {
                    "total_files": 0,
                    "registry_exists": False,
                    "registry_size_bytes": 0
                }
            
            import json
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
            
            # Count files (excluding metadata entries)
            file_count = len([k for k in registry_data.keys() if not k.startswith('_')])
            
            return {
                "total_files": file_count,
                "registry_exists": True,
                "registry_size_bytes": self.registry_file.stat().st_size,
                "last_modified": datetime.fromtimestamp(
                    self.registry_file.stat().st_mtime
                ).isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error reading registry stats: {e}")
            return {
                "total_files": 0,
                "registry_exists": False,
                "error": str(e)
            }
    
    def _get_file_system_stats(self) -> Dict[str, Any]:
        """Get file system statistics"""
        try:
            if not self.documents_dir.exists():
                return {
                    "documents_directory_exists": False,
                    "total_files_on_disk": 0
                }
            
            # Count all files in documents directory
            all_files = list(self.documents_dir.rglob("*"))
            file_count = len([f for f in all_files if f.is_file()])
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in all_files if f.is_file())
            
            return {
                "documents_directory_exists": True,
                "total_files_on_disk": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.warning(f"Error collecting file system stats: {e}")
            return {
                "documents_directory_exists": False,
                "error": str(e)
            }
    
    def _get_extension_stats(self) -> Dict[str, Any]:
        """Get statistics by file extension"""
        try:
            if not self.documents_dir.exists():
                return {"by_extension": {}}
            
            extension_counts = {}
            for ext in self.supported_extensions:
                files = list(self.documents_dir.rglob(f"*{ext}"))
                extension_counts[ext] = len(files)
            
            # Count other extensions
            all_files = [f for f in self.documents_dir.rglob("*") if f.is_file()]
            other_count = len([
                f for f in all_files 
                if f.suffix not in self.supported_extensions
            ])
            
            return {
                "by_extension": extension_counts,
                "other_extensions": other_count,
                "supported_extensions": self.supported_extensions
            }
            
        except Exception as e:
            logger.warning(f"Error collecting extension stats: {e}")
            return {"by_extension": {}, "error": str(e)}

# Global instance - This is what your stats.py imports
document_service = DocumentService()