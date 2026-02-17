"""Email parsing and classification service."""
import email
import imaplib
import logging
from datetime import datetime, timezone
from typing import Optional

from persistence.models import EmailMessage, ApplicationStatus
from services.llm_interface import get_llm
from config import Config

logger = logging.getLogger(__name__)


def connect_to_imap() -> Optional[imaplib.IMAP4_SSL]:
    """Connect to IMAP server."""
    if not Config.EMAIL_SCANNING_ENABLED:
        return None
    
    if not all([Config.IMAP_SERVER, Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD]):
        logger.warning("Email scanning enabled but credentials not configured")
        return None
    
    try:
        mail = imaplib.IMAP4_SSL(Config.IMAP_SERVER, Config.IMAP_PORT)
        mail.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
        logger.info("Connected to IMAP server")
        return mail
    except Exception as e:
        logger.error(f"Failed to connect to IMAP: {e}", exc_info=True)
        return None


def fetch_unread_messages(mail: imaplib.IMAP4_SSL) -> list[EmailMessage]:
    """Fetch unread messages from inbox."""
    messages = []
    
    try:
        mail.select('INBOX')
        status, data = mail.search(None, 'UNSEEN')
        
        if status != 'OK':
            return messages
        
        for num in data[0].split():
            status, msg_data = mail.fetch(num, '(RFC822)')
            
            if status != 'OK':
                continue
            
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            message_id = msg.get('Message-ID', '')
            sender = msg.get('From', '')
            subject = msg.get('Subject', '')
            date_str = msg.get('Date', '')
            
            # Parse body
            body = ''
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            # Parse date
            received_at = datetime.now(timezone.utc)
            try:
                received_at = email.utils.parsedate_to_datetime(date_str)
            except:
                pass
            
            email_msg = EmailMessage(
                message_id=message_id,
                sender=sender,
                subject=subject,
                body=body,
                received_at=received_at
            )
            
            classify_email(email_msg)
            messages.append(email_msg)
    
    except Exception as e:
        logger.error(f"Error fetching emails: {e}", exc_info=True)
    
    return messages


def classify_email(email_msg: EmailMessage) -> None:
    """Classify email and suggest application status update."""
    llm = get_llm()
    
    prompt = f"""Analyze this email and determine:
1. Is it an auto-reply? (yes/no)
2. Is it a recruiter response? (yes/no)
3. What application status does it suggest? (APPLIED, WAITING_FOR_RESPONSE, INTERVIEW_REQUESTED, DENIED, OFFER_SENT, or NONE)

Email:
From: {email_msg.sender}
Subject: {email_msg.subject}
Body: {email_msg.body[:500]}

Respond in this exact format:
auto_reply: yes/no
recruiter_response: yes/no
suggested_status: STATUS
"""
    
    try:
        response = llm.generate(prompt, max_tokens=100)
        
        lines = response.strip().lower().split('\n')
        for line in lines:
            if 'auto_reply:' in line:
                email_msg.is_auto_reply = 'yes' in line
            elif 'recruiter_response:' in line:
                email_msg.is_recruiter_response = 'yes' in line
            elif 'suggested_status:' in line:
                for status in ApplicationStatus:
                    if status.value.lower() in line:
                        email_msg.suggested_status = status.value
                        break
    
    except Exception as e:
        logger.error(f"Failed to classify email: {e}", exc_info=True)