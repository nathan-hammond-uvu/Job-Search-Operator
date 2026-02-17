"""Dashboard blueprint."""
from flask import Blueprint, render_template
from sqlalchemy import select, func

from persistence.database import db
from persistence.models import JobPosting, JobStatus, Application, ApplicationStatus

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    """Main dashboard view."""
    
    # Count jobs by status
    pending_count = db.session.execute(
        select(func.count()).select_from(JobPosting).where(JobPosting.status == JobStatus.PENDING_REVIEW)
    ).scalar()
    
    approved_count = db.session.execute(
        select(func.count()).select_from(JobPosting).where(JobPosting.status == JobStatus.APPROVED)
    ).scalar()
    
    # Count applications by status
    need_to_apply_count = db.session.execute(
        select(func.count()).select_from(Application).where(Application.status == ApplicationStatus.NEED_TO_APPLY)
    ).scalar()
    
    applied_count = db.session.execute(
        select(func.count()).select_from(Application).where(Application.status == ApplicationStatus.APPLIED)
    ).scalar()
    
    waiting_count = db.session.execute(
        select(func.count()).select_from(Application).where(Application.status == ApplicationStatus.WAITING_FOR_RESPONSE)
    ).scalar()
    
    interview_count = db.session.execute(
        select(func.count()).select_from(Application).where(Application.status == ApplicationStatus.INTERVIEW_REQUESTED)
    ).scalar()
    
    # Get recent pending jobs
    recent_pending = db.session.execute(
        select(JobPosting)
        .where(JobPosting.status == JobStatus.PENDING_REVIEW)
        .order_by(JobPosting.fit_score.desc().nullslast(), JobPosting.discovered_at.desc())
        .limit(5)
    ).scalars().all()
    
    return render_template(
        'dashboard.html',
        pending_count=pending_count,
        approved_count=approved_count,
        need_to_apply_count=need_to_apply_count,
        applied_count=applied_count,
        waiting_count=waiting_count,
        interview_count=interview_count,
        recent_pending=recent_pending
    )