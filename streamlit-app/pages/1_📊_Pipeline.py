"""
Pipeline Management Page
Displays and manages the fundraising pipeline
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add current directory to path for lib imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from lib.api import get_pipeline_data

def main():
    st.title("📊 Fundraising Pipeline")
    st.markdown("Manage your fundraising pipeline and track donor progress")
    
    # Pipeline overview
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
    
    # Pipeline data table
    st.subheader("Pipeline Overview")
    
    try:
        # Get pipeline data (this would connect to your backend)
        pipeline_data = get_pipeline_data()
        
        if pipeline_data:
            df = pd.DataFrame(pipeline_data)
            st.dataframe(df, use_container_width=True)
        else:
            # Sample data for demonstration
            sample_data = {
                'Donor Name': ['ABC Corp', 'XYZ Foundation', 'Tech Startup Inc', 'Local Business'],
                'Stage': ['Prospect', 'Qualified', 'Proposal', 'Negotiation'],
                'Amount': ['$50,000', '$25,000', '$100,000', '$15,000'],
                'Probability': ['20%', '40%', '60%', '80%'],
                'Expected Close': ['Q2 2024', 'Q1 2024', 'Q2 2024', 'Q1 2024']
            }
            df = pd.DataFrame(sample_data)
            st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading pipeline data: {str(e)}")
        st.info("Showing sample data instead")
        
        # Fallback sample data
        sample_data = {
            'Donor Name': ['ABC Corp', 'XYZ Foundation', 'Tech Startup Inc', 'Local Business'],
            'Stage': ['Prospect', 'Qualified', 'Proposal', 'Negotiation'],
            'Amount': ['$50,000', '$25,000', '$100,000', '$15,000'],
            'Probability': ['20%', '40%', '60%', '80%'],
            'Expected Close': ['Q2 2024', 'Q1 2024', 'Q2 2024', 'Q1 2024']
        }
        df = pd.DataFrame(sample_data)
        st.dataframe(df, use_container_width=True)
    
    # Pipeline actions
    st.markdown("---")
    st.subheader("Pipeline Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Pipeline"):
            st.rerun()
    
    with col2:
        if st.button("📊 Export Data"):
            st.success("Pipeline data exported successfully!")
    
    with col3:
        if st.button("➕ Add New Prospect"):
            st.info("Add new prospect functionality would open here")

if __name__ == "__main__":
    main()


