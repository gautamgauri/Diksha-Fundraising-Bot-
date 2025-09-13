"""
API Integration Module
Handles communication with the Node.js backend
"""

import requests
import streamlit as st
import os
import time
from typing import List, Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Get API base URL from environment
API_BASE = os.getenv("API_BASE", "http://localhost:5000")

# For Railway deployment, use the Flask backend URL
if not API_BASE or API_BASE == "http://localhost:5000":
    # Use the Flask backend URL from Railway
    flask_backend_url = os.getenv("FLASK_BACKEND_URL", "https://web-production-0d249.up.railway.app")
    if flask_backend_url:
        API_BASE = flask_backend_url
    else:
        # Fallback to localhost for development
        API_BASE = "http://localhost:5000"

# Create a robust session with retry logic
def create_robust_session():
    """Create a requests session with retry logic and robust error handling"""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,  # Total number of retries
        backoff_factor=1,  # Wait time between retries (1, 2, 4 seconds)
        status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry
        allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
    )
    
    # Mount adapter with retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set default timeout
    session.timeout = (5, 15)  # (connect timeout, read timeout)
    
    return session

# Global session instance
_robust_session = None

def get_robust_session():
    """Get or create the robust session"""
    global _robust_session
    if _robust_session is None:
        _robust_session = create_robust_session()
    return _robust_session

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
    # Try backend API first with robust session
    try:
        url = f"{API_BASE}{endpoint}"
        session = get_robust_session()
        
        if method == "GET":
            response = session.get(url)
        elif method == "POST":
            response = session.post(url, json=data)
        elif method == "PUT":
            response = session.put(url, json=data)
        elif method == "DELETE":
            response = session.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
        
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"❌ Backend connection failed: {e}")
        # Backend not available, use direct Google Sheets integration
        return get_data_directly_from_sheets(endpoint)
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e.response.status_code} - {e.response.text}")
        if 'st' in globals():
            st.error(f"❌ API Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        if 'st' in globals():
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
        # Import self-contained Google Sheets integration
        try:
            from .sheets_integration import sheets_integration
        except ImportError:
            from sheets_integration import sheets_integration
        
        # Check if integration is initialized
        if not sheets_integration.initialized:
            print("❌ Google Sheets integration not initialized")
            return None
        
        # Route to appropriate data based on endpoint
        if endpoint == "/api/donors" or endpoint == "/api/pipeline":
            data = sheets_integration.get_pipeline_data()
        elif endpoint == "/api/activities":
            data = sheets_integration.get_interaction_log()
        elif endpoint == "/api/proposals":
            data = sheets_integration.get_proposals()
        elif endpoint == "/api/alerts":
            data = sheets_integration.get_alerts()
        elif endpoint == "/api/templates":
            data = sheets_integration.get_templates()
        else:
            return None
        
        return {"success": True, "data": data}
        
    except Exception as e:
        print(f"Direct sheets access failed: {e}")
        return None

def get_donors() -> Optional[List[Dict]]:
    """Get list of all donors"""
    result = make_api_request("/api/pipeline")
    if result and isinstance(result, dict):
        # Flask backend returns data directly in 'data' field
        return result.get("data", [])
    return result

def get_donor_profile(donor_id: str) -> Optional[Dict]:
    """Get detailed donor profile"""
    result = make_api_request(f"/api/donor/{donor_id}")
    if result and isinstance(result, dict):
        return result.get("data")
    return result

def get_pipeline_data() -> Optional[List[Dict]]:
    """Get fundraising pipeline data"""
    result = make_api_request("/api/pipeline")
    if result and isinstance(result, dict):
        # Flask backend returns data directly in 'data' field
        return result.get("data", [])
    return result

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_pipeline_data() -> Optional[List[Dict]]:
    """Get cached pipeline data"""
    result = get_pipeline_data()
    if result and isinstance(result, dict) and result.get("success"):
        return result.get("data", [])
    return result

def get_templates() -> Optional[Dict]:
    """Get email templates"""
    result = make_api_request("/debug/templates")
    if result and isinstance(result, dict):
        return result
    return result

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

def test_api_connection() -> Dict[str, Any]:
    """Test API connection and return status"""
    try:
        # Test health endpoint with timing
        start_time = time.time()
        health_response = make_api_request("/health")
        end_time = time.time()
        
        if health_response:
            return {
                "status": "connected",
                "api_base": API_BASE,
                "health_check": "passed",
                "backend_type": "flask",
                "response_time": f"{end_time - start_time:.2f}s",
                "components": health_response.get("components", {}),
                "environment": health_response.get("environment", {})
            }
        else:
            return {
                "status": "disconnected",
                "api_base": API_BASE,
                "health_check": "failed",
                "backend_type": "unknown",
                "response_time": f"{end_time - start_time:.2f}s"
            }
    except Exception as e:
        return {
            "status": "error",
            "api_base": API_BASE,
            "error": str(e),
            "backend_type": "unknown"
        }

def test_connection_robustness() -> Dict[str, Any]:
    """Test connection robustness with multiple scenarios"""
    results = {
        "health_check": None,
        "pipeline_data": None,
        "templates": None,
        "overall_status": "unknown"
    }
    
    # Test 1: Health endpoint
    try:
        start_time = time.time()
        health_response = make_api_request("/health")
        end_time = time.time()
        results["health_check"] = {
            "status": "success" if health_response else "failed",
            "response_time": f"{end_time - start_time:.2f}s",
            "data_size": len(str(health_response)) if health_response else 0
        }
    except Exception as e:
        results["health_check"] = {"status": "error", "error": str(e)}
    
    # Test 2: Pipeline data
    try:
        start_time = time.time()
        pipeline_data = make_api_request("/api/pipeline")
        end_time = time.time()
        results["pipeline_data"] = {
            "status": "success" if pipeline_data else "failed",
            "response_time": f"{end_time - start_time:.2f}s",
            "record_count": len(pipeline_data.get("data", [])) if pipeline_data else 0
        }
    except Exception as e:
        results["pipeline_data"] = {"status": "error", "error": str(e)}
    
    # Test 3: Templates
    try:
        start_time = time.time()
        templates = make_api_request("/debug/templates")
        end_time = time.time()
        results["templates"] = {
            "status": "success" if templates else "failed",
            "response_time": f"{end_time - start_time:.2f}s",
            "template_count": len(templates.get("templates", {})) if templates else 0
        }
    except Exception as e:
        results["templates"] = {"status": "error", "error": str(e)}
    
    # Determine overall status
    success_count = sum(1 for test in results.values() if isinstance(test, dict) and test.get("status") == "success")
    if success_count == 3:
        results["overall_status"] = "excellent"
    elif success_count >= 2:
        results["overall_status"] = "good"
    elif success_count >= 1:
        results["overall_status"] = "poor"
    else:
        results["overall_status"] = "failed"
    
    return results