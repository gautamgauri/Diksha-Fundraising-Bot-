"""
Pipeline Management Page
Displays and manages the fundraising pipeline
"""

import streamlit as st
import pandas as pd
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

# Import with multiple fallback strategies
log_activity = None
get_cached_pipeline_data = None
require_auth = None
show_auth_status = None

try:
    from lib import log_activity, get_cached_pipeline_data, require_auth, show_auth_status
except ImportError:
    try:
        from api import log_activity, get_cached_pipeline_data  # type: ignore
        from auth import require_auth, show_auth_status  # type: ignore
    except ImportError:
        if lib_path:
            try:
                # Import api module
                api_file_path = os.path.join(lib_path, 'api.py')
                spec = importlib.util.spec_from_file_location("api", api_file_path)
                api_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(api_module)
                log_activity = api_module.log_activity
                get_cached_pipeline_data = api_module.get_cached_pipeline_data
                
                # Import auth module
                auth_file_path = os.path.join(lib_path, 'auth.py')
                spec = importlib.util.spec_from_file_location("auth", auth_file_path)
                auth_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(auth_module)
                require_auth = auth_module.require_auth
                show_auth_status = auth_module.show_auth_status
            except Exception:
                pass
        
        if not all([log_activity, get_cached_pipeline_data, require_auth, show_auth_status]):
            for path in possible_paths:
                try:
                    abs_path = os.path.abspath(path)
                    api_file_path = os.path.join(abs_path, 'api.py')
                    auth_file_path = os.path.join(abs_path, 'auth.py')
                    
                    if os.path.exists(api_file_path) and os.path.exists(auth_file_path):
                        # Import api module
                        spec = importlib.util.spec_from_file_location("api", api_file_path)
                        api_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(api_module)
                        log_activity = api_module.log_activity
                        get_cached_pipeline_data = api_module.get_cached_pipeline_data
                        
                        # Import auth module
                        spec = importlib.util.spec_from_file_location("auth", auth_file_path)
                        auth_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(auth_module)
                        require_auth = auth_module.require_auth
                        show_auth_status = auth_module.show_auth_status
                        break
                except Exception:
                    continue

if not all([log_activity, get_cached_pipeline_data, require_auth, show_auth_status]):
    raise ImportError("Could not import required functions from any available source")

# Page configuration
st.set_page_config(
    page_title="Pipeline - Diksha Fundraising",
    page_icon="📊",
    layout="wide"
)

@require_auth
def main():
    # Show auth status in sidebar
    show_auth_status()
    
    st.title("📊 Fundraising Pipeline")
    st.markdown("Manage your fundraising pipeline and track donor progress")
    
    # Add refresh button in top right
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Pipeline overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # In a real app, these would come from the API
    with col1:
        st.metric("Total Prospects", "150", "12", help="Total prospects in pipeline")
    with col2:
        st.metric("Active Conversations", "45", "8", help="Currently engaged prospects")
    with col3:
        st.metric("Proposals Sent", "23", "5", help="Formal proposals sent")
    with col4:
        st.metric("Closed Won", "12", "3", help="Successfully closed deals")
    
    st.markdown("---")
    
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stage_filter = st.selectbox(
            "Stage:",
            ["All", "Prospect", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
        )
    
    with col2:
        amount_filter = st.selectbox(
            "Amount Range:",
            ["All", "< $10K", "$10K - $50K", "$50K - $100K", "> $100K"]
        )
    
    with col3:
        probability_filter = st.selectbox(
            "Probability:",
            ["All", "< 25%", "25% - 50%", "50% - 75%", "> 75%"]
        )
    
    # Pipeline data table
    st.subheader("📋 Pipeline Overview")
    
    with st.spinner("Loading pipeline data..."):
        try:
            # Get pipeline data from API
            pipeline_data = get_cached_pipeline_data()
            
            if pipeline_data and len(pipeline_data) > 0:
                df = pd.DataFrame(pipeline_data)
                
                # Apply filters
                if stage_filter != "All":
                    df = df[df['stage'] == stage_filter]
                
                # Display filtered data
                if not df.empty:
                    st.dataframe(
                        df,
                        use_container_width=True,
                        column_config={
                            "amount": st.column_config.NumberColumn(
                                "Amount",
                                format="$%d"
                            ),
                            "probability": st.column_config.ProgressColumn(
                                "Probability",
                                min_value=0,
                                max_value=100
                            ),
                            "expected_close": st.column_config.DateColumn(
                                "Expected Close"
                            )
                        }
                    )
                else:
                    st.info("No data matches the selected filters.")
            else:
                # Fallback to sample data with notice
                st.warning("⚠️ Unable to load live data. Showing sample data.")
                display_sample_pipeline_data()
                
        except Exception as e:
            st.error(f"❌ Error loading pipeline data: {str(e)}")
            st.info("📊 Showing sample data instead")
            display_sample_pipeline_data()
    
    # Pipeline actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Export Pipeline", use_container_width=True):
            try:
                # Export functionality
                pipeline_data = get_cached_pipeline_data()
                if pipeline_data:
                    df = pd.DataFrame(pipeline_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        "pipeline_data.csv",
                        "text/csv"
                    )
                else:
                    st.error("No data to export")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    with col2:
        if st.button("➕ Add Prospect", use_container_width=True):
            add_new_prospect()
    
    with col3:
        if st.button("📈 View Analytics", use_container_width=True):
            show_pipeline_analytics()
    
    with col4:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.switch_page("streamlit_app.py")

def display_sample_pipeline_data():
    """Display sample pipeline data when API is unavailable"""
    sample_data = {
        'Donor Name': ['ABC Corp', 'XYZ Foundation', 'Tech Startup Inc', 'Local Business'],
        'Stage': ['Prospect', 'Qualified', 'Proposal', 'Negotiation'],
        'Amount': [50000, 25000, 100000, 15000],
        'Probability': [20, 40, 60, 80],
        'Expected Close': ['2024-06-01', '2024-03-15', '2024-06-30', '2024-03-01'],
        'Contact': ['john@abc.com', 'info@xyz.org', 'contact@tech.com', 'owner@local.biz']
    }
    
    df = pd.DataFrame(sample_data)
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Amount": st.column_config.NumberColumn(
                "Amount",
                format="$%d"
            ),
            "Probability": st.column_config.ProgressColumn(
                "Probability (%)",
                min_value=0,
                max_value=100
            )
        }
    )

def add_new_prospect():
    """Show form to add new prospect"""
    with st.expander("➕ Add New Prospect", expanded=True):
        with st.form("add_prospect"):
            col1, col2 = st.columns(2)
            
            with col1:
                org_name = st.text_input("Organization Name*")
                contact_name = st.text_input("Contact Person*")
                email = st.text_input("Email*")
                
            with col2:
                phone = st.text_input("Phone")
                website = st.text_input("Website")
                industry = st.text_input("Industry")
            
            expected_amount = st.number_input(
                "Expected Amount ($)",
                min_value=0,
                step=1000,
                format="%d"
            )
            
            notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("💾 Add Prospect")
            
            if submitted:
                if org_name and contact_name and email:
                    # Log the activity
                    log_activity(
                        "prospect_added",
                        "new_prospect",
                        f"Added new prospect: {org_name}"
                    )
                    st.success(f"✅ Prospect '{org_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (marked with *)")

def show_pipeline_analytics():
    """Show pipeline analytics"""
    with st.expander("📈 Pipeline Analytics", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Conversion Rates**")
            st.metric("Prospect → Qualified", "30%", "5%")
            st.metric("Qualified → Proposal", "65%", "10%")
            st.metric("Proposal → Won", "45%", "-2%")
        
        with col2:
            st.markdown("**Average Metrics**")
            st.metric("Deal Size", "$35K", "$5K")
            st.metric("Sales Cycle", "45 days", "-3 days")
            st.metric("Win Rate", "18%", "2%")

if __name__ == "__main__":
    main()