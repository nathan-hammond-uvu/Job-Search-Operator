#!/usr/bin/env python3
"""
Local Job Search Agent
A human-in-the-loop Flask application for managing job searches locally.
"""

import logging
import os
from pathlib import Path

from flask import Flask

from persistence.database import db

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_path: str | None = None) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///job_search.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=Path('data/uploads'),
        TEMPLATES_AUTO_RELOAD=True,
    )
    
    if config_path:
        app.config.from_pyfile(config_path)
    
    # Ensure directories exist
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path('data/documents').mkdir(parents=True, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from blueprints.dashboard import bp as dashboard_bp
    from blueprints.jobs import bp as jobs_bp
    from blueprints.documents import bp as documents_bp
    from blueprints.applications import bp as applications_bp
    from blueprints.email import bp as email_bp
    from blueprints.profile import bp as profile_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(applications_bp, url_prefix='/applications')
    app.register_blueprint(email_bp, url_prefix='/email')
    app.register_blueprint(profile_bp)
    
    # Create tables
    with app.app_context():
        from persistence import models  # noqa
        db.create_all()
        logger.info("Database tables created")
    
    # Run daily orchestrator on startup
    with app.app_context():
        from agent.daily_orchestrator import run_daily_tasks
        try:
            run_daily_tasks()
        except Exception as e:
            logger.error(f"Daily orchestrator failed: {e}", exc_info=True)
    
    logger.info("Job Search Agent started")
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)