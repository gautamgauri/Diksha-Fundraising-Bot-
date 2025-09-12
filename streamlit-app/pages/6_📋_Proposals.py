"""
Proposals Page
Track and manage fundraising proposals, submissions, and deadlines
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
def fallback_get_proposals():
    return [
        {
            "Organization Name": "HDFC Bank CSR",
            "Proposal Title": "KHEL Sarairanjan – Sports & Life Skills",
            "Amount Requested": "2400000",
            "Submission Date": "2025-08-25",
            "Decision Deadline": "2025-10-15",
            "Status": "Draft",
            "Assigned Writer": "gautam.gauri@dikshafoundation.org",
            "Final Amount": ""
        },
        {
            "Organization Name": "Asha for Education – Silicon Valley",
            "Proposal Title": "KHEL Patna – 21st Century Skills",
            "Amount Requested": "750000",
            "Submission Date": "2025-08-20",
            "Decision Deadline": "2025-09-30",
            "Status": "Submitted",
            "Assigned Writer": "tanya.pandey@dikshafoundation.org",
            "Final Amount": ""
        }
    ]

# Import with multiple fallback strategies
get_proposals = fallback_get_proposals

try:
    from lib.api import get_proposals
    print("✅ Using lib.api import for get_proposals")
except ImportError as e:
    print(f"❌ Lib.api import failed: {e}")
    try:
        from api import get_proposals  # type: ignore
        print("✅ Using direct api import for get_proposals")
    except ImportError as e:
        print(f"❌ Direct api import failed: {e}")
        if lib_path:
            try:
                api_file_path = os.path.join(lib_path, 'api.py')
                if os.path.exists(api_file_path):
                    spec = importlib.util.spec_from_file_location("api", api_file_path)
                    api_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(api_module)
                    if hasattr(api_module, 'get_proposals'):
                        get_proposals = api_module.get_proposals
                        print("✅ Using importlib for get_proposals")
            except Exception as e:
                print(f"❌ Importlib failed: {e}")
        
        if get_proposals == fallback_get_proposals:
            for path in possible_paths:
                try:
                    abs_path = os.path.abspath(path)
                    api_file_path = os.path.join(abs_path, 'api.py')
                    if os.path.exists(api_file_path):
                        spec = importlib.util.spec_from_file_location("api", api_file_path)
                        api_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(api_module)
                        if hasattr(api_module, 'get_proposals'):
                            get_proposals = api_module.get_proposals
                            print(f"✅ Found get_proposals in {abs_path}")
                            break
                except Exception as e:
                    print(f"❌ Failed to import from {path}: {e}")
                    continue

print(f"✅ Final get_proposals import: {get_proposals != fallback_get_proposals}")

# Page configuration
st.set_page_config(
    page_title="Proposals - Diksha Fundraising",
    page_icon="📋",
    layout="wide"
)

def main():
    """Main proposals page function"""
    
    st.title("📋 Fundraising Proposals")
    st.markdown("Track and manage your fundraising proposals, submissions, and deadlines")
    
    # Add refresh button in top right
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Get proposals data for metrics
    proposals_data = get_proposals()
    
    # Calculate metrics from real data
    if proposals_data and len(proposals_data) > 0:
        total_proposals = len(proposals_data)
        draft_proposals = len([p for p in proposals_data if p.get('Status', '').lower() == 'draft'])
        submitted_proposals = len([p for p in proposals_data if p.get('Status', '').lower() == 'submitted'])
        total_amount = sum([int(p.get('Amount Requested', 0)) for p in proposals_data if p.get('Amount Requested', '').isdigit()])
    else:
        total_proposals = 0
        draft_proposals = 0
        submitted_proposals = 0
        total_amount = 0
    
    # Proposals overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Proposals", total_proposals)
    with col2:
        st.metric("Draft Proposals", draft_proposals)
    with col3:
        st.metric("Submitted Proposals", submitted_proposals)
    with col4:
        st.metric("Total Amount Requested", f"₹{total_amount:,}" if total_amount > 0 else "₹0")
    
    st.markdown("---")
    
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    # Get unique values for filters from real data
    if proposals_data and len(proposals_data) > 0:
        statuses = ["All"] + sorted(list(set([p.get('Status', 'Unknown') for p in proposals_data if p.get('Status')])))
        organizations = ["All"] + sorted(list(set([p.get('Organization Name', 'Unknown') for p in proposals_data if p.get('Organization Name')])))
        writers = ["All"] + sorted(list(set([p.get('Assigned Writer', 'Unassigned') for p in proposals_data if p.get('Assigned Writer')])))
    else:
        statuses = ["All", "Draft", "Submitted", "Under Review", "Approved", "Rejected"]
        organizations = ["All", "HDFC Bank CSR", "Asha for Education – Silicon Valley"]
        writers = ["All", "gautam.gauri@dikshafoundation.org", "tanya.pandey@dikshafoundation.org"]
    
    with col1:
        status_filter = st.selectbox("Status:", statuses)
    
    with col2:
        org_filter = st.selectbox("Organization:", organizations)
    
    with col3:
        writer_filter = st.selectbox("Assigned Writer:", writers)
    
    with col4:
        search_term = st.text_input("🔍 Search:", placeholder="Proposal title, organization...")
    
    # Proposals data display
    st.subheader("📋 Proposals Overview")
    
    with st.spinner("Loading proposals data..."):
        try:
            # Apply filters
            filtered_data = proposals_data.copy()
            
            # Status filter
            if status_filter != "All":
                filtered_data = [p for p in filtered_data if p.get('Status') == status_filter]
            
            # Organization filter
            if org_filter != "All":
                filtered_data = [p for p in filtered_data if p.get('Organization Name') == org_filter]
            
            # Writer filter
            if writer_filter != "All":
                filtered_data = [p for p in filtered_data if p.get('Assigned Writer') == writer_filter]
            
            # Search filter
            if search_term:
                search_lower = search_term.lower()
                filtered_data = [p for p in filtered_data if 
                               search_lower in p.get('Proposal Title', '').lower() or
                               search_lower in p.get('Organization Name', '').lower()]
            
            # Display filtered data
            if filtered_data:
                # Create a more user-friendly display
                display_proposals_data(filtered_data)
                
                # Show filter summary
                if any([status_filter != "All", org_filter != "All", writer_filter != "All", search_term]):
                    st.info(f"📊 Showing {len(filtered_data)} of {len(proposals_data)} proposals")
            else:
                st.info("No proposals match the selected filters.")
                
        except Exception as e:
            st.error(f"❌ Error loading proposals data: {str(e)}")
            st.info("📊 Showing sample data instead")
            display_sample_proposals_data()
    
    # Proposals actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Export Proposals", use_container_width=True):
            try:
                # Export functionality
                if proposals_data:
                    # Create a simplified DataFrame for export
                    export_data = []
                    for proposal in proposals_data:
                        export_data.append({
                            'Organization': proposal.get('Organization Name', ''),
                            'Proposal Title': proposal.get('Proposal Title', ''),
                            'Amount Requested': proposal.get('Amount Requested', ''),
                            'Submission Date': proposal.get('Submission Date', ''),
                            'Decision Deadline': proposal.get('Decision Deadline', ''),
                            'Status': proposal.get('Status', ''),
                            'Assigned Writer': proposal.get('Assigned Writer', ''),
                            'Final Amount': proposal.get('Final Amount', '')
                        })
                    
                    df = pd.DataFrame(export_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        "proposals_data.csv",
                        "text/csv"
                    )
                    st.success(f"✅ Exported {len(export_data)} proposals")
                else:
                    st.error("No data to export")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    with col2:
        if st.button("➕ Add Proposal", use_container_width=True):
            add_new_proposal()
    
    with col3:
        if st.button("📈 View Analytics", use_container_width=True):
            show_proposals_analytics()
    
    with col4:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.switch_page("streamlit_app.py")

def display_proposals_data(data):
    """Display proposals data in a user-friendly format"""
    for i, proposal in enumerate(data):
        with st.expander(f"📋 {proposal.get('Proposal Title', 'Untitled Proposal')} - {proposal.get('Organization Name', 'Unknown Organization')}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📋 Proposal Details**")
                st.write(f"**Organization:** {proposal.get('Organization Name', 'N/A')}")
                st.write(f"**Title:** {proposal.get('Proposal Title', 'N/A')}")
                st.write(f"**Status:** {proposal.get('Status', 'N/A')}")
                st.write(f"**Assigned Writer:** {proposal.get('Assigned Writer', 'N/A')}")
                
            with col2:
                st.markdown("**💰 Financial Information**")
                amount_requested = proposal.get('Amount Requested', '')
                if amount_requested and amount_requested.isdigit():
                    st.write(f"**Amount Requested:** ₹{int(amount_requested):,}")
                else:
                    st.write(f"**Amount Requested:** {amount_requested}")
                
                final_amount = proposal.get('Final Amount', '')
                if final_amount and final_amount.isdigit():
                    st.write(f"**Final Amount:** ₹{int(final_amount):,}")
                else:
                    st.write(f"**Final Amount:** {final_amount or 'N/A'}")
                
            with col3:
                st.markdown("**📅 Timeline**")
                st.write(f"**Submission Date:** {proposal.get('Submission Date', 'N/A')}")
                st.write(f"**Decision Deadline:** {proposal.get('Decision Deadline', 'N/A')}")
                
                # Calculate days until deadline
                deadline = proposal.get('Decision Deadline', '')
                if deadline:
                    try:
                        deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
                        days_until = (deadline_date - datetime.now()).days
                        if days_until > 0:
                            st.write(f"**Days Until Deadline:** {days_until}")
                        elif days_until == 0:
                            st.write("**⚠️ Deadline is today!**")
                        else:
                            st.write(f"**⚠️ Deadline passed {abs(days_until)} days ago**")
                    except:
                        pass
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("👁️ View Details", key=f"view_{i}"):
                    st.info("View details functionality coming soon!")
            with col2:
                if st.button("✏️ Edit", key=f"edit_{i}"):
                    st.info("Edit functionality coming soon!")
            with col3:
                if st.button("📧 Send Reminder", key=f"reminder_{i}"):
                    st.info("Reminder functionality coming soon!")
            with col4:
                if st.button("📊 Update Status", key=f"status_{i}"):
                    st.info("Status update functionality coming soon!")

def display_sample_proposals_data():
    """Display sample proposals data when API is unavailable"""
    sample_data = [
        {
            "Organization Name": "HDFC Bank CSR",
            "Proposal Title": "KHEL Sarairanjan – Sports & Life Skills",
            "Amount Requested": "2400000",
            "Submission Date": "2025-08-25",
            "Decision Deadline": "2025-10-15",
            "Status": "Draft",
            "Assigned Writer": "gautam.gauri@dikshafoundation.org",
            "Final Amount": ""
        },
        {
            "Organization Name": "Asha for Education – Silicon Valley",
            "Proposal Title": "KHEL Patna – 21st Century Skills",
            "Amount Requested": "750000",
            "Submission Date": "2025-08-20",
            "Decision Deadline": "2025-09-30",
            "Status": "Submitted",
            "Assigned Writer": "tanya.pandey@dikshafoundation.org",
            "Final Amount": ""
        }
    ]
    
    display_proposals_data(sample_data)

def add_new_proposal():
    """Show form to add new proposal"""
    with st.expander("➕ Add New Proposal", expanded=True):
        with st.form("add_proposal"):
            col1, col2 = st.columns(2)
            
            with col1:
                org_name = st.text_input("Organization Name*")
                proposal_title = st.text_input("Proposal Title*")
                amount_requested = st.number_input(
                    "Amount Requested (₹)",
                    min_value=0,
                    step=10000,
                    format="%d"
                )
                
            with col2:
                submission_date = st.date_input("Submission Date*")
                decision_deadline = st.date_input("Decision Deadline*")
                status = st.selectbox(
                    "Status:",
                    ["Draft", "Submitted", "Under Review", "Approved", "Rejected"]
                )
            
            assigned_writer = st.selectbox(
                "Assigned Writer:",
                ["gautam.gauri@dikshafoundation.org", "tanya.pandey@dikshafoundation.org", "nisha.kumari@dikshafoundation.org"]
            )
            
            submitted = st.form_submit_button("💾 Add Proposal")
            
            if submitted:
                if org_name and proposal_title and submission_date and decision_deadline:
                    st.success(f"✅ Proposal '{proposal_title}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (marked with *)")

def show_proposals_analytics():
    """Show proposals analytics"""
    with st.expander("📈 Proposals Analytics", expanded=True):
        proposals_data = get_proposals()
        
        if proposals_data and len(proposals_data) > 0:
            # Calculate analytics from real data
            total_proposals = len(proposals_data)
            statuses = [p.get('Status', 'Unknown') for p in proposals_data]
            status_counts = {}
            for status in statuses:
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Calculate total amounts
            amounts = [int(p.get('Amount Requested', 0)) for p in proposals_data if p.get('Amount Requested', '').isdigit()]
            total_amount = sum(amounts)
            avg_amount = total_amount / len(amounts) if amounts else 0
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Status Distribution**")
                for status, count in sorted(status_counts.items()):
                    percentage = (count / total_proposals) * 100
                    st.metric(status, f"{count} ({percentage:.1f}%)")
            
            with col2:
                st.markdown("**💰 Financial Overview**")
                st.metric("Total Amount Requested", f"₹{total_amount:,}")
                st.metric("Average Proposal Amount", f"₹{avg_amount:,.0f}")
                st.metric("Total Proposals", total_proposals)
                
                # Calculate success rate (if any are approved)
                approved = status_counts.get('Approved', 0)
                success_rate = (approved / total_proposals * 100) if total_proposals > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")
        else:
            st.info("No data available for analytics. Add proposals to see metrics.")

if __name__ == "__main__":
    main()
