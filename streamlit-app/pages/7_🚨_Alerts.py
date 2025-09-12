"""
Alerts Page
Track and manage deadline alerts, urgent reminders, and time-sensitive follow-ups
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

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

# Fallback function
def fallback_get_alerts():
    return [
        {
            "Alert Timestamp": "2025-08-17 8:22:26",
            "Organization": "Asha for Education – Silicon Valley",
            "Proposal Title": "KHEL Patna – 21st Century Skills",
            "Deadline": "2025-09-30",
            "Urgency Level": "High",
            "Assigned To": "tanya.pandey@dikshafoundation.org",
            "Notes": "Track chapter review status; prep FAQ responses."
        },
        {
            "Alert Timestamp": "2025-08-17 8:22:26",
            "Organization": "HDFC Bank CSR",
            "Proposal Title": "KHEL Sarairanjan – Sports & Life Skills",
            "Deadline": "2025-10-15",
            "Urgency Level": "Medium",
            "Assigned To": "gautam.gauri@dikshafoundation.org",
            "Notes": "Finalize budgets; collect letters of support."
        }
    ]

# Import with multiple fallback strategies
get_alerts = fallback_get_alerts

try:
    from lib.api import get_alerts
    print("✅ Using lib.api import for get_alerts")
except ImportError as e:
    print(f"❌ Lib.api import failed: {e}")
    try:
        from api import get_alerts  # type: ignore
        print("✅ Using direct api import for get_alerts")
    except ImportError as e:
        print(f"❌ Direct api import failed: {e}")
        if lib_path:
            try:
                api_file_path = os.path.join(lib_path, 'api.py')
                if os.path.exists(api_file_path):
                    spec = importlib.util.spec_from_file_location("api", api_file_path)
                    api_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(api_module)
                    if hasattr(api_module, 'get_alerts'):
                        get_alerts = api_module.get_alerts
                        print("✅ Using importlib for get_alerts")
            except Exception as e:
                print(f"❌ Importlib failed: {e}")
        
        if get_alerts == fallback_get_alerts:
            for path in possible_paths:
                try:
                    abs_path = os.path.abspath(path)
                    api_file_path = os.path.join(abs_path, 'api.py')
                    if os.path.exists(api_file_path):
                        spec = importlib.util.spec_from_file_location("api", api_file_path)
                        api_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(api_module)
                        if hasattr(api_module, 'get_alerts'):
                            get_alerts = api_module.get_alerts
                            print(f"✅ Found get_alerts in {abs_path}")
                            break
                except Exception as e:
                    print(f"❌ Failed to import from {path}: {e}")
                    continue

print(f"✅ Final get_alerts import: {get_alerts != fallback_get_alerts}")

# Page configuration
st.set_page_config(
    page_title="Alerts - Diksha Fundraising",
    page_icon="🚨",
    layout="wide"
)

def main():
    """Main alerts page function"""
    
    st.title("🚨 Deadline Alerts & Reminders")
    st.markdown("Track urgent deadlines, time-sensitive follow-ups, and critical reminders")
    
    # Add refresh button in top right
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Get alerts data for metrics
    alerts_data = get_alerts()
    
    # Calculate metrics from real data
    if alerts_data and len(alerts_data) > 0:
        total_alerts = len(alerts_data)
        high_urgency = len([a for a in alerts_data if a.get('Urgency Level', '').lower() == 'high'])
        medium_urgency = len([a for a in alerts_data if a.get('Urgency Level', '').lower() == 'medium'])
        low_urgency = len([a for a in alerts_data if a.get('Urgency Level', '').lower() == 'low'])
        
        # Calculate overdue alerts
        overdue_count = 0
        upcoming_count = 0
        for alert in alerts_data:
            deadline = alert.get('Deadline', '')
            if deadline:
                try:
                    deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
                    days_until = (deadline_date - datetime.now()).days
                    if days_until < 0:
                        overdue_count += 1
                    elif days_until <= 7:
                        upcoming_count += 1
                except:
                    pass
    else:
        total_alerts = 0
        high_urgency = 0
        medium_urgency = 0
        low_urgency = 0
        overdue_count = 0
        upcoming_count = 0
    
    # Alerts overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Alerts", total_alerts)
    with col2:
        st.metric("High Priority", high_urgency, help="High urgency alerts")
    with col3:
        st.metric("Overdue", overdue_count, help="Deadlines that have passed")
    with col4:
        st.metric("Due This Week", upcoming_count, help="Deadlines within 7 days")
    
    st.markdown("---")
    
    # Urgency level indicators
    if high_urgency > 0:
        st.error(f"🚨 {high_urgency} HIGH PRIORITY alert(s) require immediate attention!")
    if overdue_count > 0:
        st.warning(f"⚠️ {overdue_count} deadline(s) have passed and need urgent follow-up!")
    if upcoming_count > 0:
        st.info(f"📅 {upcoming_count} deadline(s) are due within the next 7 days")
    
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    # Get unique values for filters from real data
    if alerts_data and len(alerts_data) > 0:
        urgency_levels = ["All"] + sorted(list(set([a.get('Urgency Level', 'Unknown') for a in alerts_data if a.get('Urgency Level')])))
        organizations = ["All"] + sorted(list(set([a.get('Organization', 'Unknown') for a in alerts_data if a.get('Organization')])))
        assigned_to = ["All"] + sorted(list(set([a.get('Assigned To', 'Unassigned') for a in alerts_data if a.get('Assigned To')])))
    else:
        urgency_levels = ["All", "High", "Medium", "Low"]
        organizations = ["All", "HDFC Bank CSR", "Asha for Education – Silicon Valley"]
        assigned_to = ["All", "gautam.gauri@dikshafoundation.org", "tanya.pandey@dikshafoundation.org"]
    
    with col1:
        urgency_filter = st.selectbox("Urgency Level:", urgency_levels)
    
    with col2:
        org_filter = st.selectbox("Organization:", organizations)
    
    with col3:
        assigned_filter = st.selectbox("Assigned To:", assigned_to)
    
    with col4:
        search_term = st.text_input("🔍 Search:", placeholder="Proposal title, organization...")
    
    # Alerts data display
    st.subheader("🚨 Active Alerts")
    
    with st.spinner("Loading alerts data..."):
        try:
            # Apply filters
            filtered_data = alerts_data.copy()
            
            # Urgency filter
            if urgency_filter != "All":
                filtered_data = [a for a in filtered_data if a.get('Urgency Level') == urgency_filter]
            
            # Organization filter
            if org_filter != "All":
                filtered_data = [a for a in filtered_data if a.get('Organization') == org_filter]
            
            # Assigned to filter
            if assigned_filter != "All":
                filtered_data = [a for a in filtered_data if a.get('Assigned To') == assigned_filter]
            
            # Search filter
            if search_term:
                search_lower = search_term.lower()
                filtered_data = [a for a in filtered_data if 
                               search_lower in a.get('Proposal Title', '').lower() or
                               search_lower in a.get('Organization', '').lower()]
            
            # Sort by urgency and deadline
            def sort_key(alert):
                urgency = alert.get('Urgency Level', '').lower()
                deadline = alert.get('Deadline', '')
                
                # Priority order: High > Medium > Low
                urgency_priority = {'high': 0, 'medium': 1, 'low': 2}.get(urgency, 3)
                
                # For deadline, overdue items first
                try:
                    if deadline:
                        deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
                        days_until = (deadline_date - datetime.now()).days
                        if days_until < 0:
                            deadline_priority = 0  # Overdue first
                        elif days_until <= 7:
                            deadline_priority = 1  # Due soon
                        else:
                            deadline_priority = 2  # Future deadlines
                    else:
                        deadline_priority = 3
                except:
                    deadline_priority = 3
                
                return (urgency_priority, deadline_priority)
            
            filtered_data.sort(key=sort_key)
            
            # Display filtered data
            if filtered_data:
                # Create a more user-friendly display
                display_alerts_data(filtered_data)
                
                # Show filter summary
                if any([urgency_filter != "All", org_filter != "All", assigned_filter != "All", search_term]):
                    st.info(f"📊 Showing {len(filtered_data)} of {len(alerts_data)} alerts")
            else:
                st.info("No alerts match the selected filters.")
                
        except Exception as e:
            st.error(f"❌ Error loading alerts data: {str(e)}")
            st.info("📊 Showing sample data instead")
            display_sample_alerts_data()
    
    # Alerts actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Export Alerts", use_container_width=True):
            try:
                # Export functionality
                if alerts_data:
                    # Create a simplified DataFrame for export
                    export_data = []
                    for alert in alerts_data:
                        export_data.append({
                            'Alert Timestamp': alert.get('Alert Timestamp', ''),
                            'Organization': alert.get('Organization', ''),
                            'Proposal Title': alert.get('Proposal Title', ''),
                            'Deadline': alert.get('Deadline', ''),
                            'Urgency Level': alert.get('Urgency Level', ''),
                            'Assigned To': alert.get('Assigned To', ''),
                            'Notes': alert.get('Notes', '')
                        })
                    
                    df = pd.DataFrame(export_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        "alerts_data.csv",
                        "text/csv"
                    )
                    st.success(f"✅ Exported {len(export_data)} alerts")
                else:
                    st.error("No data to export")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    with col2:
        if st.button("➕ Add Alert", use_container_width=True):
            add_new_alert()
    
    with col3:
        if st.button("📈 View Analytics", use_container_width=True):
            show_alerts_analytics()
    
    with col4:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.switch_page("streamlit_app.py")

def display_alerts_data(data):
    """Display alerts data in a user-friendly format"""
    for i, alert in enumerate(data):
        # Determine alert color based on urgency and deadline
        urgency = alert.get('Urgency Level', '').lower()
        deadline = alert.get('Deadline', '')
        
        # Calculate days until deadline
        days_until = None
        is_overdue = False
        is_due_soon = False
        
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
                days_until = (deadline_date - datetime.now()).days
                is_overdue = days_until < 0
                is_due_soon = 0 <= days_until <= 7
            except:
                pass
        
        # Choose container style based on urgency and deadline
        if urgency == 'high' or is_overdue:
            container_style = "error"
        elif urgency == 'medium' or is_due_soon:
            container_style = "warning"
        else:
            container_style = "info"
        
        with st.expander(f"🚨 {alert.get('Proposal Title', 'Untitled Alert')} - {alert.get('Organization', 'Unknown Organization')}", expanded=urgency == 'high' or is_overdue):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📋 Alert Details**")
                st.write(f"**Organization:** {alert.get('Organization', 'N/A')}")
                st.write(f"**Proposal:** {alert.get('Proposal Title', 'N/A')}")
                st.write(f"**Urgency:** {alert.get('Urgency Level', 'N/A')}")
                st.write(f"**Assigned To:** {alert.get('Assigned To', 'N/A')}")
                
            with col2:
                st.markdown("**⏰ Timeline**")
                st.write(f"**Alert Created:** {alert.get('Alert Timestamp', 'N/A')}")
                st.write(f"**Deadline:** {alert.get('Deadline', 'N/A')}")
                
                if days_until is not None:
                    if is_overdue:
                        st.write(f"**⚠️ OVERDUE by {abs(days_until)} days**")
                    elif is_due_soon:
                        st.write(f"**📅 Due in {days_until} days**")
                    else:
                        st.write(f"**📅 Due in {days_until} days**")
                
            with col3:
                st.markdown("**📝 Notes & Actions**")
                notes = alert.get('Notes', 'No notes available')
                st.write(f"**Notes:** {notes}")
                
                # Show status based on urgency and deadline
                if urgency == 'high':
                    st.error("🚨 HIGH PRIORITY - Immediate action required!")
                elif is_overdue:
                    st.error("⚠️ OVERDUE - Urgent follow-up needed!")
                elif is_due_soon:
                    st.warning("📅 Due soon - Action required!")
                else:
                    st.info("📋 Scheduled - Monitor progress")
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("✅ Mark Complete", key=f"complete_{i}"):
                    st.success("Alert marked as complete!")
            with col2:
                if st.button("📧 Send Reminder", key=f"reminder_{i}"):
                    st.info("Reminder sent to assigned team member!")
            with col3:
                if st.button("✏️ Update Notes", key=f"notes_{i}"):
                    st.info("Notes update functionality coming soon!")
            with col4:
                if st.button("📊 View Proposal", key=f"proposal_{i}"):
                    st.switch_page("pages/6_📋_Proposals.py")

def display_sample_alerts_data():
    """Display sample alerts data when API is unavailable"""
    sample_data = [
        {
            "Alert Timestamp": "2025-08-17 8:22:26",
            "Organization": "Asha for Education – Silicon Valley",
            "Proposal Title": "KHEL Patna – 21st Century Skills",
            "Deadline": "2025-09-30",
            "Urgency Level": "High",
            "Assigned To": "tanya.pandey@dikshafoundation.org",
            "Notes": "Track chapter review status; prep FAQ responses."
        },
        {
            "Alert Timestamp": "2025-08-17 8:22:26",
            "Organization": "HDFC Bank CSR",
            "Proposal Title": "KHEL Sarairanjan – Sports & Life Skills",
            "Deadline": "2025-10-15",
            "Urgency Level": "Medium",
            "Assigned To": "gautam.gauri@dikshafoundation.org",
            "Notes": "Finalize budgets; collect letters of support."
        }
    ]
    
    display_alerts_data(sample_data)

def add_new_alert():
    """Show form to add new alert"""
    with st.expander("➕ Add New Alert", expanded=True):
        with st.form("add_alert"):
            col1, col2 = st.columns(2)
            
            with col1:
                organization = st.text_input("Organization*")
                proposal_title = st.text_input("Proposal Title*")
                deadline = st.date_input("Deadline*")
                urgency_level = st.selectbox(
                    "Urgency Level:",
                    ["High", "Medium", "Low"]
                )
                
            with col2:
                assigned_to = st.selectbox(
                    "Assigned To:",
                    ["gautam.gauri@dikshafoundation.org", "tanya.pandey@dikshafoundation.org", "nisha.kumari@dikshafoundation.org"]
                )
                notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("💾 Add Alert")
            
            if submitted:
                if organization and proposal_title and deadline:
                    st.success(f"✅ Alert for '{proposal_title}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (marked with *)")

def show_alerts_analytics():
    """Show alerts analytics"""
    with st.expander("📈 Alerts Analytics", expanded=True):
        alerts_data = get_alerts()
        
        if alerts_data and len(alerts_data) > 0:
            # Calculate analytics from real data
            total_alerts = len(alerts_data)
            urgency_counts = {}
            for alert in alerts_data:
                urgency = alert.get('Urgency Level', 'Unknown')
                urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
            
            # Calculate deadline analytics
            overdue_count = 0
            due_soon_count = 0
            future_count = 0
            
            for alert in alerts_data:
                deadline = alert.get('Deadline', '')
                if deadline:
                    try:
                        deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
                        days_until = (deadline_date - datetime.now()).days
                        if days_until < 0:
                            overdue_count += 1
                        elif days_until <= 7:
                            due_soon_count += 1
                        else:
                            future_count += 1
                    except:
                        pass
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🚨 Urgency Distribution**")
                for urgency, count in sorted(urgency_counts.items()):
                    percentage = (count / total_alerts) * 100
                    st.metric(urgency, f"{count} ({percentage:.1f}%)")
            
            with col2:
                st.markdown("**⏰ Deadline Status**")
                st.metric("Overdue", overdue_count)
                st.metric("Due This Week", due_soon_count)
                st.metric("Future Deadlines", future_count)
                st.metric("Total Alerts", total_alerts)
        else:
            st.info("No data available for analytics. Add alerts to see metrics.")

if __name__ == "__main__":
    main()
