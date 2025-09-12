"""
API Integration Module
Handles communication with the Node.js backend
"""

import requests
import streamlit as st
import os
from typing import List, Dict, Any, Optional

# Get API base URL from environment
API_BASE = os.getenv("API_BASE", "http://localhost:5000")

def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
    """
    Make a request to the backend API
    
    Args:
        endpoint: API endpoint (e.g., "/api/donors")
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request payload for POST/PUT requests
    
    Returns:
        API response data or None if error
    """
    try:
        url = f"{API_BASE}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.ConnectionError:
        st.error("❌ Unable to connect to backend API. Please check if the server is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None

def get_donors() -> Optional[List[Dict]]:
    """Get list of all donors"""
    return make_api_request("/api/donors")

def get_donor_profile(donor_id: str) -> Optional[Dict]:
    """Get detailed donor profile"""
    return make_api_request(f"/api/donors/{donor_id}")

def get_pipeline_data() -> Optional[List[Dict]]:
    """Get fundraising pipeline data"""
    return make_api_request("/api/pipeline")

def get_templates() -> Optional[List[Dict]]:
    """Get email templates"""
    return make_api_request("/api/templates")

def get_activity_log() -> Optional[List[Dict]]:
    """Get activity log entries"""
    return make_api_request("/api/activities")

def get_proposals() -> Optional[List[Dict]]:
    """Get proposals data"""
    return make_api_request("/api/proposals")

def get_alerts() -> Optional[List[Dict]]:
    """Get alerts data"""
    return make_api_request("/api/alerts")

def send_email(recipient: str, subject: str, body: str) -> bool:
    """
    Send an email through the backend
    
    Args:
        recipient: Email recipient
        subject: Email subject
        body: Email body content
    
    Returns:
        True if successful, False otherwise
    """
    data = {
        "recipient": recipient,
        "subject": subject,
        "body": body
    }
    
    response = make_api_request("/api/email/send", method="POST", data=data)
    return response is not None

def log_activity(activity_type: str, donor_id: str, details: str) -> bool:
    """
    Log an activity
    
    Args:
        activity_type: Type of activity (email, call, meeting, etc.)
        donor_id: ID of the donor involved
        details: Activity details
    
    Returns:
        True if successful, False otherwise
    """
    data = {
        "type": activity_type,
        "donor_id": donor_id,
        "details": details,
        "timestamp": None  # Backend will set current timestamp
    }
    
    response = make_api_request("/api/log", method="POST", data=data)
    return response is not None

def create_template(name: str, category: str, subject: str, content: str, description: str = "") -> bool:
    """
    Create a new email template
    
    Args:
        name: Template name
        category: Template category
        subject: Email subject template
        content: Email body template
        description: Template description
    
    Returns:
        True if successful, False otherwise
    """
    data = {
        "name": name,
        "category": category,
        "subject": subject,
        "content": content,
        "description": description
    }
    
    response = make_api_request("/api/templates", method="POST", data=data)
    return response is not None

def update_donor(donor_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update donor information
    
    Args:
        donor_id: ID of the donor to update
        updates: Dictionary of fields to update
    
    Returns:
        True if successful, False otherwise
    """
    response = make_api_request(f"/api/donors/{donor_id}", method="PUT", data=updates)
    return response is not None

# Cache API responses to improve performance
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_donors():
    """Get cached donor list"""
    return get_donors()

@st.cache_data(ttl=300)
def get_cached_pipeline_data():
    """Get cached pipeline data"""
    return get_pipeline_data()

@st.cache_data(ttl=600)  # Cache templates for 10 minutes
def get_cached_templates():
    """Get cached templates"""
    return get_templates()