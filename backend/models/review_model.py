from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class ReviewSeverity(str, Enum):
    """Severity levels for code review issues"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CodeIssue(BaseModel):
    """Individual code issue found during review"""
    line_number: Optional[int] = None
    issue_type: str
    severity: ReviewSeverity
    description: str
    suggestion: Optional[str] = None

class CodeReview(BaseModel):
    """Complete code review result"""
    readability: str
    modularity: str
    potential_bugs: str
    suggestions: List[str]
    issues: List[CodeIssue] = []
    overall_score: int  # 1-10 scale
    summary: str

class FileUploadResponse(BaseModel):
    """Response model for file upload and review"""
    filename: str
    file_size: int
    language: str
    review: CodeReview
    processing_time: float

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None

# Database-related Pydantic models
class ReviewCreate(BaseModel):
    """Model for creating a new review record in database"""
    filename: str
    review_json: Dict[str, Any]
    overall_score: float
    language: Optional[str] = None
    file_size: Optional[float] = None
    processing_time: Optional[float] = None
    total_issues: Optional[int] = 0
    critical_issues: Optional[int] = 0
    high_issues: Optional[int] = 0
    medium_issues: Optional[int] = 0
    low_issues: Optional[int] = 0

class ReviewResponse(BaseModel):
    """Model for API response of review record"""
    id: int
    filename: str
    overall_score: float
    language: Optional[str] = None
    file_size: Optional[float] = None
    processing_time: Optional[float] = None
    total_issues: Optional[int] = 0
    critical_issues: Optional[int] = 0
    high_issues: Optional[int] = 0
    medium_issues: Optional[int] = 0
    low_issues: Optional[int] = 0
    created_at: str
    updated_at: Optional[str] = None

class ReviewDetailResponse(BaseModel):
    """Model for detailed review response including full review data"""
    id: int
    filename: str
    review_json: Dict[str, Any]
    overall_score: float
    language: Optional[str] = None
    file_size: Optional[float] = None
    processing_time: Optional[float] = None
    total_issues: Optional[int] = 0
    critical_issues: Optional[int] = 0
    high_issues: Optional[int] = 0
    medium_issues: Optional[int] = 0
    low_issues: Optional[int] = 0
    created_at: str
    updated_at: Optional[str] = None

class HistoryResponse(BaseModel):
    """Model for history endpoint response"""
    reviews: List[ReviewResponse]
    total_count: int
    page: int = 1
    per_page: int = 10
