"""Database models for the job search agent."""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.database import db


class JobStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    RECYCLE_BIN = "RECYCLE_BIN"


class ApplicationStatus(str, Enum):
    NEED_TO_APPLY = "NEED_TO_APPLY"
    APPLIED = "APPLIED"
    WAITING_FOR_RESPONSE = "WAITING_FOR_RESPONSE"
    INTERVIEW_REQUESTED = "INTERVIEW_REQUESTED"
    DENIED = "DENIED"
    OFFER_SENT = "OFFER_SENT"


class DocumentType(str, Enum):
    RESUME = "RESUME"
    COVER_LETTER = "COVER_LETTER"


class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Resume base content
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    education: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Job search preferences
    target_roles: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_locations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    remote_only: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


class JobPosting(db.Model):
    __tablename__ = 'job_posting'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    salary: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # AI-generated
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fit_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status tracking
    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus, native_enum=False),
        default=JobStatus.PENDING_REVIEW,
        nullable=False,
        index=True
    )
    
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    moved_to_recycle_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    application: Mapped[Optional["Application"]] = relationship("Application", back_populates="job", uselist=False)
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="job")


class Application(db.Model):
    __tablename__ = 'application'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey('job_posting.id'), nullable=False, unique=True)
    
    status: Mapped[ApplicationStatus] = mapped_column(
        SQLEnum(ApplicationStatus, native_enum=False),
        default=ApplicationStatus.NEED_TO_APPLY,
        nullable=False,
        index=True
    )
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    job: Mapped["JobPosting"] = relationship("JobPosting", back_populates="application")


class Document(db.Model):
    __tablename__ = 'document'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey('job_posting.id'), nullable=False)
    
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType, native_enum=False),
        nullable=False
    )
    
    content_html: Mapped[str] = mapped_column(Text, nullable=False)
    content_markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    job: Mapped["JobPosting"] = relationship("JobPosting", back_populates="documents")


class EmailMessage(db.Model):
    __tablename__ = 'email_message'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Classification
    is_auto_reply: Mapped[bool] = mapped_column(Boolean, default=False)
    is_recruiter_response: Mapped[bool] = mapped_column(Boolean, default=False)
    suggested_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Optional link to application
    application_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('application.id'), nullable=True)