import os
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

class PDFGenerator:
    """Service for generating PDF reports from code review data"""
    
    def __init__(self):
        self.reports_dir = "reports"
        self._ensure_reports_dir()
    
    def _ensure_reports_dir(self):
        """Ensure the reports directory exists"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def generate_pdf(self, review_data: Dict[str, Any], filename: str) -> str:
        """
        Generate a PDF report from review data
        Returns the path to the generated PDF file
        """
        # Create PDF filename
        base_filename = os.path.splitext(filename)[0]
        pdf_filename = f"{base_filename}_review_report.pdf"
        pdf_path = os.path.join(self.reports_dir, pdf_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkgreen
        )
        
        # Build PDF content
        story = []
        
        # Title
        story.append(Paragraph("Code Review Report", title_style))
        story.append(Spacer(1, 20))
        
        # File information
        story.append(Paragraph("File Information", heading_style))
        file_info_data = [
            ["File Name:", review_data.get("filename", "Unknown")],
            ["Overall Score:", f"{review_data.get('overall_score', 0)}/10"],
            ["Total Issues:", str(review_data.get("total_issues", 0))],
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        file_info_table = Table(file_info_data, colWidths=[2*inch, 4*inch])
        file_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(file_info_table)
        story.append(Spacer(1, 20))
        
        # Summary
        story.append(Paragraph("Summary", heading_style))
        summary_text = review_data.get("summary", "No summary available.")
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Quality Metrics
        quality_metrics = review_data.get("quality_metrics", {})
        if quality_metrics:
            story.append(Paragraph("Quality Metrics", heading_style))
            metrics_data = [
                ["Metric", "Score"],
                ["Complexity Score", f"{quality_metrics.get('complexity_score', 0)}/10"],
                ["Maintainability Score", f"{quality_metrics.get('maintainability_score', 0)}/10"],
                ["Suggestions Count", str(quality_metrics.get('suggestions_count', 0))],
                ["Issues per Suggestion", str(quality_metrics.get('issues_per_suggestion', 0))]
            ]
            
            metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metrics_table)
            story.append(Spacer(1, 20))
        
        # Detailed Analysis
        story.append(Paragraph("Detailed Analysis", heading_style))
        
        # Readability
        story.append(Paragraph("Readability", subheading_style))
        story.append(Paragraph(review_data.get("readability", "No readability assessment available."), styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Modularity
        story.append(Paragraph("Modularity", subheading_style))
        story.append(Paragraph(review_data.get("modularity", "No modularity assessment available."), styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Potential Bugs
        story.append(Paragraph("Potential Bugs", subheading_style))
        story.append(Paragraph(review_data.get("potential_bugs", "No bug analysis available."), styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Suggestions
        suggestions = review_data.get("suggestions", [])
        if suggestions:
            story.append(Paragraph("Improvement Suggestions", heading_style))
            for i, suggestion in enumerate(suggestions, 1):
                story.append(Paragraph(f"{i}. {suggestion}", styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Issues by Severity
        issues_by_severity = review_data.get("issues_by_severity", {})
        if any(issues_by_severity.values()):
            story.append(Paragraph("Issues by Severity", heading_style))
            
            for severity in ["critical", "high", "medium", "low"]:
                issues = issues_by_severity.get(severity, [])
                if issues:
                    story.append(Paragraph(f"{severity.title()} Issues ({len(issues)})", subheading_style))
                    
                    # Create issues table
                    issues_data = [["Line", "Type", "Description", "Suggestion"]]
                    for issue in issues:
                        issues_data.append([
                            str(issue.get("line_number", "N/A")),
                            issue.get("type", "Unknown"),
                            issue.get("description", "No description"),
                            issue.get("suggestion", "No suggestion")
                        ])
                    
                    issues_table = Table(issues_data, colWidths=[0.8*inch, 1.2*inch, 2.5*inch, 2.5*inch])
                    issues_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkred if severity == "critical" else 
                         colors.darkorange if severity == "high" else 
                         colors.darkyellow if severity == "medium" else colors.darkgreen),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    
                    story.append(issues_table)
                    story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        
        return pdf_path

# Create a singleton instance
pdf_generator = PDFGenerator()
