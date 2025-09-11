"""
Diksha Fundraising Bot - Main Application
Streamlit multi-page application for fundraising management
"""

import streamlit as st
import sys
import os

# Add current directory to path for lib imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from lib.auth import check_auth, show_auth_status
from lib.api import get_cached_donors, get_cached_pipeline_data

# Page configuration
st.set_page_config(
    page_title="Diksha Fundraising Bot",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    
    # Check authentication first
    if not check_auth():
        return  # Authentication form will be shown
    
    # Show auth status in sidebar
    show_auth_status()
    
    # Main dashboard content
    st.title("🏠 Diksha Fundraising Dashboard")
    st.markdown("Welcome to the Diksha Foundation Fundraising Management System")
    
    # Dashboard overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Prospects", "150", "12")
    with col2:
        st.metric("Active Conversations", "45", "8")
    with col3:
        st.metric("Proposals Sent", "23", "5")
    with col4:
        st.metric("Closed Won", "12", "3")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 View Pipeline", use_container_width=True):
            st.switch_page("pages/1_📊_Pipeline.py")
    
    with col2:
        if st.button("🏷️ Donor Profiles", use_container_width=True):
            st.switch_page("pages/2_🏷️_Donor_Profile.py")
    
    with col3:
        if st.button("✉️ Email Composer", use_container_width=True):
            st.switch_page("pages/3_✉️_Composer.py")
    
    with col4:
        if st.button("📝 Activity Log", use_container_width=True):
            st.switch_page("pages/5_📝_Activity_Log.py")
    
    # Recent activity
    st.markdown("---")
    st.subheader("📈 Recent Activity")
    
    # Sample recent activity data
    recent_activities = [
        {"action": "Email sent", "target": "ABC Corp", "time": "2 hours ago", "user": "John Doe"},
        {"action": "Prospect added", "target": "XYZ Foundation", "time": "4 hours ago", "user": "Jane Smith"},
        {"action": "Meeting scheduled", "target": "Tech Startup Inc", "time": "1 day ago", "user": "John Doe"},
        {"action": "Proposal sent", "target": "Local Business", "time": "2 days ago", "user": "Jane Smith"},
    ]
    
    for activity in recent_activities:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{activity['action']}** - {activity['target']}")
            with col2:
                st.write(activity['time'])
            with col3:
                st.write(activity['user'])
            st.divider()
    
    # Footer
    st.markdown("---")
    st.markdown("**Diksha Fundraising Bot** - Version 2.0")
    st.markdown("Built with ❤️ for Diksha Foundation")

if __name__ == "__main__":
    main()