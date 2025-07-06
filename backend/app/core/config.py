"""
Centralized application configuration
Single point of configuration for all parameters
Easily configurable from this single file
"""
import os
from datetime import datetime
from pathlib import Path

class AppConfig:
    # ===== APPLICATION INFORMATION =====
    APP_NAME = "Backend RAG"
    APP_VERSION = "1.0.0"
    BUILD_DATE = "2025-01-20"
    ARCHITECTURE = "modular"
    
    # ===== TECHNICAL VERSIONS =====
    PYTHON_VERSION = "3.11+"
    LANGCHAIN_VERSION = "0.1.0+"
    CHROMADB_VERSION = "0.4.18+"
    FASTAPI_VERSION = "0.104.0+"
    
    # ===== 🤖 OLLAMA CONFIGURATION (EASILY CONFIGURABLE) =====
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-coder:6.7b")  # 🎯 CONFIGURABLE
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")# "http://localhost:11434")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))
    OLLAMA_DATA_VERSION = os.getenv("OLLAMA_DATA_VERSION", "v2025.01.20")  
    OLLAMA_CONNECT_TIMEOUT = int(os.getenv("OLLAMA_CONNECT_TIMEOUT", "60"))    # Connexion: 1 min
    OLLAMA_READ_TIMEOUT = int(os.getenv("OLLAMA_READ_TIMEOUT", "600"))         # Lecture: 10 min
    OLLAMA_INITIALIZATION_TIMEOUT = int(os.getenv("OLLAMA_INITIALIZATION_TIMEOUT", "900"))  # Init: 15 min

    # ===== 📁 FILE CACHE STRATEGIES (EASILY CONFIGURABLE) =====
    FILE_CACHE_STRATEGY = os.getenv("FILE_CACHE_STRATEGY", "smart")
    # Options: "smart", "full", "incremental", "disabled"
    FILE_SCAN_INTERVAL = int(os.getenv("FILE_SCAN_INTERVAL", "300"))  # 5 minutes
    METADATA_VALIDATION_STRICT = os.getenv("METADATA_VALIDATION_STRICT", "true").lower() == "true"
    REGISTRY_AUTO_BACKUP = os.getenv("REGISTRY_AUTO_BACKUP", "true").lower() == "true"
    
    # ===== PATHS =====
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR: Path = Path("/app/shared_data") 
    DOCUMENTS_DIR = DATA_DIR / "documents"
    CHROMA_DB_DIR: Path = Path("/app/shared_data/chroma_db") 
    REGISTRY_FILE = DATA_DIR / "file_registry.json"
    
    # ===== LOGGING =====
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K", "5"))
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # ===== SUPPORTED EXTENSIONS =====
    SUPPORTED_EXTENSIONS = [".txt", ".md", ".pdf", ".docx", ".py", ".json"]
    
    # ===== APPLICATION HEALTH =====
    HEALTH_CHECK_COMPONENTS = [
        "file_system",
        "registry",
        "ollama_connection",
        "memory_usage",
        "cache_strategy",
        "dependencies"
    ]
    
    @classmethod
    def get_version_info(cls) -> dict:
        """Complete version information - ENRICHED"""
        return {
            "application": cls.APP_NAME,
            "version": cls.APP_VERSION,
            "build_date": cls.BUILD_DATE,
            "python_version": cls.PYTHON_VERSION,
            "langchain_version": cls.LANGCHAIN_VERSION,
            "chromadb_version": cls.CHROMADB_VERSION,
            "fastapi_version": cls.FASTAPI_VERSION,
            "architecture": cls.ARCHITECTURE,
            "ollama_model": cls.OLLAMA_MODEL,
            "ollama_data_version": cls.OLLAMA_DATA_VERSION,
            "file_cache_strategy": cls.FILE_CACHE_STRATEGY,
            "scan_interval_seconds": cls.FILE_SCAN_INTERVAL,
            "metadata_validation": "strict" if cls.METADATA_VALIDATION_STRICT else "permissive",
            "auto_backup": cls.REGISTRY_AUTO_BACKUP
        }
    
    @classmethod
    def get_health_base_info(cls) -> dict:
        """Basic health information"""
        return {
            "service": cls.APP_NAME,
            "status": "operational",
            "version": cls.APP_VERSION,
            "architecture": cls.ARCHITECTURE
        }
    
    @classmethod
    def get_configuration_summary(cls) -> dict:
        """Current configuration summary"""
        return {
            "cache_strategy": cls.FILE_CACHE_STRATEGY,
            "ollama_model": cls.OLLAMA_MODEL,
            "ollama_data_version": cls.OLLAMA_DATA_VERSION,
            "scan_interval": cls.FILE_SCAN_INTERVAL,
            "supported_extensions": cls.SUPPORTED_EXTENSIONS,
            "validation_strict": cls.METADATA_VALIDATION_STRICT
        }

# Global instance
config = AppConfig()