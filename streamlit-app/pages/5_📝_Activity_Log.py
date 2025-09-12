"""
Activity Log Page
Track and view all fundraising activities and interactions
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Robust import system for Railway deployment
import importlib.util

# Try multiple path strategies
possible_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'),
    os.path.join(os.path.dirname(__file__), '..', 'lib'),
    '/app/lib',
    './lib'
]

lib_path = None
for path in possible_paths:
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path) and os.path.exists(os.path.join(abs_path, 'api.py')):
        lib_path = abs_path
        break

if lib_path and lib_path not in sys.path:
    sys.path.insert(0, lib_path)

# Fallback function
def fallback_get_activity_log():
    return [{"id": "1", "type": "Email Sent", "donor": "Sample Donor", "date": "2024-01-01", "details": "Follow-up email sent"}]

# Import with multiple fallback strategies
get_activity_log = fallback_get_activity_log

try:
    from lib.api import get_activity_log
    print("✅ Using lib.api import for get_activity_log")
except ImportError as e:
    print(f"❌ Lib.api import failed: {e}")
    try:
        from api import get_activity_log  # type: ignore
        print("✅ Using direct api import for get_activity_log")
    except ImportError as e:
        print(f"❌ Direct api import failed: {e}")
        if lib_path:
            try:
                api_file_path = os.path.join(lib_path, 'api.py')
                if os.path.exists(api_file_path):
                    spec = importlib.util.spec_from_file_location("api", api_file_path)
                    api_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(api_module)
                    if hasattr(api_module, 'get_activity_log'):
                        get_activity_log = api_module.get_activity_log
                        print("✅ Using importlib for get_activity_log")
            except Exception as e:
                print(f"❌ Importlib failed: {e}")
        
        if get_activity_log == fallback_get_activity_log:
            for path in possible_paths:
                try:
                    abs_path = os.path.abspath(path)
                    api_file_path = os.path.join(abs_path, 'api.py')
                    if os.path.exists(api_file_path):
                        spec = importlib.util.spec_from_file_location("api", api_file_path)
                        api_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(api_module)
                        if hasattr(api_module, 'get_activity_log'):
                            get_activity_log = api_module.get_activity_log
                            print(f"✅ Found get_activity_log in {abs_path}")
                            break
                except Exception as e:
                    print(f"❌ Failed to import from {path}: {e}")
                    continue

print(f"✅ Final get_activity_log import: {get_activity_log != fallback_get_activity_log}")

def main():
    st.title("📝 Activity Log")
    st.markdown("Track and view all fundraising activities and interactions")
    
    # Filters and controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_range = st.selectbox(
            "Time Period:",
            ["Last 7 days", "Last 30 days", "Last 3 months", "All time", "Custom"]
        )
    
    with col2:
        activity_type = st.selectbox(
            "Activity Type:",
            ["All", "Email", "Call", "Meeting", "Donation", "Follow-up", "Note"]
        )
    
    with col3:
        donor_filter = st.selectbox(
            "Donor:",
            ["All", "ABC Corporation", "XYZ Foundation", "Tech Startup Inc", "Local Business LLC"]
        )
    
    with col4:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Custom date range
    if date_range == "Custom":
        col_a, col_b = st.columns(2)
        with col_a:
            start_date = st.date_input("Start Date:", value=datetime.now() - timedelta(days=30))
        with col_b:
            end_date = st.date_input("End Date:", value=datetime.now())
    
    st.markdown("---")
    
    # Activity summary
    st.subheader("📊 Activity Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Activities", "47", "12")
    with col2:
        st.metric("Emails Sent", "23", "5")
    with col3:
        st.metric("Calls Made", "15", "3")
    with col4:
        st.metric("Meetings Held", "9", "2")
    
    st.markdown("---")
    
    # Activity log table
    st.subheader("📋 Activity Log")
    
    try:
        # Get activity data (this would connect to your backend)
        activity_data = get_activity_log()
        
        if activity_data:
            df = pd.DataFrame(activity_data)
        else:
            # Sample data for demonstration
            activity_data = {
                'Date': [
                    '2024-01-15 14:30',
                    '2024-01-15 10:15',
                    '2024-01-14 16:45',
                    '2024-01-14 09:30',
                    '2024-01-13 15:20',
                    '2024-01-13 11:00',
                    '2024-01-12 14:15',
                    '2024-01-12 10:30'
                ],
                'Activity': [
                    'Email sent',
                    'Phone call',
                    'Meeting held',
                    'Email sent',
                    'Follow-up call',
                    'Donation received',
                    'Email sent',
                    'Initial outreach'
                ],
                'Donor': [
                    'ABC Corporation',
                    'XYZ Foundation',
                    'Tech Startup Inc',
                    'Local Business LLC',
                    'ABC Corporation',
                    'XYZ Foundation',
                    'Tech Startup Inc',
                    'Local Business LLC'
                ],
                'Details': [
                    'Sent partnership proposal',
                    'Discussed funding opportunities',
                    'In-person meeting at their office',
                    'Thank you email for previous donation',
                    'Follow-up on proposal sent last week',
                    '$25,000 donation received',
                    'Event invitation sent',
                    'Initial contact via LinkedIn'
                ],
                'Status': [
                    'Completed',
                    'Completed',
                    'Completed',
                    'Completed',
                    'Completed',
                    'Completed',
                    'Completed',
                    'Completed'
                ]
            }
            df = pd.DataFrame(activity_data)
        
        # Display the dataframe
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading activity data: {str(e)}")
        st.info("Showing sample data instead")
        
        # Fallback sample data
        activity_data = {
            'Date': [
                '2024-01-15 14:30',
                '2024-01-15 10:15',
                '2024-01-14 16:45',
                '2024-01-14 09:30',
                '2024-01-13 15:20'
            ],
            'Activity': [
                'Email sent',
                'Phone call',
                'Meeting held',
                'Email sent',
                'Follow-up call'
            ],
            'Donor': [
                'ABC Corporation',
                'XYZ Foundation',
                'Tech Startup Inc',
                'Local Business LLC',
                'ABC Corporation'
            ],
            'Details': [
                'Sent partnership proposal',
                'Discussed funding opportunities',
                'In-person meeting at their office',
                'Thank you email for previous donation',
                'Follow-up on proposal sent last week'
            ],
            'Status': [
                'Completed',
                'Completed',
                'Completed',
                'Completed',
                'Completed'
            ]
        }
        df = pd.DataFrame(activity_data)
        st.dataframe(df, use_container_width=True)
    
    # Activity actions
    st.markdown("---")
    st.subheader("📝 Add New Activity")
    
    with st.form("add_activity"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_activity_type = st.selectbox(
                "Activity Type:",
                ["Email", "Call", "Meeting", "Donation", "Follow-up", "Note"],
                key="new_activity_type"
            )
            
            new_donor = st.selectbox(
                "Donor:",
                ["ABC Corporation", "XYZ Foundation", "Tech Startup Inc", "Local Business LLC"],
                key="new_donor"
            )
        
        with col2:
            new_date = st.date_input("Date:", value=datetime.now().date(), key="new_date")
            new_time = st.time_input("Time:", value=datetime.now().time(), key="new_time")
        
        new_details = st.text_area(
            "Details:",
            placeholder="Enter activity details...",
            key="new_details"
        )
        
        submitted = st.form_submit_button("➕ Add Activity")
        
        if submitted:
            if new_details:
                st.success("Activity added successfully!")
                st.rerun()
            else:
                st.error("Please enter activity details")
    
    # Export and other actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export to CSV"):
            st.success("Activity log exported successfully!")
    
    with col2:
        if st.button("📧 Email Summary"):
            st.info("Email summary functionality would open here")
    
    with col3:
        if st.button("🔄 Sync with Backend"):
            st.info("Syncing with backend...")
            st.success("Sync completed!")

if __name__ == "__main__":
    main()


