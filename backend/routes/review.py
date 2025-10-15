import os
import time
import tempfile
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query, Depends
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.env")

from models.review_model import FileUploadResponse, ErrorResponse, ReviewCreate
from models.db_models import ReviewRecord
from services.llm_review import llm_review_service
from services.report_formatter import report_formatter
from utils.pdf_generator import pdf_generator
from database.db import get_db_session, close_session

router = APIRouter(prefix="/api", tags=["code-review"])

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.py', '.js', '.java', '.cpp', '.c', '.ts', '.go', '.rs', '.php', '.rb', '.txt'}

# File size limits
MAX_FILE_SIZE_KB = int(os.getenv("MAX_FILE_SIZE_KB", 200))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_KB * 1024

def validate_file_extension(filename: str) -> bool:
    """Validate if file extension is allowed"""
    if not filename:
        return False
    
    extension = '.' + filename.split('.')[-1].lower()
    return extension in ALLOWED_EXTENSIONS

def get_file_size_mb(file_size: int) -> float:
    """Convert bytes to MB"""
    return round(file_size / (1024 * 1024), 2)

@router.post("/upload")
async def upload_and_review_code(
    file: UploadFile = File(..., description="Source code file to review"),
    export_pdf: bool = Query(False, description="Generate PDF report"),
    db: Session = Depends(get_db_session)
):
    """
    Upload a source code file and get AI-powered code review
    
    Supported file types: .py, .js, .java, .cpp, .c, .ts, .go, .rs, .php, .rb, .txt
    """
    start_time = time.time()
    
    try:
        # Validate file extension
        if not validate_file_extension(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size (limit to configured KB)
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size too large. Maximum allowed size is {MAX_FILE_SIZE_KB}KB."
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty."
            )
        
        # Decode file content
        try:
            content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File contains invalid characters. Please ensure the file is UTF-8 encoded."
            )
        
        # Analyze the code
        review = llm_review_service.analyze_code(content, file.filename)
        
        # Calculate processing time
        processing_time = round(time.time() - start_time, 2)
        
        # Detect language
        language = llm_review_service.detect_language(file.filename)
        
        # Format the review with enhanced structure
        formatted_review = report_formatter.format_review(review, file.filename)
        
        # Add additional metadata
        formatted_review.update({
            "file_size": get_file_size_mb(file_size),
            "language": language,
            "processing_time": processing_time
        })
        
        # Generate PDF if requested
        pdf_path = None
        if export_pdf:
            try:
                pdf_path = pdf_generator.generate_pdf(formatted_review, file.filename)
                formatted_review["pdf_report"] = f"/api/download-pdf/{os.path.basename(pdf_path)}"
            except Exception as e:
                print(f"Error generating PDF: {e}")
                formatted_review["pdf_error"] = "Failed to generate PDF report"
        
        # Save review to database
        try:
            new_review = ReviewRecord(
                filename=file.filename,
                review_json=formatted_review,
                overall_score=formatted_review.get("overall_score", 0),
                language=language,
                file_size=get_file_size_mb(file_size),
                processing_time=processing_time,
                total_issues=formatted_review.get("total_issues", 0),
                critical_issues=formatted_review.get("critical_issues", 0),
                high_issues=formatted_review.get("high_issues", 0),
                medium_issues=formatted_review.get("medium_issues", 0),
                low_issues=formatted_review.get("low_issues", 0)
            )
            db.add(new_review)
            db.commit()
            db.refresh(new_review)
            
            # Add database ID to response
            formatted_review["review_id"] = new_review.id
            
        except Exception as e:
            print(f"Error saving review to database: {e}")
            # Don't fail the request if database save fails
            db.rollback()
        
        return formatted_review
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the file: {str(e)}"
        )

@router.get("/download-pdf/{filename}")
async def download_pdf(filename: str):
    """Download a generated PDF report"""
    pdf_path = os.path.join("reports", filename)
    
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF report not found"
        )
    
    return FileResponse(
        path=pdf_path,
        filename=filename,
        media_type="application/pdf"
    )

@router.post("/upload-multiple")
async def upload_and_review_multiple_files(
    files: List[UploadFile] = File(..., description="Multiple source code files to review"),
    export_pdf: bool = Query(False, description="Generate PDF reports")
):
    """
    Upload multiple source code files and get AI-powered code reviews
    
    Supported file types: .py, .js, .java, .cpp, .c, .ts, .go, .rs, .php, .rb, .txt
    Maximum 5 files per request
    """
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 files allowed per request."
        )
    
    results = []
    
    for file in files:
        try:
            # Use the single file upload logic
            result = await upload_and_review_code(file, export_pdf)
            results.append(result)
        except HTTPException as e:
            # Add error result for failed files
            results.append({
                "filename": file.filename or "unknown",
                "file_size": 0,
                "language": "Unknown",
                "error": str(e.detail),
                "processing_time": 0
            })
    
    return results

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "supported_extensions": list(ALLOWED_EXTENSIONS),
        "max_file_size_kb": MAX_FILE_SIZE_KB,
        "max_files_per_request": 5
    }

@router.get("/health")
async def health_check():
    """Health check endpoint for the review service"""
    return {
        "status": "healthy",
        "service": "code-review",
        "supported_languages": list(llm_review_service.supported_languages.values())
    }
