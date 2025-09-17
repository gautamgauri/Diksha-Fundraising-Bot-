"""
Pipeline Management Page
Displays and manages the fundraising pipeline
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional

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

def fallback_update_donor(donor_id: str, updates: Dict[str, Any]) -> bool:
    print(f"Fallback: update_donor called for {donor_id} with {updates}")
    return False

def fallback_update_donor_database(donor_data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"Fallback: update_donor_database called with {donor_data}")
    return {"success": False, "error": "update_donor_database not available"}

def fallback_archive_duplicate_entries(payload: Dict[str, Any]) -> Dict[str, Any]:
    print(f"Fallback: archive_duplicate_entries called with {payload}")
    return {"success": False, "error": "archive_duplicate_entries not available"}

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

MERGE_FIELDS = [
    'organization_name',
    'current_stage',
    'assigned_to',
    'next_action',
    'next_action_date',
    'last_contact_date',
    'sector_tags',
    'probability',
    'contact_person',
    'contact_email',
    'contact_role',
    'notes',
]

FIELD_LABELS = {
    'organization_name': 'Organization Name',
    'current_stage': 'Current Stage',
    'assigned_to': 'Assigned To',
    'next_action': 'Next Action',
    'next_action_date': 'Next Action Date',
    'last_contact_date': 'Last Contact Date',
    'sector_tags': 'Sector Tags',
    'probability': 'Probability (%)',
    'contact_person': 'Contact Person',
    'contact_email': 'Contact Email',
    'contact_role': 'Contact Role',
    'notes': 'Notes',
}

STAGE_MAPPING = {
    "initial research": "Initial Outreach",
    "first contact": "Initial Outreach",
    "initial contact": "Initial Outreach",
    "intro sent": "Initial Outreach",
    "initial outreach": "Initial Outreach",
    "in prospect list": "In Prospect List",
    "engaged": "Engaged",
    "relationship building": "Engaged",
    "follow-up sent": "Engaged",
    "meeting scheduled": "Engaged",
    "proposal sent": "Proposal Sent",
    "negotiation": "Proposal Sent",
    "decision pending": "Proposal Sent",
    "grant received": "Grant Received",
    "closed won": "Grant Received",
    "closed lost": "Rejected",
    "rejected": "Rejected",
}


def map_stage(stage_value: Optional[str]) -> str:
    if not stage_value:
        return "Unknown"
    normalized = stage_value.strip().lower()
    return STAGE_MAPPING.get(normalized, stage_value.strip())

# Import with multiple fallback strategies
log_activity = fallback_log_activity
get_cached_pipeline_data = fallback_get_cached_pipeline_data
require_auth = fallback_require_auth
show_auth_status = fallback_show_auth_status
update_donor = fallback_update_donor
update_donor_database = fallback_update_donor_database
archive_duplicate_entries = fallback_archive_duplicate_entries

try:
    from lib import (
        log_activity,
        get_cached_pipeline_data,
        require_auth,
        show_auth_status,
        update_donor,
        update_donor_database,
        archive_duplicate_entries,
    )
    print("Using lib package imports")
except ImportError as e:
    print(f"Lib package import failed: {e}")
    try:
        from api import (
            log_activity,
            get_cached_pipeline_data,
            update_donor,
            update_donor_database,
            archive_duplicate_entries,
        )  # type: ignore
        from auth import require_auth, show_auth_status  # type: ignore
        print("Using direct module imports")
    except ImportError as e:
        print(f"Direct module import failed: {e}")
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
                    if hasattr(api_module, 'update_donor'):
                        update_donor = api_module.update_donor
                    if hasattr(api_module, 'update_donor_database'):
                        update_donor_database = api_module.update_donor_database
                    if hasattr(api_module, 'archive_duplicate_entries'):
                        archive_duplicate_entries = api_module.archive_duplicate_entries
                    print("Using importlib for api module")

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
                    print("Using importlib for auth module")
            except Exception as e:
                print(f"Importlib failed: {e}")
        
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
                    if hasattr(api_module, 'update_donor'):
                        update_donor = api_module.update_donor
                    if hasattr(api_module, 'update_donor_database'):
                        update_donor_database = api_module.update_donor_database
                    if hasattr(api_module, 'archive_duplicate_entries'):
                        archive_duplicate_entries = api_module.archive_duplicate_entries
                    print(f"Found api functions in {abs_path}")

                    if os.path.exists(auth_file_path):
                        spec = importlib.util.spec_from_file_location("auth", auth_file_path)
                        auth_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(auth_module)
                        if hasattr(auth_module, 'require_auth'):
                            require_auth = auth_module.require_auth
                        if hasattr(auth_module, 'show_auth_status'):
                            show_auth_status = auth_module.show_auth_status
                        print(f"Found auth functions in {abs_path}")
                        
                except Exception as e:
                    print(f"Failed to import from {path}: {e}")
                    continue

print(
    "Final imports - log_activity: {0}, get_cached_pipeline_data: {1}, require_auth: {2}, show_auth_status: {3}, update_donor: {4}, update_donor_database: {5}, archive_duplicate_entries: {6}".format(
        log_activity != fallback_log_activity,
        get_cached_pipeline_data != fallback_get_cached_pipeline_data,
        require_auth != fallback_require_auth,
        show_auth_status != fallback_show_auth_status,
        update_donor != fallback_update_donor,
        update_donor_database != fallback_update_donor_database,
        archive_duplicate_entries != fallback_archive_duplicate_entries,
    )
)

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
    raw_pipeline_data = get_cached_pipeline_data() or []

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
    primary_map: Dict[str, Dict] = {}
    duplicate_summary: Dict[str, Dict[str, Any]] = {}

    for record in raw_pipeline_data:
        identifier = record.get('id') or record.get('organization_name') or ''
        key = identifier.strip().lower()
        if not key:
            key = f"record_{len(duplicate_groups)}_{hash(tuple(sorted(record.items())))}"
        group = duplicate_groups.setdefault(key, {'records': []})
        group['records'].append(record)

    pipeline_data = []
    for key, group in duplicate_groups.items():
        records = sorted(group['records'], key=record_timestamp, reverse=True)
        primary = dict(records[0])
        primary_map[key] = primary
        pipeline_data.append(primary)
        identifier = records[0].get('organization_name') or records[0].get('id') or key
        if len(records) > 1:
            duplicate_summary[key] = {
                'records': records,
                'identifier': identifier,
            }

    pipeline_merges = st.session_state.setdefault('pipeline_merges', {})
    for key, merged in pipeline_merges.items():
        if key in primary_map:
            primary_map[key].update(merged)

    pipeline_data = list(primary_map.values())
    
    # Calculate metrics from real data
    if pipeline_data and len(pipeline_data) > 0:
        total_prospects = len(pipeline_data)

        def stage_matches(record, targets):
            mapped = map_stage(record.get('current_stage'))
            return mapped in targets

        active_targets = {
            'Initial Outreach',
            'In Prospect List',
            'Engaged',
        }

        proposals_targets = {'Proposal Sent'}

        grant_targets = {'Grant Received'}

        active_conversations = sum(1 for d in pipeline_data if stage_matches(d, active_targets))
        proposals_sent = sum(1 for d in pipeline_data if stage_matches(d, proposals_targets))
        grant_received = sum(1 for d in pipeline_data if stage_matches(d, grant_targets))
    else:
        total_prospects = 0
        active_conversations = 0
        proposals_sent = 0
        grant_received = 0
    
    # Pipeline overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Prospects", total_prospects, help="Total prospects in pipeline")
    with col2:
        st.metric("Active Conversations", active_conversations, help="Currently engaged prospects")
    with col3:
        st.metric("Proposals Sent", proposals_sent, help="Formal proposals sent")
    with col4:
        st.metric("Grant Received", grant_received, help="Successfully secured funding")
    
    duplicate_groups_for_ui = {
        key: value for key, value in duplicate_summary.items() if len(value['records']) > 1
    }

    if duplicate_groups_for_ui:
        st.warning(
            f"Detected {len(duplicate_groups_for_ui)} prospects with duplicate entries. "
            "The latest record is shown below; you can merge fields from older entries."
        )

        def format_duplicate_option(key: str) -> str:
            info = duplicate_groups_for_ui[key]
            return f"{info['identifier']} ({len(info['records'])} entries)"

        selected_duplicate_key = st.selectbox(
            "Select a duplicate prospect to review",
            options=list(duplicate_groups_for_ui.keys()),
            format_func=format_duplicate_option,
            key="duplicate_selector",
        )

        selected_group = duplicate_groups_for_ui[selected_duplicate_key]
        records = selected_group['records']

        with st.expander("View duplicate records", expanded=False):
            st.dataframe(pd.DataFrame(records))

        with st.form(f"merge_form_{selected_duplicate_key}"):
            st.markdown("Select preferred values for each field")
            selection_indices: Dict[str, int] = {}
            existing_merge = pipeline_merges.get(selected_duplicate_key, {})

            for field in MERGE_FIELDS:
                label = FIELD_LABELS[field]
                options = []
                for idx, rec in enumerate(records):
                    source_name = rec.get('organization_name') or rec.get('id') or f"Record {idx + 1}"
                    value = rec.get(field, '')
                    display_value = value if value not in (None, '') else '—'
                    options.append((idx, f"{source_name}: {display_value}"))

                default_idx = next((idx for idx, rec in enumerate(records) if rec.get(field)), 0)
                if field in existing_merge:
                    for idx, rec in enumerate(records):
                        if rec.get(field) == existing_merge[field]:
                            default_idx = idx
                            break

                selection_indices[field] = st.selectbox(
                    label,
                    options=[idx for idx, _ in options],
                    format_func=lambda i, choices=options: choices[i][1],
                    index=default_idx,
                    key=f"merge_select_{selected_duplicate_key}_{field}",
                )

            combine_notes = st.checkbox(
                "Combine notes from all entries", value=False, key=f"merge_notes_{selected_duplicate_key}"
            )

            submitted_merge = st.form_submit_button("Merge selected values")
            if submitted_merge:
                merged_record = {}
                for field, idx in selection_indices.items():
                    merged_record[field] = records[idx].get(field, '')

                if combine_notes:
                    notes = []
                    for rec in records:
                        note = rec.get('notes')
                        if note and note not in notes:
                            notes.append(note)
                    merged_record['notes'] = "\n".join(notes)

                pipeline_merges[selected_duplicate_key] = merged_record
                if selected_duplicate_key in primary_map:
                    primary_map[selected_duplicate_key].update(merged_record)
                try:
                    identifier = (
                        primary_map[selected_duplicate_key].get('id')
                        or primary_map[selected_duplicate_key].get('organization_name')
                        or selected_duplicate_key
                    )
                    log_activity('merge_duplicates', str(identifier), 'Merged duplicate pipeline entries')
                except Exception:
                    pass

                update_success = False
                update_error: Optional[str] = None
                try:
                    donor_id = primary_map[selected_duplicate_key].get('id')
                    if donor_id:
                        update_success = update_donor(donor_id, merged_record)
                    else:
                        donor_name = (
                            primary_map[selected_duplicate_key].get('organization_name')
                            or selected_duplicate_key
                        )
                        payload = {**primary_map[selected_duplicate_key], **merged_record}
                        payload['donor_name'] = donor_name
                        response = update_donor_database(payload)
                        update_success = bool(response and response.get('success'))
                        if response and not response.get('success'):
                            update_error = response.get('error')
                except Exception as err:
                    update_error = str(err)

                if update_success:
                    st.success("Merged values applied and saved to Sheets. Cache will refresh on next load.")
                    try:
                        st.cache_data.clear()
                    except Exception:
                        pass
                else:
                    message = "Merged values applied locally, but saving to Sheets failed."
                    if update_error:
                        message += f" Details: {update_error}"
                    st.warning(message)

                st.experimental_rerun()

        older_records = records[1:]
        if older_records:
            archive_clicked = st.button(
                "Archive older entries",
                key=f"archive_{selected_duplicate_key}",
                help="Move historical duplicates to an archive sheet",
            )
            if archive_clicked:
                payload = {
                    "primary_id": primary_map[selected_duplicate_key].get('id'),
                    "identifier": selected_group['identifier'],
                    "records": older_records,
                }
                archive_response = archive_duplicate_entries(payload)
                if archive_response and archive_response.get('success'):
                    st.success("Older entries archived successfully. Cache will refresh on next load.")
                    try:
                        st.cache_data.clear()
                    except Exception:
                        pass
                    st.experimental_rerun()
                else:
                    error_msg = "Archiving failed."
                    if archive_response and archive_response.get('error'):
                        error_msg += f" Details: {archive_response['error']}"
                    st.warning(error_msg)

    st.markdown("---")
    
    # Enhanced Search Bar - Make it prominent
    st.subheader("🔍 Search Pipeline")
    
    # Search input with clear button
    col1, col2 = st.columns([4, 1])
    with col1:
        search_term = st.text_input(
            "Search your fundraising pipeline:", 
            placeholder="Search by organization, contact person, email, notes, sector, or assigned person...",
            help="Search across all prospect fields including organization name, contact details, notes, and more",
            key="main_search"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        if st.button("🗑️ Clear Search", help="Clear the search field"):
            st.session_state.main_search = ""
            st.rerun()
    
    # Quick search suggestions if search term is provided
    if search_term:
        search_lower = search_term.lower()
        if pipeline_data:
            # Count matches across different fields
            org_matches = len([d for d in pipeline_data if search_lower in d.get('organization_name', '').lower()])
            contact_matches = len([d for d in pipeline_data if search_lower in d.get('contact_person', '').lower()])
            email_matches = len([d for d in pipeline_data if search_lower in d.get('contact_email', '').lower()])
            notes_matches = len([d for d in pipeline_data if search_lower in d.get('notes', '').lower()])
            sector_matches = len([d for d in pipeline_data if search_lower in d.get('sector_tags', '').lower()])
            assigned_matches = len([d for d in pipeline_data if search_lower in d.get('assigned_to', '').lower()])
            
            total_matches = len([d for d in pipeline_data if 
                               search_lower in d.get('organization_name', '').lower() or
                               search_lower in d.get('contact_person', '').lower() or
                               search_lower in d.get('contact_email', '').lower() or
                               search_lower in d.get('notes', '').lower() or
                               search_lower in d.get('sector_tags', '').lower() or
                               search_lower in d.get('assigned_to', '').lower()])
            
            if total_matches > 0:
                match_details = []
                if org_matches > 0: match_details.append(f"{org_matches} organizations")
                if contact_matches > 0: match_details.append(f"{contact_matches} contacts")
                if email_matches > 0: match_details.append(f"{email_matches} emails")
                if notes_matches > 0: match_details.append(f"{notes_matches} notes")
                if sector_matches > 0: match_details.append(f"{sector_matches} sectors")
                if assigned_matches > 0: match_details.append(f"{assigned_matches} assigned")
                
                st.info(f"🎯 Found **{total_matches}** matches: {', '.join(match_details)}")
            else:
                st.warning(f"🔍 No matches found for '{search_term}'. Try a different search term.")
    
    # Quick Search Shortcuts
    if not search_term:  # Only show shortcuts when no search is active
        st.markdown("**🚀 Quick Search Shortcuts:**")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("🏢 High Value", help="Show prospects with expected amount > ₹50L"):
                st.session_state.quick_search_filter = "high_value"
                st.rerun()
        
        with col2:
            if st.button("📄 Proposals", help="Show prospects with proposals sent"):
                st.session_state.quick_search_filter = "proposals"
                st.rerun()
        
        with col3:
            if st.button("🤝 Active", help="Show actively engaged prospects"):
                st.session_state.quick_search_filter = "active"
                st.rerun()
        
        with col4:
            if st.button("⚠️ Overdue", help="Show prospects with overdue actions"):
                st.session_state.quick_search_filter = "overdue"
                st.rerun()
        
        with col5:
            if st.button("🔄 Clear All", help="Clear all filters"):
                if hasattr(st.session_state, 'quick_search_filter'):
                    del st.session_state.quick_search_filter
                st.rerun()
    
    # Filters Section
    st.subheader("🔧 Additional Filters")
    col1, col2, col3 = st.columns(3)
    
    # Get unique values for filters from real data
    if pipeline_data and len(pipeline_data) > 0:
        stages = ["All"] + sorted(list(set([d.get('current_stage', 'Unknown') for d in pipeline_data])))
        sectors = ["All"] + sorted(list(set([d.get('sector_tags', 'Unknown') for d in pipeline_data if d.get('sector_tags')])))
        assigned_to = ["All"] + sorted(list(set([d.get('assigned_to', 'Unassigned') for d in pipeline_data if d.get('assigned_to')])))
    else:
        stages = ["All", "Initial Outreach", "In Prospect List", "Engaged", "Proposal Sent", "Grant Received", "Rejected"]
        sectors = ["All", "Technology", "Education", "Healthcare", "Environment"]
        assigned_to = ["All", "John Doe", "Sarah Johnson", "Mike Wilson"]
    
    with col1:
        stage_filter = st.selectbox("Filter by Stage:", stages)
    
    with col2:
        sector_filter = st.selectbox("Filter by Sector:", sectors)
    
    with col3:
        assigned_filter = st.selectbox("Filter by Assigned:", assigned_to)
    
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
                
                # Enhanced search filter - search across all relevant fields
                if search_term:
                    search_lower = search_term.lower()
                    filtered_data = [d for d in filtered_data if 
                                   search_lower in d.get('organization_name', '').lower() or
                                   search_lower in d.get('contact_person', '').lower() or
                                   search_lower in d.get('contact_email', '').lower() or
                                   search_lower in d.get('notes', '').lower() or
                                   search_lower in d.get('sector_tags', '').lower() or
                                   search_lower in d.get('assigned_to', '').lower() or
                                   search_lower in d.get('contact_role', '').lower()]
                
                # Quick search filters
                if hasattr(st.session_state, 'quick_search_filter'):
                    quick_filter = st.session_state.quick_search_filter
                    
                    if quick_filter == "high_value":
                        filtered_data = [d for d in filtered_data if d.get('expected_amount', 0) > 5000000]  # ₹50L
                        st.info("🏢 Showing high-value prospects (>₹50L expected amount)")
                    
                    elif quick_filter == "proposals":
                        filtered_data = [d for d in filtered_data if d.get('current_stage') == 'Proposal Sent']
                        st.info("📄 Showing prospects with proposals sent")
                    
                    elif quick_filter == "active":
                        active_stages = ['Engaged', 'In Prospect List', 'Initial Outreach']
                        filtered_data = [d for d in filtered_data if d.get('current_stage') in active_stages]
                        st.info("🤝 Showing actively engaged prospects")
                    
                    elif quick_filter == "overdue":
                        from datetime import datetime
                        today = datetime.now().date()
                        filtered_data = [d for d in filtered_data if 
                                       d.get('next_action_date') and 
                                       pd.to_datetime(d.get('next_action_date')).date() < today]
                        st.warning("⚠️ Showing prospects with overdue actions")
                
                # Display data in Kanban style
                if filtered_data:
                    # Create Kanban-style display
                    display_kanban_pipeline(filtered_data)
                    
                    # Show comprehensive filter summary
                    active_filters = []
                    if stage_filter != "All": active_filters.append(f"Stage: {stage_filter}")
                    if sector_filter != "All": active_filters.append(f"Sector: {sector_filter}")
                    if assigned_filter != "All": active_filters.append(f"Assigned: {assigned_filter}")
                    if search_term: active_filters.append(f"Search: '{search_term}'")
                    if hasattr(st.session_state, 'quick_search_filter'): 
                        active_filters.append(f"Quick Filter: {st.session_state.quick_search_filter.replace('_', ' ').title()}")
                    
                    if active_filters or len(filtered_data) != len(pipeline_data):
                        filter_text = f"📊 Showing **{len(filtered_data)}** of **{len(pipeline_data)}** prospects"
                        if active_filters:
                            filter_text += f" | Active filters: {', '.join(active_filters)}"
                        st.info(filter_text)
                else:
                    st.info("No data matches the selected filters.")
            else:
                # Fallback to sample data with notice
                st.warning("⚠️ Unable to load live data. Showing sample data.")
                display_sample_kanban_pipeline()
            
            # Check if we're in edit mode
            if hasattr(st.session_state, 'edit_donor_id') and st.session_state.edit_donor_id:
                show_edit_donor_form()
                
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
        if st.button("➕ Add Prospect", use_container_width=True, type="primary", help="Add a new prospect to the fundraising pipeline"):
            add_new_prospect()
    
    with col3:
        if st.button("📈 View Analytics", use_container_width=True):
            show_pipeline_analytics()
    
    with col4:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.switch_page("streamlit_app.py")

def display_kanban_pipeline(data):
    """Display pipeline data in Kanban-style with stage tabs"""
    
    # Define the stages for Kanban view
    stages = {
        "Initial Outreach": {
            "icon": "📞",
            "color": "#e3f2fd",
            "description": "First contact and initial research"
        },
        "In Prospect List": {
            "icon": "📋",
            "color": "#f3e5f5",
            "description": "Qualified prospects being tracked"
        },
        "Engaged": {
            "icon": "🤝",
            "color": "#e8f5e8",
            "description": "Active conversations and relationship building"
        },
        "Proposal Sent": {
            "icon": "📄",
            "description": "Formal proposals submitted"
        },
        "Grant Received": {
            "icon": "🎉",
            "color": "#e8f5e8",
            "description": "Successfully secured funding"
        },
        "Rejected": {
            "icon": "❌",
            "color": "#ffebee",
            "description": "Declined or unsuccessful prospects"
        }
    }

    # Categorize data by stages
    stage_data = {stage: [] for stage in stages.keys()}

    for donor in data:
        current_stage = donor.get('current_stage', '')
        mapped_stage = map_stage(current_stage)
        if mapped_stage not in stage_data:
            mapped_stage = 'In Prospect List'
        stage_data[mapped_stage].append(donor)
    
    # Create tabs for each stage
    tab_names = [f"{stages[stage]['icon']} {stage}" for stage in stages.keys()]
    tabs = st.tabs(tab_names)
    
    for i, (stage, stage_info) in enumerate(stages.items()):
        with tabs[i]:
            donors_in_stage = stage_data[stage]
            stage_count = len(donors_in_stage)
            
            # Stage header with metrics
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### {stage_info['icon']} {stage}")
                st.caption(stage_info['description'])
            
            with col2:
                st.metric("Count", stage_count)
            
            with col3:
                if stage_count > 0:
                    total_value = sum([d.get('expected_amount', 0) for d in donors_in_stage])
                    st.metric("Total Value", f"₹{total_value:,.0f}")
                else:
                    st.metric("Total Value", "₹0")
            
            st.markdown("---")
            
            # Display donor cards for this stage
            if donors_in_stage:
                # Create columns for better layout
                cols = st.columns(2) if stage_count > 4 else st.columns(1)
                
                for idx, donor in enumerate(donors_in_stage):
                    col_idx = idx % len(cols)
                    
                    with cols[col_idx]:
                        display_donor_card(donor, idx, stage)
            else:
                st.info(f"No prospects currently in {stage} stage")
                st.markdown("---")

def display_donor_card(donor, index, current_stage):
    """Display individual donor card in Kanban style"""
    
    # Card styling
    with st.container():
        st.markdown(f"""
        <div style="
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            background-color: #fafafa;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
        """, unsafe_allow_html=True)
        
        # Organization name and stage
        st.markdown(f"**🏢 {donor.get('organization_name', 'Unknown Organization')}**")
        st.caption(f"📍 {current_stage}")
        
        # Contact information
        contact_person = donor.get('contact_person', 'N/A')
        contact_email = donor.get('contact_email', 'N/A')
        st.markdown(f"👤 **Contact:** {contact_person}")
        st.markdown(f"📧 **Email:** {contact_email}")
        
        # Financial information
        expected_amount = donor.get('expected_amount', 0)
        probability = donor.get('probability', 0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"💰 **Amount:** ₹{expected_amount:,}")
        with col2:
            st.markdown(f"📊 **Probability:** {probability}%")
        
        # Progress bar for probability
        if probability > 0:
            st.progress(probability / 100)
        
        # Assigned team member
        assigned_to = donor.get('assigned_to', 'Unassigned')
        st.markdown(f"👥 **Assigned:** {assigned_to}")
        
        # Industry/Sector
        sector = donor.get('sector_tags', 'N/A')
        st.markdown(f"🏭 **Sector:** {sector}")
        
        # Notes preview (truncated)
        notes = donor.get('notes', '')
        if notes:
            notes_preview = notes[:100] + "..." if len(notes) > 100 else notes
            st.markdown(f"📝 **Notes:** {notes_preview}")
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✏️ Edit", key=f"kanban_edit_{index}_{current_stage}"):
                st.session_state.edit_donor_id = donor.get('id', f'donor_{index}')
                st.session_state.edit_donor_data = donor.copy()
                st.rerun()
        
        with col2:
            if st.button("👁️ View", key=f"kanban_view_{index}_{current_stage}"):
                st.switch_page("pages/2_🏷️_Donor_Profile.py")
        
        with col3:
            if st.button("✉️ Email", key=f"kanban_email_{index}_{current_stage}"):
                st.switch_page("pages/3_✉️_Composer.py")
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_sample_kanban_pipeline():
    """Display sample Kanban pipeline when API is unavailable"""
    sample_data = [
        {
            "id": "sample_donor_1",
            "organization_name": "ABC Corporation",
            "current_stage": "Initial Contact",
            "assigned_to": "John Doe",
            "sector_tags": "Technology",
            "contact_person": "Jane Smith",
            "contact_email": "jane@abc.com",
            "contact_role": "CFO",
            "probability": 25,
            "expected_amount": 5000000,  # ₹50L
            "next_action": "Send introduction email",
            "next_action_date": "2024-01-15",
            "last_contact_date": "2024-01-10",
            "notes": "Interested in education technology initiatives"
        },
        {
            "id": "sample_donor_2",
            "organization_name": "XYZ Foundation",
            "current_stage": "Proposal Sent",
            "assigned_to": "Sarah Johnson",
            "sector_tags": "Education",
            "contact_person": "Mike Wilson",
            "contact_email": "mike@xyz.org",
            "contact_role": "Program Director",
            "probability": 60,
            "expected_amount": 10000000,  # ₹1Cr
            "next_action": "Follow up on proposal",
            "next_action_date": "2024-01-20",
            "last_contact_date": "2024-01-12",
            "notes": "Very interested in our rural education program"
        },
        {
            "id": "sample_donor_3",
            "organization_name": "Green Energy Corp",
            "current_stage": "Closed Won",
            "assigned_to": "Mike Wilson",
            "sector_tags": "Environment",
            "contact_person": "Lisa Green",
            "contact_email": "lisa@greenenergy.com",
            "contact_role": "CEO",
            "probability": 100,
            "expected_amount": 7500000,  # ₹75L
            "next_action": "Send thank you note",
            "next_action_date": "2024-01-25",
            "last_contact_date": "2024-01-18",
            "notes": "Successfully secured funding for environmental education program"
        }
    ]
    
    display_kanban_pipeline(sample_data)

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
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("👁️ View Details", key=f"view_{i}"):
                    st.switch_page(f"pages/2_🏷️_Donor_Profile.py")
            with col2:
                if st.button("✏️ Edit", key=f"edit_{i}"):
                    st.session_state.edit_donor_id = donor.get('id', f'donor_{i}')
                    st.session_state.edit_donor_data = donor.copy()
                    st.rerun()
            with col3:
                if st.button("✉️ Send Email", key=f"email_{i}"):
                    st.switch_page(f"pages/3_✉️_Composer.py")
            with col4:
                if st.button("📝 Add Note", key=f"note_{i}"):
                    st.info("Note functionality coming soon!")
            with col5:
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
    """Show enhanced form to add new prospect"""
    st.markdown("---")
    st.markdown("### 🆕 Add New Prospect")
    st.markdown("Fill out the form below to add a new prospect to your fundraising pipeline.")
    
    with st.container():
        with st.form("add_prospect", clear_on_submit=True):
            # Header with instructions
            st.info("💡 **Tip:** Fill in as much information as possible to create a comprehensive prospect profile.")
            
            # Basic Information Section
            st.markdown("#### 📋 Basic Information")
            col1, col2 = st.columns(2)
            
            with col1:
                org_name = st.text_input(
                    "Organization Name*", 
                    placeholder="e.g., ABC Corporation",
                    help="The full legal name of the organization"
                )
                contact_name = st.text_input(
                    "Contact Person*", 
                    placeholder="e.g., John Smith",
                    help="Primary contact person's full name"
                )
                email = st.text_input(
                    "Email Address*", 
                    placeholder="e.g., john@abc.com",
                    help="Primary contact's email address"
                )
                
            with col2:
                phone = st.text_input(
                    "Phone Number", 
                    placeholder="e.g., +1 (555) 123-4567",
                    help="Primary contact's phone number"
                )
                website = st.text_input(
                    "Website", 
                    placeholder="e.g., https://www.abc.com",
                    help="Organization's website URL"
                )
                industry = st.selectbox(
                    "Industry/Sector",
                    ["Technology", "Education", "Healthcare", "Finance", "Non-Profit", "Government", "Manufacturing", "Retail", "Other"],
                    help="Select the primary industry sector"
                )
            
            # Financial Information Section
            st.markdown("#### 💰 Financial Information")
            col1, col2 = st.columns(2)
            
            with col1:
                expected_amount = st.number_input(
                    "Expected Amount (₹)",
                    min_value=0,
                    step=10000,
                    format="%d",
                    help="Estimated donation amount in INR"
                )
                
            with col2:
                probability = st.slider(
                    "Success Probability (%)",
                    min_value=0,
                    max_value=100,
                    value=25,
                    step=5,
                    help="Estimated probability of securing this donation"
                )
            
            # Pipeline Information Section
            st.markdown("#### 📈 Pipeline Information")
            col1, col2 = st.columns(2)
            
            with col1:
                current_stage = st.selectbox(
                    "Current Stage*",
                    ["Initial Outreach", "In Prospect List", "Engaged", "Proposal Sent", "Grant Received", "Rejected"],
                    help="Current stage in the fundraising process"
                )
                
            with col2:
                assigned_to = st.text_input(
                    "Assigned To",
                    placeholder="e.g., Sarah Johnson",
                    help="Team member responsible for this prospect"
                )
            
            # Additional Information Section
            st.markdown("#### 📝 Additional Information")
            notes = st.text_area(
                "Notes & Research",
                placeholder="Add any relevant notes, research findings, or context about this prospect...",
                height=100,
                help="Any additional information that might be helpful for the team"
            )
            
            # Form submission
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button(
                    "💾 Add Prospect to Pipeline", 
                    type="primary",
                    use_container_width=True
                )
            
            # Validation and submission handling
            if submitted:
                # Validate required fields
                validation_errors = []
                
                if not org_name or not org_name.strip():
                    validation_errors.append("Organization Name is required")
                
                if not contact_name or not contact_name.strip():
                    validation_errors.append("Contact Person is required")
                
                if not email or not email.strip():
                    validation_errors.append("Email Address is required")
                elif "@" not in email or "." not in email:
                    validation_errors.append("Please enter a valid email address")
                
                if not current_stage:
                    validation_errors.append("Current Stage is required")
                
                # Display validation errors
                if validation_errors:
                    st.error("❌ **Please fix the following errors:**")
                    for error in validation_errors:
                        st.error(f"• {error}")
                else:
                    # All validation passed - proceed with adding prospect
                    try:
                        # Create prospect data
                        prospect_data = {
                            "organization_name": org_name.strip(),
                            "contact_person": contact_name.strip(),
                            "contact_email": email.strip(),
                            "phone": phone.strip() if phone else "",
                            "website": website.strip() if website else "",
                            "sector_tags": industry,
                            "expected_amount": expected_amount,
                            "probability": probability,
                            "current_stage": current_stage,
                            "assigned_to": assigned_to.strip() if assigned_to else "Unassigned",
                            "notes": notes.strip() if notes else "",
                            "date_added": st.session_state.get("current_date", "2024-01-01"),
                            "last_contact_date": "",
                            "next_action": "Initial follow-up",
                            "next_action_date": ""
                        }
                        
                        # Log the activity
                        log_activity(
                            "prospect_added",
                            "new_prospect",
                            f"Added new prospect: {org_name.strip()}"
                        )
                        
                        # Track analytics
                        if "prospect_analytics" not in st.session_state:
                            st.session_state.prospect_analytics = {
                                "total_added": 0,
                                "by_stage": {},
                                "by_industry": {},
                                "total_value": 0
                            }
                        
                        # Update analytics
                        analytics = st.session_state.prospect_analytics
                        analytics["total_added"] += 1
                        analytics["total_value"] += expected_amount
                        analytics["by_stage"][current_stage] = analytics["by_stage"].get(current_stage, 0) + 1
                        analytics["by_industry"][industry] = analytics["by_industry"].get(industry, 0) + 1
                        
                        # Show success message with details
                        st.success("🎉 **Prospect Added Successfully!**")
                        
                        # Display summary
                        with st.expander("📋 Prospect Summary", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Organization:** {org_name.strip()}")
                                st.write(f"**Contact:** {contact_name.strip()}")
                                st.write(f"**Email:** {email.strip()}")
                                st.write(f"**Stage:** {current_stage}")
                            with col2:
                                st.write(f"**Expected Amount:** ₹{expected_amount:,}")
                                st.write(f"**Probability:** {probability}%")
                                st.write(f"**Industry:** {industry}")
                                st.write(f"**Assigned To:** {assigned_to.strip() if assigned_to else 'Unassigned'}")
                        
                        # Auto-refresh after a short delay
                        st.balloons()
                        st.info("🔄 Refreshing pipeline data...")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ **Error adding prospect:** {str(e)}")
                        st.error("Please try again or contact support if the issue persists.")

def show_edit_donor_form():
    """Show form to edit donor details"""
    if not hasattr(st.session_state, 'edit_donor_data') or not st.session_state.edit_donor_data:
        return
    
    donor_data = st.session_state.edit_donor_data
    donor_id = st.session_state.edit_donor_id
    
    st.markdown("---")
    st.markdown("### ✏️ Edit Donor Details")
    st.markdown(f"Editing: **{donor_data.get('organization_name', 'Unknown Organization')}**")
    
    with st.container():
        with st.form("edit_donor", clear_on_submit=False):
            # Header with instructions
            st.info("💡 **Tip:** Update the information below and click 'Save Changes' to update the donor record.")
            
            # Basic Information Section
            st.markdown("#### 📋 Basic Information")
            col1, col2 = st.columns(2)
            
            with col1:
                org_name = st.text_input(
                    "Organization Name*", 
                    value=donor_data.get('organization_name', ''),
                    placeholder="e.g., ABC Corporation",
                    help="The full legal name of the organization"
                )
                contact_name = st.text_input(
                    "Contact Person*", 
                    value=donor_data.get('contact_person', ''),
                    placeholder="e.g., John Smith",
                    help="Primary contact person's full name"
                )
                email = st.text_input(
                    "Email Address*", 
                    value=donor_data.get('contact_email', ''),
                    placeholder="e.g., john@abc.com",
                    help="Primary contact's email address"
                )
                
            with col2:
                phone = st.text_input(
                    "Phone Number", 
                    value=donor_data.get('phone', ''),
                    placeholder="e.g., +1 (555) 123-4567",
                    help="Primary contact's phone number"
                )
                website = st.text_input(
                    "Website", 
                    value=donor_data.get('website', ''),
                    placeholder="e.g., https://www.abc.com",
                    help="Organization's website URL"
                )
                industry = st.selectbox(
                    "Industry/Sector",
                    ["Technology", "Education", "Healthcare", "Finance", "Non-Profit", "Government", "Manufacturing", "Retail", "Other"],
                    index=["Technology", "Education", "Healthcare", "Finance", "Non-Profit", "Government", "Manufacturing", "Retail", "Other"].index(donor_data.get('sector_tags', 'Technology')) if donor_data.get('sector_tags') in ["Technology", "Education", "Healthcare", "Finance", "Non-Profit", "Government", "Manufacturing", "Retail", "Other"] else 0,
                    help="Select the primary industry sector"
                )
            
            # Financial Information Section
            st.markdown("#### 💰 Financial Information")
            col1, col2 = st.columns(2)
            
            with col1:
                expected_amount = st.number_input(
                    "Expected Amount (₹)",
                    min_value=0,
                    step=10000,
                    format="%d",
                    value=donor_data.get('expected_amount', 0),
                    help="Estimated donation amount in INR"
                )
                
            with col2:
                probability = st.slider(
                    "Success Probability (%)",
                    min_value=0,
                    max_value=100,
                    value=donor_data.get('probability', 25),
                    step=5,
                    help="Estimated probability of securing this donation"
                )
            
            # Pipeline Information Section
            st.markdown("#### 📈 Pipeline Information")
            col1, col2 = st.columns(2)
            
            with col1:
                current_stage = st.selectbox(
                    "Current Stage*",
                    ["Initial Outreach", "In Prospect List", "Engaged", "Proposal Sent", "Grant Received", "Rejected"],
                    index=["Initial Outreach", "In Prospect List", "Engaged", "Proposal Sent", "Grant Received", "Rejected"].index(donor_data.get('current_stage', 'Initial Outreach')) if donor_data.get('current_stage') in ["Initial Outreach", "In Prospect List", "Engaged", "Proposal Sent", "Grant Received", "Rejected"] else 0,
                    help="Current stage in the fundraising process"
                )
                
            with col2:
                assigned_to = st.text_input(
                    "Assigned To",
                    value=donor_data.get('assigned_to', ''),
                    placeholder="e.g., Sarah Johnson",
                    help="Team member responsible for this prospect"
                )
            
            # Contact and Activity Information
            st.markdown("#### 📞 Contact & Activity Information")
            col1, col2 = st.columns(2)
            
            with col1:
                contact_role = st.text_input(
                    "Contact Role",
                    value=donor_data.get('contact_role', ''),
                    placeholder="e.g., CFO, Program Director",
                    help="Contact person's role/title"
                )
                last_contact_date = st.date_input(
                    "Last Contact Date",
                    value=pd.to_datetime(donor_data.get('last_contact_date', '2024-01-01')).date() if donor_data.get('last_contact_date') else None,
                    help="Date of last contact with this prospect"
                )
                
            with col2:
                next_action = st.text_input(
                    "Next Action",
                    value=donor_data.get('next_action', ''),
                    placeholder="e.g., Send follow-up email",
                    help="Next planned action"
                )
                next_action_date = st.date_input(
                    "Next Action Date",
                    value=pd.to_datetime(donor_data.get('next_action_date', '2024-01-15')).date() if donor_data.get('next_action_date') else None,
                    help="Due date for next action"
                )
            
            # Additional Information Section
            st.markdown("#### 📝 Additional Information")
            notes = st.text_area(
                "Notes & Research",
                value=donor_data.get('notes', ''),
                placeholder="Add any relevant notes, research findings, or context about this prospect...",
                height=100,
                help="Any additional information that might be helpful for the team"
            )
            
            # Form submission buttons
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                cancel_clicked = st.form_submit_button("❌ Cancel", use_container_width=True)
            with col2:
                save_clicked = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
            with col3:
                delete_clicked = st.form_submit_button("🗑️ Delete", use_container_width=True)
            
            # Handle form submissions
            if cancel_clicked:
                # Clear edit state and return to pipeline view
                if hasattr(st.session_state, 'edit_donor_id'):
                    del st.session_state.edit_donor_id
                if hasattr(st.session_state, 'edit_donor_data'):
                    del st.session_state.edit_donor_data
                st.rerun()
            
            elif save_clicked:
                # Validate required fields
                validation_errors = []
                
                if not org_name or not org_name.strip():
                    validation_errors.append("Organization Name is required")
                
                if not contact_name or not contact_name.strip():
                    validation_errors.append("Contact Person is required")
                
                if not email or not email.strip():
                    validation_errors.append("Email Address is required")
                elif "@" not in email or "." not in email:
                    validation_errors.append("Please enter a valid email address")
                
                if not current_stage:
                    validation_errors.append("Current Stage is required")
                
                # Display validation errors
                if validation_errors:
                    st.error("❌ **Please fix the following errors:**")
                    for error in validation_errors:
                        st.error(f"• {error}")
                else:
                    # All validation passed - proceed with saving
                    try:
                        # Create updated donor data
                        updated_donor_data = {
                            "id": donor_id,
                            "organization_name": org_name.strip(),
                            "contact_person": contact_name.strip(),
                            "contact_email": email.strip(),
                            "phone": phone.strip() if phone else "",
                            "website": website.strip() if website else "",
                            "sector_tags": industry,
                            "expected_amount": expected_amount,
                            "probability": probability,
                            "current_stage": current_stage,
                            "assigned_to": assigned_to.strip() if assigned_to else "Unassigned",
                            "contact_role": contact_role.strip() if contact_role else "",
                            "last_contact_date": last_contact_date.strftime("%Y-%m-%d") if last_contact_date else "",
                            "next_action": next_action.strip() if next_action else "",
                            "next_action_date": next_action_date.strftime("%Y-%m-%d") if next_action_date else "",
                            "notes": notes.strip() if notes else "",
                            "date_updated": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Log the activity
                        log_activity(
                            "donor_updated",
                            donor_id,
                            f"Updated donor details for: {org_name.strip()}"
                        )
                        
                        # Show success message
                        st.success("🎉 **Donor Details Updated Successfully!**")
                        
                        # Display summary of changes
                        with st.expander("📋 Updated Information Summary", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Organization:** {org_name.strip()}")
                                st.write(f"**Contact:** {contact_name.strip()}")
                                st.write(f"**Email:** {email.strip()}")
                                st.write(f"**Stage:** {current_stage}")
                            with col2:
                                st.write(f"**Expected Amount:** ₹{expected_amount:,}")
                                st.write(f"**Probability:** {probability}%")
                                st.write(f"**Industry:** {industry}")
                                st.write(f"**Assigned To:** {assigned_to.strip() if assigned_to else 'Unassigned'}")
                        
                        # Clear edit state and refresh
                        if hasattr(st.session_state, 'edit_donor_id'):
                            del st.session_state.edit_donor_id
                        if hasattr(st.session_state, 'edit_donor_data'):
                            del st.session_state.edit_donor_data
                        
                        st.balloons()
                        st.info("🔄 Refreshing pipeline data...")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ **Error updating donor:** {str(e)}")
                        st.error("Please try again or contact support if the issue persists.")
            
            elif delete_clicked:
                # Show confirmation dialog
                st.warning("⚠️ **Are you sure you want to delete this donor?**")
                st.error("This action cannot be undone!")
                
                # In a real implementation, you would add a confirmation step here
                # For now, we'll just show a warning
                st.info("💡 **Note:** Delete functionality requires additional confirmation. Please contact your administrator.")

def show_pipeline_analytics():
    """Show comprehensive pipeline analytics"""
    # Fetch fresh pipeline data
    pipeline_data = get_cached_pipeline_data()
    
    st.markdown("---")
    st.markdown("### 📈 Pipeline Analytics Dashboard")
    st.markdown("Comprehensive insights into your fundraising pipeline performance.")
    
    if pipeline_data and len(pipeline_data) > 0:
        # Calculate comprehensive analytics
        total_prospects = len(pipeline_data)
        stages = [d.get('current_stage', 'Unknown') for d in pipeline_data]
        stage_counts = {}
        for stage in stages:
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
        # Calculate financial metrics
        expected_amounts = [d.get('expected_amount', 0) for d in pipeline_data if d.get('expected_amount')]
        total_pipeline_value = sum(expected_amounts)
        avg_deal_size = total_pipeline_value / len(expected_amounts) if expected_amounts else 0
        
        # Calculate probability metrics
        probabilities = [d.get('probability', 0) for d in pipeline_data if d.get('probability')]
        avg_probability = sum(probabilities) / len(probabilities) if probabilities else 0
        weighted_value = sum([d.get('expected_amount', 0) * (d.get('probability', 0) / 100) for d in pipeline_data])
        
        # Calculate stage-based metrics
        active_stages = ['Initial Outreach', 'In Prospect List', 'Engaged', 'Proposal Sent']
        active_count = sum([count for stage, count in stage_counts.items() if stage in active_stages])
        grant_received = stage_counts.get('Grant Received', 0)
        rejected = stage_counts.get('Rejected', 0)
        total_closed = grant_received + rejected
        win_rate = (grant_received / total_closed * 100) if total_closed > 0 else 0
        
        # Industry analysis
        industries = [d.get('sector_tags', 'Unknown') for d in pipeline_data]
        industry_counts = {}
        for industry in industries:
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        # Assigned team analysis
        assigned_to = [d.get('assigned_to', 'Unassigned') for d in pipeline_data]
        team_counts = {}
        for person in assigned_to:
            team_counts[person] = team_counts.get(person, 0) + 1
        
        # Key Metrics Row
        st.markdown("#### 🎯 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Prospects", 
                total_prospects,
                help="Total number of prospects in the pipeline"
            )
        
        with col2:
            st.metric(
                "Pipeline Value", 
                f"₹{total_pipeline_value:,.0f}",
                help="Total expected value of all prospects"
            )
        
        with col3:
            st.metric(
                "Weighted Value", 
                f"₹{weighted_value:,.0f}",
                help="Probability-weighted pipeline value"
            )
        
        with col4:
            st.metric(
                "Win Rate", 
                f"{win_rate:.1f}%",
                help="Percentage of closed deals that were won"
            )
        
        # Detailed Analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Stage Distribution")
            if stage_counts:
                # Create a more visual representation
                for stage, count in sorted(stage_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_prospects) * 100
                    progress_bar = "█" * int(percentage / 2) + "░" * (50 - int(percentage / 2))
                    st.write(f"**{stage}**")
                    st.write(f"{progress_bar} {count} ({percentage:.1f}%)")
                    st.progress(percentage / 100)
                    st.write("")
        
        with col2:
            st.markdown("#### 🏢 Industry Breakdown")
            if industry_counts:
                for industry, count in sorted(industry_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_prospects) * 100
                    st.metric(industry, f"{count} ({percentage:.1f}%)")
        
        # Additional Metrics
        st.markdown("#### 📈 Advanced Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Prospects", active_count)
            st.metric("Average Deal Size", f"₹{avg_deal_size:,.0f}")
        
        with col2:
            st.metric("Average Probability", f"{avg_probability:.1f}%")
            st.metric("Closed Deals", total_closed)
        
        with col3:
            st.metric("Conversion Rate", f"{(total_closed / total_prospects * 100):.1f}%" if total_prospects > 0 else "0%")
            st.metric("Team Members", len([p for p in team_counts.keys() if p != 'Unassigned']))
        
        # Team Performance (if data available)
        if len([p for p in team_counts.keys() if p != 'Unassigned']) > 0:
            st.markdown("#### 👥 Team Performance")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Prospects by Team Member**")
                for person, count in sorted(team_counts.items(), key=lambda x: x[1], reverse=True):
                    if person != 'Unassigned':
                        percentage = (count / total_prospects) * 100
                        st.write(f"**{person}:** {count} prospects ({percentage:.1f}%)")
            
            with col2:
                unassigned_count = team_counts.get('Unassigned', 0)
                if unassigned_count > 0:
                    st.warning(f"⚠️ {unassigned_count} prospects are unassigned")
                else:
                    st.success("✅ All prospects are assigned to team members")
        
        # Recent Activity Summary
        st.markdown("#### 📅 Recent Activity Summary")
        st.info(f"📊 **Pipeline Health:** {active_count} active prospects out of {total_prospects} total")
        st.info(f"💰 **Financial Outlook:** ₹{weighted_value:,.0f} in probability-weighted pipeline value")
        st.info(f"🎯 **Success Rate:** {win_rate:.1f}% win rate from {total_closed} closed deals")
    
    else:
        st.warning("⚠️ **No Pipeline Data Available**")
        st.info("Connect to your Google Sheets or add some prospects to see analytics.")
        
        # Show sample analytics for demonstration
        st.markdown("#### 📊 Sample Analytics (Demo Data)")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Prospects", "0")
        with col2:
            st.metric("Pipeline Value", "₹0")
        with col3:
            st.metric("Active Prospects", "0")
        with col4:
            st.metric("Win Rate", "0%")
        
        st.info("💡 **Tip:** Add prospects using the 'Add Prospect' button above to populate your pipeline with real data.")

if __name__ == "__main__":
    main()
