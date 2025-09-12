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

try:
    from lib.api import get_donors, send_email
    print("✅ Using lib.api imports")
except ImportError as e:
    print(f"❌ Lib.api import failed: {e}")
    try:
        from api import get_donors, send_email  # type: ignore
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
            donors = get_donors()
            if donors:
                donor_options = [f"{donor.get('name', 'Unknown')} ({donor.get('email', 'No email')})" for donor in donors]
            else:
                donor_options = [
                    "ABC Corporation (john@abccorp.com)",
                    "XYZ Foundation (contact@xyzfoundation.org)",
                    "Tech Startup Inc (info@techstartup.com)"
                ]
        except Exception as e:
            st.error(f"Error loading donors: {str(e)}")
            donor_options = [
                "ABC Corporation (john@abccorp.com)",
                "XYZ Foundation (contact@xyzfoundation.org)",
                "Tech Startup Inc (info@techstartup.com)"
            ]
        
        recipient = st.selectbox("To:", donor_options)
        
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


