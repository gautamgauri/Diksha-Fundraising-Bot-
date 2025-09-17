"""
Authentication helpers wired through streamlit-authenticator.

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
from typing import Any, Dict, List, Optional

import streamlit as st
from streamlit_authenticator import Authenticate


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


def _build_config() -> Dict[str, Any]:
    cookie_conf = _get_cookie_config()
    oauth_conf = _get_oauth_config()

    # Use domain-based authorization by default (allow any @dikshafoundation.org email)
    # Only use specific allowed_emails if explicitly configured
    allowed_emails = _read_list("auth", "allowed_emails")
    denied_emails = _read_list("auth", "denied_emails")

    credentials: Dict[str, Any] = {"usernames": {}}  # Google OAuth handles users

    return {
        "credentials": credentials,
        "cookie": cookie_conf,
        "oauth2": {"google": oauth_conf},
        "auth": {
            "allowed_emails": [email.lower() for email in allowed_emails],
            "denied_emails": [email.lower() for email in denied_emails],
        },
    }


def _create_authenticator() -> Authenticate:
    config = _build_config()

    missing = [
        name
        for name in ("client_id", "client_secret", "redirect_uri")
        if not config["oauth2"]["google"].get(name)
    ]
    if missing:
        raise RuntimeError(
            "Missing Google OAuth configuration values: " + ", ".join(missing)
        )

    authenticator = Authenticate(
        credentials=config["credentials"],
        cookie_name=config["cookie"]["name"],
        key=config["cookie"]["key"],
        cookie_expiry_days=config["cookie"]["expiry_days"],
        oauth2_credentials={"google": config["oauth2"]["google"]},
    )

    st.session_state.setdefault("auth_allowed_emails", config["auth"]["allowed_emails"])
    st.session_state.setdefault("auth_denied_emails", config["auth"]["denied_emails"])
    st.session_state.setdefault("auth_authorized_domains", config["oauth2"]["google"]["authorized_domains"])

    return authenticator


def _is_email_authorized(email: str) -> bool:
    lowered = email.lower()

    # First check if email is explicitly denied
    if lowered in st.session_state.get("auth_denied_emails", []):
        return False

    # Check if email is from an authorized domain
    authorized_domains = st.session_state.get("auth_authorized_domains", ["dikshafoundation.org"])
    for domain in authorized_domains:
        if lowered.endswith(f"@{domain.lower()}"):
            # If there's a specific allowed emails list, check that too
            allowed = st.session_state.get("auth_allowed_emails", [])
            if allowed:
                return lowered in allowed
            # Otherwise, any email from authorized domain is allowed
            return True

    # If not from authorized domain, check specific allowed emails
    allowed = st.session_state.get("auth_allowed_emails", [])
    return lowered in allowed if allowed else False


def check_auth() -> bool:
    """Validate authentication using streamlit-authenticator."""
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("user_email", None)

    if st.session_state.authenticated:
        return True

    authenticator = _create_authenticator()
    name, auth_status, email = authenticator.login("main", location="main")

    if auth_status and email:
        if not _is_email_authorized(email):
            st.error("This account is not authorized for Diksha fundraising tools.")
            authenticator.logout("Return to login", "main")
            return False

        st.session_state.authenticated = True
        st.session_state.user_email = email
        st.session_state.user_name = name
        return True

    if auth_status is False:
        st.error("Authentication failed. Please try again with an authorized account.")
    else:
        st.info("Sign in with your Diksha Google Workspace account to continue.")

    return False


def logout(location: str = "sidebar") -> None:
    authenticator = _create_authenticator()
    logout_clicked = authenticator.logout("Logout", location)

    if logout_clicked:
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_name = None


def get_current_user() -> Optional[str]:
    if st.session_state.get("authenticated"):
        return st.session_state.get("user_email")
    return None


def require_auth(func):
    def wrapper(*args, **kwargs):
        if check_auth():
            return func(*args, **kwargs)
        st.stop()

    return wrapper


def show_auth_status(location: str = "sidebar") -> bool:
    if not st.session_state.get("authenticated"):
        return False

    user_email = st.session_state.get("user_email") or "Unknown user"
    user_name = st.session_state.get("user_name")

    container = st.sidebar if location == "sidebar" else st.container()
    with container:
        st.markdown("---")
        st.markdown("**👤 Signed in**")
        if user_name:
            st.markdown(f"**{user_name}**")
        st.markdown(f"📧 {user_email}")
        logout(location=location)

    return True
