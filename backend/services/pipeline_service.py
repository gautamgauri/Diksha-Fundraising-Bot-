#!/usr/bin/env python3
"""
Pipeline Service - Unified interface for pipeline operations
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PipelineService:
    """Service for pipeline-related operations"""
    
    def __init__(self, sheets_db=None):
        """Initialize with sheets database"""
        self.sheets_db = sheets_db
    
    def get_pipeline(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all pipeline data grouped by current stage"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return {}
        
        try:
            return self.sheets_db.get_pipeline()
        except Exception as e:
            logger.error(f"Error getting pipeline: {e}")
            return {}
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get pipeline summary statistics"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return {}
        
        try:
            pipeline = self.sheets_db.get_pipeline()
            
            summary = {
                "total_organizations": sum(len(orgs) for orgs in pipeline.values()),
                "stage_breakdown": {stage: len(orgs) for stage, orgs in pipeline.items()},
                "recent_updates": []
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
            
            summary['active_prospects'] = active_prospects[:6]  # Limit total
            return summary
            
        except Exception as e:
            logger.error(f"Error getting pipeline summary: {e}")
            return {}
    
    def get_stages(self) -> List[str]:
        """Get list of all current stages in the pipeline"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return []
        
        try:
            return self.sheets_db.get_stages()
        except Exception as e:
            logger.error(f"Error getting stages: {e}")
            return []
    
    def get_organizations_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        """Get all organizations in a specific stage"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return []
        
        try:
            return self.sheets_db.get_orgs_by_stage(stage)
        except Exception as e:
            logger.error(f"Error getting organizations by stage: {e}")
            return []
    
    def search_organizations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for organizations across all tabs"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return []
        
        try:
            return self.sheets_db.search_across_all_tabs(query, limit)
        except Exception as e:
            logger.error(f"Error searching organizations: {e}")
            return []
    
    def get_tab_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary information for all tabs"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return {}
        
        try:
            return self.sheets_db.get_tab_summary()
        except Exception as e:
            logger.error(f"Error getting tab summary: {e}")
            return {}
    
    def get_all_tabs(self) -> List[str]:
        """Get list of all available tabs in the spreadsheet"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return []
        
        try:
            return self.sheets_db.get_all_tabs()
        except Exception as e:
            logger.error(f"Error getting all tabs: {e}")
            return []
    
    def get_tab_data(self, tab_name: str) -> List[List[str]]:
        """Get all data from a specific tab"""
        if not self.sheets_db or not self.sheets_db.initialized:
            return []
        
        try:
            return self.sheets_db.get_tab_data(tab_name)
        except Exception as e:
            logger.error(f"Error getting tab data: {e}")
            return []
