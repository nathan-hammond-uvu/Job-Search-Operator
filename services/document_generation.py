"""Document generation service for resumes and cover letters."""
import logging
from pathlib import Path
from typing import Optional

from persistence.models import JobPosting, UserProfile, Document, DocumentType
from services.llm_interface import get_llm
from config import Config

logger = logging.getLogger(__name__)


def generate_resume_html(job: JobPosting, profile: UserProfile) -> str:
    """Generate tailored resume HTML."""
    llm = get_llm()
    
    prompt = f"""Generate a professional resume in HTML format tailored for this job.
Use semantic HTML (h1, h2, p, ul, li, strong, em).
Do not include <html>, <head>, or <body> tags - only the content.

Candidate Profile:
Name: {profile.full_name}
Email: {profile.email}
Phone: {profile.phone or 'Not provided'}
Location: {profile.location or 'Not provided'}
Summary: {profile.summary or 'Not provided'}
Experience: {profile.experience or 'Not provided'}
Education: {profile.education or 'Not provided'}
Skills: {profile.skills or 'Not provided'}

Job:
Title: {job.title}
Company: {job.company}
Requirements: {job.requirements or 'Not specified'}

Generate tailored resume HTML:"""
    
    try:
        html = llm.generate(prompt, max_tokens=1500)
        return html.strip()
    except Exception as e:
        logger.error(f"Failed to generate resume for job {job.id}: {e}", exc_info=True)
        return f"<h1>{profile.full_name}</h1><p>Resume generation failed.</p>"


def generate_cover_letter_html(job: JobPosting, profile: UserProfile) -> str:
    """Generate tailored cover letter HTML."""
    llm = get_llm()
    
    prompt = f"""Generate a professional cover letter in HTML format tailored for this job.
Use semantic HTML (p, strong, em).
Do not include <html>, <head>, or <body> tags - only the content.
Keep it concise (3-4 paragraphs).

Candidate Profile:
Name: {profile.full_name}
Summary: {profile.summary or 'Not provided'}
Experience: {profile.experience or 'Not provided'}
Skills: {profile.skills or 'Not provided'}

Job:
Title: {job.title}
Company: {job.company}
Requirements: {job.requirements or 'Not specified'}
Description: {job.description or 'Not specified'}

Generate tailored cover letter HTML:"""
    
    try:
        html = llm.generate(prompt, max_tokens=1000)
        return html.strip()
    except Exception as e:
        logger.error(f"Failed to generate cover letter for job {job.id}: {e}", exc_info=True)
        return f"<p>Dear Hiring Manager,</p><p>Cover letter generation failed.</p>"


def create_document(
    job: JobPosting,
    profile: UserProfile,
    document_type: DocumentType
) -> Document:
    """Create and persist a document."""
    if document_type == DocumentType.RESUME:
        content_html = generate_resume_html(job, profile)
    else:
        content_html = generate_cover_letter_html(job, profile)
    
    doc = Document(
        job_id=job.id,
        document_type=document_type,
        content_html=content_html
    )
    
    return doc


def export_document_html(document: Document, output_path: Path) -> None:
    """Export document as standalone HTML file."""
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{document.document_type.value}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; margin-top: 20px; }}
    </style>
</head>
<body>
    {document.content_html}
</body>
</html>"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_template, encoding='utf-8')
    logger.info(f"Exported document to {output_path}")