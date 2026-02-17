"""Cleanup tasks for old data."""
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, delete

from persistence.database import db
from persistence.models import JobPosting, JobStatus
from config import Config

logger = logging.getLogger(__name__)


def cleanup_recycle_bin() -> int:
    """Delete jobs in recycle bin older than threshold."""
    threshold = datetime.now(timezone.utc) - timedelta(days=Config.RECYCLE_BIN_DAYS)
    
    result = db.session.execute(
        delete(JobPosting).where(
            JobPosting.status == JobStatus.RECYCLE_BIN,
            JobPosting.moved_to_recycle_at < threshold
        )
    )
    
    db.session.commit()
    deleted_count = result.rowcount
    
    logger.info(f"Deleted {deleted_count} jobs from recycle bin")
    return deleted_count