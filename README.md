# Job Search Agent

A local, free, human-in-the-loop job search automation system.

## Features

- **Job Discovery & Ranking**: Automatically discover jobs and rank by fit score
- **Human Approval**: Review and approve/deny jobs before taking action
- **Document Generation**: Generate tailored resumes and cover letters using local LLM
- **Application Tracking**: Track application status through the entire pipeline
- **Email Scanning** (Optional): Read-only inbox scanning for recruiter responses
- **Recycle Bin**: Safe deletion with 7-day auto-cleanup

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Architecture
```
job_search_agent/
├── job_search_agent.py       # Flask app factory
├── config.py                  # Configuration
├── requirements.txt
├── .env
├── persistence/
│   └── models.py             # SQLAlchemy models
├── services/
│   ├── llm_interface.py      # LLM abstraction
│   ├── job_discovery.py      # Job discovery
│   ├── job_ranking.py        # Ranking & analysis
│   ├── document_generation.py # Resume/cover letter
│   └── email_parser.py       # Email scanning
├── agent/
│   ├── daily_orchestrator.py # Daily tasks
│   └── cleanup_tasks.py      # Cleanup jobs
├── blueprints/
│   ├── dashboard.py          # Main dashboard
│   ├── jobs.py               # Job management
│   ├── documents.py          # Document generation
│   ├── applications.py       # Application tracking
│   └── email.py              # Email scanner
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── jobs/
    ├── documents/
    ├── applications/
    └── email/
```