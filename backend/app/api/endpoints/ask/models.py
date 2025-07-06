"""
Pydantic models for Ask endpoint
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class QuestionRequest(BaseModel):
    question: str
    max_results: Optional[int] = 5
    use_context: Optional[bool] = True

class Source(BaseModel):
    document: str
    score: float
    excerpt: str
    metadata: Optional[Dict[str, Any]] = None

class QuestionResponse(BaseModel):
    success: bool
    question: str
    answer: str
    sources: List[Source]
    timestamp: str
    service_context: Optional[Dict[str, Any]] = None