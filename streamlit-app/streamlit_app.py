"""
Diksha Fundraising Bot - Streamlit App
Main application file for the fundraising management system
"""

import streamlit as st
import sys
import os

# Configure UTF-8 encoding for consistent emoji support
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7 fallback
        pass

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

# Import with multiple fallback strategies - Enhanced with streamlit-authenticator
check_auth = fallback_check_auth
enhanced_check_auth = fallback_check_auth
show_auth_status = None

try:
    from lib.auth import check_auth, show_auth_status
    print("SUCCESS: Using streamlit-authenticator authentication")
except ImportError as e:
    print(f"ERROR: Auth import failed: {e}, trying fallback")
    try:
        from lib.auth import check_auth, show_auth_status
        print("SUCCESS: Using legacy authentication")
    except ImportError as e:
        print(f"ERROR: Lib package import failed: {e}")
        try:
            from auth import check_auth  # type: ignore
            print("SUCCESS: Using direct module import for check_auth")
        except ImportError as e:
            print(f"ERROR: Direct module import failed: {e}")
            if lib_path:
                try:
                    auth_file_path = os.path.join(lib_path, 'auth.py')
                    if os.path.exists(auth_file_path):
                        spec = importlib.util.spec_from_file_location("auth", auth_file_path)
                        auth_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(auth_module)
                        if hasattr(auth_module, 'check_auth'):
                            check_auth = auth_module.check_auth
                            show_auth_status = getattr(auth_module, 'show_auth_status', None)
                            print("SUCCESS: Using importlib for check_auth")
                except Exception as e:
                    print(f"ERROR: Importlib failed: {e}")

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
                                show_auth_status = getattr(auth_module, 'show_auth_status', None)
                                print(f"SUCCESS: Found check_auth in {abs_path}")
                                break
                    except Exception as e:
                        print(f"ERROR: Failed to import from {path}: {e}")
                        continue

print(f"SUCCESS: Final authentication import: Enhanced={check_auth != fallback_check_auth}")

# Import datetime for deduplication
from datetime import datetime
from typing import Dict, Any, Optional

# Deduplication function (same logic as Pipeline page)
def deduplicate_pipeline_data(raw_data):
    """Remove duplicates from pipeline data, keeping the newest record for each organization"""
    if not raw_data:
        return []

    def parse_datetime(value: str) -> Optional[datetime]:
        if not value:
            return None
        value = str(value).strip()
        if not value:
            return None
        candidate = value.replace('Z', '+00:00')
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            pass
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%m/%d/%Y'):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    def record_timestamp(record: Dict) -> datetime:
        for field in ('updated_at', 'last_contact_date', 'next_action_date'):
            candidate = parse_datetime(record.get(field))
            if candidate:
                return candidate
        return datetime.min

    duplicate_groups: Dict[str, Dict[str, Any]] = {}

    for record in raw_data:
        identifier = record.get('id') or record.get('organization_name') or ''
        key = identifier.strip().lower()
        if not key:
            key = f"record_{len(duplicate_groups)}_{hash(tuple(sorted(record.items())))}"
        group = duplicate_groups.setdefault(key, {'records': []})
        group['records'].append(record)

    pipeline_data = []
    for key, group in duplicate_groups.items():
        records = sorted(group['records'], key=record_timestamp, reverse=True)
        primary = dict(records[0])  # Use the newest record
        pipeline_data.append(primary)

    return pipeline_data

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
    print("SUCCESS: Using lib.api imports for dashboard metrics")
except ImportError as e:
    print(f"ERROR: Lib.api import failed: {e}")
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

    # Check authentication with enhanced login experience
    if not check_auth():
        # Authentication UI is handled by the auth module
        return

    # Show authentication status in sidebar if available
    if show_auth_status:
        show_auth_status()
    
    # Main dashboard content
    st.title("🏠 Diksha Fundraising Dashboard")
    st.markdown("Welcome to your fundraising management system")
    
    # Get real data for metrics and deduplicate
    raw_pipeline_data = get_pipeline_data()
    pipeline_data = deduplicate_pipeline_data(raw_pipeline_data)
    proposals_data = get_proposals_data()
    activity_data = get_activity_data()

    # Calculate real metrics (now using deduplicated data)
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
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 View Pipeline", use_container_width=True):
            st.switch_page("pages/1_📊_Pipeline.py")
    
    with col2:
        if st.button("✉️ Compose Email", use_container_width=True):
            st.switch_page("pages/3_✉️_Composer.py")
    
    with col3:
        if st.button("💬 WhatsApp Messages", use_container_width=True):
            st.switch_page("pages/8_💬_WhatsApp.py")
    
    with col4:
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

        # Quick navigation buttons
        if st.button("📊 Pipeline", use_container_width=True):
            st.switch_page("pages/1_📊_Pipeline.py")
        
        if st.button("🏷️ Donor Profiles", use_container_width=True):
            st.switch_page("pages/2_🏷️_Donor_Profile.py")
        
        if st.button("✉️ Email Composer", use_container_width=True):
            st.switch_page("pages/3_✉️_Composer.py")
        
        if st.button("💬 WhatsApp Messages", use_container_width=True):
            st.switch_page("pages/8_💬_WhatsApp.py")
        
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
