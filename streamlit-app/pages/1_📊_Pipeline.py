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

# Fallback functions in case imports fail
def fallback_log_activity(activity_type: str, donor_id: str, details: str) -> bool:
    """Fallback function for log_activity"""
    print(f"Fallback: Logging activity - {activity_type} for donor {donor_id}: {details}")
    return True

def fallback_get_cached_pipeline_data():
    """Fallback function for get_cached_pipeline_data"""
    return [
        {
            "id": "sample_donor_1",
            "organization_name": "ABC Corporation",
            "current_stage": "Initial Contact",
            "assigned_to": "John Doe",
            "next_action": "Send introduction email",
            "next_action_date": "2024-01-15",
            "last_contact_date": "2024-01-10",
            "sector_tags": "Technology",
            "probability": 25,
            "contact_person": "Jane Smith",
            "contact_email": "jane@abc.com",
            "contact_role": "CFO",
            "notes": "Interested in education technology initiatives"
        },
        {
            "id": "sample_donor_2", 
            "organization_name": "XYZ Foundation",
            "current_stage": "Proposal Sent",
            "assigned_to": "Sarah Johnson",
            "next_action": "Follow up on proposal",
            "next_action_date": "2024-01-20",
            "last_contact_date": "2024-01-12",
            "sector_tags": "Education",
            "probability": 60,
            "contact_person": "Mike Wilson",
            "contact_email": "mike@xyz.org",
            "contact_role": "Program Director",
            "notes": "Very interested in our rural education program"
        }
    ]

def fallback_require_auth(func):
    """Fallback decorator for require_auth"""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def fallback_show_auth_status():
    """Fallback function for show_auth_status"""
    return True

# Import with multiple fallback strategies
log_activity = fallback_log_activity
get_cached_pipeline_data = fallback_get_cached_pipeline_data
require_auth = fallback_require_auth
show_auth_status = fallback_show_auth_status

try:
    from lib import log_activity, get_cached_pipeline_data, require_auth, show_auth_status
    print("✅ Using lib package imports")
except ImportError as e:
    print(f"❌ Lib package import failed: {e}")
    try:
        from api import log_activity, get_cached_pipeline_data  # type: ignore
        from auth import require_auth, show_auth_status  # type: ignore
        print("✅ Using direct module imports")
    except ImportError as e:
        print(f"❌ Direct module import failed: {e}")
        if lib_path:
            try:
                # Import api module
                api_file_path = os.path.join(lib_path, 'api.py')
                if os.path.exists(api_file_path):
                    spec = importlib.util.spec_from_file_location("api", api_file_path)
                    api_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(api_module)
                    if hasattr(api_module, 'log_activity'):
                        log_activity = api_module.log_activity
                    if hasattr(api_module, 'get_cached_pipeline_data'):
                        get_cached_pipeline_data = api_module.get_cached_pipeline_data
                    print("✅ Using importlib for api module")
                
                # Import auth module
                auth_file_path = os.path.join(lib_path, 'auth.py')
                if os.path.exists(auth_file_path):
                    spec = importlib.util.spec_from_file_location("auth", auth_file_path)
                    auth_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(auth_module)
                    if hasattr(auth_module, 'require_auth'):
                        require_auth = auth_module.require_auth
                    if hasattr(auth_module, 'show_auth_status'):
                        show_auth_status = auth_module.show_auth_status
                    print("✅ Using importlib for auth module")
            except Exception as e:
                print(f"❌ Importlib failed: {e}")
        
        # Try all possible paths with importlib
        if log_activity == fallback_log_activity or get_cached_pipeline_data == fallback_get_cached_pipeline_data:
            for path in possible_paths:
                try:
                    abs_path = os.path.abspath(path)
                    api_file_path = os.path.join(abs_path, 'api.py')
                    auth_file_path = os.path.join(abs_path, 'auth.py')
                    
                    if os.path.exists(api_file_path):
                        spec = importlib.util.spec_from_file_location("api", api_file_path)
                        api_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(api_module)
                        if hasattr(api_module, 'log_activity'):
                            log_activity = api_module.log_activity
                        if hasattr(api_module, 'get_cached_pipeline_data'):
                            get_cached_pipeline_data = api_module.get_cached_pipeline_data
                        print(f"✅ Found api functions in {abs_path}")
                    
                    if os.path.exists(auth_file_path):
                        spec = importlib.util.spec_from_file_location("auth", auth_file_path)
                        auth_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(auth_module)
                        if hasattr(auth_module, 'require_auth'):
                            require_auth = auth_module.require_auth
                        if hasattr(auth_module, 'show_auth_status'):
                            show_auth_status = auth_module.show_auth_status
                        print(f"✅ Found auth functions in {abs_path}")
                        
                except Exception as e:
                    print(f"❌ Failed to import from {path}: {e}")
                    continue

print(f"✅ Final imports - log_activity: {log_activity != fallback_log_activity}, get_cached_pipeline_data: {get_cached_pipeline_data != fallback_get_cached_pipeline_data}, require_auth: {require_auth != fallback_require_auth}, show_auth_status: {show_auth_status != fallback_show_auth_status}")

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
    
    # Get pipeline data for metrics
    pipeline_data = get_cached_pipeline_data()
    
    # Calculate metrics from real data
    if pipeline_data and len(pipeline_data) > 0:
        total_prospects = len(pipeline_data)
        active_conversations = len([d for d in pipeline_data if d.get('current_stage') in ['Initial Contact', 'Intro Sent', 'Follow-up Sent']])
        proposals_sent = len([d for d in pipeline_data if d.get('current_stage') in ['Proposal Sent', 'Negotiation']])
        closed_won = len([d for d in pipeline_data if d.get('current_stage') == 'Closed Won'])
    else:
        total_prospects = 0
        active_conversations = 0
        proposals_sent = 0
        closed_won = 0
    
    # Pipeline overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Prospects", total_prospects, help="Total prospects in pipeline")
    with col2:
        st.metric("Active Conversations", active_conversations, help="Currently engaged prospects")
    with col3:
        st.metric("Proposals Sent", proposals_sent, help="Formal proposals sent")
    with col4:
        st.metric("Closed Won", closed_won, help="Successfully closed deals")
    
    st.markdown("---")
    
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    # Get unique values for filters from real data
    if pipeline_data and len(pipeline_data) > 0:
        stages = ["All"] + sorted(list(set([d.get('current_stage', 'Unknown') for d in pipeline_data])))
        sectors = ["All"] + sorted(list(set([d.get('sector_tags', 'Unknown') for d in pipeline_data if d.get('sector_tags')])))
        assigned_to = ["All"] + sorted(list(set([d.get('assigned_to', 'Unassigned') for d in pipeline_data if d.get('assigned_to')])))
    else:
        stages = ["All", "Initial Contact", "Intro Sent", "Follow-up Sent", "Proposal Sent", "Negotiation", "Closed Won", "Closed Lost"]
        sectors = ["All", "Technology", "Education", "Healthcare", "Environment"]
        assigned_to = ["All", "John Doe", "Sarah Johnson", "Mike Wilson"]
    
    with col1:
        stage_filter = st.selectbox("Stage:", stages)
    
    with col2:
        sector_filter = st.selectbox("Sector:", sectors)
    
    with col3:
        assigned_filter = st.selectbox("Assigned To:", assigned_to)
    
    with col4:
        search_term = st.text_input("🔍 Search:", placeholder="Organization name, contact, email...")
    
    # Pipeline data table
    st.subheader("📋 Pipeline Overview")
    
    with st.spinner("Loading pipeline data..."):
        try:
            # Get pipeline data from API (already loaded above for metrics)
            if pipeline_data and len(pipeline_data) > 0:
                # Apply filters
                filtered_data = pipeline_data.copy()
                
                # Stage filter
                if stage_filter != "All":
                    filtered_data = [d for d in filtered_data if d.get('current_stage') == stage_filter]
                
                # Sector filter
                if sector_filter != "All":
                    filtered_data = [d for d in filtered_data if d.get('sector_tags') == sector_filter]
                
                # Assigned to filter
                if assigned_filter != "All":
                    filtered_data = [d for d in filtered_data if d.get('assigned_to') == assigned_filter]
                
                # Search filter
                if search_term:
                    search_lower = search_term.lower()
                    filtered_data = [d for d in filtered_data if 
                                   search_lower in d.get('organization_name', '').lower() or
                                   search_lower in d.get('contact_person', '').lower() or
                                   search_lower in d.get('contact_email', '').lower()]
                
                # Display filtered data
                if filtered_data:
                    # Create a more user-friendly display
                    display_pipeline_data(filtered_data)
                    
                    # Show filter summary
                    if any([stage_filter != "All", sector_filter != "All", assigned_filter != "All", search_term]):
                        st.info(f"📊 Showing {len(filtered_data)} of {len(pipeline_data)} prospects")
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
                if pipeline_data:
                    # Create a simplified DataFrame for export
                    export_data = []
                    for donor in pipeline_data:
                        export_data.append({
                            'Organization': donor.get('organization_name', ''),
                            'Stage': donor.get('current_stage', ''),
                            'Contact Person': donor.get('contact_person', ''),
                            'Email': donor.get('contact_email', ''),
                            'Sector': donor.get('sector_tags', ''),
                            'Assigned To': donor.get('assigned_to', ''),
                            'Probability (%)': donor.get('probability', 0),
                            'Next Action': donor.get('next_action', ''),
                            'Next Action Date': donor.get('next_action_date', ''),
                            'Last Contact': donor.get('last_contact_date', ''),
                            'Notes': donor.get('notes', '')
                        })
                    
                    df = pd.DataFrame(export_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        "pipeline_data.csv",
                        "text/csv"
                    )
                    st.success(f"✅ Exported {len(export_data)} prospects")
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

def display_pipeline_data(data):
    """Display pipeline data in a user-friendly format"""
    for i, donor in enumerate(data):
        with st.expander(f"🏢 {donor.get('organization_name', 'Unknown Organization')} - {donor.get('current_stage', 'Unknown Stage')}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📋 Basic Info**")
                st.write(f"**Organization:** {donor.get('organization_name', 'N/A')}")
                st.write(f"**Stage:** {donor.get('current_stage', 'N/A')}")
                st.write(f"**Sector:** {donor.get('sector_tags', 'N/A')}")
                st.write(f"**Assigned To:** {donor.get('assigned_to', 'Unassigned')}")
                
            with col2:
                st.markdown("**👤 Contact Info**")
                st.write(f"**Contact:** {donor.get('contact_person', 'N/A')}")
                st.write(f"**Email:** {donor.get('contact_email', 'N/A')}")
                st.write(f"**Role:** {donor.get('contact_role', 'N/A')}")
                st.write(f"**Last Contact:** {donor.get('last_contact_date', 'N/A')}")
                
            with col3:
                st.markdown("**📈 Progress**")
                probability = donor.get('probability', 0)
                st.progress(probability / 100 if probability else 0)
                st.write(f"**Probability:** {probability}%")
                st.write(f"**Next Action:** {donor.get('next_action', 'N/A')}")
                st.write(f"**Due Date:** {donor.get('next_action_date', 'N/A')}")
            
            # Notes section
            if donor.get('notes'):
                st.markdown("**📝 Notes**")
                st.write(donor.get('notes'))
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("👁️ View Details", key=f"view_{i}"):
                    st.switch_page(f"pages/2_🏷️_Donor_Profile.py")
            with col2:
                if st.button("✉️ Send Email", key=f"email_{i}"):
                    st.switch_page(f"pages/3_✉️_Composer.py")
            with col3:
                if st.button("📝 Add Note", key=f"note_{i}"):
                    st.info("Note functionality coming soon!")
            with col4:
                if st.button("📊 Update Stage", key=f"stage_{i}"):
                    st.info("Stage update functionality coming soon!")

def display_sample_pipeline_data():
    """Display sample pipeline data when API is unavailable"""
    sample_data = [
        {
            "organization_name": "ABC Corporation",
            "current_stage": "Initial Contact",
            "assigned_to": "John Doe",
            "sector_tags": "Technology",
            "contact_person": "Jane Smith",
            "contact_email": "jane@abc.com",
            "contact_role": "CFO",
            "probability": 25,
            "next_action": "Send introduction email",
            "next_action_date": "2024-01-15",
            "last_contact_date": "2024-01-10",
            "notes": "Interested in education technology initiatives"
        },
        {
            "organization_name": "XYZ Foundation",
            "current_stage": "Proposal Sent",
            "assigned_to": "Sarah Johnson",
            "sector_tags": "Education",
            "contact_person": "Mike Wilson",
            "contact_email": "mike@xyz.org",
            "contact_role": "Program Director",
            "probability": 60,
            "next_action": "Follow up on proposal",
            "next_action_date": "2024-01-20",
            "last_contact_date": "2024-01-12",
            "notes": "Very interested in our rural education program"
        }
    ]
    
    display_pipeline_data(sample_data)

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
        if pipeline_data and len(pipeline_data) > 0:
            # Calculate real analytics from data
            total_prospects = len(pipeline_data)
            stages = [d.get('current_stage', 'Unknown') for d in pipeline_data]
            stage_counts = {}
            for stage in stages:
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            # Calculate average probability
            probabilities = [d.get('probability', 0) for d in pipeline_data if d.get('probability')]
            avg_probability = sum(probabilities) / len(probabilities) if probabilities else 0
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Stage Distribution**")
                for stage, count in sorted(stage_counts.items()):
                    percentage = (count / total_prospects) * 100
                    st.metric(stage, f"{count} ({percentage:.1f}%)")
            
            with col2:
                st.markdown("**📈 Key Metrics**")
                st.metric("Total Prospects", total_prospects)
                st.metric("Average Probability", f"{avg_probability:.1f}%")
                
                # Calculate active prospects (not closed)
                active_stages = ['Initial Contact', 'Intro Sent', 'Follow-up Sent', 'Proposal Sent', 'Negotiation']
                active_count = sum([count for stage, count in stage_counts.items() if stage in active_stages])
                st.metric("Active Prospects", active_count)
                
                # Calculate closed won rate
                closed_won = stage_counts.get('Closed Won', 0)
                closed_lost = stage_counts.get('Closed Lost', 0)
                total_closed = closed_won + closed_lost
                win_rate = (closed_won / total_closed * 100) if total_closed > 0 else 0
                st.metric("Win Rate", f"{win_rate:.1f}%")
        else:
            st.info("No data available for analytics. Connect to your Google Sheets to see real metrics.")

if __name__ == "__main__":
    main()