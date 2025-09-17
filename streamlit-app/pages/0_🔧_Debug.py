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
    from lib import test_api_connection, get_pipeline_data, get_templates, test_connection_robustness, get_data_quality_stats
    print("Using lib package imports for debug")
except ImportError as e:
    print(f"❌ Lib package import failed: {e}")
    try:
        from api import test_api_connection, get_pipeline_data, get_templates, test_connection_robustness, get_data_quality_stats
        print("Using direct module imports for debug")
    except ImportError as e:
        print(f"❌ Direct module import failed: {e}")
        # Fallback functions
        def test_api_connection():
            return {"status": "error", "error": "API module not available"}
        def get_pipeline_data():
            return None
        def get_templates():
            return None
        def test_connection_robustness():
            return {"overall_status": "error", "error": "API module not available"}
        def get_data_quality_stats():
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
    
    # Data Quality Test
    st.header("📊 Data Quality Analysis")
    
    if st.button("🔄 Analyze Data Quality", use_container_width=True):
        with st.spinner("Analyzing data quality..."):
            quality_stats = get_data_quality_stats()
            
            if quality_stats and quality_stats.get("data_quality"):
                stats = quality_stats["data_quality"]
                
                # Overall quality
                quality_pct = stats.get("data_quality_percentage", 0)
                if quality_pct >= 80:
                    st.success(f"🟢 Excellent Data Quality: {quality_pct}%")
                elif quality_pct >= 60:
                    st.warning(f"🟡 Good Data Quality: {quality_pct}%")
                elif quality_pct >= 40:
                    st.error(f"🟠 Poor Data Quality: {quality_pct}%")
                else:
                    st.error(f"🔴 Very Poor Data Quality: {quality_pct}%")
                
                # Detailed breakdown
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Rows", stats.get("total_rows", 0))
                    st.metric("Actual Records", stats.get("actual_records", 0))
                
                with col2:
                    st.metric("With Organization Name", stats.get("records_with_organization_name", 0))
                    st.metric("With Contact Person", stats.get("records_with_contact_person", 0))
                
                with col3:
                    st.metric("With Email", stats.get("records_with_email", 0))
                    st.metric("With Stage", stats.get("records_with_stage", 0))
                
                # Show the actual records
                if stats.get("actual_records", 0) > 0:
                    st.subheader("📋 Actual Records Found:")
                    pipeline_data = get_pipeline_data()
                    if pipeline_data:
                        for i, record in enumerate(pipeline_data[:10]):  # Show first 10
                            with st.expander(f"Record {i+1}: {record.get('organization_name', 'Unknown')}"):
                                st.json(record)
                        
                        if len(pipeline_data) > 10:
                            st.info(f"Showing first 10 of {len(pipeline_data)} actual records")
                
            else:
                st.error("❌ Failed to retrieve data quality statistics")
    
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
    
    # Connection Robustness Test
    st.header("🛡️ Connection Robustness Test")
    
    if st.button("🛡️ Test Connection Robustness", use_container_width=True):
        with st.spinner("Testing connection robustness..."):
            robustness_results = test_connection_robustness()
            
            # Overall status
            status = robustness_results.get("overall_status", "unknown")
            if status == "excellent":
                st.success("🟢 Excellent - All tests passed!")
            elif status == "good":
                st.warning("🟡 Good - Most tests passed")
            elif status == "poor":
                st.error("🟠 Poor - Some tests failed")
            else:
                st.error("🔴 Failed - All tests failed")
            
            # Detailed results
            st.subheader("Detailed Test Results:")
            
            # Health check
            health_test = robustness_results.get("health_check", {})
            if health_test.get("status") == "success":
                st.success(f"✅ Health Check: {health_test.get('response_time')} - {health_test.get('data_size')} bytes")
            else:
                st.error(f"❌ Health Check: {health_test.get('error', 'Failed')}")
            
            # Pipeline data
            pipeline_test = robustness_results.get("pipeline_data", {})
            if pipeline_test.get("status") == "success":
                st.success(f"✅ Pipeline Data: {pipeline_test.get('response_time')} - {pipeline_test.get('record_count')} records")
            else:
                st.error(f"❌ Pipeline Data: {pipeline_test.get('error', 'Failed')}")
            
            # Templates
            templates_test = robustness_results.get("templates", {})
            if templates_test.get("status") == "success":
                st.success(f"✅ Templates: {templates_test.get('response_time')} - {templates_test.get('template_count')} templates")
            else:
                st.error(f"❌ Templates: {templates_test.get('error', 'Failed')}")
            
            # Data Quality
            data_quality_test = robustness_results.get("data_quality", {})
            if data_quality_test.get("status") == "success":
                actual_records = data_quality_test.get('actual_records', 0)
                total_rows = data_quality_test.get('total_rows', 0)
                quality_pct = data_quality_test.get('quality_percentage', 0)
                st.success(f"✅ Data Quality: {data_quality_test.get('response_time')} - {actual_records}/{total_rows} records ({quality_pct}%)")
            else:
                st.error(f"❌ Data Quality: {data_quality_test.get('error', 'Failed')}")
    
    # Clear Cache
    st.header("🗑️ Cache Management")
    
    if st.button("🗑️ Clear All Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Cache cleared!")
        st.rerun()

if __name__ == "__main__":
    main()
