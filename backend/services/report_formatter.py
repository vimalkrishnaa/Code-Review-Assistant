from typing import Dict, List, Any
from models.review_model import CodeReview, CodeIssue, ReviewSeverity

class ReportFormatter:
    """Service for formatting and enhancing code review reports"""
    
    def __init__(self):
        self.severity_weights = {
            ReviewSeverity.CRITICAL: 4,
            ReviewSeverity.HIGH: 3,
            ReviewSeverity.MEDIUM: 2,
            ReviewSeverity.LOW: 1
        }
    
    def format_review(self, review_data: CodeReview, filename: str) -> Dict[str, Any]:
        """
        Format and enhance the raw review data with computed fields
        """
        # Calculate overall score based on issues and suggestions
        overall_score = self._calculate_overall_score(review_data)
        
        # Generate summary paragraph
        summary = self._generate_summary(review_data, overall_score)
        
        # Group issues by severity
        issues_by_severity = self._group_issues_by_severity(review_data.issues)
        
        # Count issues by type
        issues_by_type = self._count_issues_by_type(review_data.issues)
        
        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(review_data)
        
        return {
            "filename": filename,
            "overall_score": overall_score,
            "summary": summary,
            "readability": review_data.readability,
            "modularity": review_data.modularity,
            "potential_bugs": review_data.potential_bugs,
            "suggestions": review_data.suggestions,
            "issues_by_severity": issues_by_severity,
            "issues_by_type": issues_by_type,
            "quality_metrics": quality_metrics,
            "total_issues": len(review_data.issues),
            "critical_issues": len([i for i in review_data.issues if i.severity == ReviewSeverity.CRITICAL]),
            "high_issues": len([i for i in review_data.issues if i.severity == ReviewSeverity.HIGH]),
            "medium_issues": len([i for i in review_data.issues if i.severity == ReviewSeverity.MEDIUM]),
            "low_issues": len([i for i in review_data.issues if i.severity == ReviewSeverity.LOW])
        }
    
    def _calculate_overall_score(self, review_data: CodeReview) -> int:
        """Calculate overall score based on issues and suggestions"""
        base_score = 10
        
        # Deduct points for issues based on severity
        for issue in review_data.issues:
            base_score -= self.severity_weights.get(issue.severity, 1) * 0.5
        
        # Deduct points for too many suggestions (indicates more problems)
        if len(review_data.suggestions) > 5:
            base_score -= 1
        elif len(review_data.suggestions) > 3:
            base_score -= 0.5
        
        # Ensure score is between 1 and 10
        return max(1, min(10, round(base_score)))
    
    def _generate_summary(self, review_data: CodeReview, overall_score: int) -> str:
        """Generate a comprehensive summary paragraph"""
        total_issues = len(review_data.issues)
        critical_issues = len([i for i in review_data.issues if i.severity == ReviewSeverity.CRITICAL])
        high_issues = len([i for i in review_data.issues if i.severity == ReviewSeverity.HIGH])
        
        if overall_score >= 8:
            quality_level = "excellent"
        elif overall_score >= 6:
            quality_level = "good"
        elif overall_score >= 4:
            quality_level = "fair"
        else:
            quality_level = "needs improvement"
        
        summary_parts = [f"Code quality is {quality_level} with an overall score of {overall_score}/10."]
        
        if total_issues == 0:
            summary_parts.append("No issues were identified.")
        else:
            issue_desc = []
            if critical_issues > 0:
                issue_desc.append(f"{critical_issues} critical")
            if high_issues > 0:
                issue_desc.append(f"{high_issues} high")
            if total_issues - critical_issues - high_issues > 0:
                issue_desc.append(f"{total_issues - critical_issues - high_issues} minor")
            
            summary_parts.append(f"Found {total_issues} issues: {', '.join(issue_desc)}.")
        
        if review_data.suggestions:
            summary_parts.append(f"Provided {len(review_data.suggestions)} improvement suggestions.")
        
        return " ".join(summary_parts)
    
    def _group_issues_by_severity(self, issues: List[CodeIssue]) -> Dict[str, List[Dict]]:
        """Group issues by severity level"""
        grouped = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for issue in issues:
            issue_dict = {
                "line_number": issue.line_number,
                "type": issue.issue_type,
                "description": issue.description,
                "suggestion": issue.suggestion
            }
            grouped[issue.severity.value].append(issue_dict)
        
        return grouped
    
    def _count_issues_by_type(self, issues: List[CodeIssue]) -> Dict[str, int]:
        """Count issues by type"""
        type_counts = {}
        for issue in issues:
            issue_type = issue.issue_type
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
        return type_counts
    
    def _calculate_quality_metrics(self, review_data: CodeReview) -> Dict[str, Any]:
        """Calculate additional quality metrics"""
        total_issues = len(review_data.issues)
        suggestions_count = len(review_data.suggestions)
        
        # Calculate complexity score (lower is better)
        complexity_score = min(10, max(1, 10 - (total_issues * 0.5) - (suggestions_count * 0.2)))
        
        # Calculate maintainability score
        maintainability_score = min(10, max(1, 10 - (total_issues * 0.3) - (suggestions_count * 0.1)))
        
        return {
            "complexity_score": round(complexity_score, 1),
            "maintainability_score": round(maintainability_score, 1),
            "suggestions_count": suggestions_count,
            "issues_per_suggestion": round(total_issues / max(1, suggestions_count), 2)
        }

# Create a singleton instance
report_formatter = ReportFormatter()
