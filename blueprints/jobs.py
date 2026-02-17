"""Jobs blueprint."""
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import select

from persistence.database import db
from persistence.models import JobPosting, JobStatus, Application, ApplicationStatus

bp = Blueprint('jobs', __name__)


@bp.route('/pending')
def pending():
    """View pending jobs."""
    jobs = db.session.execute(
        select(JobPosting)
        .where(JobPosting.status == JobStatus.PENDING_REVIEW)
        .order_by(JobPosting.fit_score.desc().nullslast(), JobPosting.discovered_at.desc())
    ).scalars().all()
    
    return render_template('jobs/pending.html', jobs=jobs)


@bp.route('/approved')
def approved():
    """View approved jobs."""
    jobs = db.session.execute(
        select(JobPosting)
        .where(JobPosting.status == JobStatus.APPROVED)
        .order_by(JobPosting.reviewed_at.desc())
    ).scalars().all()
    
    return render_template('jobs/approved.html', jobs=jobs)


@bp.route('/recycle-bin')
def recycle_bin():
    """View recycle bin."""
    jobs = db.session.execute(
        select(JobPosting)
        .where(JobPosting.status == JobStatus.RECYCLE_BIN)
        .order_by(JobPosting.moved_to_recycle_at.desc())
    ).scalars().all()
    
    return render_template('jobs/recycle_bin.html', jobs=jobs)


@bp.route('/<int:job_id>')
def detail(job_id: int):
    """View job details."""
    job = db.session.get(JobPosting, job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('dashboard.index'))
    
    return render_template('jobs/detail.html', job=job)


@bp.route('/<int:job_id>/approve', methods=['POST'])
def approve(job_id: int):
    """Approve a job."""
    job = db.session.get(JobPosting, job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('jobs.pending'))
    
    job.status = JobStatus.APPROVED
    job.reviewed_at = datetime.now(timezone.utc)
    
    # Create application record
    application = Application(
        job_id=job.id,
        status=ApplicationStatus.NEED_TO_APPLY
    )
    db.session.add(application)
    
    db.session.commit()
    flash(f'Job approved: {job.title}', 'success')
    return redirect(url_for('jobs.pending'))


@bp.route('/<int:job_id>/deny', methods=['POST'])
def deny(job_id: int):
    """Deny a job (move to recycle bin)."""
    job = db.session.get(JobPosting, job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('jobs.pending'))
    
    job.status = JobStatus.RECYCLE_BIN
    job.moved_to_recycle_at = datetime.now(timezone.utc)
    
    db.session.commit()
    flash(f'Job moved to recycle bin: {job.title}', 'info')
    return redirect(url_for('jobs.pending'))


@bp.route('/<int:job_id>/restore', methods=['POST'])
def restore(job_id: int):
    """Restore a job from recycle bin."""
    job = db.session.get(JobPosting, job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('jobs.recycle_bin'))
    
    job.status = JobStatus.PENDING_REVIEW
    job.moved_to_recycle_at = None
    
    db.session.commit()
    flash(f'Job restored: {job.title}', 'success')
    return redirect(url_for('jobs.recycle_bin'))


@bp.route('/<int:job_id>/delete', methods=['POST'])
def delete(job_id: int):
    """Permanently delete a job."""
    job = db.session.get(JobPosting, job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('jobs.recycle_bin'))
    
    db.session.delete(job)
    db.session.commit()
    flash(f'Job permanently deleted: {job.title}', 'warning')
    return redirect(url_for('jobs.recycle_bin'))