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
    Make a request to the backend API or use direct Google Sheets integration
    
    Args:
        endpoint: API endpoint (e.g., "/api/donors")
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request payload for POST/PUT requests
    
    Returns:
        API response data or None if error
    """
    # Try backend API first
    try:
        url = f"{API_BASE}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, timeout=5)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
        
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # Backend not available, use direct Google Sheets integration
        return get_data_directly_from_sheets(endpoint)
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None

def get_data_directly_from_sheets(endpoint: str) -> Optional[Dict]:
    """
    Get data directly from Google Sheets when backend is not available
    
    Args:
        endpoint: API endpoint to determine which data to fetch
    
    Returns:
        Data from Google Sheets or None if error
    """
    try:
        # Import Google Sheets functionality directly
        import sys
        import os
        
        # Add parent directory to path to access backend modules
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from backend.core.sheets_db import SheetsDB
        
        # Initialize SheetsDB
        sheets_db = SheetsDB()
        if not sheets_db.initialized:
            return None
        
        # Route to appropriate data based on endpoint
        if endpoint == "/api/donors" or endpoint == "/api/pipeline":
            data = sheets_db.get_pipeline_data()
        elif endpoint == "/api/activities":
            data = sheets_db.get_interaction_log()
        elif endpoint == "/api/proposals":
            data = sheets_db.get_proposals()
        elif endpoint == "/api/alerts":
            data = sheets_db.get_alerts()
        else:
            return None
        
        return {"success": True, "data": data}
        
    except Exception as e:
        print(f"Direct sheets access failed: {e}")
        return None

def get_donors() -> Optional[List[Dict]]:
    """Get list of all donors"""
    result = make_api_request("/api/donors")
    if result and isinstance(result, dict) and result.get("success"):
        return result.get("data", [])
    return result

def get_donor_profile(donor_id: str) -> Optional[Dict]:
    """Get detailed donor profile"""
    result = make_api_request(f"/api/donors/{donor_id}")
    if result and isinstance(result, dict) and result.get("success"):
        return result.get("data")
    return result

def get_pipeline_data() -> Optional[List[Dict]]:
    """Get fundraising pipeline data"""
    result = make_api_request("/api/pipeline")
    if result and isinstance(result, dict) and result.get("success"):
        return result.get("data", [])
    return result

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_pipeline_data() -> Optional[List[Dict]]:
    """Get cached pipeline data"""
    result = get_pipeline_data()
    if result and isinstance(result, dict) and result.get("success"):
        return result.get("data", [])
    return result

def get_templates() -> Optional[List[Dict]]:
    """Get email templates"""
    return make_api_request("/api/templates")

def get_activity_log() -> Optional[List[Dict]]:
    """Get activity log entries"""
    result = make_api_request("/api/activities")
    if result and isinstance(result, dict) and result.get("success"):
        return result.get("data", [])
    return result

def get_proposals() -> Optional[List[Dict]]:
    """Get proposals data"""
    result = make_api_request("/api/proposals")
    if result and isinstance(result, dict) and result.get("success"):
        return result.get("data", [])
    return result

def get_alerts() -> Optional[List[Dict]]:
    """Get alerts data"""
    result = make_api_request("/api/alerts")
    if result and isinstance(result, dict) and result.get("success"):
        return result.get("data", [])
    return result

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