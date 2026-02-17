"""User profile blueprint."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import select

from persistence.database import db
from persistence.models import UserProfile
from services.linkedin_scraper import extract_linkedin_profile

bp = Blueprint('profile', __name__)


@bp.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    """Create or update the user profile."""
    profile = db.session.execute(select(UserProfile)).scalar_one_or_none()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()

        if not full_name or not email:
            flash('Full name and email are required.', 'error')
            return render_template('profile.html', profile=profile)

        phone = request.form.get('phone') or None
        location = request.form.get('location') or None
        summary = request.form.get('summary') or None
        experience = request.form.get('experience') or None
        education = request.form.get('education') or None
        skills = request.form.get('skills') or None
        target_roles = request.form.get('target_roles') or None
        target_locations = request.form.get('target_locations') or None

        salary_min_raw = request.form.get('salary_min') or ''
        salary_min = int(salary_min_raw) if salary_min_raw.strip() else None
        remote_only = request.form.get('remote_only') == 'on'

        if profile is None:
            profile = UserProfile(
                full_name=full_name,
                email=email,
                phone=phone,
                location=location,
                summary=summary,
                experience=experience,
                education=education,
                skills=skills,
                target_roles=target_roles,
                target_locations=target_locations,
                salary_min=salary_min,
                remote_only=remote_only,
            )
            db.session.add(profile)
        else:
            profile.full_name = full_name
            profile.email = email
            profile.phone = phone
            profile.location = location
            profile.summary = summary
            profile.experience = experience
            profile.education = education
            profile.skills = skills
            profile.target_roles = target_roles
            profile.target_locations = target_locations
            profile.salary_min = salary_min
            profile.remote_only = remote_only

        db.session.commit()
        flash('Profile saved.', 'success')
        return redirect(url_for('profile.edit_profile'))

    return render_template('profile.html', profile=profile)


@bp.route('/profile/import-linkedin', methods=['POST'])
def import_linkedin():
    """Import profile data from LinkedIn URL via AJAX."""
    linkedin_url = request.form.get('linkedin_url', '').strip()
    
    if not linkedin_url:
        return jsonify({'success': False, 'error': 'LinkedIn URL is required'}), 400
    
    profile_data = extract_linkedin_profile(linkedin_url)
    
    if not profile_data:
        return jsonify({'success': False, 'error': 'Failed to extract data from LinkedIn URL. Make sure the profile is public.'}), 400
    
    return jsonify({
        'success': True,
        'data': {
            'full_name': profile_data.full_name or '',
            'email': profile_data.email or '',
            'phone': profile_data.phone or '',
            'location': profile_data.location or '',
            'summary': profile_data.summary or '',
            'experience': profile_data.experience or '',
            'education': profile_data.education or '',
            'skills': profile_data.skills or '',
        }
    })
