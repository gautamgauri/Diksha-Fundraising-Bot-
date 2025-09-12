"""
Donor Profile Management Page
View and manage individual donor profiles
"""

import streamlit as st
import sys
import os
from datetime import datetime

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

# Fallback functions
def fallback_get_donors():
    return [{"id": "1", "name": "Sample Donor", "email": "donor@example.com"}]

def fallback_get_donor_profile(donor_id):
    return {"id": donor_id, "name": "Sample Donor", "email": "donor@example.com", "total_donated": "$5,000"}

# Import with multiple fallback strategies
get_donors = fallback_get_donors
get_donor_profile = fallback_get_donor_profile

try:
    from lib.api import get_donors, get_donor_profile
    print("✅ Using lib.api imports")
except ImportError as e:
    print(f"❌ Lib.api import failed: {e}")
    try:
        from api import get_donors, get_donor_profile  # type: ignore
        print("✅ Using direct api imports")
    except ImportError as e:
        print(f"❌ Direct api import failed: {e}")
        if lib_path:
            try:
                api_file_path = os.path.join(lib_path, 'api.py')
                if os.path.exists(api_file_path):
                    spec = importlib.util.spec_from_file_location("api", api_file_path)
                    api_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(api_module)
                    if hasattr(api_module, 'get_donors'):
                        get_donors = api_module.get_donors
                    if hasattr(api_module, 'get_donor_profile'):
                        get_donor_profile = api_module.get_donor_profile
                    print("✅ Using importlib for api module")
            except Exception as e:
                print(f"❌ Importlib failed: {e}")
        
        if get_donors == fallback_get_donors or get_donor_profile == fallback_get_donor_profile:
            for path in possible_paths:
                try:
                    abs_path = os.path.abspath(path)
                    api_file_path = os.path.join(abs_path, 'api.py')
                    if os.path.exists(api_file_path):
                        spec = importlib.util.spec_from_file_location("api", api_file_path)
                        api_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(api_module)
                        if hasattr(api_module, 'get_donors'):
                            get_donors = api_module.get_donors
                        if hasattr(api_module, 'get_donor_profile'):
                            get_donor_profile = api_module.get_donor_profile
                        print(f"✅ Found api functions in {abs_path}")
                        break
                except Exception as e:
                    print(f"❌ Failed to import from {path}: {e}")
                    continue

print(f"✅ Final imports - get_donors: {get_donors != fallback_get_donors}, get_donor_profile: {get_donor_profile != fallback_get_donor_profile}")

def main():
    st.title("🏷️ Donor Profiles")
    st.markdown("View and manage individual donor information")
    
    # Donor selection
    st.subheader("Select Donor")
    
    try:
        donors = get_donors()
        if donors:
            donor_names = [donor.get('name', 'Unknown') for donor in donors]
            selected_donor = st.selectbox("Choose a donor:", donor_names)
        else:
            # Sample data
            donor_names = ["ABC Corporation", "XYZ Foundation", "Tech Startup Inc", "Local Business LLC"]
            selected_donor = st.selectbox("Choose a donor:", donor_names)
    except Exception as e:
        st.error(f"Error loading donors: {str(e)}")
        donor_names = ["ABC Corporation", "XYZ Foundation", "Tech Startup Inc", "Local Business LLC"]
        selected_donor = st.selectbox("Choose a donor:", donor_names)
    
    if selected_donor:
        st.markdown("---")
        
        # Donor profile display
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"📋 {selected_donor} Profile")
            
            # Basic information
            st.markdown("**Contact Information**")
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.text_input("Organization", value="ABC Corporation", disabled=True)
                st.text_input("Contact Person", value="John Smith", disabled=True)
                st.text_input("Email", value="john@abccorp.com", disabled=True)
            
            with col_b:
                st.text_input("Phone", value="+1 (555) 123-4567", disabled=True)
                st.text_input("Website", value="www.abccorp.com", disabled=True)
                st.text_input("Industry", value="Technology", disabled=True)
            
            # Donation history
            st.markdown("**Donation History**")
            donation_data = {
                'Date': ['2024-01-15', '2023-12-10', '2023-11-05'],
                'Amount': ['$25,000', '$15,000', '$10,000'],
                'Purpose': ['Education Program', 'General Fund', 'Emergency Relief'],
                'Status': ['Completed', 'Completed', 'Completed']
            }
            
            import pandas as pd
            df = pd.DataFrame(donation_data)
            st.dataframe(df, use_container_width=True)
        
        with col2:
            st.subheader("📊 Quick Stats")
            
            # Key metrics
            st.metric("Total Donated", "$50,000", "$5,000")
            st.metric("Donations Count", "3", "1")
            st.metric("Avg Donation", "$16,667", "$2,000")
            st.metric("Last Donation", "Jan 2024", "2 months ago")
            
            st.markdown("---")
            
            # Engagement score
            st.markdown("**Engagement Score**")
            st.progress(0.75)
            st.caption("75% - High Engagement")
            
            # Communication preferences
            st.markdown("**Communication Preferences**")
            st.checkbox("Email Updates", value=True, disabled=True)
            st.checkbox("Newsletter", value=True, disabled=True)
            st.checkbox("Event Invitations", value=False, disabled=True)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✏️ Edit Profile"):
            st.info("Edit profile functionality would open here")
    
    with col2:
        if st.button("📧 Send Email"):
            st.info("Email composer would open here")
    
    with col3:
        if st.button("📅 Schedule Meeting"):
            st.info("Meeting scheduler would open here")
    
    with col4:
        if st.button("📊 View Analytics"):
            st.info("Analytics dashboard would open here")

if __name__ == "__main__":
    main()


