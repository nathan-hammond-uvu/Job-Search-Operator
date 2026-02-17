"""Email scanning blueprint."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import select

from persistence.database import db
from persistence.models import EmailMessage, Application
from services.email_parser import connect_to_imap, fetch_unread_messages
from config import Config

bp = Blueprint('email', __name__)


@bp.route('/')
def index():
    """View email messages."""
    if not Config.EMAIL_SCANNING_ENABLED:
        flash('Email scanning is disabled', 'info')
    
    messages = db.session.execute(
        select(EmailMessage).order_by(EmailMessage.received_at.desc()).limit(50)
    ).scalars().all()
    
    return render_template('email/index.html', messages=messages, scanning_enabled=Config.EMAIL_SCANNING_ENABLED)


@bp.route('/scan', methods=['POST'])
def scan():
    """Scan for new emails."""
    if not Config.EMAIL_SCANNING_ENABLED:
        flash('Email scanning is disabled', 'warning')
        return redirect(url_for('email.index'))
    
    mail = connect_to_imap()
    if not mail:
        flash('Failed to connect to email server', 'error')
        return redirect(url_for('email.index'))
    
    try:
        messages = fetch_unread_messages(mail)
        
        for msg in messages:
            # Check if message already exists
            existing = db.session.execute(
                select(EmailMessage).where(EmailMessage.message_id == msg.message_id)
            ).scalar_one_or_none()
            
            if not existing:
                db.session.add(msg)
        
        db.session.commit()
        flash(f'Scanned and found {len(messages)} new messages', 'success')
    
    finally:
        mail.logout()
    
    return redirect(url_for('email.index'))


@bp.route('/<int:msg_id>/apply-suggestion', methods=['POST'])
def apply_suggestion(msg_id: int):
    """Apply suggested status update from email."""
    msg = db.session.get(EmailMessage, msg_id)
    if not msg:
        flash('Email not found', 'error')
        return redirect(url_for('email.index'))
    
    if not msg.application_id or not msg.suggested_status:
        flash('No suggestion available', 'warning')
        return redirect(url_for('email.index'))
    
    app = db.session.get(Application, msg.application_id)
    if not app:
        flash('Application not found', 'error')
        return redirect(url_for('email.index'))
    
    from persistence.models import ApplicationStatus
    try:
        new_status = ApplicationStatus[msg.suggested_status]
        app.status = new_status
        db.session.commit()
        flash(f'Application status updated to {new_status.value}', 'success')
    except KeyError:
        flash('Invalid status', 'error')
    
    return redirect(url_for('email.index'))