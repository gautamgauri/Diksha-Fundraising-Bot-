#!/usr/bin/env python3
"""
Context Helpers for Diksha Foundation Fundraising Bot
Gathers relevant context data for natural language processing
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ContextHelpers:
    """Context gathering for natural language processing"""
    
    def __init__(self, sheets_db=None, email_generator=None):
        """Initialize with dependencies"""
        self.sheets_db = sheets_db
        self.email_generator = email_generator
    
    def get_relevant_donor_context(self, query: str) -> dict:
        """Extract relevant donor information based on user query"""
        context = {}
        
        try:
            if not self.sheets_db or not self.sheets_db.initialized:
                return context
            
            # Extract organization names from query
            query_lower = query.lower()
            words = query_lower.split()
            
            # Common organization keywords to look for
            org_indicators = ['wipro', 'tata', 'hdfc', 'infosys', 'bharti', 'azim premji', 'ford', 'gates']
            
            found_orgs = []
            for word in words:
                if any(indicator in word for indicator in org_indicators):
                    # Try to find matching organizations
                    matches = self.sheets_db.find_org(word)
                    if matches:
                        found_orgs.extend(matches[:2])  # Limit to 2 matches per word
            
            # If specific orgs mentioned, include their data
            if found_orgs:
                context['mentioned_organizations'] = found_orgs[:3]  # Limit to 3 total
            
            # If asking about sector/geography, get relevant orgs
            if any(sector in query_lower for sector in ['education', 'health', 'technology', 'rural', 'urban']):
                # Get sample organizations from relevant sectors
                pipeline = self.sheets_db.get_pipeline()
                sample_orgs = []
                for stage, orgs in pipeline.items():
                    for org in orgs[:2]:  # Limit samples
                        if any(sector in org.get('sector_tags', '').lower() for sector in ['education', 'health', 'technology']):
                            sample_orgs.append({
                                'name': org['organization_name'],
                                'sector': org.get('sector_tags', ''),
                                'stage': org['current_stage']
                            })
                            if len(sample_orgs) >= 5:
                                break
                    if len(sample_orgs) >= 5:
                        break
                
                if sample_orgs:
                    context['sector_examples'] = sample_orgs
        
        except Exception as e:
            logger.error(f"Error getting donor context: {e}")
        
        return context
    
    def get_template_context(self) -> dict:
        """Get available email templates information with enhanced Drive template support"""
        try:
            if not self.email_generator:
                return {}
            
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
                'available_templates': templates,
                'current_mode': current_mode,
                'drive_templates_available': bool(drive_templates),
                'template_sources': template_sources,
                'drive_template_count': len(drive_templates),
                'template_descriptions': {
                    'identification': 'Initial outreach to new prospects',
                    'engagement': 'Building relationships and sharing concepts',
                    'proposal': 'Formal proposal submissions',
                    'followup': 'Follow-up communications',
                    'celebration': 'Grant secured celebrations'
                }
            }
        except Exception as e:
            logger.error(f"Error getting template context: {e}")
            return {}
    
    def get_pipeline_insights(self) -> dict:
        """Get current pipeline insights and statistics"""
        try:
            if not self.sheets_db or not self.sheets_db.initialized:
                return {}
            
            pipeline = self.sheets_db.get_pipeline()
            insights = {
                'total_organizations': sum(len(orgs) for orgs in pipeline.values()),
                'stage_breakdown': {stage: len(orgs) for stage, orgs in pipeline.items()},
                'recent_updates': []
            }
            
            # Add sample of active prospects
            active_prospects = []
            for stage, orgs in pipeline.items():
                if stage in ['Identification', 'Engagement', 'Proposal']:
                    for org in orgs[:2]:  # Limit to 2 per stage
                        active_prospects.append({
                            'name': org['organization_name'],
                            'stage': stage,
                            'sector': org.get('sector_tags', ''),
                            'priority': org.get('priority', '')
                        })
            
            insights['active_prospects'] = active_prospects[:6]  # Limit total
            return insights
            
        except Exception as e:
            logger.error(f"Error getting pipeline insights: {e}")
            return {}
    
    def get_combined_context(self, query: str) -> dict:
        """Get combined context for natural language processing"""
        donor_context = self.get_relevant_donor_context(query)
        template_context = self.get_template_context()
        pipeline_context = self.get_pipeline_insights()
        
        return {
            **donor_context,
            **template_context,
            **pipeline_context
        }
