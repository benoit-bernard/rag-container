"""
File Scanner Service
Handles document scanning with centralized configuration
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Set
from pathlib import Path
from app.core.config import config

logger = logging.getLogger(__name__)

class FileScanner:
    def __init__(self):
        self.documents_dir = config.DOCUMENTS_DIR
        self.supported_extensions = config.SUPPORTED_EXTENSIONS
        self.validation_strict = config.METADATA_VALIDATION_STRICT
        logger.debug(f"FileScanner initialized (extensions: {self.supported_extensions})")
    
    async def scan_for_changes(self) -> Dict[str, Any]:
        try:
            logger.info("Scanning for file changes")
            
            # Get current registry
            from app.services.documents.registry import RegistryManager
            registry_manager = RegistryManager()
            current_registry = registry_manager.get_current_registry()
            
            # Scan current files
            current_files = await self._scan_directory()
            
            # Compare with registry
            changed_files = {}
            deleted_files = []
            
            # Check for new or modified files
            for file_path, metadata in current_files.items():
                if file_path not in current_registry:
                    # New file
                    changed_files[file_path] = metadata
                elif self._file_modified(metadata, current_registry[file_path]):
                    # Modified file
                    changed_files[file_path] = metadata
            
            # Check for deleted files
            for file_path in current_registry:
                if file_path not in current_files and not file_path.startswith('_'):
                    deleted_files.append(file_path)
            
            result = {
                "scan_type": "changes",
                "changed_files": changed_files,
                "deleted_files": deleted_files,
                "total_current_files": len(current_files),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Change scan complete: {len(changed_files)} changed, {len(deleted_files)} deleted")
            return result
            
        except Exception as e:
            logger.error(f"Error scanning for changes: {e}")
            raise
    
    async def full_scan(self) -> Dict[str, Any]:
        """Perform full directory scan"""
        try:
            logger.info("Performing full directory scan")
            
            all_files = await self._scan_directory()
            
            result = {
                "scan_type": "full",
                "all_files": all_files,
                "total_files": len(all_files),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Full scan complete: {len(all_files)} files found")
            return result
            
        except Exception as e:
            logger.error(f"Error in full scan: {e}")
            raise
    
    async def scan_new_files(self) -> Dict[str, Any]:
        """Scan for new files only"""
        try:
            logger.info("Scanning for new files")
            
            # Get current registry
            from app.services.documents.registry import RegistryManager
            registry_manager = RegistryManager()
            current_registry = registry_manager.get_current_registry()
            
            # Scan current files
            current_files = await self._scan_directory()
            
            # Find new files
            new_files = {
                file_path: metadata 
                for file_path, metadata in current_files.items()
                if file_path not in current_registry
            }
            
            result = {
                "scan_type": "new",
                "new_files": new_files,
                "total_new_files": len(new_files),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"New files scan complete: {len(new_files)} new files")
            return result
            
        except Exception as e:
            logger.error(f"Error scanning for new files: {e}")
            raise
    
    async def _scan_directory(self) -> Dict[str, Any]:
        """Scan documents directory for supported files"""
        files_metadata = {}
        
        if not self.documents_dir.exists():
            logger.warning(f"Documents directory doesn't exist: {self.documents_dir}")
            return files_metadata
        
        try:
            # Use asyncio to make scanning non-blocking
            await asyncio.sleep(0)  # Yield control
            
            for file_path in self.documents_dir.rglob("*"):
                if file_path.is_file() and self._is_supported_file(file_path):
                    try:
                        metadata = await self._extract_file_metadata(file_path)
                        if metadata:
                            files_metadata[str(file_path)] = metadata
                    except Exception as e:
                        logger.warning(f"Error processing file {file_path}: {e}")
                        if not self.validation_strict:
                            # Add basic metadata even if extraction fails
                            files_metadata[str(file_path)] = {
                                "size": file_path.stat().st_size,
                                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                                "extension": file_path.suffix,
                                "error": str(e)
                            }
            
            return files_metadata
            
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
            raise
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """Check if file extension is supported"""
        return file_path.suffix.lower() in self.supported_extensions
    
    async def _extract_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from file"""
        try:
            stat = file_path.stat()
            
            metadata = {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "extension": file_path.suffix.lower(),
                "name": file_path.name,
                "relative_path": str(file_path.relative_to(self.documents_dir)),
                "scan_timestamp": datetime.now().isoformat()
            }
            
            # Add content-specific metadata based on file type
            if file_path.suffix.lower() in ['.txt', '.md']:
                metadata.update(await self._extract_text_metadata(file_path))
            elif file_path.suffix.lower() == '.json':
                metadata.update(await self._extract_json_metadata(file_path))
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Error extracting metadata from {file_path}: {e}")
            if self.validation_strict:
                raise
            return None
    
    async def _extract_text_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "content_length": len(content),
                "line_count": content.count('\n') + 1,
                "encoding": "utf-8"
            }
        except Exception as e:
            logger.warning(f"Error reading text file {file_path}: {e}")
            return {"content_error": str(e)}
    
    async def _extract_json_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from JSON files"""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "json_keys": list(data.keys()) if isinstance(data, dict) else [],
                "json_type": type(data).__name__,
                "valid_json": True
            }
        except Exception as e:
            logger.warning(f"Error reading JSON file {file_path}: {e}")
            return {"json_error": str(e), "valid_json": False}
    
    def _file_modified(self, current_metadata: Dict[str, Any], registry_metadata: Dict[str, Any]) -> bool:
        """Check if file has been modified"""
        try:
            return (
                current_metadata.get("modified") != registry_metadata.get("modified") or
                current_metadata.get("size") != registry_metadata.get("size")
            )
        except Exception:
            return True  # Assume modified if comparison fails
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        return self.supported_extensions.copy()