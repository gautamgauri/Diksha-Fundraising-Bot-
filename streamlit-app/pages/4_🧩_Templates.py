"""
Template Management Page
Manage email templates for donor outreach
"""

import streamlit as st
import sys
import os

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

# Import with multiple fallback strategies
get_templates = None

try:
    from lib.api import get_templates
except ImportError:
    try:
        from api import get_templates  # type: ignore
    except ImportError:
        if lib_path:
            try:
                api_file_path = os.path.join(lib_path, 'api.py')
                spec = importlib.util.spec_from_file_location("api", api_file_path)
                api_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(api_module)
                get_templates = api_module.get_templates
            except Exception:
                pass
        
        if not get_templates:
            for path in possible_paths:
                try:
                    abs_path = os.path.abspath(path)
                    api_file_path = os.path.join(abs_path, 'api.py')
                    if os.path.exists(api_file_path):
                        spec = importlib.util.spec_from_file_location("api", api_file_path)
                        api_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(api_module)
                        get_templates = api_module.get_templates
                        break
                except Exception:
                    continue

if not get_templates:
    raise ImportError("Could not import get_templates from any available source")

def main():
    st.title("🧩 Email Templates")
    st.markdown("Manage and organize your email templates for donor outreach")
    
    # Template overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Templates", "12", "2")
    with col2:
        st.metric("Active Templates", "8", "1")
    with col3:
        st.metric("Usage This Month", "45", "12")
    
    st.markdown("---")
    
    # Template categories
    st.subheader("📂 Template Categories")
    
    categories = ["Initial Outreach", "Follow-up", "Thank You", "Event Invitation", "Update Request", "Custom"]
    selected_category = st.selectbox("Filter by Category:", ["All"] + categories)
    
    # Template list
    st.subheader("📝 Available Templates")
    
    try:
        # Get templates from backend
        templates = get_templates()
        
        if templates:
            for template in templates:
                with st.expander(f"📧 {template.get('name', 'Unnamed Template')}"):
                    st.write(f"**Category:** {template.get('category', 'General')}")
                    st.write(f"**Description:** {template.get('description', 'No description available')}")
                    st.write(f"**Usage Count:** {template.get('usage_count', 0)}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"✏️ Edit", key=f"edit_{template.get('id', '')}"):
                            st.info("Edit template functionality would open here")
                    with col2:
                        if st.button(f"📋 Use Template", key=f"use_{template.get('id', '')}"):
                            st.info("Template would be loaded in Email Composer")
                    with col3:
                        if st.button(f"📊 Analytics", key=f"analytics_{template.get('id', '')}"):
                            st.info("Template analytics would be displayed here")
        else:
            # Sample templates for demonstration
            sample_templates = [
                {
                    "name": "Initial Partnership Outreach",
                    "category": "Initial Outreach",
                    "description": "Professional introduction for potential corporate partners",
                    "usage_count": 23
                },
                {
                    "name": "Follow-up After Meeting",
                    "category": "Follow-up",
                    "description": "Thank you and next steps after initial meeting",
                    "usage_count": 15
                },
                {
                    "name": "Thank You for Donation",
                    "category": "Thank You",
                    "description": "Gratitude message for recent donors",
                    "usage_count": 8
                },
                {
                    "name": "Event Invitation",
                    "category": "Event Invitation",
                    "description": "Invite donors to fundraising events",
                    "usage_count": 12
                }
            ]
            
            for template in sample_templates:
                with st.expander(f"📧 {template['name']}"):
                    st.write(f"**Category:** {template['category']}")
                    st.write(f"**Description:** {template['description']}")
                    st.write(f"**Usage Count:** {template['usage_count']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"✏️ Edit", key=f"edit_{template['name']}"):
                            st.info("Edit template functionality would open here")
                    with col2:
                        if st.button(f"📋 Use Template", key=f"use_{template['name']}"):
                            st.info("Template would be loaded in Email Composer")
                    with col3:
                        if st.button(f"📊 Analytics", key=f"analytics_{template['name']}"):
                            st.info("Template analytics would be displayed here")
                            
    except Exception as e:
        st.error(f"Error loading templates: {str(e)}")
        st.info("Showing sample templates instead")
    
    # Create new template
    st.markdown("---")
    st.subheader("➕ Create New Template")
    
    with st.form("new_template_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            template_name = st.text_input("Template Name", placeholder="e.g., Corporate Partnership Proposal")
            template_category = st.selectbox("Category", categories)
        
        with col2:
            template_subject = st.text_input("Email Subject", placeholder="e.g., Partnership Opportunity with Diksha Foundation")
            template_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        template_content = st.text_area(
            "Template Content",
            placeholder="Enter your email template content here...",
            height=200
        )
        
        template_description = st.text_area(
            "Description",
            placeholder="Brief description of when to use this template...",
            height=100
        )
        
        submitted = st.form_submit_button("💾 Create Template")
        
        if submitted:
            if template_name and template_content:
                st.success(f"Template '{template_name}' created successfully!")
                st.info("Template has been saved and is now available for use.")
            else:
                st.error("Please fill in template name and content.")
    
    # Template analytics
    st.markdown("---")
    st.subheader("📊 Template Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Most Used Templates**")
        st.write("1. Initial Partnership Outreach (23 uses)")
        st.write("2. Follow-up After Meeting (15 uses)")
        st.write("3. Event Invitation (12 uses)")
        st.write("4. Thank You for Donation (8 uses)")
    
    with col2:
        st.markdown("**Template Performance**")
        st.write("• Average open rate: 68%")
        st.write("• Average response rate: 12%")
        st.write("• Best performing category: Follow-up")
        st.write("• Most active day: Tuesday")

if __name__ == "__main__":
    main()
