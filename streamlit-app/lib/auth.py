"""
Authentication Module
Handles user authentication and authorization
"""

import streamlit as st
import os
from typing import Optional, List, Dict

def get_user_credentials() -> Dict[str, str]:
    """
    Get user credentials from environment variable or use defaults
    
    Returns:
        Dictionary mapping email addresses to passwords
    """
    # Try to get from environment variable first
    credentials_str = os.getenv("USER_CREDENTIALS", "")
    if credentials_str:
        credentials = {}
        for pair in credentials_str.split(","):
            if ":" in pair:
                email, password = pair.split(":", 1)
                credentials[email.strip()] = password.strip()
        return credentials
    
    # Default fallback for development - individual passwords for each user
    return {
        "admin@dikshafoundation.org": "admin2024",
        "gautamgauri@dikshafoundation.org": "gautam2024",
        "gautam.gauri@dikshafoundation.org": "gautam2024",
        "nisha.kumari@dikshafoundation.org": "nisha2024",
        "neha.anand@dikshafoundation.org": "neha2024",
        "nishant.kumar@dikshafoundation.org": "nishant2024",
        "shivam.mishra@dikshafoundation.org": "shivam2024"
    }

def get_allowed_users() -> List[str]:
    """
    Get list of allowed users from credentials
    
    Returns:
        List of allowed email addresses
    """
    credentials = get_user_credentials()
    return list(credentials.keys())

def check_auth() -> bool:
    """
    Check if user is authenticated and authorized
    
    Returns:
        True if user is authenticated and authorized, False otherwise
    """
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_email = None
    
    # If already authenticated, return True
    if st.session_state.authenticated:
        return True
    
    # Show authentication form
    show_auth_form()
    
    return st.session_state.authenticated

def show_auth_form():
    """Display authentication form"""
    st.title("🔐 Authentication Required")
    st.markdown("Please enter your email to access the Diksha Fundraising Bot")
    
    with st.form("auth_form"):
        email = st.text_input(
            "Email Address:",
            placeholder="your.email@dikshafoundation.org"
        )
        
        password = st.text_input(
            "Password:",
            type="password",
            placeholder="Enter your password"
        )
        
        submitted = st.form_submit_button("🚀 Login")
        
        if submitted:
            if authenticate_user(email, password):
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.success("✅ Authentication successful!")
                st.rerun()
            else:
                st.error("❌ Authentication failed. Please check your credentials.")

def authenticate_user(email: str, password: str) -> bool:
    """
    Authenticate user credentials
    
    Args:
        email: User email address
        password: User password
    
    Returns:
        True if authentication successful, False otherwise
    """
    if not email or not password:
        return False
    
    # Get user credentials
    credentials = get_user_credentials()
    
    # Check if email is in allowed users list
    if email.lower() not in [user.lower() for user in credentials.keys()]:
        st.error(f"❌ Email {email} is not authorized to access this application.")
        return False
    
    # Check password for specific user
    expected_password = credentials.get(email.lower())
    if not expected_password:
        # Try case-insensitive match
        for user_email, user_password in credentials.items():
            if user_email.lower() == email.lower():
                expected_password = user_password
                break
    
    if expected_password and password == expected_password:
        return True
    
    # You could also integrate with external auth systems here
    # For example, Google OAuth, Active Directory, etc.
    
    return False

def logout():
    """Logout the current user"""
    st.session_state.authenticated = False
    st.session_state.user_email = None

def show_user_credentials():
    """Display current user credentials for reference (admin only)"""
    if st.session_state.get("user_email") == "admin@dikshafoundation.org":
        with st.expander("🔑 User Credentials (Admin Only)", expanded=False):
            st.markdown("**Current User Credentials:**")
            credentials = get_user_credentials()
            for email, password in credentials.items():
                st.code(f"{email} : {password}")
            
            st.markdown("**Environment Variable Format:**")
            env_format = ",".join([f"{email}:{password}" for email, password in credentials.items()])
            st.code(f"USER_CREDENTIALS={env_format}")
            
            st.info("💡 Set the USER_CREDENTIALS environment variable in Railway to override these defaults.")

def get_current_user() -> Optional[str]:
    """
    Get current authenticated user email
    
    Returns:
        User email if authenticated, None otherwise
    """
    if st.session_state.get("authenticated", False):
        return st.session_state.get("user_email")
    return None

def require_auth(func):
    """
    Decorator to require authentication for page functions
    
    Usage:
        @require_auth
        def my_page_function():
            # Page content here
    """
    def wrapper(*args, **kwargs):
        if check_auth():
            return func(*args, **kwargs)
        else:
            st.stop()
    return wrapper

# Add authentication status to sidebar
def show_auth_status():
    """Display authentication status in sidebar"""
    if st.session_state.get("authenticated", False):
        user_email = st.session_state.get("user_email", "Unknown")
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("**👤 User Info**")
            st.markdown(f"📧 {user_email}")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
    
    return st.session_state.get("authenticated", False)