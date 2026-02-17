"""Daily orchestration tasks."""
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from persistence.database import db
from persistence.models import JobPosting, JobStatus, UserProfile
from services.job_discovery import discover_jobs, MockJobSource
from services.job_ranking import rank_jobs

logger = logging.getLogger(__name__)


def run_daily_tasks() -> None:
    """Run daily orchestration tasks."""
    logger.info("Starting daily orchestration tasks")
    
    # Discover new jobs
    discover_new_jobs()
    
    # Rank pending jobs
    rank_pending_jobs()
    
    logger.info("Daily orchestration tasks completed")


def discover_new_jobs() -> None:
    """Discover and persist new jobs."""
    logger.info("Discovering new jobs")
    
    # Use mock source for now
    sources = [MockJobSource()]
    discovered = discover_jobs(sources)
    
    added_count = 0
    for job in discovered:
        # Check if job already exists
        existing = db.session.execute(
            select(JobPosting).where(JobPosting.external_id == job.external_id)
        ).scalar_one_or_none()
        
        if existing:
            logger.debug(f"Job already exists: {job.external_id}")
            continue
        
        db.session.add(job)
        added_count += 1
    
    db.session.commit()
    logger.info(f"Added {added_count} new jobs")


def rank_pending_jobs() -> None:
    """Rank all pending jobs."""
    logger.info("Ranking pending jobs")
    
    profile = db.session.execute(select(UserProfile)).scalar_one_or_none()
    
    pending_jobs = db.session.execute(
        select(JobPosting).where(JobPosting.status == JobStatus.PENDING_REVIEW)
    ).scalars().all()
    
    if not pending_jobs:
        logger.info("No pending jobs to rank")
        return
    
    ranked = rank_jobs(list(pending_jobs), profile)
    
    for job in ranked:
        db.session.add(job)
    
    db.session.commit()
    logger.info(f"Ranked {len(ranked)} jobs")