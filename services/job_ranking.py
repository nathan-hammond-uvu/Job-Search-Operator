"""Job ranking and analysis service."""
import logging
from typing import Optional

from persistence.models import JobPosting, UserProfile
from services.llm_interface import get_llm

logger = logging.getLogger(__name__)


def generate_job_summary(job: JobPosting) -> str:
    """Generate AI summary for a job posting."""
    llm = get_llm()
    
    prompt = f"""Summarize this job posting in 2-3 sentences. Focus on key responsibilities and requirements.

Title: {job.title}
Company: {job.company}
Location: {job.location or 'Not specified'}
Salary: {job.salary or 'Not specified'}

Description:
{job.description or 'No description'}

Requirements:
{job.requirements or 'No requirements listed'}

Summary:"""
    
    try:
        summary = llm.generate(prompt, max_tokens=200)
        return summary.strip()
    except Exception as e:
        logger.error(f"Failed to generate summary for job {job.id}: {e}", exc_info=True)
        return "Summary generation failed."


def calculate_fit_score(job: JobPosting, profile: Optional[UserProfile]) -> float:
    """Calculate fit score between job and user profile."""
    if not profile:
        return 0.5  # Neutral score if no profile
    
    llm = get_llm()
    
    prompt = f"""Rate how well this job matches the candidate's profile on a scale of 0.0 to 1.0.
Only respond with a number between 0.0 and 1.0.

Job:
Title: {job.title}
Company: {job.company}
Requirements: {job.requirements or 'Not specified'}

Candidate:
Target roles: {profile.target_roles or 'Not specified'}
Skills: {profile.skills or 'Not specified'}
Experience: {profile.experience or 'Not specified'}

Fit score (0.0-1.0):"""
    
    try:
        response = llm.generate(prompt, max_tokens=10).strip()
        # Extract first number from response
        import re
        match = re.search(r'0\.\d+|1\.0|0|1', response)
        if match:
            score = float(match.group())
            return max(0.0, min(1.0, score))
        return 0.5
    except Exception as e:
        logger.error(f"Failed to calculate fit score for job {job.id}: {e}", exc_info=True)
        return 0.5


def rank_jobs(jobs: list[JobPosting], profile: Optional[UserProfile]) -> list[JobPosting]:
    """Rank jobs by fit score."""
    for job in jobs:
        if job.summary is None:
            job.summary = generate_job_summary(job)
        if job.fit_score is None:
            job.fit_score = calculate_fit_score(job, profile)
    
    # Sort by fit score descending
    return sorted(jobs, key=lambda j: j.fit_score or 0.0, reverse=True)