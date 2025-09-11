"""
Diksha Fundraising Bot - Streamlit App
Main application file for the fundraising management system
"""

import streamlit as st
import sys
import os

# Add the parent directory to the path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.api import get_donors, get_pipeline_data
from lib.auth import check_auth

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
        st.error("Please authenticate to access the application")
        return
    
    # Sidebar navigation
    st.sidebar.title("🏠 Diksha Fundraising")
    st.sidebar.markdown("---")
    
    # Navigation menu
    pages = {
        "📊 Pipeline": "1_📊_Pipeline.py",
        "🏷️ Donor Profile": "2_🏷️_Donor_Profile.py", 
        "✉️ Composer": "3_✉️_Composer.py",
        "🧩 Templates": "4_🧩_Templates.py",
        "📝 Activity Log": "5_📝_Activity_Log.py"
    }
    
    selected_page = st.sidebar.selectbox(
        "Navigate to:",
        list(pages.keys())
    )
    
    # Load the selected page
    if selected_page:
        page_file = pages[selected_page]
        try:
            # Import and run the page
            exec(open(f"pages/{page_file}").read())
        except FileNotFoundError:
            st.error(f"Page {page_file} not found. Please check the file exists.")
        except Exception as e:
            st.error(f"Error loading page: {str(e)}")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Diksha Fundraising Bot**")
    st.sidebar.markdown("Version 1.0")

if __name__ == "__main__":
    main()


