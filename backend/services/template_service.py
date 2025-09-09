#!/usr/bin/env python3
"""
Template Service - Unified interface for template operations
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class TemplateService:
    """Service for template-related operations"""
    
    def __init__(self, email_generator=None):
        """Initialize with email generator"""
        self.email_generator = email_generator
    
    def get_available_templates(self) -> Dict[str, str]:
        """Get available email templates"""
        if not self.email_generator:
            return {}
        
        try:
            return self.email_generator.get_available_templates()
        except Exception as e:
            logger.error(f"Error getting available templates: {e}")
            return {}
    
    def get_template_content(self, template_name: str) -> Optional[str]:
        """Get the actual content of a specific template"""
        if not self.email_generator:
            return None
        
        try:
            return self.email_generator.get_template_content(template_name)
        except Exception as e:
            logger.error(f"Error getting template content: {e}")
            return None
    
    def get_current_mode(self) -> str:
        """Get current email generation mode"""
        if not self.email_generator:
            return "template"
        
        try:
            return self.email_generator.get_mode()
        except Exception as e:
            logger.error(f"Error getting current mode: {e}")
            return "template"
    
    def set_mode(self, mode: str) -> str:
        """Set the email generation mode"""
        if not self.email_generator:
            return f"Email generator not available"
        
        try:
            return self.email_generator.set_mode(mode)
        except Exception as e:
            logger.error(f"Error setting mode: {e}")
            return f"Error setting mode: {e}"
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get comprehensive template information"""
        if not self.email_generator:
            return {
                "available": False,
                "error": "Email generator not available"
            }
        
        try:
            templates = self.email_generator.get_available_templates()
            current_mode = self.email_generator.get_mode()
            
            # Check if we have actual template content from Drive
            drive_templates = {}
            template_sources = {}
            
            for template_name in templates.keys():
                template_content = self.email_generator.get_template_content(template_name)
                if template_content and len(template_content) > 50:
                    # This is actual content from Drive
                    drive_templates[template_name] = True
                    template_sources[template_name] = "Drive"
                else:
                    # This is a hardcoded description
                    template_sources[template_name] = "Hardcoded"
            
            return {
                "available": True,
                "templates": templates,
                "current_mode": current_mode,
                "drive_templates_available": bool(drive_templates),
                "template_sources": template_sources,
                "drive_template_count": len(drive_templates),
                "template_descriptions": {
                    'identification': 'Initial outreach to new prospects',
                    'engagement': 'Building relationships and sharing concepts',
                    'proposal': 'Formal proposal submissions',
                    'followup': 'Follow-up communications',
                    'celebration': 'Grant secured celebrations'
                }
            }
        except Exception as e:
            logger.error(f"Error getting template info: {e}")
            return {
                "available": False,
                "error": str(e)
            }
