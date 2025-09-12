"""
Authentication Module
Handles user authentication and authorization
"""

import streamlit as st
import os
from typing import Optional, List

def get_allowed_users() -> List[str]:
    """
    Get list of allowed users from environment variable
    
    Returns:
        List of allowed email addresses
    """
    allowed_users_str = os.getenv("ALLOWED_USERS", "")
    if not allowed_users_str:
        # Default fallback for development
        return ["admin@dikshafoundation.org"]
    
    return [email.strip() for email in allowed_users_str.split(",")]

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
    
    # Check if email is in allowed users list
    allowed_users = get_allowed_users()
    if email.lower() not in [user.lower() for user in allowed_users]:
        st.error(f"❌ Email {email} is not authorized to access this application.")
        return False
    
    # Simple password check (in production, use proper authentication)
    # This is a basic implementation - replace with your actual auth system
    expected_password = os.getenv("APP_PASSWORD", "diksha2024")
    
    if password == expected_password:
        return True
    
    # You could also integrate with external auth systems here
    # For example, Google OAuth, Active Directory, etc.
    
    return False

def logout():
    """Logout the current user"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.rerun()

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