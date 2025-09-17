"""
Donor Profile Management Page
View and manage individual donor profiles
"""

import streamlit as st
import sys
import os
from datetime import datetime
from streamlit.errors import StreamlitAPIException

# Configure page to use wide layout for better readability
try:
    st.set_page_config(
        page_title="Donor Profile Management",
        page_icon="🏷️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
except StreamlitAPIException:
    # Another page already set the config in this session; ignore the redundant call.
    pass

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

# Fallback functions
def fallback_get_donors():
    return [{"id": "1", "name": "Sample Donor", "email": "donor@example.com"}]

def fallback_get_donor_profile(donor_id):
    return {"id": donor_id, "name": "Sample Donor", "email": "donor@example.com", "total_donated": "₹5,00,000"}

# Import with multiple fallback strategies
get_donors = fallback_get_donors
get_donor_profile = fallback_get_donor_profile
generate_donor_profile = None
generate_donor_profile_stream = None
get_profile_generator_status = None
update_donor_database = None
update_donor = None
check_existing_donor = None

try:
    from lib.api import get_donors, get_donor_profile, generate_donor_profile, generate_donor_profile_stream, get_profile_generator_status, update_donor_database, update_donor, check_existing_donor
    print("✅ Using lib.api imports")
except ImportError as e:
    print(f"❌ Lib.api import failed: {e}")
    try:
        from api import get_donors, get_donor_profile  # type: ignore
        print("✅ Using direct api imports")
    except ImportError as e:
        print(f"❌ Direct api import failed: {e}")
        if lib_path:
            try:
                api_file_path = os.path.join(lib_path, 'api.py')
                if os.path.exists(api_file_path):
                    spec = importlib.util.spec_from_file_location("api", api_file_path)
                    api_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(api_module)
                    if hasattr(api_module, 'get_donors'):
                        get_donors = api_module.get_donors
                    if hasattr(api_module, 'get_donor_profile'):
                        get_donor_profile = api_module.get_donor_profile
                    print("✅ Using importlib for api module")
            except Exception as e:
                print(f"❌ Importlib failed: {e}")
        
        if get_donors == fallback_get_donors or get_donor_profile == fallback_get_donor_profile:
            for path in possible_paths:
                try:
                    abs_path = os.path.abspath(path)
                    api_file_path = os.path.join(abs_path, 'api.py')
                    if os.path.exists(api_file_path):
                        spec = importlib.util.spec_from_file_location("api", api_file_path)
                        api_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(api_module)
                        if hasattr(api_module, 'get_donors'):
                            get_donors = api_module.get_donors
                        if hasattr(api_module, 'get_donor_profile'):
                            get_donor_profile = api_module.get_donor_profile
                        print(f"✅ Found api functions in {abs_path}")
                        break
                except Exception as e:
                    print(f"❌ Failed to import from {path}: {e}")
                    continue

print(f"✅ Final imports - get_donors: {get_donors != fallback_get_donors}, get_donor_profile: {get_donor_profile != fallback_get_donor_profile}")

def main():
    st.title("🏷️ Donor Profiles")
    st.markdown("View and manage individual donor information")
    
    # Donor selection
    st.subheader("Select or Add Donor")

    # Option to choose between existing or custom donor
    input_mode = st.radio(
        "Choose input method:",
        ["Select from existing", "Enter custom donor"],
        horizontal=True
    )

    selected_donor = None
    custom_website = None

    if input_mode == "Select from existing":
        try:
            donors = get_donors()
            if donors:
                # Filter out empty/invalid donors and extract proper names
                valid_donors = []
                for donor in donors:
                    # Try multiple possible field names for organization name
                    org_name = (donor.get('organization_name') or 
                               donor.get('name') or 
                               donor.get('org_name') or 
                               donor.get('company_name', ''))
                    
                    # Only include donors with valid, non-empty names
                    if org_name and str(org_name).strip() and str(org_name).strip().lower() not in ['unknown', 'n/a', 'null', '']:
                        valid_donors.append({
                            'name': str(org_name).strip(),
                            'original_data': donor
                        })
                
                if valid_donors:
                    # Sort donors alphabetically for better UX
                    valid_donors.sort(key=lambda x: x['name'].lower())
                    donor_names = [donor['name'] for donor in valid_donors]
                    selected_donor = st.selectbox("Choose a donor:", donor_names)
                    
                    # Store the selected donor's original data for later use
                    if selected_donor:
                        selected_donor_data = next((d['original_data'] for d in valid_donors if d['name'] == selected_donor), None)
                        st.session_state.selected_donor_data = selected_donor_data
                else:
                    st.warning("⚠️ No valid donors found in the database. Please add some prospects first.")
                    donor_names = ["ABC Corporation", "XYZ Foundation", "Tech Startup Inc", "Local Business LLC"]
                    selected_donor = st.selectbox("Choose a donor (sample data):", donor_names)
            else:
                # Sample data
                donor_names = ["ABC Corporation", "XYZ Foundation", "Tech Startup Inc", "Local Business LLC"]
                selected_donor = st.selectbox("Choose a donor:", donor_names)
        except Exception as e:
            st.error(f"Error loading donors: {str(e)}")
            donor_names = ["ABC Corporation", "XYZ Foundation", "Tech Startup Inc", "Local Business LLC"]
            selected_donor = st.selectbox("Choose a donor:", donor_names)

    else:  # Enter custom donor
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_donor = st.text_input(
                "Donor/Organization Name *",
                placeholder="e.g., Ford Foundation, Gates Foundation, etc.",
                help="Enter the full name of the donor organization or foundation"
            )
        with col2:
            custom_website = st.text_input(
                "Website (optional)",
                placeholder="e.g., www.foundation.org",
                help="If you know the website, this will improve the profile generation"
            )

        if selected_donor:
            st.info(f"🎯 Ready to generate profile for: **{selected_donor}**")
        else:
            st.warning("Please enter a donor name to proceed")
    
    if selected_donor:
        st.markdown("---")

        # Database Management Section
        with st.expander("🔧 Database Management", expanded=False):
            st.markdown("**Duplicate Detection and Removal**")

            col_detect, col_remove = st.columns(2)

            with col_detect:
                if st.button("🔍 Detect Duplicates", help="Scan the database for duplicate organizations"):
                    with st.spinner("Scanning for duplicates..."):
                        try:
                            # Try to call the new API endpoint if available
                            result = make_api_request("/api/donor/detect-duplicates", method="GET")

                            if result and result.get("success"):
                                duplicates_found = result.get("duplicates_found", 0)
                                if duplicates_found > 0:
                                    st.warning(f"⚠️ Found {duplicates_found} duplicate groups!")

                                    duplicates = result.get("duplicates", [])
                                    for dup in duplicates:
                                        with st.expander(f"📋 {dup['original_name']} ({dup['count']} records)", expanded=True):
                                            for i, record in enumerate(dup['records']):
                                                st.write(f"**Record {i+1}:**")
                                                st.write(f"- Stage: {record.get('current_stage', 'N/A')}")
                                                st.write(f"- Contact: {record.get('contact_person', 'N/A')}")
                                                st.write(f"- Date Added: {record.get('date_added', 'N/A')}")
                                                if record.get('notes'):
                                                    st.write(f"- Notes: {record.get('notes', 'N/A')}")
                                                st.write("---")

                                    st.session_state.duplicates_detected = duplicates
                                else:
                                    st.success("✅ No duplicates found!")
                                    st.session_state.duplicates_detected = []
                            else:
                                error = result.get("error", "API not available") if result else "Backend API not available"
                                st.error(f"❌ Could not detect duplicates: {error}")

                        except Exception as e:
                            st.error(f"❌ Error detecting duplicates: {str(e)}")

            with col_remove:
                if st.button("🗑️ Remove Duplicates", help="Remove duplicate organizations (keep newest)", type="primary"):
                    if not hasattr(st.session_state, 'duplicates_detected') or not st.session_state.duplicates_detected:
                        st.warning("⚠️ Please detect duplicates first!")
                    else:
                        with st.spinner("Removing duplicates..."):
                            try:
                                # Try to call the new API endpoint if available
                                result = make_api_request("/api/donor/remove-duplicates", method="POST",
                                                        data={"keep_strategy": "newest"})

                                if result and result.get("success"):
                                    removed_count = result.get("removed_count", 0)
                                    st.success(f"✅ Successfully removed {removed_count} duplicate records!")

                                    if result.get("removed_records"):
                                        with st.expander("📋 Removed Records"):
                                            for record in result["removed_records"]:
                                                st.write(f"- {record['name']} (Stage: {record['stage']})")

                                    # Clear the duplicates session state
                                    st.session_state.duplicates_detected = []

                                    # Suggest refreshing the page
                                    st.info("💡 Refresh the page to see updated data")

                                else:
                                    error = result.get("error", "API not available") if result else "Backend API not available"
                                    st.error(f"❌ Could not remove duplicates: {error}")

                            except Exception as e:
                                st.error(f"❌ Error removing duplicates: {str(e)}")

        st.markdown("---")

        # Display existing donor information if available
        if input_mode == "Select from existing" and hasattr(st.session_state, 'selected_donor_data') and st.session_state.selected_donor_data:
            st.subheader(f"📊 Current Information for {selected_donor}")

            donor_data = st.session_state.selected_donor_data

            # Create columns for organized display
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**📋 Basic Information**")
                st.write(f"**Organization:** {donor_data.get('organization_name', donor_data.get('name', 'N/A'))}")
                st.write(f"**Contact Person:** {donor_data.get('contact_person', 'N/A')}")
                st.write(f"**Role:** {donor_data.get('contact_role', 'N/A')}")
                st.write(f"**Email:** {donor_data.get('contact_email', donor_data.get('email', 'N/A'))}")

            with col2:
                st.markdown("**💰 Fundraising Status**")
                st.write(f"**Current Stage:** {donor_data.get('current_stage', 'N/A')}")
                st.write(f"**Probability:** {donor_data.get('probability', 0)}%")
                st.write(f"**Assigned To:** {donor_data.get('assigned_to', 'Unassigned')}")

                # Next action and date
                next_action = donor_data.get('next_action', 'N/A')
                next_date = donor_data.get('next_action_date', 'N/A')
                st.write(f"**Next Action:** {next_action}")
                if next_date and next_date != 'N/A':
                    st.write(f"**Next Action Date:** {next_date}")

            # Additional information in a third row
            col3, col4 = st.columns(2)

            with col3:
                if donor_data.get('sector_tags'):
                    st.markdown("**🏷️ Sector Tags**")
                    st.write(donor_data.get('sector_tags', 'N/A'))

                if donor_data.get('last_contact_date'):
                    st.markdown("**📅 Last Contact**")
                    st.write(donor_data.get('last_contact_date', 'N/A'))

            with col4:
                if donor_data.get('notes'):
                    st.markdown("**📝 Notes**")
                    st.write(donor_data.get('notes', 'No notes available'))

                if donor_data.get('updated_at'):
                    st.markdown("**🕐 Last Updated**")
                    st.write(donor_data.get('updated_at', 'N/A'))

            # Alignment score with visual indicator
            if donor_data.get('alignment_score'):
                try:
                    alignment_score = float(donor_data.get('alignment_score', 0))
                    st.markdown("**🎯 Alignment Score**")
                    st.progress(alignment_score / 100.0)
                    st.write(f"{alignment_score}% alignment with Diksha Foundation")
                except (ValueError, TypeError):
                    st.write(f"**Alignment Score:** {donor_data.get('alignment_score', 'N/A')}")

            # Show documents if available
            if donor_data.get('documents') and len(donor_data.get('documents', [])) > 0:
                st.markdown("**📄 Documents**")
                documents = donor_data.get('documents', [])
                for doc in documents:
                    st.write(f"• {doc}")

            # Debug information (collapsible)
            with st.expander("🔧 Debug: Raw Donor Data"):
                st.json(donor_data)

            # Edit Information Section
            st.markdown("### ✏️ Actions")
            col_edit, col_refresh = st.columns(2)

            with col_edit:
                if st.button("✏️ Edit Information", type="secondary", use_container_width=True):
                    st.session_state.editing_donor = True

            with col_refresh:
                if st.button("🔄 Refresh Data", type="secondary", use_container_width=True):
                    # Clear cache and reload
                    st.cache_data.clear()
                    st.rerun()

            # Edit Form (appears when edit button is clicked)
            if st.session_state.get('editing_donor', False):
                st.markdown("---")
                st.markdown("### ✏️ Edit Donor Information")
                st.info("📝 Make changes below and click 'Save Changes' to update the Google Sheets database.")

                # Create editable form with current values
                with st.form("edit_donor_form"):
                    st.markdown("**📋 Basic Information**")
                    col1, col2 = st.columns(2)

                    with col1:
                        edit_org_name = st.text_input("Organization Name", value=donor_data.get('organization_name', ''))
                        edit_contact_person = st.text_input("Contact Person", value=donor_data.get('contact_person', ''))
                        edit_contact_role = st.text_input("Contact Role", value=donor_data.get('contact_role', ''))
                        edit_contact_email = st.text_input("Contact Email", value=donor_data.get('contact_email', ''))

                    with col2:
                        # Current stage dropdown
                        stage_options = ["Initial Contact", "Building", "Proposal Sent", "Under Review", "Negotiation", "Closed Won", "Closed Lost"]
                        current_stage_index = stage_options.index(donor_data.get('current_stage', 'Initial Contact')) if donor_data.get('current_stage') in stage_options else 0
                        edit_current_stage = st.selectbox("Current Stage", stage_options, index=current_stage_index)

                        edit_probability = st.slider("Probability (%)", 0, 100, int(donor_data.get('probability', 0)))
                        edit_assigned_to = st.text_input("Assigned To", value=donor_data.get('assigned_to', ''))
                        edit_next_action = st.text_input("Next Action", value=donor_data.get('next_action', ''))

                    st.markdown("**🏷️ Additional Information**")
                    col3, col4 = st.columns(2)

                    with col3:
                        edit_sector_tags = st.text_input("Sector Tags", value=donor_data.get('sector_tags', ''), help="Comma-separated tags (e.g., Education,Sports,Youth)")
                        edit_next_action_date = st.date_input("Next Action Date", value=None, help="Optional: Set a date for the next action")

                    with col4:
                        edit_notes = st.text_area("Notes", value=donor_data.get('notes', ''), height=100)
                        edit_alignment_score = st.slider("Alignment Score", 0, 100, int(donor_data.get('alignment_score', 0)))

                    # Form buttons
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        save_changes = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                    with col_cancel:
                        cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)

                    # Handle form submission
                    if save_changes:
                        # Prepare updated data
                        updated_data = {
                            'organization_name': edit_org_name,
                            'contact_person': edit_contact_person,
                            'contact_role': edit_contact_role,
                            'contact_email': edit_contact_email,
                            'current_stage': edit_current_stage,
                            'probability': edit_probability,
                            'assigned_to': edit_assigned_to,
                            'next_action': edit_next_action,
                            'sector_tags': edit_sector_tags,
                            'notes': edit_notes,
                            'alignment_score': edit_alignment_score,
                        }

                        # Add next action date if provided
                        if edit_next_action_date:
                            updated_data['next_action_date'] = edit_next_action_date.strftime('%Y-%m-%d')

                        # Update the database
                        with st.spinner("Updating donor information..."):
                            try:
                                # Try to get a unique identifier for the donor
                                # Use organization name as the primary identifier since that's what we store
                                original_org_name = donor_data.get('organization_name', selected_donor)
                                donor_id = original_org_name.lower().replace(' ', '_').replace('-', '_').replace('.', '_')

                                # Always use the database update method since it's more reliable
                                # and handles the Google Sheets backend properly
                                updated_data['donor_name'] = edit_org_name
                                updated_data['original_name'] = original_org_name  # For finding the record

                                if update_donor_database:
                                    result = update_donor_database(updated_data)
                                    if result and result.get('success'):
                                        st.success("✅ Donor information updated successfully!")
                                        st.session_state.editing_donor = False
                                        # Update the session state data
                                        st.session_state.selected_donor_data.update(updated_data)
                                        # Clear cache to force refresh of data
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        error_msg = result.get('error', 'Unknown error') if result else 'Update service unavailable'
                                        st.error(f"❌ Failed to update donor information: {error_msg}")

                                        # Show detailed error information for debugging
                                        if result:
                                            with st.expander("🔧 Debug Information"):
                                                st.json(result)
                                elif update_donor and donor_id:
                                    # Fallback to individual record update (though less reliable)
                                    success = update_donor(donor_id, updated_data)
                                    if success:
                                        st.success("✅ Donor information updated successfully!")
                                        st.session_state.editing_donor = False
                                        # Update the session state data
                                        st.session_state.selected_donor_data.update(updated_data)
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to update donor information")
                                else:
                                    st.error("❌ Update services not available")

                            except Exception as e:
                                st.error(f"❌ Error updating donor: {str(e)}")

                    if cancel_edit:
                        st.session_state.editing_donor = False
                        st.rerun()

            st.markdown("---")

        # AI Profile Generation Section - MOVED UP for immediate access
        st.subheader("🤖 AI-Powered Profile Generation")
        
        # Check if profile generator is available
        profile_status = None
        if get_profile_generator_status:
            try:
                profile_status = get_profile_generator_status()
            except Exception as e:
                st.error(f"Error checking profile generator status: {e}")
        
        # Show backend connection status
        backend_status = profile_status.get("backend_status", "unknown") if profile_status else "unknown"
        if backend_status == "unavailable":
            st.error("🚨 Backend Service Unavailable")
            st.warning("The Railway deployment appears to be down. Profile generation is currently unavailable.")
            st.info("💡 **Troubleshooting Steps:**")
            st.markdown("""
            1. Check your Railway deployment status
            2. Verify environment variables are configured
            3. Check Railway logs for errors
            4. Ensure the Flask app is running on the correct port
            """)
        elif backend_status == "error":
            st.warning("⚠️ Backend Connection Error")
            st.info("There was an error connecting to the backend service.")

        if profile_status and profile_status.get("available"):
            st.success("✅ AI Profile Generator Available")

            # Show available models
            models = profile_status.get("models", {})
            if models:
                model_info = []
                for provider, info in models.items():
                    model_info.append(f"**{provider.title()}**: {', '.join(info.get('models', []))}")
                st.info("Available models: " + " | ".join(model_info))

            # Google Docs status
            if profile_status.get("google_docs"):
                st.success("📄 Google Docs export enabled")
            else:
                st.warning("⚠️ Google Docs export not configured")
            
            # Profile generation controls with prominent buttons
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown("**Generate comprehensive donor profile with AI research and analysis**")
                st.caption("This will research the organization online and create a detailed profile document.")
            
            with col2:
                # Only show button if we have a donor name
                can_generate = selected_donor and selected_donor.strip()

                # Choose between regular and streaming generation
                use_streaming = st.checkbox("🔄 Show real-time progress", value=True, help="Display live progress updates during generation")

                if st.button("🚀 Generate Profile", type="primary", disabled=not can_generate, use_container_width=True):
                    if not can_generate:
                        st.error("Please enter a donor name first")
                    elif generate_donor_profile or generate_donor_profile_stream:
                        # Show additional info for custom donors
                        if custom_website:
                            st.info(f"🌐 Using website hint: {custom_website}")

                        # First check if donor already exists
                        if check_existing_donor:
                            with st.spinner(f"Checking if {selected_donor} already exists..."):
                                existing_check = check_existing_donor(selected_donor.strip())

                                if existing_check and existing_check.get("exists"):
                                    st.warning(f"⚠️ **Donor Already Exists!**")

                                    # Show existing donor data
                                    existing_donor = existing_check.get("donor_data", {})
                                    with st.expander("📋 Existing Donor Data", expanded=True):
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.write(f"**Organization:** {existing_donor.get('organization_name', 'N/A')}")
                                            st.write(f"**Contact:** {existing_donor.get('contact_person', 'N/A')}")
                                            st.write(f"**Email:** {existing_donor.get('contact_email', 'N/A')}")
                                            st.write(f"**Stage:** {existing_donor.get('current_stage', 'N/A')}")
                                        with col2:
                                            st.write(f"**Expected Amount:** ₹{existing_donor.get('expected_amount', 0):,}")
                                            st.write(f"**Probability:** {existing_donor.get('probability', 0)}%")
                                            st.write(f"**Assigned To:** {existing_donor.get('assigned_to', 'Unassigned')}")
                                            if existing_donor.get('document_url'):
                                                st.write(f"**Profile URL:** [View Document]({existing_donor['document_url']})")

                                    # Offer options
                                    col_force, col_cancel = st.columns(2)
                                    with col_force:
                                        if st.button("🔄 Generate New Profile Anyway", type="secondary", help="Force generate a new profile even though one exists"):
                                            # Use appropriate generation method
                                            if use_streaming and generate_donor_profile_stream:
                                                # Use streaming with progress tracking - improved layout
                                                force_progress_container = st.container()
                                                with force_progress_container:
                                                    st.markdown("---")
                                                    col_status_f, col_progress_f = st.columns([1, 3])

                                                    with col_status_f:
                                                        status_text = st.empty()
                                                    with col_progress_f:
                                                        progress_text = st.empty()
                                                        progress_bar = st.progress(0)

                                                def update_progress(progress_data):
                                                    step = progress_data.get('step', 0)
                                                    total_steps = progress_data.get('total_steps', 7)
                                                    message = progress_data.get('message', '')
                                                    progress_percent = (step / total_steps) * 100 if total_steps > 0 else 0

                                                    # Update progress bar with improved layout
                                                    progress_bar.progress(step / total_steps)
                                                    progress_text.markdown(f"**Progress: {progress_percent:.1f}%** - Step {step}/{total_steps}")
                                                    status_text.info(f"📊 {message}")

                                                result = generate_donor_profile_stream(
                                                    selected_donor.strip(),
                                                    export_to_docs=True,
                                                    force_generate=True,
                                                    progress_callback=update_progress
                                                )

                                                # Clear progress indicators with completion message
                                                progress_bar.progress(1.0)
                                                progress_text.markdown("**Progress: 100%** - Complete!")
                                                status_text.success("✅ Generation completed!")
                                            else:
                                                # Use regular generation
                                                with st.spinner(f"Force generating new AI profile for {selected_donor}..."):
                                                    result = generate_donor_profile(selected_donor.strip(), export_to_docs=True, force_generate=True)

                                            # Process result (same as below)
                                            if result and result.get("success"):
                                                st.success("✅ Profile generated successfully!")
                                                st.session_state.last_profile_result = result
                                                st.session_state.last_donor_name = selected_donor.strip()
                                                st.rerun()
                                            else:
                                                error = result.get('error', 'Unknown error') if result else 'No response'
                                                st.error(f"❌ Error generating profile: {error}")
                                                return
                                    with col_cancel:
                                        if st.button("✅ Use Existing Data", help="Use the existing donor data"):
                                            st.success("✅ Using existing donor data!")
                                            # Store existing data as if it were a generated result
                                            st.session_state.last_profile_result = {
                                                "success": True,
                                                "already_exists": True,
                                                "existing_donor": existing_donor,
                                                "message": "Using existing donor data"
                                            }
                                            st.session_state.last_donor_name = selected_donor.strip()
                                            st.rerun()
                                    return

                        # If no existing donor found, proceed with generation
                        if use_streaming and generate_donor_profile_stream:
                            # Use streaming with real-time progress
                            st.info("🔄 **Generating profile with real-time progress updates...**")

                            # Create a dedicated container for progress display with full width
                            progress_container = st.container()
                            with progress_container:
                                st.markdown("---")
                                col_status, col_progress = st.columns([1, 3])

                                with col_status:
                                    status_text = st.empty()
                                with col_progress:
                                    progress_text = st.empty()
                                    progress_bar = st.progress(0)

                            def update_progress(progress_data):
                                step = progress_data.get('step', 0)
                                total_steps = progress_data.get('total_steps', 0)
                                message = progress_data.get('message', '')

                                if total_steps and total_steps > 0:
                                    progress_ratio = min(max(step / total_steps, 0.0), 1.0)
                                    progress_percent = progress_ratio * 100
                                    step_display = f"{step}/{total_steps}"
                                else:
                                    progress_ratio = 0.0
                                    progress_percent = 0.0
                                    step_display = f"{step}/?"

                                # Update progress bar and status with better layout
                                progress_bar.progress(progress_ratio)
                                progress_text.markdown(f"**Progress: {progress_percent:.1f}%** - Step {step_display}")
                                status_text.info(f"📊 {message}")

                            try:
                                result = generate_donor_profile_stream(
                                    selected_donor.strip(),
                                    export_to_docs=True,
                                    progress_callback=update_progress
                                )

                                # Clear progress indicators with completion message
                                progress_bar.progress(1.0)
                                progress_text.markdown("**Progress: 100%** - Complete!")
                                status_text.success("✅ Generation completed!")

                            except Exception as e:
                                progress_bar.empty()
                                status_text.error(f"❌ Error during streaming generation: {e}")
                                return
                        else:
                            # Use regular generation with spinner
                            with st.spinner(f"Generating AI profile for {selected_donor}..."):
                                try:
                                    result = generate_donor_profile(selected_donor.strip(), export_to_docs=True)
                                except Exception as e:
                                    st.error(f"❌ Error generating profile: {e}")
                                    return

                        # Handle case where result is None
                        if result is None:
                            st.error("❌ Service returned no response. Backend may be unavailable.")
                            st.info("💡 Try again in a few minutes or check your Railway deployment status.")
                            return

                        if result.get("success"):
                            st.success("✅ Profile generated successfully!")

                            # Store the result in session state for later use
                            st.session_state.last_profile_result = result
                            st.session_state.last_donor_name = selected_donor.strip()

                            # Show results with action buttons
                            col_doc, col_pdf, col_db = st.columns(3)

                            with col_doc:
                                if result.get("document_url"):
                                    st.markdown(f"📄 **[View Google Doc]({result['document_url']})**")

                            with col_pdf:
                                if result.get("pdf_url"):
                                    st.markdown(f"📄 **[View PDF]({result['pdf_url']})**")
                                elif result.get("document_url"):
                                    if st.button("📄 Export PDF", help="Export the profile as PDF"):
                                        st.info("PDF export is included automatically with Google Docs export!")

                            with col_db:
                                if st.button("💾 Save to Database", type="secondary", help="Save this donor to your Google Sheets database"):
                                    # Prepare comprehensive donor data for database update
                                    donor_data = {
                                        "donor_name": selected_donor.strip(),
                                        "organization_name": selected_donor.strip(),
                                        "website": custom_website or "",
                                        "document_url": result.get("document_url", ""),
                                        "pdf_url": result.get("pdf_url", ""),
                                        "profile_generated": "Yes",
                                        "profile_date": result.get("end_time", "").split("T")[0] if result.get("end_time") else "",
                                        "current_stage": "Initial Outreach",
                                        "probability": 50,  # Default probability for generated profiles
                                        "next_action": "Review generated profile and initiate contact",
                                        "notes": f"AI-generated profile on {result.get('end_time', '').split('T')[0] if result.get('end_time') else ''}",
                                        "sector_tags": "Research Generated",
                                        "expected_amount": 0,
                                        "assigned_to": "",
                                        "alignment_score": 0
                                    }

                                    # Try to extract additional info from research data if available
                                    steps = result.get("steps", {})
                                    if steps.get("research", {}).get("success"):
                                        research_data = steps["research"].get("data", {})

                                        # Extract website from research if not provided
                                        if not donor_data["website"] and research_data.get("website_data", {}).get("url"):
                                            donor_data["website"] = research_data["website_data"]["url"]

                                        # Extract additional metadata from research
                                        if research_data.get("wikipedia"):
                                            wiki_data = research_data["wikipedia"]
                                            if isinstance(wiki_data, dict):
                                                # Look for sector information in wikipedia data
                                                sectors = []
                                                for key, value in wiki_data.items():
                                                    if key.lower() in ['industry', 'type', 'focus', 'sector'] and value:
                                                        sectors.append(str(value))
                                                if sectors:
                                                    donor_data["sector_tags"] = ", ".join(sectors[:3])  # Limit to 3 tags

                                    # Add generation quality score if available
                                    if steps.get("evaluation", {}).get("success"):
                                        score = steps["evaluation"].get("score", 0)
                                        if score:
                                            donor_data["alignment_score"] = min(score, 100)  # Cap at 100
                                            donor_data["notes"] += f" | Quality Score: {score}/100"

                                    # Update database
                                    if update_donor_database:
                                        with st.spinner("Saving to database..."):
                                            db_result = update_donor_database(donor_data)
                                            if db_result and db_result.get("success"):
                                                action = db_result.get("action", "saved")
                                                st.success(f"✅ Donor {action} to database successfully!")

                                                # Show what was saved
                                                with st.expander("📝 Saved Information"):
                                                    st.write(f"**Organization:** {donor_data['organization_name']}")
                                                    st.write(f"**Stage:** {donor_data['current_stage']}")
                                                    st.write(f"**Probability:** {donor_data['probability']}%")
                                                    if donor_data['website']:
                                                        st.write(f"**Website:** {donor_data['website']}")
                                                    if donor_data['sector_tags']:
                                                        st.write(f"**Sectors:** {donor_data['sector_tags']}")
                                                    if donor_data['alignment_score']:
                                                        st.write(f"**Alignment Score:** {donor_data['alignment_score']}/100")
                                                    st.write(f"**Documents:** [Profile]({donor_data['document_url']})")

                                            else:
                                                error = db_result.get("error", "Unknown error") if db_result else "Service unavailable"
                                                st.error(f"❌ Failed to save to database: {error}")

                                                # Show debug information for troubleshooting
                                                with st.expander("🔧 Debug Information"):
                                                    st.write("**Data being sent:**")
                                                    st.json(donor_data)
                                                    if db_result:
                                                        st.write("**Response received:**")
                                                        st.json(db_result)
                                    else:
                                        st.error("❌ Database update service not available")

                            # Show profile preview
                            if result.get("profile_content"):
                                with st.expander("📋 Profile Preview"):
                                    st.text_area(
                                        "Generated Profile",
                                        value=result["profile_content"][:1000] + "..." if len(result["profile_content"]) > 1000 else result["profile_content"],
                                        height=300,
                                        disabled=True
                                    )

                            # Show generation details
                            if result.get("steps"):
                                with st.expander("🔍 Generation Details"):
                                    steps = result["steps"]

                                    # Research step with enhanced info
                                    if steps.get("research", {}).get("success"):
                                        research_data = steps["research"].get("data", {})
                                        services_used = research_data.get("services_used", [])
                                        website_found = research_data.get("website_data", {}).get("url")

                                        st.success("✅ Research completed")
                                        if services_used:
                                            st.info(f"🔍 Services used: {', '.join(services_used)}")
                                        if website_found:
                                            st.info(f"🌐 Website found: {website_found}")

                                    # Generation step
                                    if steps.get("generation", {}).get("success"):
                                        model_used = steps["generation"].get("model_used", "Unknown")
                                        st.success(f"✅ Profile generated using {model_used}")

                                    # Evaluation step with detailed feedback
                                    if steps.get("evaluation", {}).get("success"):
                                        score = steps["evaluation"].get("score", "N/A")
                                        evaluation_text = steps["evaluation"].get("evaluation", "")
                                        st.success(f"✅ Quality evaluation: {score}/100")

                                        if evaluation_text and "SCORE:" in evaluation_text:
                                            # Extract feedback from evaluation
                                            feedback_start = evaluation_text.find("SCORE:") + len(f"SCORE: {score}")
                                            feedback = evaluation_text[feedback_start:].strip()
                                            if feedback:
                                                with st.expander("📊 Quality Feedback"):
                                                    st.text_area("AI Evaluation", feedback, height=150, disabled=True)

                                    # Export step
                                    if steps.get("export", {}).get("success"):
                                        st.success("✅ Exported to Google Docs")
                                    elif steps.get("export", {}).get("error"):
                                        st.warning(f"⚠️ Export issue: {steps['export']['error']}")

                                    # PDF Export step
                                    if steps.get("pdf_export", {}).get("success"):
                                        st.success("✅ Exported to PDF")
                                    elif steps.get("pdf_export", {}).get("error"):
                                        st.warning(f"⚠️ PDF export issue: {steps['pdf_export']['error']}")

                                    # Search services status
                                    research_data = steps.get("research", {}).get("data", {})
                                    if research_data.get("services_status"):
                                        with st.expander("🔧 Search Services Status"):
                                            services_status = research_data["services_status"]
                                            for service, status in services_status.items():
                                                if status.get("enabled"):
                                                    quota_status = "💚 Active" if not status.get("quota_exhausted") else "🔴 Quota Exhausted"
                                                    limit = status.get('free_limit', 'N/A')
                                                    if limit == float('inf'):
                                                        limit = "Unlimited"
                                                    st.write(f"**{service.title()}**: {quota_status} (Priority: {status.get('priority', 'N/A')}, Limit: {limit}/month)")

                        else:
                            st.error(f"❌ Profile generation failed: {result.get('error', 'Unknown error')}")

                    else:
                        st.error("Profile generation function not available")
            
            with col3:
                # Highlight Save/Add to Database button
                if st.button("💾 Save Prospect", type="secondary", use_container_width=True, help="Save this prospect to your database"):
                    # Prepare basic prospect data for database
                    prospect_data = {
                        "donor_name": selected_donor.strip(),
                        "organization_name": selected_donor.strip(),
                        "website": custom_website or "",
                        "current_stage": "Initial Contact",
                        "probability": 25,  # Default probability for prospects
                        "next_action": "Initial research and outreach",
                        "notes": f"Prospect added manually on {datetime.now().strftime('%Y-%m-%d')}",
                        "sector_tags": "Manual Entry",
                        "expected_amount": 0,
                        "assigned_to": "",
                        "alignment_score": 0,
                        "profile_generated": "No",
                        "document_url": "",
                        "pdf_url": ""
                    }

                    # Save to database
                    if update_donor_database:
                        with st.spinner("Saving prospect to database..."):
                            db_result = update_donor_database(prospect_data)
                            if db_result and db_result.get("success"):
                                action = db_result.get("action", "saved")
                                st.success(f"✅ Prospect {action} to database successfully!")

                                # Show what was saved
                                with st.expander("📝 Saved Prospect Information"):
                                    st.write(f"**Organization:** {prospect_data['organization_name']}")
                                    st.write(f"**Stage:** {prospect_data['current_stage']}")
                                    st.write(f"**Probability:** {prospect_data['probability']}%")
                                    if prospect_data['website']:
                                        st.write(f"**Website:** {prospect_data['website']}")
                                    st.write(f"**Next Action:** {prospect_data['next_action']}")
                            else:
                                error = db_result.get("error", "Unknown error") if db_result else "Service unavailable"
                                st.error(f"❌ Failed to save prospect: {error}")

                                # Show debug information
                                with st.expander("🔧 Debug Information"):
                                    st.json(prospect_data)
                                    if db_result:
                                        st.json(db_result)
                    else:
                        st.error("❌ Database update service not available")
        
        else:
            st.warning("⚠️ AI Profile Generator not available")
            if profile_status and profile_status.get("error"):
                st.error(f"Error: {profile_status['error']}")
            st.info("To enable AI profile generation, configure AI models (Anthropic/OpenAI) and Google credentials.")
        
        st.markdown("---")

        # Display Generated Profile Results
        if hasattr(st.session_state, 'last_profile_result') and st.session_state.last_profile_result:
            result = st.session_state.last_profile_result

            if result.get("success") and result.get("profile_content"):
                st.subheader("🎯 Generated Profile Results")

                # Show the full generated profile
                with st.expander("📄 Complete AI-Generated Profile", expanded=True):
                    st.markdown(result["profile_content"])

                # Show research data and sources
                steps = result.get("steps") or {}
                if steps:

                    # Research data section
                    if steps.get("research", {}).get("success"):
                        research_data = steps["research"].get("data", {})
                        if research_data:
                            with st.expander("🔍 Research Data & Sources"):
                                st.markdown("**Sources used for profile generation:**")

                                # Wikipedia data
                                if research_data.get("wikipedia"):
                                    st.markdown("**📚 Wikipedia Information:**")
                                    wiki_data = research_data["wikipedia"]
                                    if isinstance(wiki_data, dict):
                                        for key, value in wiki_data.items():
                                            if value and str(value).strip():
                                                st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
                                    else:
                                        st.write(f"• {wiki_data}")
                                    st.markdown("---")

                                # Website data
                                if research_data.get("website"):
                                    st.markdown("**🌐 Website Information:**")
                                    website_data = research_data["website"]
                                    if isinstance(website_data, dict):
                                        for key, value in website_data.items():
                                            if value and str(value).strip():
                                                st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
                                    else:
                                        st.write(f"• {website_data}")
                                    st.markdown("---")

                                # Additional sources
                                if research_data.get("additional_sources"):
                                    st.markdown("**📰 Additional Sources:**")
                                    sources = research_data["additional_sources"]
                                    if isinstance(sources, list):
                                        for source in sources:
                                            st.write(f"• {source}")
                                    else:
                                        st.write(f"• {sources}")

                # Show generation metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    model_used = steps.get("generation", {}).get("model_used", "Unknown")
                    st.metric("AI Model Used", model_used)
                with col2:
                    if steps.get("evaluation", {}).get("success"):
                        score = steps["evaluation"].get("score", "N/A")
                        st.metric("Quality Score", f"{score}/100")
                with col3:
                    profile_length = len(result.get("profile_content", ""))
                    st.metric("Profile Length", f"{profile_length:,} chars")

                st.markdown("---")

        # Donor profile display - sample data section
        st.subheader(f"📋 {selected_donor} Profile")

        # Basic information
        st.markdown("**Contact Information**")
        col_a, col_b = st.columns(2)

        with col_a:
            st.text_input("Organization", value="ABC Corporation", disabled=True)
            st.text_input("Contact Person", value="John Smith", disabled=True)
            st.text_input("Email", value="john@abccorp.com", disabled=True)

        with col_b:
            st.text_input("Phone", value="+1 (555) 123-4567", disabled=True)
            st.text_input("Website", value="www.abccorp.com", disabled=True)
            st.text_input("Industry", value="Technology", disabled=True)

        # Quick Stats in a horizontal layout for better space usage
        st.markdown("---")
        st.markdown("**📊 Quick Stats**")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Donated", "₹50,00,000", "₹5,00,000")
        with col2:
            st.metric("Donations Count", "3", "1")
        with col3:
            st.metric("Avg Donation", "₹16,66,667", "₹2,00,000")
        with col4:
            st.metric("Last Donation", "Jan 2024", "2 months ago")

        # Engagement score
        st.markdown("---")
        st.markdown("**Engagement Score**")
        col_eng1, col_eng2 = st.columns([3, 1])
        with col_eng1:
            st.progress(0.75)
        with col_eng2:
            st.caption("75% - High Engagement")

        # Donation history - DEMOTED and collapsed by default
        has_donation_data = True  # For demo purposes, we'll assume there's data

        if has_donation_data:
            with st.expander("📊 Donation History", expanded=False):
                donation_data = {
                    'Date': ['2024-01-15', '2023-12-10', '2023-11-05'],
                    'Amount': ['₹25,00,000', '₹15,00,000', '₹10,00,000'],
                    'Purpose': ['Education Program', 'General Fund', 'Emergency Relief'],
                    'Status': ['Completed', 'Completed', 'Completed']
                }

                import pandas as pd
                df = pd.DataFrame(donation_data)
                st.dataframe(df, use_container_width=True)
        else:
            st.info("📊 No donation history available for this prospect")
            
            # Communication preferences
            st.markdown("**Communication Preferences**")
            st.checkbox("Email Updates", value=True, disabled=True)
            st.checkbox("Newsletter", value=True, disabled=True)
            st.checkbox("Event Invitations", value=False, disabled=True)
    
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✏️ Edit Profile"):
            st.info("Edit profile functionality would open here")
    
    with col2:
        if st.button("📧 Send Email"):
            st.info("Email composer would open here")
    
    with col3:
        if st.button("📅 Schedule Meeting"):
            st.info("Meeting scheduler would open here")
    
    with col4:
        if st.button("📊 View Analytics"):
            st.info("Analytics dashboard would open here")

if __name__ == "__main__":
    main()
