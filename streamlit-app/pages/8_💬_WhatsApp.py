"""
WhatsApp Message Composer Page
AI-powered WhatsApp message composition with personalization
"""

import streamlit as st
import sys
import os
from datetime import datetime
import json
import re

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
    if os.path.exists(abs_path) and (os.path.exists(os.path.join(abs_path, 'api.py')) or os.path.exists(os.path.join(abs_path, 'whatsapp_generator.py'))):
        lib_path = abs_path
        break

if lib_path and lib_path not in sys.path:
    sys.path.insert(0, lib_path)

# Fallback functions
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

# Initialize WhatsAppGenerator
whatsapp_generator = None
try:
    # Try to import WhatsAppGenerator from the root directory
    whatsapp_generator_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'whatsapp_generator.py')
    if os.path.exists(whatsapp_generator_path):
        spec = importlib.util.spec_from_file_location("whatsapp_generator", whatsapp_generator_path)
        whatsapp_generator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(whatsapp_generator_module)
        WhatsAppGenerator = whatsapp_generator_module.WhatsAppGenerator
        whatsapp_generator = WhatsAppGenerator()
        print("SUCCESS: WhatsAppGenerator loaded from root directory")
    else:
        print("WhatsAppGenerator not found in root directory")
except Exception as e:
    print(f"Failed to load WhatsAppGenerator: {e}")

# Import other functions with fallbacks
get_cached_pipeline_data = fallback_get_cached_pipeline_data

try:
    from lib.api import get_cached_pipeline_data
    print("Using lib.api imports")
except ImportError as e:
    print(f"Lib.api import failed: {e}")

# Page configuration
st.set_page_config(
    page_title="WhatsApp Composer - Diksha Fundraising",
    page_icon="💬",
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
        st.markdown("### 👤 Selected Contact Profile")
        st.markdown(f"**Organization:** {donor_data.get('organization_name', 'N/A')}")
        st.markdown(f"**Contact:** {donor_data.get('contact_person', 'N/A')}")
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

def format_whatsapp_message(message: str) -> str:
    """Format message for WhatsApp display"""
    # Convert markdown-style formatting to WhatsApp formatting
    message = re.sub(r'\*\*(.*?)\*\*', r'*\1*', message)  # Bold
    message = re.sub(r'\*(.*?)\*', r'_\1_', message)      # Italic
    return message

def get_whatsapp_link(phone_number: str, message: str) -> str:
    """Generate WhatsApp web link"""
    # Clean phone number (remove non-digits)
    clean_phone = re.sub(r'[^\d]', '', phone_number)
    
    # URL encode the message
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    
    return f"https://wa.me/{clean_phone}?text={encoded_message}"

def main():
    st.title("💬 WhatsApp Message Composer")
    st.markdown("🤖 **AI-powered WhatsApp messages optimized for mobile engagement**")

    # Workflow indicator
    st.markdown("### 📋 Workflow: Template → AI Customize → Preview → Send via WhatsApp")

    col_flow1, col_flow2, col_flow3, col_flow4 = st.columns(4)
    with col_flow1:
        st.info("1️⃣ **Select Template**\nChoose from 12+ WhatsApp templates")
    with col_flow2:
        st.info("2️⃣ **AI Personalization**\nAutomatic customization with donor data")
    with col_flow3:
        st.info("3️⃣ **Mobile Preview**\nSee how it looks on WhatsApp")
    with col_flow4:
        st.info("4️⃣ **Quick Send**\nOne-click WhatsApp Web launch")

    st.markdown("---")

    # Check if WhatsAppGenerator is available
    if not whatsapp_generator:
        st.error("⚠️ WhatsAppGenerator not available. Using basic mode.")
        st.info("💡 To enable advanced features, ensure whatsapp_generator.py is available in the project root.")
    else:
        st.success("💬 WhatsApp message system with AI enhancement ready!")

    # Main layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Compose WhatsApp Message")

        # Step 1: Recipient Selection
        st.markdown("#### Step 1: Select Contact")

        try:
            pipeline_data = get_cached_pipeline_data()
            if pipeline_data:
                # Create enhanced donor options with profile data
                donor_options = []
                donor_lookup = {}

                for donor in pipeline_data:
                    org_name = donor.get('organization_name', '').strip()
                    contact_person = donor.get('contact_person', '').strip()
                    stage = donor.get('current_stage', 'Unknown')
                    alignment = donor.get('alignment_score', '7')
                    priority = donor.get('priority', 'Medium')

                    if org_name and contact_person:
                        # Enhanced display with priority and alignment indicators
                        priority_emoji = "🔴" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
                        display_name = f"{priority_emoji} {org_name} ({contact_person}) - {stage} - Score: {alignment}/10"
                        donor_options.append(display_name)
                        donor_lookup[display_name] = donor

                if not donor_options:
                    st.warning("No valid contacts found in pipeline. Using sample data.")
                    donor_options = ["🟡 Sample Corporation (John Smith) - Initial Contact - Score: 8/10"]
                    donor_lookup = {donor_options[0]: fallback_get_cached_pipeline_data()[0]}
            else:
                donor_options = ["🟡 Sample Corporation (John Smith) - Initial Contact - Score: 8/10"]
                donor_lookup = {donor_options[0]: fallback_get_cached_pipeline_data()[0]}
        except Exception as e:
            st.error(f"Error loading contact data: {str(e)}")
            donor_options = ["🟡 Sample Corporation (John Smith) - Initial Contact - Score: 8/10"]
            donor_lookup = {donor_options[0]: fallback_get_cached_pipeline_data()[0]}

        recipient = st.selectbox("Select Contact:", donor_options)
        selected_donor = donor_lookup.get(recipient)

        if selected_donor:
            display_donor_profile_preview(selected_donor)

        # Step 2: Enhanced Template Selection
        st.markdown("#### Step 2: Choose Message Template")

        if whatsapp_generator:
            # Get WhatsApp templates
            available_templates = whatsapp_generator.get_available_templates()

            # Group templates by category
            template_categories = {
                "🎯 **First Contact & Introduction**": ["initial_intro", "quick_connect", "program_highlight"],
                "🤝 **Engagement & Meetings**": ["meeting_request", "follow_up", "thank_you"],
                "📊 **Updates & Sharing**": ["milestone_share", "impact_update", "partnership_proposal"],
                "🎉 **Events & Special Occasions**": ["event_invite", "festival_greeting", "urgent_connect"]
            }

            # Template selection with enhanced UI
            selected_category = st.selectbox(
                "Message Category:",
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
                selected_template_key = "initial_intro"
                st.warning("Using default template")
        else:
            # Basic template selection for fallback
            basic_templates = {
                "Initial Introduction": "initial_intro",
                "Quick Connect": "quick_connect",
                "Meeting Request": "meeting_request",
                "Follow Up": "follow_up",
                "Thank You": "thank_you"
            }
            selected_template_display = st.selectbox("Template:", list(basic_templates.keys()))
            selected_template_key = basic_templates[selected_template_display]

        # Step 3: Additional Context
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

        # Phone number input
        phone_number = st.text_input(
            "📱 WhatsApp Number (optional):",
            placeholder="+91XXXXXXXXXX",
            help="Include country code for direct WhatsApp link"
        )

        # Step 4: Generate AI-Customized Message
        st.markdown("#### Step 4: Generate AI-Customized Message")

        if st.button("💬 Generate AI-Customized WhatsApp Message", type="primary", use_container_width=True):
            if selected_donor and whatsapp_generator:
                with st.spinner("🤖 AI is customizing your WhatsApp message..."):
                    try:
                        # Prepare donor data for generation
                        donor_data_for_generation = selected_donor.copy()

                        # Add custom context if provided
                        if custom_context:
                            existing_notes = donor_data_for_generation.get('notes', '')
                            donor_data_for_generation['notes'] = f"{existing_notes}\n\nCustom Context: {custom_context}"

                        if key_points:
                            donor_data_for_generation['key_points'] = key_points

                        # Generate base template for comparison
                        whatsapp_generator.set_mode("template")
                        base_message = whatsapp_generator.generate_message(
                            selected_template_key,
                            donor_data_for_generation,
                            mode="template"
                        )

                        # Store base version
                        if base_message:
                            st.session_state.base_message = base_message

                        # Generate AI-enhanced version
                        whatsapp_generator.set_mode("claude")
                        enhanced_message = whatsapp_generator.generate_message(
                            selected_template_key,
                            donor_data_for_generation,
                            mode="claude"
                        )

                        if enhanced_message:
                            st.session_state.generated_message = enhanced_message
                            st.session_state.customization_successful = True

                            st.success("🎉 AI-customized WhatsApp message ready!")

                            # Show customization analysis
                            if base_message:
                                base_length = len(base_message.split())
                                enhanced_length = len(enhanced_message.split())
                                improvement = ((enhanced_length - base_length) / base_length * 100) if base_length > 0 else 0

                                with st.expander("📊 AI Customization Analysis", expanded=True):
                                    st.markdown("**🎯 Message Transformation:**")

                                    col_before, col_after = st.columns(2)
                                    with col_before:
                                        st.markdown("**📋 Base Template**")
                                        st.metric("Word Count", base_length)
                                        st.caption("Template-based message")

                                    with col_after:
                                        st.markdown("**🤖 AI Customized**")
                                        st.metric("Word Count", enhanced_length, delta=f"{improvement:+.1f}%")
                                        st.caption("AI-enhanced message")

                                    # Get analytics
                                    analytics = whatsapp_generator.get_message_analytics(enhanced_message)
                                    
                                    col_analytics1, col_analytics2 = st.columns(2)
                                    with col_analytics1:
                                        st.markdown("**📱 WhatsApp Optimization:**")
                                        st.write(f"• Character Count: {analytics.get('character_count', 0)}")
                                        st.write(f"• Emoji Count: {analytics.get('emoji_count', 0)}")
                                        st.write(f"• Mobile Optimized: {'✅' if analytics.get('platform_optimized') else '❌'}")

                                    with col_analytics2:
                                        st.markdown("**🎯 Effectiveness:**")
                                        effectiveness = analytics.get('effectiveness_score', 0)
                                        st.metric("Effectiveness Score", f"{effectiveness:.0f}%")
                                        st.write(f"• Readability: {analytics.get('readability', 'Unknown')}")

                        else:
                            # Fallback to base template if AI fails
                            st.warning("⚠️ AI enhancement failed, using base template")
                            if base_message:
                                st.session_state.generated_message = base_message
                            else:
                                st.error("❌ Message generation failed completely")

                    except Exception as e:
                        st.error(f"❌ Customization error: {str(e)}")
            else:
                st.error("Please select a contact and ensure WhatsAppGenerator is available")

        # Template Preview Option
        if selected_template_key and whatsapp_generator:
            with st.expander("👁️ Preview Template Before Customization", expanded=False):
                try:
                    # Get template description
                    available_templates = whatsapp_generator.get_available_templates()
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
                    preview_message = whatsapp_generator.generate_message(
                        selected_template_key,
                        sample_donor,
                        mode="template"
                    )

                    if preview_message:
                        st.markdown("**Sample Message:**")
                        st.text_area("Template Preview", preview_message, height=150, disabled=True)

                except Exception as e:
                    st.error(f"Preview failed: {str(e)}")

        # Step 5: Review & Edit Message
        st.markdown("#### Step 5: Review & Edit Message")

        # Message body
        message_body = st.text_area(
            "WhatsApp Message:",
            value=st.session_state.get('generated_message', ''),
            placeholder="Enter your WhatsApp message content...",
            height=200,
            help="Keep it concise and mobile-friendly (under 300 words)"
        )

    with col2:
        st.subheader("📱 WhatsApp Preview")

        # Enhanced mobile preview
        if message_body and selected_donor:
            st.markdown("**Mobile Preview:**")

            # WhatsApp-style preview
            with st.container():
                st.markdown(f"""
                <div style="
                    border: 2px solid #25D366;
                    border-radius: 15px;
                    padding: 16px;
                    margin-bottom: 16px;
                    background-color: #F0F8F0;
                    box-shadow: 0 2px 8px rgba(37,211,102,0.2);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                ">
                <div style="
                    display: flex;
                    align-items: center;
                    margin-bottom: 12px;
                    padding-bottom: 8px;
                    border-bottom: 1px solid #E0E0E0;
                ">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #25D366, #128C7E);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 12px;
                        color: white;
                        font-weight: bold;
                    ">
                        {selected_donor.get('contact_person', 'Contact')[0]}
                    </div>
                    <div>
                        <strong>{selected_donor.get('contact_person', 'Contact')}</strong><br>
                        <small style="color: #666;">{selected_donor.get('organization_name', 'Organization')}</small>
                    </div>
                </div>
                <div style="
                    background: white;
                    padding: 12px;
                    border-radius: 8px;
                    border-left: 4px solid #25D366;
                    white-space: pre-wrap;
                    line-height: 1.4;
                ">{format_whatsapp_message(message_body)}</div>
                </div>
                """, unsafe_allow_html=True)

            # Message analytics
            if whatsapp_generator:
                analytics = whatsapp_generator.get_message_analytics(message_body)
                
                st.markdown("---")
                st.markdown("**📊 Message Analysis**")

                col_metric1, col_metric2 = st.columns(2)
                with col_metric1:
                    st.metric("Word Count", analytics.get('word_count', 0))
                    st.metric("Character Count", analytics.get('character_count', 0))

                with col_metric2:
                    effectiveness = analytics.get('effectiveness_score', 0)
                    effectiveness_color = "🟢" if effectiveness >= 80 else "🟡" if effectiveness >= 60 else "🔴"
                    st.metric("Effectiveness", f"{effectiveness_color} {effectiveness:.0f}%")
                    st.metric("Emojis", f"😊 {analytics.get('emoji_count', 0)}")

                # Mobile optimization status
                if analytics.get('platform_optimized'):
                    st.success("📱 Optimized for mobile")
                else:
                    st.warning("📱 Consider shortening for mobile")

        else:
            st.info("📝 Select contact and generate message to see preview")

            # Template suggestions based on donor stage
            if selected_donor:
                stage = selected_donor.get('current_stage', '').lower()
                st.markdown("**💡 Template Suggestions**")

                if 'initial' in stage or 'outreach' in stage:
                    st.info("🎯 Try 'Initial Intro' or 'Quick Connect' for new contacts")
                elif 'engaged' in stage:
                    st.info("🤝 Use 'Meeting Request' or 'Program Highlight' to deepen engagement")
                elif 'proposal' in stage:
                    st.info("📊 Consider 'Partnership Proposal' or 'Impact Update'")
                else:
                    st.info("✨ Choose template based on your communication goal")

        # WhatsAppGenerator status
        if whatsapp_generator:
            st.markdown("---")
            st.markdown("**🤖 AI Status**")

            mode = whatsapp_generator.get_mode()
            available_templates = len(whatsapp_generator.get_available_templates())

            st.success(f"✅ Mode: {mode.title()}")
            st.info(f"📱 Templates: {available_templates} available")

            # Health check button
            if st.button("🔍 System Health Check", use_container_width=True):
                try:
                    health = whatsapp_generator.get_system_health()
                    st.json(health)
                except Exception as e:
                    st.error(f"Health check failed: {str(e)}")

    # Action buttons
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("💬 Send via WhatsApp", type="primary", use_container_width=True):
            if message_body and selected_donor:
                try:
                    contact_name = selected_donor.get('contact_person', 'Contact')
                    
                    if phone_number:
                        # Generate WhatsApp link
                        whatsapp_link = get_whatsapp_link(phone_number, message_body)
                        
                        st.success(f"✅ Ready to send to {contact_name}!")
                        st.markdown(f"**[📱 Open WhatsApp Web]({whatsapp_link})**", unsafe_allow_html=True)
                        
                        # Show instructions
                        with st.expander("📱 How to Send", expanded=True):
                            st.markdown("""
                            **Steps to send:**
                            1. Click the 'Open WhatsApp Web' link above
                            2. WhatsApp Web will open with your message pre-filled
                            3. Review the message and click Send
                            4. Your message will be delivered instantly!
                            
                            **Note:** You need to be logged into WhatsApp Web for this to work.
                            """)
                    else:
                        st.success(f"✅ Message ready for {contact_name}!")
                        st.info("💡 Add a phone number to get direct WhatsApp link")
                        
                        # Copy-paste option
                        with st.expander("📋 Copy Message", expanded=True):
                            st.text_area("Message to copy:", message_body, height=100, key="copy_message")
                            st.caption("Copy this message and paste it in WhatsApp")

                except Exception as e:
                    st.error(f"❌ Error preparing WhatsApp message: {str(e)}")
            else:
                st.error("❌ Please complete the message before sending")

    with col2:
        if st.button("💾 Save Draft", use_container_width=True):
            if message_body:
                # Save draft logic would go here
                st.success("💾 Draft saved successfully!")
            else:
                st.warning("Nothing to save")

    with col3:
        if st.button("🔄 Reset Form", use_container_width=True):
            # Clear session state
            for key in ['generated_message', 'base_message', 'customization_successful']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    with col4:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.switch_page("streamlit_app.py")

if __name__ == "__main__":
    main()
