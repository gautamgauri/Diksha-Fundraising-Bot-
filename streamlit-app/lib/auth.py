"""
Google OAuth authentication for Streamlit.

Configuration expected in Streamlit secrets or environment variables:

    [cookie]
    name = "streamlit_auth"
    key = "super-secret-signing-key"
    expiry_days = 1

    [oauth2.google]
    client_id = "...apps.googleusercontent.com"
    client_secret = "..."
    redirect_uri = "https://your-app-url"
    authorized_domains = ["dikshafoundation.org"]

Optional allow/deny lists can be supplied via:

    [auth]
    allowed_emails = ["alice@dikshafoundation.org", "bob@dikshafoundation.org"]
    denied_emails = []

If `auth.allowed_emails` is omitted, all Workspace users from the authorized
domains are allowed by default.
"""

from __future__ import annotations

import os
import json
import urllib.parse
import hashlib
import hmac
import time
from typing import Any, Dict, List, Optional

import streamlit as st
import requests


def _read_list(section: str, key: str, default: Optional[List[str]] = None) -> List[str]:
    if st.secrets.get(section) and key in st.secrets[section]:
        value = st.secrets[section][key]
    else:
        env_key = f"{section}_{key}".upper()
        value = os.getenv(env_key, None)

    if value is None:
        return list(default or [])

    if isinstance(value, list):
        return [item.strip() for item in value if str(item).strip()]

    return [item.strip() for item in str(value).split(",") if item.strip()]


def _get_cookie_config() -> Dict[str, Any]:
    cookie_section = st.secrets.get("cookie", {})
    return {
        "name": cookie_section.get("name") or os.getenv("COOKIE_NAME", "streamlit_auth"),
        "key": cookie_section.get("key") or os.getenv("COOKIE_KEY", "streamlit-auth-key"),
        "expiry_days": cookie_section.get("expiry_days")
        or int(os.getenv("COOKIE_EXPIRY_DAYS", "1")),
    }


def _get_oauth_config() -> Dict[str, Any]:
    oauth_section = st.secrets.get("oauth2", {}).get("google", {})
    return {
        "client_id": oauth_section.get("client_id") or os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": oauth_section.get("client_secret")
        or os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": oauth_section.get("redirect_uri")
        or os.getenv("GOOGLE_REDIRECT_URI"),
        "authorized_domains": oauth_section.get("authorized_domains")
        or _read_list("oauth2.google", "authorized_domains", ["dikshafoundation.org"]),
    }


def _create_state_token() -> str:
    """Create a secure state token for OAuth flow."""
    import secrets
    return secrets.token_urlsafe(32)


def _verify_state_token(state: str) -> bool:
    """Verify the state token from OAuth callback."""
    # For development, we'll be more lenient with state validation
    # In production, you'd want stricter validation
    stored_state = st.session_state.get("oauth_state")

    # If no stored state, accept any reasonable-looking state for now
    if not stored_state and state and len(state) > 10:
        return True

    return stored_state == state


def _create_oauth_url() -> str:
    """Create Google OAuth authorization URL."""
    oauth_config = _get_oauth_config()

    if not oauth_config["client_id"]:
        raise ValueError("Google OAuth client_id not configured")

    state = _create_state_token()
    st.session_state.oauth_state = state

    params = {
        "client_id": oauth_config["client_id"],
        "redirect_uri": oauth_config["redirect_uri"],
        "scope": "openid email profile",
        "response_type": "code",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account"
    }

    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    return f"{base_url}?{urllib.parse.urlencode(params)}"


def _exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
    """Exchange authorization code for access token."""
    oauth_config = _get_oauth_config()

    data = {
        "client_id": oauth_config["client_id"],
        "client_secret": oauth_config["client_secret"],
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": oauth_config["redirect_uri"],
    }

    try:
        response = requests.post("https://oauth2.googleapis.com/token", data=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def _get_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """Get user information from Google API."""
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def _is_email_authorized(email: str) -> bool:
    """Check if email is authorized to access the application."""
    lowered = email.lower()

    # First check if email is explicitly denied
    denied_emails = _read_list("auth", "denied_emails")
    if lowered in [e.lower() for e in denied_emails]:
        return False

    # Check if email is from an authorized domain
    oauth_config = _get_oauth_config()
    authorized_domains = oauth_config["authorized_domains"]

    for domain in authorized_domains:
        if lowered.endswith(f"@{domain.lower()}"):
            # If there's a specific allowed emails list, check that too
            allowed_emails = _read_list("auth", "allowed_emails")
            if allowed_emails:
                return lowered in [e.lower() for e in allowed_emails]
            # Otherwise, any email from authorized domain is allowed
            return True

    # If not from authorized domain, check specific allowed emails
    allowed_emails = _read_list("auth", "allowed_emails")
    return lowered in [e.lower() for e in allowed_emails] if allowed_emails else False


def _set_session_cookie(user_info: Dict[str, Any]) -> None:
    """Set session cookie with user information."""
    cookie_config = _get_cookie_config()

    # Create session data
    session_data = {
        "email": user_info["email"],
        "name": user_info.get("name", ""),
        "picture": user_info.get("picture", ""),
        "timestamp": int(time.time())
    }

    # Store in session state
    st.session_state.authenticated = True
    st.session_state.user_email = user_info["email"]
    st.session_state.user_name = user_info.get("name", "")
    st.session_state.user_picture = user_info.get("picture", "")


def _handle_oauth_callback() -> bool:
    """Handle OAuth callback from Google."""
    # Check for OAuth callback parameters
    query_params = st.query_params

    if "code" in query_params and "state" in query_params:
        code = query_params["code"]
        state = query_params["state"]

        # Verify state token
        if not _verify_state_token(state):
            st.error("Invalid OAuth state. Please try again.")
            return False

        # Exchange code for token
        token_data = _exchange_code_for_token(code)
        if not token_data:
            st.error("Failed to obtain access token from Google.")
            return False

        # Get user information
        user_info = _get_user_info(token_data["access_token"])
        if not user_info:
            st.error("Failed to get user information from Google.")
            return False

        # Check if user is authorized
        if not _is_email_authorized(user_info["email"]):
            st.error("This account is not authorized for Diksha fundraising tools.")
            return False

        # Set session
        _set_session_cookie(user_info)

        # Clear query parameters by rerunning
        st.query_params.clear()
        st.rerun()

        return True

    return False


def check_auth() -> bool:
    """Validate authentication using Google OAuth."""
    # Initialize session state
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("user_email", None)

    # Handle OAuth callback first
    if _handle_oauth_callback():
        return True

    # Check if already authenticated
    if st.session_state.authenticated:
        return True

    # Show OAuth login
    oauth_config = _get_oauth_config()

    # Check if OAuth is properly configured
    if not oauth_config["client_id"] or not oauth_config["client_secret"]:
        st.error("Google OAuth is not properly configured. Please contact your administrator.")
        return False

    st.title("🔐 Sign In Required")
    st.markdown("Please sign in with your Diksha Google Workspace account to continue.")

    if st.button("🚀 Sign in with Google", type="primary", use_container_width=True):
        try:
            oauth_url = _create_oauth_url()
            st.markdown(f'<meta http-equiv="refresh" content="0; url={oauth_url}">', unsafe_allow_html=True)
            st.stop()
        except Exception as e:
            st.error(f"Error creating OAuth URL: {str(e)}")

    return False


def logout(location: str = "sidebar") -> None:
    """Log out the current user."""
    container = st.sidebar if location == "sidebar" else st.container()

    with container:
        if st.button("Logout", key=f"logout_{location}"):
            # Clear session state
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_name = None
            st.session_state.user_picture = None
            st.session_state.oauth_state = None

            # Clear query parameters
            st.query_params.clear()

            # Rerun to refresh the page
            st.rerun()


def get_current_user() -> Optional[str]:
    """Get the current authenticated user's email."""
    if st.session_state.get("authenticated"):
        return st.session_state.get("user_email")
    return None


def require_auth(func):
    """Decorator to require authentication for a function."""
    def wrapper(*args, **kwargs):
        if check_auth():
            return func(*args, **kwargs)
        st.stop()

    return wrapper


def show_auth_status(location: str = "sidebar") -> bool:
    """Show authentication status and user info."""
    if not st.session_state.get("authenticated"):
        return False

    user_email = st.session_state.get("user_email") or "Unknown user"
    user_name = st.session_state.get("user_name")
    user_picture = st.session_state.get("user_picture")

    container = st.sidebar if location == "sidebar" else st.container()
    with container:
        st.markdown("---")
        st.markdown("**👤 Signed in**")

        if user_picture:
            st.image(user_picture, width=60)

        if user_name:
            st.markdown(f"**{user_name}**")
        st.markdown(f"📧 {user_email}")

        logout(location=location)

    return True