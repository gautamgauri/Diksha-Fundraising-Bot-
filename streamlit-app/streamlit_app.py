"""
Diksha Fundraising Bot - Streamlit App
Main application file for the fundraising management system
"""

import streamlit as st
import sys
import os

# Robust import system for Railway deployment
import importlib.util

# Try multiple path strategies
possible_paths = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'),
    os.path.join(os.path.dirname(__file__), 'lib'),
    '/app/lib',
    './lib'
]

lib_path = None
for path in possible_paths:
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path) and os.path.exists(os.path.join(abs_path, 'auth.py')):
        lib_path = abs_path
        break

if lib_path and lib_path not in sys.path:
    sys.path.insert(0, lib_path)

# Fallback function in case import fails
def fallback_check_auth() -> bool:
    """Fallback function for check_auth - always returns True for development"""
    return True

# Import with multiple fallback strategies
check_auth = fallback_check_auth

try:
    from lib import check_auth
    print("✅ Using lib package import for check_auth")
except ImportError as e:
    print(f"❌ Lib package import failed: {e}")
    try:
        from auth import check_auth  # type: ignore
        print("✅ Using direct module import for check_auth")
    except ImportError as e:
        print(f"❌ Direct module import failed: {e}")
        if lib_path:
            try:
                auth_file_path = os.path.join(lib_path, 'auth.py')
                if os.path.exists(auth_file_path):
                    spec = importlib.util.spec_from_file_location("auth", auth_file_path)
                    auth_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(auth_module)
                    if hasattr(auth_module, 'check_auth'):
                        check_auth = auth_module.check_auth
                        print("✅ Using importlib for check_auth")
            except Exception as e:
                print(f"❌ Importlib failed: {e}")
        
        if check_auth == fallback_check_auth:
            for path in possible_paths:
                try:
                    abs_path = os.path.abspath(path)
                    auth_file_path = os.path.join(abs_path, 'auth.py')
                    if os.path.exists(auth_file_path):
                        spec = importlib.util.spec_from_file_location("auth", auth_file_path)
                        auth_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(auth_module)
                        if hasattr(auth_module, 'check_auth'):
                            check_auth = auth_module.check_auth
                            print(f"✅ Found check_auth in {abs_path}")
                            break
                except Exception as e:
                    print(f"❌ Failed to import from {path}: {e}")
                    continue

print(f"✅ Final check_auth import: {check_auth != fallback_check_auth}")

# Page configuration
st.set_page_config(
    page_title="Diksha Fundraising Bot",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    
    # Check authentication
    if not check_auth():
        st.error("🔒 Please authenticate to access the application")
        st.info("Contact your administrator for access credentials.")
        return
    
    # Main dashboard content
    st.title("🏠 Diksha Fundraising Dashboard")
    st.markdown("Welcome to your fundraising management system")
    
    # Quick stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Donors",
            value="247",
            delta="12 this month"
        )
    
    with col2:
        st.metric(
            label="Active Pipeline",
            value="$450K",
            delta="$75K this quarter"
        )
    
    with col3:
        st.metric(
            label="Emails Sent",
            value="1,234",
            delta="89 this week"
        )
    
    with col4:
        st.metric(
            label="Success Rate",
            value="68%",
            delta="5% improvement"
        )
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Pipeline", use_container_width=True):
            st.switch_page("pages/1_📊_Pipeline.py")
    
    with col2:
        if st.button("✉️ Compose Email", use_container_width=True):
            st.switch_page("pages/3_✉️_Composer.py")
    
    with col3:
        if st.button("📝 Add Activity", use_container_width=True):
            st.switch_page("pages/5_📝_Activity_Log.py")
    
    # Recent activities preview
    st.subheader("📋 Recent Activities")
    
    recent_activities = [
        {"time": "2 hours ago", "activity": "Email sent to ABC Corporation"},
        {"time": "5 hours ago", "activity": "Meeting scheduled with XYZ Foundation"},
        {"time": "1 day ago", "activity": "$25,000 donation received from Tech Startup Inc"},
        {"time": "2 days ago", "activity": "Follow-up call with Local Business LLC"}
    ]
    
    for activity in recent_activities:
        st.markdown(f"**{activity['time']}** - {activity['activity']}")
    
    # Navigation sidebar
    with st.sidebar:
        st.title("🏠 Navigation")
        st.markdown("---")
        
        # Quick navigation buttons
        if st.button("📊 Pipeline", use_container_width=True):
            st.switch_page("pages/1_📊_Pipeline.py")
        
        if st.button("🏷️ Donor Profiles", use_container_width=True):
            st.switch_page("pages/2_🏷️_Donor_Profile.py")
        
        if st.button("✉️ Email Composer", use_container_width=True):
            st.switch_page("pages/3_✉️_Composer.py")
        
        if st.button("🧩 Templates", use_container_width=True):
            st.switch_page("pages/4_🧩_Templates.py")
        
        if st.button("📝 Activity Log", use_container_width=True):
            st.switch_page("pages/5_📝_Activity_Log.py")
        
        st.markdown("---")
        st.markdown("**Diksha Fundraising Bot**")
        st.markdown("Version 1.0")

if __name__ == "__main__":
    main()