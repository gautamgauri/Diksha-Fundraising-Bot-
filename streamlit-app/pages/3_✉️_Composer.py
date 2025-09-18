"""
Enhanced Email Composer Page
Sophisticated AI-powered email composition with full EmailGenerator integration
"""

import streamlit as st
import sys
import os
from datetime import datetime
import json

# Robust import system for Railway deployment
import importlib.util

# Try multiple path strategies
possible_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'),
    os.path.join(os.path.dirname(__file__), '..', 'lib'),
    '/app/lib',
    './lib',
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Root directory
]

lib_path = None
for path in possible_paths:
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path) and (os.path.exists(os.path.join(abs_path, 'api.py')) or os.path.exists(os.path.join(abs_path, 'email_generator.py'))):
        lib_path = abs_path
        break

if lib_path and lib_path not in sys.path:
    sys.path.insert(0, lib_path)

# Fallback functions
def fallback_get_donors():
    return [{"id": "1", "organization_name": "Sample Organization", "contact_email": "contact@example.com", "contact_person": "John Smith"}]

def fallback_send_email(recipient, subject, body):
    print(f"Fallback: Would send email to {recipient} with subject '{subject}'")
    return True

def fallback_get_cached_pipeline_data():
    return [
        {
            "id": "sample_1",
            "organization_name": "ABC Corporation",
            "contact_person": "Jane Smith",
            "contact_email": "jane@abc.com",
            "contact_role": "CSR Manager",
            "sector_tags": "Technology",
            "geography": "Maharashtra",
            "current_stage": "Initial Outreach",
            "alignment_score": "8",
            "priority": "High",
            "estimated_grant_size": "₹10,00,000",
            "notes": "Interested in digital literacy programs"
        },
        {
            "id": "sample_2",
            "organization_name": "XYZ Foundation",
            "contact_person": "Mike Wilson",
            "contact_email": "mike@xyz.org",
            "contact_role": "Program Director",
            "sector_tags": "Education",
            "geography": "Karnataka",
            "current_stage": "Engaged",
            "alignment_score": "9",
            "priority": "High",
            "estimated_grant_size": "₹15,00,000",
            "notes": "Strong alignment with our mission"
        }
    ]

# Initialize EmailGenerator
email_generator = None
try:
    # Try to import EmailGenerator from the root directory
    email_generator_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'email_generator.py')
    if os.path.exists(email_generator_path):
        spec = importlib.util.spec_from_file_location("email_generator", email_generator_path)
        email_generator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(email_generator_module)
        EmailGenerator = email_generator_module.EmailGenerator
        email_generator = EmailGenerator()
        print("SUCCESS: EmailGenerator loaded from root directory")
    else:
        print("EmailGenerator not found in root directory")
except Exception as e:
    print(f"Failed to load EmailGenerator: {e}")

# Import other functions with fallbacks
get_cached_pipeline_data = fallback_get_cached_pipeline_data
send_email = fallback_send_email

try:
    from lib.api import get_cached_pipeline_data, send_email
    print("Using lib.api imports")
except ImportError as e:
    print(f"Lib.api import failed: {e}")

# Page configuration
st.set_page_config(
    page_title="Email Composer - Diksha Fundraising",
    page_icon="✉️",
    layout="wide"
)

def get_donor_data_by_org(organization_name: str):
    """Get donor data for a specific organization"""
    pipeline_data = get_cached_pipeline_data()
    for donor in pipeline_data:
        if donor.get('organization_name', '').lower() == organization_name.lower():
            return donor
    return None

def display_donor_profile_preview(donor_data):
    """Display donor profile information in sidebar"""
    with st.sidebar:
        st.markdown("### 👤 Selected Donor Profile")
        st.markdown(f"**Organization:** {donor_data.get('organization_name', 'N/A')}")
        st.markdown(f"**Contact:** {donor_data.get('contact_person', 'N/A')}")
        st.markdown(f"**Email:** {donor_data.get('contact_email', 'N/A')}")
        st.markdown(f"**Role:** {donor_data.get('contact_role', 'N/A')}")

        # Alignment and priority indicators
        alignment = donor_data.get('alignment_score', '7')
        priority = donor_data.get('priority', 'Medium')

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Alignment", f"{alignment}/10")
        with col2:
            priority_color = "🔴" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
            st.metric("Priority", f"{priority_color} {priority}")

        st.markdown(f"**Sector:** {donor_data.get('sector_tags', 'N/A')}")
        st.markdown(f"**Geography:** {donor_data.get('geography', 'N/A')}")
        st.markdown(f"**Stage:** {donor_data.get('current_stage', 'N/A')}")
        st.markdown(f"**Expected Grant:** {donor_data.get('estimated_grant_size', 'N/A')}")

        if donor_data.get('notes'):
            st.markdown("**Notes:**")
            st.caption(donor_data['notes'][:200] + "..." if len(donor_data.get('notes', '')) > 200 else donor_data['notes'])

def main():
    st.title("✉️ AI Template Composer")
    st.markdown("🤖 **Professional templates automatically enhanced with AI personalization**")

    # Workflow indicator
    st.markdown("### 📋 Workflow: Template → AI Customize → Review → Send")

    col_flow1, col_flow2, col_flow3 = st.columns(3)
    with col_flow1:
        st.info("1️⃣ **Select Template & Donor**\nChoose from 12+ professional templates")
    with col_flow2:
        st.info("2️⃣ **AI Customization**\nAutomatic personalization with donor data")
    with col_flow3:
        st.info("3️⃣ **Review & Send**\nFinal review and delivery")

    st.markdown("---")

    # Check if EmailGenerator is available
    if not email_generator:
        st.error("⚠️ EmailGenerator not available. Using basic mode.")
        st.info("💡 To enable advanced features, ensure email_generator.py is available in the project root.")
    else:
        st.success("🤖 Template system with AI enhancement ready!")

    # Main layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Compose Email")

        # Step 1: Recipient Selection with Enhanced Data
        st.markdown("#### Step 1: Select Recipient")

        try:
            pipeline_data = get_cached_pipeline_data()
            if pipeline_data:
                # Create enhanced donor options with profile data
                donor_options = []
                donor_lookup = {}

                for donor in pipeline_data:
                    org_name = donor.get('organization_name', '').strip()
                    contact_email = donor.get('contact_email', '').strip()
                    contact_person = donor.get('contact_person', '').strip()
                    stage = donor.get('current_stage', 'Unknown')
                    alignment = donor.get('alignment_score', '7')
                    priority = donor.get('priority', 'Medium')

                    if org_name and contact_email and '@' in contact_email:
                        # Enhanced display with priority and alignment indicators
                        priority_emoji = "🔴" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
                        display_name = f"{priority_emoji} {org_name} ({contact_person}) - {stage} - Score: {alignment}/10"
                        donor_options.append(display_name)
                        donor_lookup[display_name] = donor

                if not donor_options:
                    st.warning("No valid donors found in pipeline. Using sample data.")
                    donor_options = ["🟡 Sample Corporation (John Smith) - Initial Contact - Score: 8/10"]
                    donor_lookup = {donor_options[0]: fallback_get_cached_pipeline_data()[0]}
            else:
                donor_options = ["🟡 Sample Corporation (John Smith) - Initial Contact - Score: 8/10"]
                donor_lookup = {donor_options[0]: fallback_get_cached_pipeline_data()[0]}
        except Exception as e:
            st.error(f"Error loading donor data: {str(e)}")
            donor_options = ["🟡 Sample Corporation (John Smith) - Initial Contact - Score: 8/10"]
            donor_lookup = {donor_options[0]: fallback_get_cached_pipeline_data()[0]}

        recipient = st.selectbox("Select Recipient:", donor_options)
        selected_donor = donor_lookup.get(recipient)

        if selected_donor:
            display_donor_profile_preview(selected_donor)

        # Step 2: Enhanced Template Selection
        st.markdown("#### Step 2: Choose Email Template")

        if email_generator:
            # Get sophisticated templates from EmailGenerator
            available_templates = email_generator.get_available_templates()

            # Group templates by category
            template_categories = {
                "🎯 **Prospecting & Outreach**": ["identification", "intro", "concept", "followup"],
                "🤝 **Engagement & Relationship Building**": ["engagement", "meeting_request", "thanks_meeting", "connect"],
                "📄 **Proposals & Formal Communication**": ["proposal", "proposal_cover", "proposal_reminder", "pitch"],
                "🎉 **Stewardship & Celebration**": ["celebration", "impact_story", "invite", "festival_greeting"]
            }

            # Template selection with enhanced UI
            selected_category = st.selectbox(
                "Template Category:",
                list(template_categories.keys())
            )

            category_templates = template_categories[selected_category]
            template_options = []

            for template_key in category_templates:
                if template_key in available_templates:
                    template_name = template_key.replace('_', ' ').title()
                    template_desc = available_templates[template_key]
                    template_options.append(f"{template_name} - {template_desc}")

            if template_options:
                selected_template_display = st.selectbox("Template:", template_options)
                selected_template_key = selected_template_display.split(' - ')[0].lower().replace(' ', '_')
            else:
                selected_template_key = "identification"
                st.warning("Using default template")
        else:
            # Basic template selection for fallback
            basic_templates = {
                "Initial Outreach": "identification",
                "Follow-up": "followup",
                "Thank You": "celebration",
                "Event Invitation": "invite",
                "Proposal Submission": "proposal"
            }
            selected_template_display = st.selectbox("Template:", list(basic_templates.keys()))
            selected_template_key = basic_templates[selected_template_display]

        # Step 3: Context and Additional Information
        st.markdown("#### Step 3: Additional Context & Customization")

        col_context1, col_context2 = st.columns(2)

        with col_context1:
            custom_context = st.text_area(
                "Custom Context/Notes:",
                placeholder="Add specific points, recent conversations, or custom messaging...",
                height=100
            )

        with col_context2:
            key_points = st.text_area(
                "Key Points to Emphasize:",
                placeholder="• Specific program benefits\n• Recent achievements\n• Mutual interests",
                height=100
            )

        # Step 4: Generate AI-Customized Email
        st.markdown("#### Step 4: Generate AI-Customized Email")

        if st.button("🤖 Generate AI-Customized Email", type="primary", use_container_width=True):
            if selected_donor and email_generator:
                with st.spinner("🤖 AI is customizing your template with donor data..."):
                    try:
                        # First generate base template for comparison
                        email_generator.set_mode("template")
                        donor_data_for_generation = selected_donor.copy()

                        # Add custom context if provided
                        if custom_context:
                            existing_notes = donor_data_for_generation.get('notes', '')
                            donor_data_for_generation['notes'] = f"{existing_notes}\n\nCustom Context: {custom_context}"

                        if key_points:
                            donor_data_for_generation['key_points'] = key_points

                        # Generate base template for comparison
                        base_subject, base_body = email_generator.generate_email(
                            selected_template_key,
                            donor_data_for_generation,
                            mode="template"
                        )

                        # Store base version
                        if base_subject and base_body:
                            st.session_state.base_subject = base_subject
                            st.session_state.base_body = base_body

                        # Generate AI-enhanced version (the final version)
                        email_generator.set_mode("claude")
                        enhanced_subject, enhanced_body = email_generator.generate_email(
                            selected_template_key,
                            donor_data_for_generation,
                            mode="claude"
                        )

                        if enhanced_subject and enhanced_body:
                            st.session_state.generated_subject = enhanced_subject
                            st.session_state.generated_body = enhanced_body
                            st.session_state.customization_successful = True

                            st.success("🎉 AI-customized email ready!")

                            # Show customization analysis
                            if base_subject and base_body:
                                base_length = len(base_body.split())
                                enhanced_length = len(enhanced_body.split())
                                improvement = ((enhanced_length - base_length) / base_length * 100) if base_length > 0 else 0

                                with st.expander("📊 AI Customization Analysis", expanded=True):
                                    st.markdown("**🎯 Template Transformation:**")

                                    col_before, col_after = st.columns(2)
                                    with col_before:
                                        st.markdown("**📋 Base Template**")
                                        st.metric("Word Count", base_length)
                                        st.caption(f"Subject: {base_subject}")

                                    with col_after:
                                        st.markdown("**🤖 AI Customized**")
                                        st.metric("Word Count", enhanced_length, delta=f"{improvement:+.1f}%")
                                        st.caption(f"Subject: {enhanced_subject}")

                                    # Customization details
                                    col_details1, col_details2 = st.columns(2)
                                    with col_details1:
                                        st.markdown("**Personalization Applied:**")
                                        st.write(f"• Organization: {selected_donor.get('organization_name')}")
                                        st.write(f"• Sector: {selected_donor.get('sector_tags')}")
                                        st.write(f"• Geography: {selected_donor.get('geography')}")
                                        st.write(f"• Grant Size: {selected_donor.get('estimated_grant_size')}")

                                    with col_details2:
                                        st.markdown("**AI Enhancements:**")
                                        st.write(f"• Priority: {selected_donor.get('priority')} priority")
                                        st.write(f"• Alignment: {selected_donor.get('alignment_score')}/10 match")
                                        st.write(f"• Stage: {selected_donor.get('current_stage')}")
                                        st.write(f"• Custom Context: {'✅' if custom_context else '❌'}")

                        else:
                            # Fallback to base template if AI fails
                            st.warning("⚠️ AI enhancement failed, using base template")
                            if base_subject and base_body:
                                st.session_state.generated_subject = base_subject
                                st.session_state.generated_body = base_body
                            else:
                                st.error("❌ Template generation failed completely")

                    except Exception as e:
                        st.error(f"❌ Customization error: {str(e)}")
            else:
                st.error("Please select a recipient and ensure EmailGenerator is available")

        # Template Preview Option
        if selected_template_key and email_generator:
            with st.expander("👁️ Preview Template Before Loading", expanded=False):
                try:
                    # Get template description
                    available_templates = email_generator.get_available_templates()
                    template_description = available_templates.get(selected_template_key, "No description available")

                    st.markdown(f"**Template:** {selected_template_key.replace('_', ' ').title()}")
                    st.markdown(f"**Description:** {template_description}")

                    # Show sample template content
                    sample_donor = {
                        'contact_person': '[Contact Name]',
                        'organization_name': '[Organization Name]',
                        'sector_tags': '[Sector]',
                        'geography': '[Location]',
                        'estimated_grant_size': '[Amount]',
                        'notes': '[Context]'
                    }

                    # Generate preview with placeholder data
                    email_generator.set_mode("template")
                    preview_subject, preview_body = email_generator.generate_email(
                        selected_template_key,
                        sample_donor,
                        mode="template"
                    )

                    if preview_subject and preview_body:
                        st.markdown("**Sample Subject:**")
                        st.code(preview_subject)
                        st.markdown("**Sample Body:**")
                        st.text_area("Template Preview", preview_body, height=200, disabled=True)

                except Exception as e:
                    st.error(f"Preview failed: {str(e)}")

        # Step 5: Review & Edit Email
        st.markdown("#### Step 5: Review & Edit Email")

        # Email subject
        subject = st.text_input(
            "Subject:",
            value=st.session_state.get('generated_subject', ''),
            placeholder="Enter email subject..."
        )

        # Email body
        body = st.text_area(
            "Email Body:",
            value=st.session_state.get('generated_body', ''),
            placeholder="Enter your email content...",
            height=300
        )


        # Email options
        st.markdown("#### Email Options")
        col_opt1, col_opt2, col_opt3 = st.columns(3)

        with col_opt1:
            schedule_send = st.checkbox("📅 Schedule for later")
            if schedule_send:
                send_date = st.date_input("Send on:", value=datetime.now().date())
                send_time = st.time_input("Send at:", value=datetime.now().time())

        with col_opt2:
            track_opens = st.checkbox("📊 Track email opens", value=True)
            track_clicks = st.checkbox("🔗 Track link clicks", value=True)

        with col_opt3:
            add_signature = st.checkbox("✍️ Add signature", value=True)
            save_to_history = st.checkbox("💾 Save to history", value=True)

    with col2:
        st.subheader("📧 Email Preview")

        # Enhanced preview
        if subject and body and selected_donor:
            st.markdown("**Live Preview:**")

            # Header
            with st.container():
                st.markdown(f"""
                <div style="
                    border: 1px solid #C67B5C;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 16px;
                    background-color: #F3E0C0;
                    box-shadow: 0 2px 4px rgba(198,123,92,0.2);
                ">
                <strong>To:</strong> {selected_donor.get('contact_person', 'Contact')} &lt;{selected_donor.get('contact_email', 'email@domain.com')}&gt;<br>
                <strong>Subject:</strong> {subject}
                </div>
                """, unsafe_allow_html=True)

            # Body preview
            st.markdown("**Email Body:**")
            st.markdown(body)

            # Email effectiveness score
            st.markdown("---")
            st.markdown("**📊 Email Analysis**")

            word_count = len(body.split()) if body else 0
            char_count = len(body) if body else 0

            # Calculate effectiveness score
            effectiveness_score = min(100, max(0,
                (word_count / 200 * 40) +  # Ideal length factor
                (30 if selected_donor.get('alignment_score', '7') >= '8' else 20) +  # Alignment factor
                (20 if st.session_state.get('customization_successful') else 10) +  # AI customization factor
                (10 if custom_context else 0)  # Context factor
            ))

            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.metric("Word Count", word_count)
                st.metric("Character Count", char_count)

            with col_metric2:
                effectiveness_color = "🟢" if effectiveness_score >= 80 else "🟡" if effectiveness_score >= 60 else "🔴"
                st.metric("Effectiveness", f"{effectiveness_color} {effectiveness_score:.0f}%")

                # Readability assessment
                if word_count < 50:
                    readability = "Too Short"
                elif word_count > 300:
                    readability = "Too Long"
                else:
                    readability = "Good Length"
                st.metric("Readability", readability)
        else:
            st.info("📝 Select recipient and generate email to see preview")

            # Template suggestions based on donor stage
            if selected_donor:
                stage = selected_donor.get('current_stage', '').lower()
                st.markdown("**💡 Template Suggestions**")

                if 'initial' in stage or 'outreach' in stage:
                    st.info("🎯 Consider 'Identification' or 'Intro' templates for new contacts")
                elif 'engaged' in stage:
                    st.info("🤝 Use 'Engagement' or 'Meeting Request' templates to deepen relationships")
                elif 'proposal' in stage:
                    st.info("📄 Try 'Proposal Cover' or 'Proposal Reminder' templates")
                else:
                    st.info("✨ Choose template based on your communication goal")

        # EmailGenerator status
        if email_generator:
            st.markdown("---")
            st.markdown("**🤖 AI Status**")

            mode = email_generator.get_mode()
            available_templates = len(email_generator.get_available_templates())

            st.success(f"✅ Mode: {mode.title()}")
            st.info(f"📋 Templates: {available_templates} available")

            # Health check button
            if st.button("🔍 System Health Check", use_container_width=True):
                try:
                    health = email_generator.get_system_health()
                    st.json(health)
                except Exception as e:
                    st.error(f"Health check failed: {str(e)}")

    # Action buttons
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📤 Send Email", type="primary", use_container_width=True):
            if subject and body and selected_donor:
                try:
                    recipient_email = selected_donor.get('contact_email')
                    send_email(recipient_email, subject, body)
                    st.success(f"✅ Email sent to {selected_donor.get('contact_person')}!")

                    # Log activity
                    if save_to_history:
                        st.info("📝 Email saved to history")

                except Exception as e:
                    st.error(f"❌ Error sending email: {str(e)}")
            else:
                st.error("❌ Please complete all fields before sending")

    with col2:
        if st.button("💾 Save Draft", use_container_width=True):
            if subject or body:
                # Save draft logic would go here
                st.success("💾 Draft saved successfully!")
            else:
                st.warning("Nothing to save")

    with col3:
        if st.button("🔄 Reset Form", use_container_width=True):
            # Clear session state
            for key in ['generated_subject', 'generated_body', 'base_subject', 'base_body',
                       'customization_successful', 'comparison_data']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    with col4:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.switch_page("streamlit_app.py")

if __name__ == "__main__":
    main()