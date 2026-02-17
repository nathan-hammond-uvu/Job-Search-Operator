"""Applications blueprint."""
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import select

from persistence.database import db
from persistence.models import Application, ApplicationStatus, JobPosting

bp = Blueprint('applications', __name__)


@bp.route('/')
def index():
    """View all applications."""
    applications = db.session.execute(
        select(Application)
        .join(JobPosting)
        .order_by(Application.updated_at.desc())
    ).scalars().all()
    
    return render_template('applications/index.html', applications=applications)


@bp.route('/<int:app_id>')
def detail(app_id: int):
    """View application details."""
    app = db.session.get(Application, app_id)
    if not app:
        flash('Application not found', 'error')
        return redirect(url_for('applications.index'))
    
    return render_template('applications/detail.html', application=app)


@bp.route('/<int:app_id>/update-status', methods=['POST'])
def update_status(app_id: int):
    """Update application status."""
    app = db.session.get(Application, app_id)
    if not app:
        flash('Application not found', 'error')
        return redirect(url_for('applications.index'))
    
    new_status = request.form.get('status')
    try:
        status_enum = ApplicationStatus[new_status]
    except KeyError:
        flash('Invalid status', 'error')
        return redirect(url_for('applications.detail', app_id=app_id))
    
    old_status = app.status
    app.status = status_enum
    app.updated_at = datetime.now(timezone.utc)
    
    if status_enum == ApplicationStatus.APPLIED and old_status != ApplicationStatus.APPLIED:
        app.applied_at = datetime.now(timezone.utc)
    
    db.session.commit()
    flash(f'Status updated to {status_enum.value}', 'success')
    
    # Redirect back to referer or detail page
    return redirect(request.referrer or url_for('applications.detail', app_id=app_id))


@bp.route('/<int:app_id>/update-notes', methods=['POST'])
def update_notes(app_id: int):
    """Update application notes."""
    app = db.session.get(Application, app_id)
    if not app:
        flash('Application not found', 'error')
        return redirect(url_for('applications.index'))
    
    notes = request.form.get('notes', '').strip()
    app.notes = notes if notes else None
    app.updated_at = datetime.now(timezone.utc)
    
    db.session.commit()
    flash('Notes updated', 'success')
    return redirect(url_for('applications.detail', app_id=app_id))