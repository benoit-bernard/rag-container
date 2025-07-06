"""
Common utilities for health endpoints
"""
import logging
import psutil
import os
from datetime import datetime
from pathlib import Path
from app.core.config import config

logger = logging.getLogger(__name__)

class HealthBase:
    
    @staticmethod
    def get_current_timestamp() -> str:
        return datetime.now().isoformat()
    
    @staticmethod
    def get_service_info() -> dict:
        return config.get_health_base_info()
    
    @staticmethod
    def get_detailed_system_health() -> dict:
        try:
            # Late import to avoid circular errors
            from app.core.dependencies import dependencies
            
            # System metrics
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(str(config.DATA_DIR))
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # File verifications
            registry_exists = config.REGISTRY_FILE.exists()
            registry_size = config.REGISTRY_FILE.stat().st_size if registry_exists else 0
            documents_exists = config.DOCUMENTS_DIR.exists()
            
            # Document file count
            doc_count = 0
            if documents_exists:
                try:
                    doc_count = len(list(config.DOCUMENTS_DIR.rglob("*")))
                except Exception:
                    doc_count = -1
            
            return {
                "system_metrics": {
                    "cpu_usage_percent": round(cpu_percent, 2),
                    "memory_usage_percent": round(memory.percent, 2),
                    "memory_total_gb": round(memory.total / (1024**3), 2),
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "memory_used_gb": round(memory.used / (1024**3), 2),
                    "disk_usage_percent": round((disk.used / disk.total) * 100, 2),
                    "disk_total_gb": round(disk.total / (1024**3), 2),
                    "disk_free_gb": round(disk.free / (1024**3), 2),
                    "disk_used_gb": round(disk.used / (1024**3), 2)
                },
                "application_health": {
                    "cache_strategy": config.FILE_CACHE_STRATEGY,
                    "scan_interval_seconds": config.FILE_SCAN_INTERVAL,
                    "metadata_validation": "strict" if config.METADATA_VALIDATION_STRICT else "permissive",
                    "auto_backup_enabled": config.REGISTRY_AUTO_BACKUP,
                    "supported_extensions": config.SUPPORTED_EXTENSIONS,
                    "data_directory": str(config.DATA_DIR),
                    "registry_file_exists": registry_exists,
                    "registry_file_size_bytes": registry_size,
                    "documents_directory_exists": documents_exists,
                    "estimated_document_count": doc_count
                },
                "ollama_configuration": {
                    "model": config.OLLAMA_MODEL,
                    "data_version": config.OLLAMA_DATA_VERSION,
                    "base_url": config.OLLAMA_BASE_URL,
                    "timeout_seconds": config.OLLAMA_TIMEOUT
                },
                "dependencies": dependencies.health_check(),
                "environment": {
                    "log_level": config.LOG_LEVEL,
                    "python_executable": os.sys.executable,
                    "working_directory": str(Path.cwd()),
                    "environment_variables": {
                        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "default"),
                        "FILE_CACHE_STRATEGY": os.getenv("FILE_CACHE_STRATEGY", "default"),
                        "LOG_LEVEL": os.getenv("LOG_LEVEL", "default")
                    }
                }
            }
        except Exception as e:
            logger.warning(f"Error collecting system metrics: {e}")
            return {
                "system_metrics": {"error": f"Unavailable: {str(e)}"},
                "application_health": config.get_configuration_summary(),
                "ollama_configuration": {
                    "model": config.OLLAMA_MODEL,
                    "data_version": config.OLLAMA_DATA_VERSION
                },
                "error": str(e)
            }

# Shared instance
health_base = HealthBase()