import time
import random
import json
import os
from typing import Dict, List
import google.generativeai as genai
from dotenv import load_dotenv
from models.review_model import CodeReview, CodeIssue, ReviewSeverity

# Load environment variables
load_dotenv("config.env")

class LLMReviewService:
    """Service for analyzing code using Google Gemini LLM"""
    
    def __init__(self):
        self.supported_languages = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.ts': 'TypeScript',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.txt': 'Text'
        }
        
        # Initialize Gemini client
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
        
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                # Configure Gemini API
                genai.configure(api_key=self.api_key)
                self.model_instance = genai.GenerativeModel(self.model)
                self.use_real_llm = True
                print("Gemini client initialized successfully.")
            except Exception as e:
                print(f"Error initializing Gemini client: {e}")
                self.model_instance = None
                self.use_real_llm = False
                print("Falling back to mock responses.")
        else:
            self.model_instance = None
            self.use_real_llm = False
            print("Warning: Gemini API key not configured. Using mock responses.")
    
    def detect_language(self, filename: str) -> str:
        """Detect programming language from file extension"""
        extension = '.' + filename.split('.')[-1].lower()
        return self.supported_languages.get(extension, 'Unknown')
    
    def analyze_code(self, content: str, filename: str) -> CodeReview:
        """
        Analyze code content using Google Gemini LLM and return structured review
        Falls back to mock responses if API key is not configured
        """
        language = self.detect_language(filename)
        
        if self.use_real_llm:
            try:
                return self._analyze_with_gemini(content, filename, language)
            except Exception as e:
                print(f"Error calling Gemini API: {e}")
                print("Falling back to mock analysis...")
                return self._analyze_with_mock(content, filename, language)
        else:
            return self._analyze_with_mock(content, filename, language)
    
    def _analyze_with_gemini(self, content: str, filename: str, language: str) -> CodeReview:
        """Analyze code using Google Gemini API"""
        prompt = f"""
You are a senior software engineer and code reviewer with 15+ years of experience. You are known for your thorough, detailed, and constructive code reviews.

TASK: Perform a comprehensive code review of the following {language} code. Be extremely thorough and identify ALL potential issues, improvements, and best practices violations.

ANALYSIS REQUIREMENTS:
1. **CRITICAL BUGS**: Look for runtime errors, logic flaws, security vulnerabilities, memory leaks, infinite loops, null pointer exceptions, array bounds violations, division by zero, etc.

2. **CODE QUALITY**: Evaluate naming conventions, code structure, complexity, maintainability, readability, and adherence to language-specific best practices.

3. **PERFORMANCE**: Identify inefficient algorithms, unnecessary computations, memory usage issues, and optimization opportunities.

4. **SECURITY**: Check for input validation, sanitization, injection vulnerabilities, hardcoded secrets, and security best practices.

5. **ARCHITECTURE**: Assess function design, separation of concerns, coupling, cohesion, and overall code organization.

6. **ERROR HANDLING**: Look for missing try-catch blocks, proper error propagation, and robust error handling.

7. **TESTING**: Consider testability, edge cases, and areas that need unit tests.

8. **DOCUMENTATION**: Check for missing docstrings, comments, type hints, and inline documentation.

For each issue found, provide:
- Exact line number
- Issue type (bug/security/performance/style/documentation/maintainability)
- Severity level (critical/high/medium/low)
- Detailed description of the problem
- Specific fix suggestion with code examples when possible

Return your analysis in this EXACT JSON format:
{{
  "overall_score": <number 1-10>,
  "summary": "Comprehensive summary of code quality, main issues found, and overall assessment",
  "readability": "Detailed assessment of code readability, naming, structure, and clarity",
  "modularity": "Evaluation of function design, separation of concerns, and code organization",
  "potential_bugs": "Detailed analysis of bugs, runtime errors, logic flaws, and edge cases",
  "suggestions": [
    "Specific improvement suggestion 1",
    "Specific improvement suggestion 2",
    "Specific improvement suggestion 3"
  ],
  "line_wise_issues": [
    {{
      "line": <line_number>,
      "type": "bug|security|performance|style|documentation|maintainability",
      "severity": "critical|high|medium|low",
      "issue": "Detailed description of the specific issue found on this line",
      "fix_suggestion": "Specific code fix or improvement suggestion"
    }}
  ]
}}

IMPORTANT: 
- Be extremely thorough - don't miss any issues
- Provide specific, actionable feedback
- Include code examples in suggestions when helpful
- Rate severity accurately (critical = will cause crashes/security issues)
- Check every line carefully for potential problems

CODE TO REVIEW:
{content}
"""

        try:
            response = self.model_instance.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=4000,
                )
            )
            
            response_text = response.text.strip()
            
            # Try to parse JSON response
            try:
                review_data = json.loads(response_text)
                return self._parse_llm_response(review_data, language)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    review_data = json.loads(json_match.group())
                    return self._parse_llm_response(review_data, language)
                else:
                    raise ValueError("Could not parse JSON from LLM response")
                    
        except Exception as e:
            print(f"Gemini API error: {e}")
            raise e
    
    def _parse_llm_response(self, review_data: dict, language: str) -> CodeReview:
        """Parse LLM response into CodeReview object"""
        # Parse line-wise issues
        issues = []
        for issue_data in review_data.get("line_wise_issues", []):
            try:
                severity = ReviewSeverity(issue_data.get("severity", "medium").lower())
                issues.append(CodeIssue(
                    line_number=issue_data.get("line"),
                    issue_type=issue_data.get("type", "general"),
                    severity=severity,
                    description=issue_data.get("issue", ""),
                    suggestion=issue_data.get("fix_suggestion")
                ))
            except (ValueError, TypeError):
                # Skip invalid issues
                continue
        
        return CodeReview(
            readability=review_data.get("readability", "No readability assessment provided"),
            modularity=review_data.get("modularity", "No modularity assessment provided"),
            potential_bugs=review_data.get("potential_bugs", "No bug analysis provided"),
            suggestions=review_data.get("suggestions", []),
            issues=issues,
            overall_score=min(10, max(1, int(review_data.get("overall_score", 5)))),
            summary=review_data.get("summary", f"Code review completed for {language} file")
        )
    
    def _analyze_with_mock(self, content: str, filename: str, language: str) -> CodeReview:
        """Fallback mock analysis when LLM is not available"""
        # Simulate processing time
        time.sleep(random.uniform(0.5, 2.0))
        
        lines = content.split('\n')
        line_count = len(lines)
        
        # Generate mock issues based on content analysis
        issues = self._generate_mock_issues(content, lines)
        
        # Generate mock review based on content
        review = self._generate_mock_review(content, line_count, language, issues)
        
        return review
    
    def _generate_mock_issues(self, content: str, lines: List[str]) -> List[CodeIssue]:
        """Generate mock code issues based on content analysis"""
        issues = []
        
        # Check for common patterns that might indicate issues
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Long lines
            if len(line) > 100:
                issues.append(CodeIssue(
                    line_number=i,
                    issue_type="style",
                    severity=ReviewSeverity.LOW,
                    description=f"Line {i} is too long ({len(line)} characters)",
                    suggestion="Consider breaking this line into multiple lines"
                ))
            
            # Check for division by zero
            if '/' in line and 'n' in line and '=' in line:
                issues.append(CodeIssue(
                    line_number=i,
                    issue_type="bug",
                    severity=ReviewSeverity.CRITICAL,
                    description=f"Potential division by zero on line {i}",
                    suggestion="Add validation to ensure divisor is not zero before division"
                ))
            
            # Check for array bounds issues
            if 'range(' in line and '[' in line:
                issues.append(CodeIssue(
                    line_number=i,
                    issue_type="bug",
                    severity=ReviewSeverity.HIGH,
                    description=f"Potential array index out of bounds on line {i}",
                    suggestion="Verify array size matches range bounds"
                ))
            
            # Check for missing input validation
            if 'input(' in line and 'int(' in line:
                issues.append(CodeIssue(
                    line_number=i,
                    issue_type="security",
                    severity=ReviewSeverity.MEDIUM,
                    description=f"Missing input validation on line {i}",
                    suggestion="Add try-catch block to handle invalid input"
                ))
            
            # Check for global variables
            if line.startswith('global '):
                issues.append(CodeIssue(
                    line_number=i,
                    issue_type="maintainability",
                    severity=ReviewSeverity.MEDIUM,
                    description=f"Use of global variables on line {i}",
                    suggestion="Consider refactoring to avoid global state"
                ))
            
            # Check for print statements
            if line.startswith('print('):
                issues.append(CodeIssue(
                    line_number=i,
                    issue_type="style",
                    severity=ReviewSeverity.LOW,
                    description=f"Use of print statement on line {i}",
                    suggestion="Consider using proper logging instead of print statements"
                ))
            
            # Check for missing docstrings
            if line.startswith('def ') and i < len(lines) - 1:
                next_line = lines[i].strip() if i < len(lines) else ""
                if not next_line.startswith('"""') and not next_line.startswith("'''"):
                    issues.append(CodeIssue(
                        line_number=i,
                        issue_type="documentation",
                        severity=ReviewSeverity.MEDIUM,
                        description=f"Function on line {i} lacks documentation",
                        suggestion="Add a docstring to describe the function's purpose and parameters"
                    ))
            
            # Missing docstrings (for Python)
            if line.startswith('def ') and not any('"""' in prev_line or "'''" in prev_line 
                                                 for prev_line in lines[max(0, i-3):i]):
                issues.append(CodeIssue(
                    line_number=i,
                    issue_type="documentation",
                    severity=ReviewSeverity.MEDIUM,
                    description=f"Function at line {i} lacks documentation",
                    suggestion="Add a docstring to describe the function's purpose"
                ))
            
            # Hardcoded strings (simple check)
            if 'http://' in line or 'https://' in line:
                issues.append(CodeIssue(
                    line_number=i,
                    issue_type="maintainability",
                    severity=ReviewSeverity.MEDIUM,
                    description=f"Hardcoded URL found at line {i}",
                    suggestion="Consider using environment variables or configuration files"
                ))
        
        # Limit issues to avoid overwhelming output
        return issues[:10]
    
    def _generate_mock_review(self, content: str, line_count: int, language: str, issues: List[CodeIssue]) -> CodeReview:
        """Generate mock review based on content analysis"""
        
        # Calculate overall score based on various factors
        score = 8  # Base score
        
        # Deduct points for various issues
        critical_issues = len([i for i in issues if i.severity == ReviewSeverity.CRITICAL])
        high_issues = len([i for i in issues if i.severity == ReviewSeverity.HIGH])
        medium_issues = len([i for i in issues if i.severity == ReviewSeverity.MEDIUM])
        
        score -= critical_issues * 3  # Critical issues heavily impact score
        score -= high_issues * 2      # High issues significantly impact score
        score -= medium_issues * 1    # Medium issues moderately impact score
        
        if line_count > 200:
            score -= 1
        if 'global ' in content:
            score -= 1
        if 'print(' in content:
            score -= 0.5
        
        # Generate contextual feedback
        readability_feedback = self._get_readability_feedback(content, line_count)
        modularity_feedback = self._get_modularity_feedback(content, line_count)
        bugs_feedback = self._get_bugs_feedback(content, issues)
        suggestions = self._get_suggestions(content, line_count, language)
        
        summary = self._generate_summary(score, len(issues), language, critical_issues, high_issues)
        
        return CodeReview(
            readability=readability_feedback,
            modularity=modularity_feedback,
            potential_bugs=bugs_feedback,
            suggestions=suggestions,
            issues=issues,
            overall_score=max(1, min(10, int(score))),
            summary=summary
        )
    
    def _get_readability_feedback(self, content: str, line_count: int) -> str:
        """Generate detailed readability feedback"""
        feedback_parts = []
        
        # Analyze code structure
        if line_count < 50:
            feedback_parts.append("Code is concise and well-structured.")
        elif line_count < 150:
            feedback_parts.append("Code is moderately sized with decent organization.")
        else:
            feedback_parts.append("Code is quite lengthy and could benefit from better modularization.")
        
        # Check for naming conventions
        if any(word in content.lower() for word in ['temp', 'tmp', 'var', 'data']):
            feedback_parts.append("Some variable names could be more descriptive.")
        else:
            feedback_parts.append("Variable naming is generally clear and meaningful.")
        
        # Check for comments
        comment_lines = len([line for line in content.split('\n') if line.strip().startswith('#')])
        if comment_lines == 0:
            feedback_parts.append("No comments found - consider adding inline documentation.")
        elif comment_lines < line_count * 0.1:
            feedback_parts.append("Minimal comments present - more documentation would improve readability.")
        else:
            feedback_parts.append("Good use of comments for code documentation.")
        
        # Check for whitespace and formatting
        if '    ' in content:  # Proper indentation
            feedback_parts.append("Proper indentation and whitespace usage.")
        else:
            feedback_parts.append("Consider improving code formatting and indentation.")
        
        return " ".join(feedback_parts)
    
    def _get_modularity_feedback(self, content: str, line_count: int) -> str:
        """Generate modularity feedback"""
        function_count = content.count('def ') + content.count('function ') + content.count('public ')
        
        if function_count == 0:
            return "No functions detected. Consider breaking code into reusable functions for better modularity."
        elif line_count / max(function_count, 1) > 30:
            return "Functions are quite long. Consider splitting large functions into smaller, more focused ones."
        else:
            return "Good modular structure with appropriately sized functions."
    
    def _get_bugs_feedback(self, content: str, issues: List[CodeIssue]) -> str:
        """Generate detailed potential bugs feedback"""
        critical_issues = [issue for issue in issues if issue.severity == ReviewSeverity.CRITICAL]
        high_issues = [issue for issue in issues if issue.severity == ReviewSeverity.HIGH]
        medium_issues = [issue for issue in issues if issue.severity == ReviewSeverity.MEDIUM]
        
        feedback_parts = []
        
        if critical_issues:
            feedback_parts.append(f"CRITICAL: Found {len(critical_issues)} critical issues that will cause runtime errors or crashes.")
            for issue in critical_issues[:2]:  # Show first 2 critical issues
                feedback_parts.append(f"- Line {issue.line_number}: {issue.description}")
        
        if high_issues:
            feedback_parts.append(f"HIGH PRIORITY: {len(high_issues)} high-priority issues that could cause problems.")
            for issue in high_issues[:2]:  # Show first 2 high issues
                feedback_parts.append(f"- Line {issue.line_number}: {issue.description}")
        
        if medium_issues:
            feedback_parts.append(f"MEDIUM PRIORITY: {len(medium_issues)} medium-priority issues for code quality.")
        
        # Check for common bug patterns
        if '/' in content and 'n' in content:
            feedback_parts.append("Potential division by zero detected - add validation.")
        
        if 'input(' in content and 'int(' in content:
            feedback_parts.append("Missing input validation - add try-catch blocks.")
        
        if 'range(' in content and '[' in content:
            feedback_parts.append("Potential array bounds issues - verify index ranges.")
        
        if not feedback_parts:
            feedback_parts.append("No obvious bugs detected, but consider adding comprehensive input validation and error handling.")
        
        return " ".join(feedback_parts)
    
    def _get_suggestions(self, content: str, line_count: int, language: str) -> List[str]:
        """Generate comprehensive improvement suggestions"""
        suggestions = []
        
        # Code organization suggestions
        if line_count > 100:
            suggestions.append("Consider breaking this file into smaller, focused modules for better maintainability")
        
        # Documentation suggestions
        if 'TODO' not in content and 'FIXME' not in content:
            suggestions.append("Add TODO comments for future improvements and known limitations")
        
        # Language-specific suggestions
        if language == 'Python':
            if 'import' in content:
                suggestions.append("Organize imports according to PEP 8: standard library, third-party, local imports")
            if 'def ' in content and 'type:' not in content:
                suggestions.append("Add type hints to function parameters and return values for better code documentation")
            if 'global ' in content:
                suggestions.append("Refactor to avoid global variables - use dependency injection or return values instead")
        
        # Error handling suggestions
        if 'input(' in content and 'try:' not in content:
            suggestions.append("Add comprehensive input validation with try-catch blocks to handle invalid user input")
        
        if '/' in content and 'if' not in content:
            suggestions.append("Add validation to prevent division by zero and other mathematical errors")
        
        # Code quality suggestions
        if 'print(' in content or 'console.log' in content:
            suggestions.append("Replace print statements with proper logging framework for production code")
        
        # Testing and reliability
        suggestions.append("Add comprehensive unit tests to cover edge cases and error conditions")
        suggestions.append("Implement proper error handling and graceful failure modes")
        
        # Performance suggestions
        if 'for ' in content and 'range(' in content:
            suggestions.append("Consider using list comprehensions or generator expressions for better performance")
        
        return suggestions[:6]  # Limit to 6 most relevant suggestions
    
    def _generate_summary(self, score: int, issue_count: int, language: str, critical_issues: int = 0, high_issues: int = 0) -> str:
        """Generate comprehensive overall summary"""
        summary_parts = []
        
        # Overall quality assessment
        if score >= 8:
            summary_parts.append(f"Excellent {language} code with high quality standards.")
        elif score >= 6:
            summary_parts.append(f"Good {language} code with room for improvement.")
        elif score >= 4:
            summary_parts.append(f"Fair {language} code that needs attention to several issues.")
        else:
            summary_parts.append(f"Poor {language} code requiring significant refactoring.")
        
        # Issue summary
        if issue_count == 0:
            summary_parts.append("No issues detected.")
        else:
            issue_breakdown = []
            if critical_issues > 0:
                issue_breakdown.append(f"{critical_issues} critical")
            if high_issues > 0:
                issue_breakdown.append(f"{high_issues} high-priority")
            if issue_count - critical_issues - high_issues > 0:
                issue_breakdown.append(f"{issue_count - critical_issues - high_issues} medium/low")
            
            summary_parts.append(f"Found {issue_count} total issues: {', '.join(issue_breakdown)}.")
        
        # Priority recommendations
        if critical_issues > 0:
            summary_parts.append("URGENT: Address critical issues immediately to prevent runtime errors.")
        elif high_issues > 0:
            summary_parts.append("PRIORITY: Focus on high-priority issues for better code reliability.")
        elif issue_count > 0:
            summary_parts.append("Consider addressing medium-priority issues for improved code quality.")
        else:
            summary_parts.append("Code is in good shape - consider adding tests and documentation.")
        
        return " ".join(summary_parts)

# Create a global instance
llm_review_service = LLMReviewService()
