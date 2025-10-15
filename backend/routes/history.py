from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db_session, close_session
from models.db_models import ReviewRecord
from models.review_model import ReviewResponse, ReviewDetailResponse, HistoryResponse

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("/", response_model=HistoryResponse)
async def get_review_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db_session)
):
    """
    Get paginated list of all code reviews sorted by newest first
    """
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count
        total_count = db.query(ReviewRecord).count()
        
        # Get paginated reviews
        reviews = db.query(ReviewRecord)\
            .order_by(ReviewRecord.created_at.desc())\
            .offset(offset)\
            .limit(per_page)\
            .all()
        
        # Convert to response models
        review_responses = [
            ReviewResponse(
                id=review.id,
                filename=review.filename,
                overall_score=review.overall_score,
                language=review.language,
                file_size=review.file_size,
                processing_time=review.processing_time,
                total_issues=review.total_issues,
                critical_issues=review.critical_issues,
                high_issues=review.high_issues,
                medium_issues=review.medium_issues,
                low_issues=review.low_issues,
                created_at=review.created_at.isoformat() if review.created_at else "",
                updated_at=review.updated_at.isoformat() if review.updated_at else None
            )
            for review in reviews
        ]
        
        return HistoryResponse(
            reviews=review_responses,
            total_count=total_count,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching review history: {str(e)}"
        )
    finally:
        close_session(db)

@router.get("/{review_id}", response_model=ReviewDetailResponse)
async def get_review_by_id(
    review_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Get a specific review by ID including full review data
    """
    try:
        review = db.query(ReviewRecord).filter(ReviewRecord.id == review_id).first()
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review with ID {review_id} not found"
            )
        
        return ReviewDetailResponse(
            id=review.id,
            filename=review.filename,
            review_json=review.review_json,
            overall_score=review.overall_score,
            language=review.language,
            file_size=review.file_size,
            processing_time=review.processing_time,
            total_issues=review.total_issues,
            critical_issues=review.critical_issues,
            high_issues=review.high_issues,
            medium_issues=review.medium_issues,
            low_issues=review.low_issues,
            created_at=review.created_at.isoformat() if review.created_at else "",
            updated_at=review.updated_at.isoformat() if review.updated_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching review: {str(e)}"
        )
    finally:
        close_session(db)

@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Delete a specific review by ID
    """
    try:
        review = db.query(ReviewRecord).filter(ReviewRecord.id == review_id).first()
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review with ID {review_id} not found"
            )
        
        db.delete(review)
        db.commit()
        
        return {
            "message": f"Review with ID {review_id} deleted successfully",
            "deleted_review": {
                "id": review.id,
                "filename": review.filename,
                "overall_score": review.overall_score
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting review: {str(e)}"
        )
    finally:
        close_session(db)

@router.get("/stats/summary")
async def get_review_stats(db: Session = Depends(get_db_session)):
    """
    Get summary statistics of all reviews
    """
    try:
        total_reviews = db.query(ReviewRecord).count()
        
        if total_reviews == 0:
            return {
                "total_reviews": 0,
                "average_score": 0,
                "total_issues": 0,
                "languages": {},
                "recent_reviews": 0
            }
        
        # Calculate average score
        avg_score = db.query(ReviewRecord.overall_score).all()
        average_score = sum(score[0] for score in avg_score) / len(avg_score)
        
        # Calculate total issues
        total_issues = db.query(ReviewRecord.total_issues).all()
        total_issues_count = sum(issues[0] or 0 for issues in total_issues)
        
        # Get language distribution
        languages = db.query(ReviewRecord.language).all()
        language_counts = {}
        for lang in languages:
            if lang[0]:
                language_counts[lang[0]] = language_counts.get(lang[0], 0) + 1
        
        # Get recent reviews (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_reviews = db.query(ReviewRecord).filter(
            ReviewRecord.created_at >= week_ago
        ).count()
        
        return {
            "total_reviews": total_reviews,
            "average_score": round(average_score, 2),
            "total_issues": total_issues_count,
            "languages": language_counts,
            "recent_reviews": recent_reviews
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching review statistics: {str(e)}"
        )
    finally:
        close_session(db)
