"""Job discovery service."""
import hashlib
import logging
from typing import Iterator
from datetime import datetime, timezone

from persistence.models import JobPosting, JobStatus

logger = logging.getLogger(__name__)


class JobSource:
    """Base class for job sources."""
    
    def discover(self) -> Iterator[dict]:
        """Yield discovered jobs as dicts."""
        raise NotImplementedError


class MockJobSource(JobSource):
    """Mock job source for testing."""
    
    def discover(self) -> Iterator[dict]:
        """Yield mock jobs."""
        mock_jobs = [
            {
                "title": "Senior Python Engineer",
                "company": "Acme Corp",
                "location": "Remote",
                "salary": "$150k - $180k",
                "url": "https://example.com/job1",
                "description": "We are looking for a senior Python engineer...",
                "requirements": "5+ years Python, Flask, PostgreSQL"
            },
            {
                "title": "Full Stack Developer",
                "company": "Tech Startup",
                "location": "San Francisco, CA",
                "salary": "$130k - $160k",
                "url": "https://example.com/job2",
                "description": "Join our fast-growing startup...",
                "requirements": "Python, React, AWS experience"
            },
            {
                "title": "Backend Engineer",
                "company": "Enterprise Solutions Inc",
                "location": "New York, NY",
                "salary": "$140k - $170k",
                "url": "https://example.com/job3",
                "description": "Build scalable backend systems...",
                "requirements": "Python, microservices, Docker"
            }
        ]
        
        for job in mock_jobs:
            yield job


def generate_external_id(title: str, company: str, url: str) -> str:
    """Generate unique external ID for a job."""
    content = f"{title}|{company}|{url}"
    return hashlib.sha256(content.encode()).hexdigest()[:32]


def discover_jobs(sources: list[JobSource]) -> list[JobPosting]:
    """Discover jobs from all sources and return new JobPosting objects."""
    discovered = []
    
    for source in sources:
        try:
            for job_data in source.discover():
                external_id = generate_external_id(
                    job_data["title"],
                    job_data["company"],
                    job_data["url"]
                )
                
                job = JobPosting(
                    external_id=external_id,
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data.get("location"),
                    salary=job_data.get("salary"),
                    url=job_data["url"],
                    description=job_data.get("description"),
                    requirements=job_data.get("requirements"),
                    status=JobStatus.PENDING_REVIEW,
                    discovered_at=datetime.now(timezone.utc)
                )
                
                discovered.append(job)
                logger.info(f"Discovered job: {job.title} at {job.company}")
        
        except Exception as e:
            logger.error(f"Error discovering jobs from {source.__class__.__name__}: {e}", exc_info=True)
    
    return discovered