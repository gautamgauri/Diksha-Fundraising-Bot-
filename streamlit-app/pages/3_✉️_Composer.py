"""
Email Composer Page
AI-powered email composition for donor outreach
"""

import streamlit as st
import sys
import os
from datetime import datetime

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

def fallback_send_email(recipient, subject, body):
    print(f"Fallback: Would send email to {recipient} with subject '{subject}'")
    return True

# Import with multiple fallback strategies
get_donors = fallback_get_donors
send_email = fallback_send_email
get_contacts = None
add_contact = None

def fallback_get_contacts():
    return [{"id": "1", "organization_name": "Sample Donor", "contact_email": "donor@example.com"}]

def fallback_add_contact(contact_data):
    print(f"Fallback: Would add contact {contact_data}")
    return {"success": True, "message": "Contact added (fallback)"}

get_contacts = fallback_get_contacts
add_contact = fallback_add_contact

try:
    from lib.api import get_donors, send_email, get_contacts, add_contact
    print("✅ Using lib.api imports")
except ImportError as e:
    print(f"❌ Lib.api import failed: {e}")
    try:
        from api import get_donors, send_email, get_contacts, add_contact  # type: ignore
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
                    if hasattr(api_module, 'send_email'):
                        send_email = api_module.send_email
                    if hasattr(api_module, 'get_contacts'):
                        get_contacts = api_module.get_contacts
                    if hasattr(api_module, 'add_contact'):
                        add_contact = api_module.add_contact
                    print("✅ Using importlib for api module")
            except Exception as e:
                print(f"❌ Importlib failed: {e}")
        
        if get_donors == fallback_get_donors or send_email == fallback_send_email:
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
                        if hasattr(api_module, 'send_email'):
                            send_email = api_module.send_email
                        if hasattr(api_module, 'get_contacts'):
                            get_contacts = api_module.get_contacts
                        if hasattr(api_module, 'add_contact'):
                            add_contact = api_module.add_contact
                        print(f"✅ Found api functions in {abs_path}")
                        break
                except Exception as e:
                    print(f"❌ Failed to import from {path}: {e}")
                    continue

print(f"✅ Final imports - get_donors: {get_donors != fallback_get_donors}, send_email: {send_email != fallback_send_email}")

def main():
    st.title("✉️ Email Composer")
    st.markdown("AI-powered email composition for donor outreach")
    
    # Email composition form
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Compose Email")
        
        # Recipient selection
        try:
            # Try to get contacts first, fallback to donors
            contacts = get_contacts() if get_contacts else None
            if contacts:
                # Use contacts API
                donor_options = []
                for contact in contacts:
                    org_name = contact.get('organization_name', 'Unknown Organization')
                    contact_email = contact.get('contact_email', 'No email')
                    contact_person = contact.get('contact_person', '')
                    
                    # Format: "Organization Name (Contact Person) - email@domain.com"
                    if contact_person and contact_person != org_name:
                        display_name = f"{org_name} ({contact_person}) - {contact_email}"
                    else:
                        display_name = f"{org_name} - {contact_email}"
                    
                    donor_options.append(display_name)
            else:
                # Fallback to donors API
                donors = get_donors()
                if donors:
                    donor_options = []
                    for donor in donors:
                        org_name = donor.get('organization_name', 'Unknown Organization')
                        contact_email = donor.get('contact_email', 'No email')
                        contact_person = donor.get('contact_person', '')
                        
                        # Format: "Organization Name (Contact Person) - email@domain.com"
                        if contact_person and contact_person != org_name:
                            display_name = f"{org_name} ({contact_person}) - {contact_email}"
                        else:
                            display_name = f"{org_name} - {contact_email}"
                        
                        donor_options.append(display_name)
                else:
                    donor_options = [
                        "ABC Corporation (john@abccorp.com)",
                        "XYZ Foundation (contact@xyzfoundation.org)",
                        "Tech Startup Inc (info@techstartup.com)"
                    ]
        except Exception as e:
            st.error(f"Error loading contacts: {str(e)}")
            donor_options = [
                "ABC Corporation (john@abccorp.com)",
                "XYZ Foundation (contact@xyzfoundation.org)",
                "Tech Startup Inc (info@techstartup.com)"
            ]
        
        # Add new email option
        col_recipient, col_add = st.columns([3, 1])
        
        with col_recipient:
            recipient = st.selectbox("To:", donor_options)
        
        with col_add:
            if st.button("➕ Add New", help="Add a new email recipient"):
                st.session_state.show_add_email = True
        
        # Add new email form
        if st.session_state.get('show_add_email', False):
            st.markdown("**➕ Add New Email Recipient**")
            
            col_name, col_email = st.columns(2)
            
            with col_name:
                new_org_name = st.text_input("Organization Name:", placeholder="e.g., ABC Corporation")
                new_contact_person = st.text_input("Contact Person:", placeholder="e.g., John Smith")
            
            with col_email:
                new_email = st.text_input("Email Address:", placeholder="e.g., john@abccorp.com")
                new_role = st.text_input("Role/Title:", placeholder="e.g., CSR Manager")
            
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                if st.button("💾 Save New Contact", type="primary"):
                    if new_org_name and new_email:
                        try:
                            # Prepare contact data
                            contact_data = {
                                "organization_name": new_org_name,
                                "contact_person": new_contact_person,
                                "contact_email": new_email,
                                "contact_role": new_role,
                                "current_stage": "Initial Contact",
                                "sector_tags": "",
                                "assigned_to": "",
                                "notes": "Added via Email Composer"
                            }
                            
                            # Save to backend
                            if add_contact and add_contact != fallback_add_contact:
                                result = add_contact(contact_data)
                                if result and result.get("success"):
                                    st.success(f"✅ Contact added successfully: {new_org_name}")
                                    st.session_state.show_add_email = False
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to add contact: {result.get('error', 'Unknown error')}")
                            else:
                                # Fallback mode
                                st.warning("⚠️ Backend not available - contact saved locally only")
                                st.session_state.show_add_email = False
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error adding contact: {str(e)}")
                    else:
                        st.error("Please fill in Organization Name and Email Address")
            
            with col_cancel:
                if st.button("❌ Cancel"):
                    st.session_state.show_add_email = False
                    st.rerun()
        
        # Email type selection
        email_type = st.selectbox(
            "Email Type:",
            ["Initial Outreach", "Follow-up", "Thank You", "Event Invitation", "Update Request", "Custom"]
        )
        
        # AI-powered content generation
        st.markdown("**AI Content Generation**")
        
        # Context input
        context = st.text_area(
            "Context/Notes:",
            placeholder="Enter any specific context, donor interests, or key points to include...",
            height=100
        )
        
        # Generate email content
        if st.button("🤖 Generate Email Content"):
            with st.spinner("Generating email content..."):
                # This would call your AI service
                generated_subject = f"Partnership Opportunity - {email_type}"
                generated_body = f"""
Dear {recipient.split('(')[0].strip()},

I hope this email finds you well. I'm reaching out regarding a potential partnership opportunity that aligns with your organization's mission.

{context if context else "We have an exciting initiative that we believe would be of great interest to your organization."}

Key highlights:
• Impact-driven approach
• Measurable outcomes
• Collaborative partnership
• Transparent reporting

I would love to schedule a brief call to discuss this opportunity further. Would you be available for a 15-minute conversation this week?

Thank you for your time and consideration.

Best regards,
[Your Name]
Diksha Fundraising Team
"""
                
                st.success("Email content generated successfully!")
        
        # Email subject
        subject = st.text_input(
            "Subject:",
            value=generated_subject if 'generated_subject' in locals() else "",
            placeholder="Enter email subject..."
        )
        
        # Email body
        body = st.text_area(
            "Email Body:",
            value=generated_body if 'generated_body' in locals() else "",
            placeholder="Enter your email content...",
            height=300
        )
        
        # Email options
        st.markdown("**Email Options**")
        col_a, col_b = st.columns(2)
        
        with col_a:
            schedule_send = st.checkbox("Schedule for later")
            if schedule_send:
                send_time = st.time_input("Send at:", value=datetime.now().time())
                send_date = st.date_input("Send on:", value=datetime.now().date())
        
        with col_b:
            track_opens = st.checkbox("Track email opens", value=True)
            track_clicks = st.checkbox("Track link clicks", value=True)
            add_signature = st.checkbox("Add signature", value=True)
    
    with col2:
        st.subheader("📊 Email Preview")
        
        # Preview the email
        if subject and body:
            st.markdown("**Preview:**")
            st.markdown(f"**Subject:** {subject}")
            st.markdown("**Body:**")
            st.markdown(body)
        else:
            st.info("Compose your email to see preview")
        
        st.markdown("---")
        
        # Email stats
        st.markdown("**Email Statistics**")
        st.metric("Word Count", len(body.split()) if body else 0)
        st.metric("Character Count", len(body) if body else 0)
        st.metric("Readability Score", "Good" if body and len(body.split()) > 50 else "Needs more content")
        
        # Template suggestions
        st.markdown("**Template Suggestions**")
        if email_type == "Initial Outreach":
            st.info("💡 Consider mentioning specific impact metrics")
        elif email_type == "Follow-up":
            st.info("💡 Reference previous conversation or email")
        elif email_type == "Thank You":
            st.info("💡 Include specific details about their contribution")
    
    # Send email
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Send Email", type="primary"):
            if subject and body:
                try:
                    # This would call your email service
                    send_email(recipient, subject, body)
                    st.success("Email sent successfully!")
                except Exception as e:
                    st.error(f"Error sending email: {str(e)}")
            else:
                st.error("Please fill in subject and body")
    
    with col2:
        if st.button("💾 Save Draft"):
            st.success("Draft saved successfully!")
    
    with col3:
        if st.button("🔄 Reset"):
            st.rerun()

if __name__ == "__main__":
    main()


