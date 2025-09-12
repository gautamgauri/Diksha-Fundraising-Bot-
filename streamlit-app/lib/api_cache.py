"""
Cached API functions for better performance
This module is now deprecated - use api.py directly with @st.cache_data decorators
"""

import streamlit as st
from .api import get_pipeline_data, get_donors, get_templates

# These functions are now available directly in api.py with caching
# Keeping this file for backward compatibility

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_pipeline_data():
    """Get cached pipeline data from backend"""
    return get_pipeline_data()

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_cached_donors():
    """Get cached donors data from backend"""
    return get_donors()

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_cached_templates():
    """Get cached templates data from backend"""
    return get_templates()
