"""
Debug Page
Test API connections and data access
"""

import streamlit as st
import sys
import os

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

# Import API functions
try:
    from lib import test_api_connection, get_pipeline_data, get_templates
    print("✅ Using lib package imports for debug")
except ImportError as e:
    print(f"❌ Lib package import failed: {e}")
    try:
        from api import test_api_connection, get_pipeline_data, get_templates
        print("✅ Using direct module imports for debug")
    except ImportError as e:
        print(f"❌ Direct module import failed: {e}")
        # Fallback functions
        def test_api_connection():
            return {"status": "error", "error": "API module not available"}
        def get_pipeline_data():
            return None
        def get_templates():
            return None

# Page configuration
st.set_page_config(
    page_title="Debug - Diksha Fundraising",
    page_icon="🔧",
    layout="wide"
)

def main():
    st.title("🔧 Debug & API Status")
    st.markdown("Test API connections and data access")
    
    # API Connection Test
    st.header("🌐 API Connection Status")
    
    if st.button("🔄 Test API Connection", use_container_width=True):
        with st.spinner("Testing API connection..."):
            connection_status = test_api_connection()
            
            if connection_status["status"] == "connected":
                st.success("✅ API Connection Successful!")
                st.json(connection_status)
            else:
                st.error("❌ API Connection Failed!")
                st.json(connection_status)
    
    # Pipeline Data Test
    st.header("📊 Pipeline Data Test")
    
    if st.button("🔄 Test Pipeline Data", use_container_width=True):
        with st.spinner("Fetching pipeline data..."):
            pipeline_data = get_pipeline_data()
            
            if pipeline_data:
                st.success(f"✅ Pipeline Data Retrieved! ({len(pipeline_data)} records)")
                
                # Show sample data
                if len(pipeline_data) > 0:
                    st.subheader("Sample Data:")
                    sample_data = pipeline_data[:3]  # Show first 3 records
                    for i, record in enumerate(sample_data):
                        with st.expander(f"Record {i+1}: {record.get('organization_name', 'Unknown')}"):
                            st.json(record)
                else:
                    st.warning("⚠️ No data found in pipeline")
            else:
                st.error("❌ Failed to retrieve pipeline data")
    
    # Templates Test
    st.header("📝 Templates Test")
    
    if st.button("🔄 Test Templates", use_container_width=True):
        with st.spinner("Fetching templates..."):
            templates = get_templates()
            
            if templates:
                st.success("✅ Templates Retrieved!")
                st.json(templates)
            else:
                st.error("❌ Failed to retrieve templates")
    
    # Environment Variables
    st.header("🔧 Environment Variables")
    
    env_vars = {
        "API_BASE": os.getenv("API_BASE", "Not set"),
        "FLASK_BACKEND_URL": os.getenv("FLASK_BACKEND_URL", "Not set"),
        "MAIN_SHEET_ID": os.getenv("MAIN_SHEET_ID", "Not set"),
        "GOOGLE_CREDENTIALS_BASE64": "Set" if os.getenv("GOOGLE_CREDENTIALS_BASE64") else "Not set"
    }
    
    for key, value in env_vars.items():
        st.text(f"{key}: {value}")
    
    # Clear Cache
    st.header("🗑️ Cache Management")
    
    if st.button("🗑️ Clear All Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Cache cleared!")
        st.rerun()

if __name__ == "__main__":
    main()
