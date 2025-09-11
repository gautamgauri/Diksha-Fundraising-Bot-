"""
Donor Profile Management Page
View and manage individual donor profiles
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lib.api import get_donors, get_donor_profile

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


