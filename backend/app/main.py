"""
Main entry point for the FastAPI application
"""
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Centralized configuration
from app.core.config import config

# Logging configuration
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)

logger = logging.getLogger(__name__)

# FastAPI application creation
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Backend API for RAG system with modular architecture"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import modular routes
from app.api.endpoints.health.health import register_health_route
from app.api.endpoints.health.version import register_version_route
from app.api.endpoints.smart_reload.smart_reload import register_smart_reload_route
from app.api.endpoints.ask.ask import register_ask_route
from app.api.endpoints.ask.stats import register_stats_route

# Startup log with configuration
logger.info(f"🚀 Starting {config.APP_NAME} v{config.APP_VERSION}")
logger.info(f"📁 Cache strategy: {config.FILE_CACHE_STRATEGY}")
logger.info(f"🤖 Ollama model: {config.OLLAMA_MODEL}")
logger.info(f"📊 Data version: {config.OLLAMA_DATA_VERSION}")

# Register modular routes
register_health_route(app)
register_version_route(app)
register_smart_reload_route(app)
register_ask_route(app)
register_stats_route(app)

# Endpoints 
@app.get("/debug")
async def debug_endpoint():
    """Debug endpoint"""
    try:
        from app.core.dependencies import dependencies
        
        return {
            "status": "ok",
            "message": "Debug endpoint working",
            "timestamp": config.get_health_base_info(),
            "services": dependencies.health_check()
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files-status")  
async def files_status_compat():
    """Files status endpoint - Frontend compatibility"""
    return await file_status()

@app.get("/files/status")
async def file_status():
    """File status endpoint"""
    try:
        from app.services.documents.document_service import document_service

        stats = document_service.get_document_stats()
        return {
            "status": "ok",
            "files": stats,
            "timestamp": stats.get("timestamp")
        }
    except Exception as e:
        logger.error(f"File status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reload")  # Route que votre frontend appelle
async def reload_compat():
    """Reload endpoint - Frontend compatibility - redirects to smart_reload"""
    try:
        from app.core.dependencies import dependencies
        
        smart_reload_service = dependencies.get_smart_reload_service()
        result = await smart_reload_service.smart_reload()
        
        return {
            "success": True,
            "message": "Reload completed successfully",
            "details": result
        }
    except Exception as e:
        logger.error(f"Reload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def general_status():
    """General status endpoint"""
    try:
        from app.core.dependencies import dependencies
        from app.services.documents.document_service import document_service
       
        # Combine health and file status
        health_info = {
            "service": config.APP_NAME,
            "version": config.APP_VERSION,
            "status": "operational"
        }
        
        file_stats = document_service.get_document_stats()
        dependencies_health = dependencies.health_check()
        
        return {
            "health": health_info,
            "files": file_stats,
            "dependencies": dependencies_health,
            "timestamp": file_stats.get("timestamp")
        }
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

app.get("/config")
async def get_config():
    """Configuration endpoint"""
    return {
        "ollama_model": config.OLLAMA_MODEL,
        "ollama_api": config.OLLAMA_BASE_URL,
        "chunk_size": getattr(config, 'CHUNK_SIZE', 1000),
        "chunk_overlap": getattr(config, 'CHUNK_OVERLAP', 200),
        "retrieval_k": getattr(config, 'RETRIEVAL_K', 5),
        "embedding_model": getattr(config, 'EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
        "persist_dir": str(config.DATA_DIR)
    }

@app.get("/stats")
async def get_stats():
    """Statistics endpoint"""
    try:
        from app.services.documents.document_service import document_service
        
        stats = document_service.get_document_stats()
        
        # Add system stats
        system_stats = {
            "ollama_model": config.OLLAMA_MODEL,
            "embedding_model": getattr(config, 'EMBEDDING_MODEL', 'unknown'),
            "chunk_size": getattr(config, 'CHUNK_SIZE', 1000),
            "qa_ready": True #todo > assuming QA service is ready
        }
        
        return {
            "files": stats,
            "system": system_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ADDITIONNAL LEGALY ENDPOINTS

@app.post("/test-simple")
async def test_simple():
    """Test simple sans documents pour vérifier Ollama (from rag_server.py)"""
    try:
        from app.services.qa.qa_service import qa_service
        
        result = qa_service.test_ollama_connection()
        return result
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/qa-status")
async def qa_status():
    """QA service status"""
    try:
        from app.services.qa.qa_service import qa_service
        
        return qa_service.get_qa_status()
    except Exception as e:
        logger.error(f"QA status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/qa/initialize")
async def initialize_qa():
    """Initialize QA chain"""
    try:
        from app.services.qa.qa_service import qa_service
        
        success = qa_service.initialize_qa_chain()
        
        if success:
            return {
                "success": True,
                "message": "QA chain initialized successfully",
                "status": qa_service.get_qa_status()
            }
        else:
            return {
                "success": False,
                "message": "Failed to initialize QA chain",
                "status": qa_service.get_qa_status()
            }
    except Exception as e:
        logger.error(f"QA initialization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/qa/rebuild")
@app.post("/rebuild")
async def rebuild_qa_system():
    """Force rebuild of QA system"""
    try:
        from app.services.qa.qa_service import qa_service
        logger.info("🔄 Forcing QA system rebuild...")
        
        if qa_service.initialize_qa_chain(force_rebuild=True):
            return {
                "success": True,
                "message": "QA system rebuilt successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "QA system rebuild failed",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error rebuilding QA system: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

app.get("/debug-ollama")
async def debug_ollama():
    """Debug Ollama connection"""
    try:
        from app.services.qa.qa_service import qa_service
        import requests
        
        # Test direct HTTP
        health_check = {}
        try:
            response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            health_check["http_status"] = response.status_code
            health_check["http_reachable"] = True
            if response.status_code == 200:
                health_check["available_models"] = response.json()
        except Exception as e:
            health_check["http_reachable"] = False
            health_check["http_error"] = str(e)
        
        # Test QA service
        qa_test = qa_service.test_ollama_connection()
        
        return {
            "config": {
                "ollama_url": config.OLLAMA_BASE_URL,
                "ollama_model": config.OLLAMA_MODEL
            },
            "http_check": health_check,
            "qa_service_test": qa_test,
            "containers_suggestion": "Run: docker-compose ps to check container status"
        }
    except Exception as e:
        return {"error": str(e)}
    


logger.info("✅ All routes registered")

@app.on_event("startup")
async def startup_event():
    """Startup events"""
    logger.info(f"🎯 Application started successfully")
    logger.info(f"🔧 Configuration: {config.get_configuration_summary()}")
    
    # Initialize QA service on startup
    try:
        from app.services.qa.qa_service import qa_service
        logger.info("🔄 Initializing QA service...")
        success = qa_service.initialize_qa_chain()
        if success:
            logger.info("✅ QA service initialized successfully")
        else:
            logger.warning("⚠️ QA service initialization failed")
    except Exception as e:
        logger.error(f"❌ QA service initialization error: {e}")

        
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown events"""
    logger.info("🛑 Application shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)