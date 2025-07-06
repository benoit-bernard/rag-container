"""
Ask Question Endpoint
Route: POST /ask
"""
import logging
from .base import ask_base
from .models import QuestionRequest, QuestionResponse

logger = logging.getLogger(__name__)

def register_ask_route(app):
    """Register the POST /ask route"""
    
    @app.post("/ask", response_model=QuestionResponse)
    async def ask_question(request: QuestionRequest):
        """
        Ask a question to the RAG system
        """
        try:
            from app.services.qa.qa_service import qa_service
            
            logger.info(f"Question received: {request.question}")
            result = qa_service.process_question(request.question)
            
            if "error" in result:
                logger.error(f"QA processing error: {result['error']}")
                return QuestionResponse(
                    success=False,
                    question=request.question,
                    answer=result["answer"],
                    sources=result.get("sources", []),
                    timestamp=ask_base.get_current_timestamp(),
                    service_context=ask_base.get_service_context()
                )
            
            # Success response
            return QuestionResponse(
                success=True,
                question=request.question,
                answer=result["answer"],
                sources=result.get("sources", []),
                timestamp=ask_base.get_current_timestamp(),
                service_context={
                    **ask_base.get_service_context(),
                    "model": result.get("model", "unknown"),
                    "confidence": result.get("confidence", 0.0),
                    "processing_time": result.get("processing_time", "unknown")
                }
            )
            
        except Exception as e:
            logger.error(f"Question processing error: {str(e)}")
            return QuestionResponse(
                success=False,
                question=request.question,
                answer=f"❌ System error: {str(e)}",
                sources=[],
                timestamp=ask_base.get_current_timestamp(),
                service_context=ask_base.get_service_context()
            )