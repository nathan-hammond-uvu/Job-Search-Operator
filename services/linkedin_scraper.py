"""LinkedIn profile scraper."""
import logging
from typing import Optional
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class LinkedInProfileData:
    """Data extracted from a LinkedIn profile."""
    
    def __init__(self):
        self.full_name: Optional[str] = None
        self.email: Optional[str] = None
        self.phone: Optional[str] = None
        self.location: Optional[str] = None
        self.summary: Optional[str] = None
        self.experience: Optional[str] = None
        self.education: Optional[str] = None
        self.skills: Optional[str] = None


def extract_linkedin_profile(url: str) -> Optional[LinkedInProfileData]:
    """
    Extract profile data from a LinkedIn profile URL using public data scraping.
    
    Note: LinkedIn's terms of service restrict scraping. This uses a basic
    approach that may not work for private profiles. Consider using the
    official LinkedIn API for production use.
    
    Args:
        url: LinkedIn profile URL
        
    Returns:
        LinkedInProfileData if successful, None otherwise
    """
    
    # Validate URL
    if not url or "linkedin.com" not in url.lower():
        logger.warning(f"Invalid LinkedIn URL: {url}")
        return None
    
    try:
        # Add public view parameter to increase chance of getting data
        if "?" not in url:
            url = url.rstrip("/") + "/"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Attempt to fetch the page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        profile_data = LinkedInProfileData()
        
        # Extract full name from title or heading
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.get_text()
            # LinkedIn titles typically follow "Name | Title | LinkedIn"
            if "|" in title_text:
                profile_data.full_name = title_text.split("|")[0].strip()
        
        # Try to extract from h1 or main heading
        if not profile_data.full_name:
            h1 = soup.find("h1")
            if h1:
                profile_data.full_name = h1.get_text().strip()
        
        # Look for summary/about section
        about_sections = soup.find_all("section")
        for section in about_sections:
            section_text = section.get_text()
            if "about" in section_text.lower() or "summary" in section_text.lower():
                profile_data.summary = section_text.strip()
                break
        
        logger.info(f"Successfully extracted LinkedIn profile data")
        
        return profile_data
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch LinkedIn profile: {e}")
        return None
    except Exception as e:
        logger.error(f"Error parsing LinkedIn profile: {e}")
        return None
