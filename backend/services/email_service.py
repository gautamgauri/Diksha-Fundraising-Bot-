#!/usr/bin/env python3
"""
Email Service - Unified interface for email operations
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    """Service for email-related operations"""
    
    def __init__(self, email_generator=None, sheets_db=None):
        """Initialize with email generator and sheets database"""
        self.email_generator = email_generator
        self.sheets_db = sheets_db
    
    def generate_email(self, template_type: str, donor_id: str, mode: Optional[str] = None) -> Dict[str, Any]:
        """Generate email for a donor"""
        if not self.email_generator:
            return {"success": False, "error": "Email generator not available"}
        
        if not self.sheets_db or not self.sheets_db.initialized:
            return {"success": False, "error": "Sheets database not available"}
        
        try:
            # Convert donor_id back to organization name
            org_name = donor_id.replace("_", " ").title()
            
            # Get organization data
            org_data = self.sheets_db.get_org_by_name(org_name)
            if not org_data:
                return {"success": False, "error": f"Organization '{org_name}' not found"}
            
            # Generate email
            subject, body = self.email_generator.generate_email(template_type, org_data, mode)
            
            if not subject or not body:
                return {"success": False, "error": f"Email generation failed: {body}"}
            
            # Create draft
            draft_id = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{donor_id}"
            
            draft = {
                "id": draft_id,
                "template_id": template_type,
                "donor_id": donor_id,
                "subject": subject,
                "content": body,
                "placeholders": {},
                "status": "draft",
                "created_at": datetime.now().isoformat(),
                "organization_name": org_name,
                "contact_person": org_data.get("contact_person", ""),
                "contact_email": org_data.get("email", ""),
                "sector": org_data.get("sector_tags", "")
            }
            
            return {"success": True, "data": draft}
            
        except Exception as e:
            logger.error(f"Error generating email: {e}")
            return {"success": False, "error": str(e)}
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get available email templates"""
        if not self.email_generator:
            return []
        
        try:
            templates = self.email_generator.get_available_templates()
            current_mode = self.email_generator.get_mode()
            
            # Convert to web UI format
            web_templates = []
            for template_id, template_info in templates.items():
                web_template = {
                    "id": template_id,
                    "name": template_info.get("name", template_id),
                    "description": template_info.get("description", ""),
                    "subject": template_info.get("subject", ""),
                    "content": template_info.get("content", ""),
                    "placeholders": template_info.get("placeholders", []),
                    "type": template_info.get("type", "intro"),
                    "mode": current_mode
                }
                web_templates.append(web_template)
            
            return web_templates
            
        except Exception as e:
            logger.error(f"Error getting templates: {e}")
            return []
    
    def get_template_content(self, template_id: str) -> Optional[str]:
        """Get template content"""
        if not self.email_generator:
            return None
        
        try:
            return self.email_generator.get_template_content(template_id)
        except Exception as e:
            logger.error(f"Error getting template content: {e}")
            return None
    
    def compare_templates(self, template_type: str, donor_id: str) -> Dict[str, Any]:
        """Compare base template vs enhanced version"""
        if not self.email_generator:
            return {"success": False, "error": "Email generator not available"}
        
        if not self.sheets_db or not self.sheets_db.initialized:
            return {"success": False, "error": "Sheets database not available"}
        
        try:
            # Convert donor_id back to organization name
            org_name = donor_id.replace("_", " ").title()
            
            # Get organization data
            org_data = self.sheets_db.get_org_by_name(org_name)
            if not org_data:
                return {"success": False, "error": f"Organization '{org_name}' not found"}
            
            # Use email generator's comparison method
            comparison_result = self.email_generator.compare_templates(template_type, org_data)
            
            if comparison_result.get("ok"):
                # Add additional context
                comparison_result["organization"] = org_name
                comparison_result["template_type"] = template_type
                comparison_result["donor_context"] = {
                    "sector": org_data.get("sector_tags", ""),
                    "geography": org_data.get("geography", ""),
                    "alignment_score": org_data.get("alignment_score", ""),
                    "priority": org_data.get("priority", ""),
                    "current_stage": org_data.get("current_stage", "")
                }
            
            return comparison_result
            
        except Exception as e:
            logger.error(f"Error comparing templates: {e}")
            return {"success": False, "error": str(e)}
    
    def get_donor_profile_info(self, donor_id: str) -> Dict[str, Any]:
        """Get donor profile information from Google Drive"""
        if not self.email_generator:
            return {"success": False, "error": "Email generator not available"}
        
        try:
            # Convert donor_id back to organization name
            org_name = donor_id.replace("_", " ").title()
            
            # Get donor profile information
            profile_info = self.email_generator.get_donor_profile_info(org_name)
            
            return profile_info
            
        except Exception as e:
            logger.error(f"Error getting donor profile info: {e}")
            return {"success": False, "error": str(e)}
    
    def send_email(self, draft_id: str) -> Dict[str, Any]:
        """Send email (mock implementation)"""
        try:
            # In a real implementation, you would:
            # 1. Retrieve the draft
            # 2. Send the email via Gmail API
            # 3. Log the thread_id and message_id
            # 4. Update the donor's last_contact_date
            
            # For now, return mock data
            thread_id = f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return {
                "success": True,
                "data": {
                    "thread_id": thread_id,
                    "message_id": message_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"success": False, "error": str(e)}
