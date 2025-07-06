"""
Document models
Contains FileMetadata and other document-related models
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from pathlib import Path

logger = logging.getLogger(__name__)

class FileMetadata(BaseModel):
    """
    File metadata model
    This is your existing FileMetadata class, enriched with configuration
    """
    # Basic file information
    name: str = Field(..., description="File name")
    extension: str = Field(..., description="File extension")
    size: int = Field(..., description="File size in bytes")
    relative_path: str = Field(..., description="Relative path from documents directory")
    
    # Timestamps
    modified: str = Field(..., description="Last modified timestamp (ISO format)")
    created: str = Field(..., description="Created timestamp (ISO format)")
    scan_timestamp: str = Field(..., description="When this metadata was extracted")
    
    # Content metadata
    content_length: Optional[int] = Field(None, description="Content length for text files")
    line_count: Optional[int] = Field(None, description="Number of lines for text files")
    word_count: Optional[int] = Field(None, description="Number of words for text files")
    encoding: Optional[str] = Field("utf-8", description="File encoding")
    
    # Categorization
    file_category: Optional[str] = Field(None, description="File category (text, document, code, etc.)")
    size_category: Optional[str] = Field(None, description="Size category (tiny, small, medium, large)")
    
    # Validation
    validation_timestamp: Optional[str] = Field(None, description="When metadata was validated")
    validation_strict: Optional[bool] = Field(None, description="Whether strict validation was used")
    
    # Errors
    content_error: Optional[str] = Field(None, description="Error message if content extraction failed")
    metadata_error: Optional[str] = Field(None, description="Error message if metadata extraction failed")
    
    # Additional metadata
    metadata_config: Optional[Dict[str, Any]] = Field(None, description="Configuration used for metadata extraction")
    path_info: Optional[Dict[str, Any]] = Field(None, description="Path-related information")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Path: lambda v: str(v)
        }
        schema_extra = {
            "example": {
                "name": "example.txt",
                "extension": ".txt",
                "size": 1024,
                "relative_path": "subfolder/example.txt",
                "modified": "2025-01-20T10:00:00",
                "created": "2025-01-20T09:00:00",
                "scan_timestamp": "2025-01-20T10:30:00",
                "content_length": 500,
                "line_count": 25,
                "word_count": 100,
                "encoding": "utf-8",
                "file_category": "text",
                "size_category": "small"
            }
        }
    
    @classmethod
    def from_file_path(cls, file_path: Path, documents_dir: Path) -> "FileMetadata":
        """
        Create FileMetadata from file path
        Uses centralized configuration for metadata extraction
        """
        try:
            from app.services.documents.metadata import MetadataManager
            
            # Get basic file stats
            stat = file_path.stat()
            
            # Create basic metadata
            basic_metadata = {
                "name": file_path.name,
                "extension": file_path.suffix.lower(),
                "size": stat.st_size,
                "relative_path": str(file_path.relative_to(documents_dir)),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "scan_timestamp": datetime.now().isoformat()
            }
            
            # Enrich with metadata manager
            metadata_manager = MetadataManager()
            enriched_metadata = metadata_manager.enrich_metadata(basic_metadata, file_path)
            
            # Extract content metadata
            content_metadata = metadata_manager.extract_content_metadata(file_path)
            enriched_metadata.update(content_metadata)
            
            return cls(**enriched_metadata)
            
        except Exception as e:
            logger.error(f"Error creating FileMetadata from {file_path}: {e}")
            # Return minimal metadata
            return cls(
                name=file_path.name,
                extension=file_path.suffix.lower(),
                size=0,
                relative_path=str(file_path),
                modified=datetime.now().isoformat(),
                created=datetime.now().isoformat(),
                scan_timestamp=datetime.now().isoformat(),
                metadata_error=str(e)
            )

class DocumentStats(BaseModel):
    """Document statistics model"""
    success: bool = Field(..., description="Whether stats collection was successful")
    timestamp: str = Field(..., description="When stats were collected")
    
    # Registry stats
    registry: Dict[str, Any] = Field(..., description="Registry-related statistics")
    
    # File system stats
    file_system: Dict[str, Any] = Field(..., description="File system statistics")
    
    # Extension stats
    extensions: Dict[str, Any] = Field(..., description="Statistics by file extension")
    
    # Configuration
    configuration: Dict[str, Any] = Field(..., description="Current configuration")
    
    # Error
    error: Optional[str] = Field(None, description="Error message if stats collection failed")

class RegistryMetadata(BaseModel):
    """Registry metadata model"""
    last_updated: str = Field(..., description="Last registry update timestamp")
    total_files: int = Field(..., description="Total number of files in registry")
    cache_strategy: str = Field(..., description="Current cache strategy")
    auto_backup_enabled: bool = Field(..., description="Whether auto backup is enabled")
    
class ScanResult(BaseModel):
    """Scan result model"""
    scan_type: str = Field(..., description="Type of scan performed")
    timestamp: str = Field(..., description="When scan was performed")
    total_files: Optional[int] = Field(None, description="Total files found")
    
    # Different scan results
    changed_files: Optional[Dict[str, FileMetadata]] = Field(None, description="Changed files")
    deleted_files: Optional[List[str]] = Field(None, description="Deleted files")
    new_files: Optional[Dict[str, FileMetadata]] = Field(None, description="New files")
    all_files: Optional[Dict[str, FileMetadata]] = Field(None, description="All files")