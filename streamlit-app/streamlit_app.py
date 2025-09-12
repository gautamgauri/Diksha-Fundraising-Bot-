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

# Import API functions for dashboard metrics
def fallback_get_pipeline_data():
    return []

def fallback_get_proposals_data():
    return []

def fallback_get_activity_data():
    return []

get_pipeline_data = fallback_get_pipeline_data
get_proposals_data = fallback_get_proposals_data
get_activity_data = fallback_get_activity_data

try:
    from lib.api import get_cached_pipeline_data, get_proposals, get_activity_log
    get_pipeline_data = get_cached_pipeline_data
    get_proposals_data = get_proposals
    get_activity_data = get_activity_log
    print("✅ Using lib.api imports for dashboard metrics")
except ImportError as e:
    print(f"❌ Lib.api import failed: {e}")
    # Fallback functions already set

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
    
    # Get real data for metrics
    pipeline_data = get_pipeline_data()
    proposals_data = get_proposals_data()
    activity_data = get_activity_data()
    
    # Calculate real metrics
    total_donors = len(pipeline_data) if pipeline_data else 0
    total_proposals = len(proposals_data) if proposals_data else 0
    total_activities = len(activity_data) if activity_data else 0
    
    # Calculate total proposal amounts
    total_proposal_amount = 0
    if proposals_data:
        for proposal in proposals_data:
            amount = proposal.get('Amount Requested', '')
            if amount and amount.isdigit():
                total_proposal_amount += int(amount)
    
    # Calculate success rate (submitted vs total proposals)
    submitted_proposals = 0
    if proposals_data:
        submitted_proposals = len([p for p in proposals_data if p.get('Status', '').lower() == 'submitted'])
    
    success_rate = (submitted_proposals / total_proposals * 100) if total_proposals > 0 else 0
    
    # Quick stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Prospects",
            value=total_donors,
            help="Organizations in your pipeline"
        )
    
    with col2:
        st.metric(
            label="Active Proposals",
            value=total_proposals,
            help="Proposals in progress"
        )
    
    with col3:
        st.metric(
            label="Total Interactions",
            value=total_activities,
            help="Communication activities logged"
        )
    
    with col4:
        st.metric(
            label="Proposal Success Rate",
            value=f"{success_rate:.1f}%",
            help="Submitted proposals vs total"
        )
    
    st.markdown("---")
    
    # Success Metrics Section
    st.subheader("📈 Success Metrics")
    
    # Financial Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Proposal Value",
            value=f"₹{total_proposal_amount:,}" if total_proposal_amount > 0 else "₹0",
            help="Total amount requested in all proposals"
        )
    
    with col2:
        # Calculate average proposal amount
        avg_proposal_amount = total_proposal_amount / total_proposals if total_proposals > 0 else 0
        st.metric(
            label="Average Proposal Size",
            value=f"₹{avg_proposal_amount:,.0f}" if avg_proposal_amount > 0 else "₹0",
            help="Average amount per proposal"
        )
    
    with col3:
        # Calculate pipeline stages distribution
        if pipeline_data:
            building_count = len([d for d in pipeline_data if d.get('current_stage', '').lower() == 'building'])
            engaged_count = len([d for d in pipeline_data if d.get('current_stage', '').lower() == 'engaged'])
            st.metric(
                label="Active Prospects",
                value=building_count + engaged_count,
                help="Prospects in Building or Engaged stages"
            )
        else:
            st.metric(
                label="Active Prospects",
                value="0",
                help="Prospects in Building or Engaged stages"
            )
    
    with col4:
        # Calculate team performance
        if proposals_data:
            writers = [p.get('Assigned Writer', '') for p in proposals_data if p.get('Assigned Writer')]
            unique_writers = len(set(writers))
            st.metric(
                label="Active Writers",
                value=unique_writers,
                help="Team members with assigned proposals"
            )
        else:
            st.metric(
                label="Active Writers",
                value="0",
                help="Team members with assigned proposals"
            )
    
    # Monthly Performance Chart (placeholder for future enhancement)
    st.markdown("---")
    st.subheader("📊 Monthly Performance")
    
    # Create sample monthly data for demonstration
    monthly_data = {
        'Month': ['January 2024', 'February 2024', 'March 2024'],
        'New Prospects': [15, 12, 18],
        'Proposals Submitted': [8, 6, 10],
        'Grants Secured': [3, 2, 4],
        'Total Amount (₹L)': [15, 12, 20]
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📈 Recent Performance**")
        for i, month in enumerate(monthly_data['Month']):
            with st.container():
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Prospects", monthly_data['New Prospects'][i])
                with col_b:
                    st.metric("Proposals", monthly_data['Proposals Submitted'][i])
                with col_c:
                    st.metric("Amount", f"₹{monthly_data['Total Amount (₹L)'][i]}L")
                st.caption(f"{month}")
                if i < len(monthly_data['Month']) - 1:
                    st.markdown("---")
    
    with col2:
        st.markdown("**🎯 Key Performance Indicators**")
        
        # Calculate KPIs from real data
        if pipeline_data and proposals_data:
            # Conversion rate (proposals to prospects ratio)
            conversion_rate = (total_proposals / total_donors * 100) if total_donors > 0 else 0
            st.metric("Conversion Rate", f"{conversion_rate:.1f}%", help="Proposals per prospect")
            
            # Pipeline health (active vs total)
            if pipeline_data:
                active_stages = ['building', 'engaged', 'proposal sent', 'negotiation']
                active_count = len([d for d in pipeline_data if d.get('current_stage', '').lower() in active_stages])
                pipeline_health = (active_count / total_donors * 100) if total_donors > 0 else 0
                st.metric("Pipeline Health", f"{pipeline_health:.1f}%", help="Active prospects percentage")
            
            # Team productivity
            if activity_data:
                avg_activities_per_prospect = total_activities / total_donors if total_donors > 0 else 0
                st.metric("Team Productivity", f"{avg_activities_per_prospect:.1f}", help="Activities per prospect")
            
            # Proposal efficiency
            if proposals_data:
                draft_count = len([p for p in proposals_data if p.get('Status', '').lower() == 'draft'])
                efficiency = ((total_proposals - draft_count) / total_proposals * 100) if total_proposals > 0 else 0
                st.metric("Proposal Efficiency", f"{efficiency:.1f}%", help="Non-draft proposals percentage")
        else:
            st.info("Add data to see KPIs")
    
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
        if st.button("🚨 View Alerts", use_container_width=True):
            st.switch_page("pages/7_🚨_Alerts.py")
    
    # Recent activities preview
    st.subheader("📋 Recent Activities")
    
    # Show real recent activities if available
    if activity_data and len(activity_data) > 0:
        # Show last 4 activities
        recent_activities = activity_data[-4:] if len(activity_data) >= 4 else activity_data
        
        for activity in reversed(recent_activities):  # Show most recent first
            org_name = activity.get('Organization Name', 'Unknown Organization')
            interaction_type = activity.get('Interaction Type', 'Activity')
            date = activity.get('Date', 'Unknown Date')
            summary = activity.get('Summary/Notes', 'No details available')
            
            st.markdown(f"**{date}** - {interaction_type} with {org_name}")
            if summary:
                st.caption(f"   {summary}")
    else:
        # Fallback to sample data
        recent_activities = [
            {"time": "2024-01-15", "activity": "Email sent to HDFC Bank CSR", "details": "Sent partnership proposal for education technology initiatives"},
            {"time": "2024-01-14", "activity": "Phone call with Asha for Education", "details": "Discussed rural education program funding opportunities"},
            {"time": "2024-01-13", "activity": "Proposal submitted to TechCorp Industries", "details": "KHEL Sarairanjan – Sports & Life Skills proposal"},
            {"time": "2024-01-12", "activity": "Follow-up call with EduFoundation Trust", "details": "KHEL Patna – 21st Century Skills discussion"}
        ]
        
        for activity in recent_activities:
            st.markdown(f"**{activity['time']}** - {activity['activity']}")
            if 'details' in activity:
                st.caption(f"   {activity['details']}")
    
    # Navigation sidebar
    with st.sidebar:
        st.title("🏠 Navigation")
        st.markdown("---")
        
        # Show user credentials for admin (if available)
        try:
            from lib.auth import show_user_credentials
            show_user_credentials()
        except:
            pass
        
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
        
        if st.button("📋 Proposals", use_container_width=True):
            st.switch_page("pages/6_📋_Proposals.py")
        
        if st.button("🚨 Alerts", use_container_width=True):
            st.switch_page("pages/7_🚨_Alerts.py")
        
        st.markdown("---")
        st.markdown("**Diksha Fundraising Bot**")
        st.markdown("Version 1.0")

if __name__ == "__main__":
    main()