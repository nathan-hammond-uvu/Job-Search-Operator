"""Documents blueprint."""
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from sqlalchemy import select

from persistence.database import db
from persistence.models import JobPosting, Document, DocumentType, UserProfile
from services.document_generation import create_document, export_document_html
from config import Config

bp = Blueprint('documents', __name__)


@bp.route('/job/<int:job_id>')
def list_documents(job_id: int):
    """List documents for a job."""
    job = db.session.get(JobPosting, job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('dashboard.index'))
    
    documents = db.session.execute(
        select(Document).where(Document.job_id == job_id).order_by(Document.created_at.desc())
    ).scalars().all()
    
    return render_template('documents/list.html', job=job, documents=documents)


@bp.route('/<int:doc_id>')
def view(doc_id: int):
    """View document."""
    doc = db.session.get(Document, doc_id)
    if not doc:
        flash('Document not found', 'error')
        return redirect(url_for('dashboard.index'))
    
    return render_template('documents/view.html', document=doc)


@bp.route('/generate/<int:job_id>/<doc_type>', methods=['POST'])
def generate(job_id: int, doc_type: str):
    """Generate a document for a job."""
    job = db.session.get(JobPosting, job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('dashboard.index'))
    
    profile = db.session.execute(select(UserProfile)).scalar_one_or_none()
    if not profile:
        flash('Please create a user profile first', 'warning')
        return redirect(url_for('dashboard.index'))
    
    try:
        document_type = DocumentType[doc_type.upper()]
    except KeyError:
        flash('Invalid document type', 'error')
        return redirect(url_for('documents.list_documents', job_id=job_id))
    
    doc = create_document(job, profile, document_type)
    db.session.add(doc)
    db.session.commit()
    
    flash(f'{document_type.value.title()} generated successfully', 'success')
    return redirect(url_for('documents.view', doc_id=doc.id))


@bp.route('/<int:doc_id>/export')
def export(doc_id: int):
    """Export document as HTML file."""
    doc = db.session.get(Document, doc_id)
    if not doc:
        flash('Document not found', 'error')
        return redirect(url_for('dashboard.index'))
    
    filename = f"{doc.document_type.value.lower()}_{doc.job_id}_{doc.id}.html"
    output_path = Config.DOCUMENTS_DIR / filename
    
    export_document_html(doc, output_path)
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name=filename
    )


@bp.route('/<int:doc_id>/regenerate', methods=['POST'])
def regenerate(doc_id: int):
    """Regenerate a document."""
    doc = db.session.get(Document, doc_id)
    if not doc:
        flash('Document not found', 'error')
        return redirect(url_for('dashboard.index'))
    
    profile = db.session.execute(select(UserProfile)).scalar_one_or_none()
    if not profile:
        flash('Please create a user profile first', 'warning')
        return redirect(url_for('dashboard.index'))
    
    # Delete old document
    job = doc.job
    doc_type = doc.document_type
    db.session.delete(doc)
    db.session.commit()
    
    # Generate new one
    new_doc = create_document(job, profile, doc_type)
    db.session.add(new_doc)
    db.session.commit()
    
    flash(f'{doc_type.value.title()} regenerated successfully', 'success')
    return redirect(url_for('documents.view', doc_id=new_doc.id))