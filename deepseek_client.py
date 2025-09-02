#!/usr/bin/env python3
"""
DeepSeek API Client for Diksha Foundation Fundraising Bot
Handles natural language processing and AI-powered responses
"""

import os
import json
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """DeepSeek API client for natural language processing"""
    
    def __init__(self, api_key: str = None):
        """Initialize DeepSeek client"""
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.initialized = bool(self.api_key)
        
        if self.initialized:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            logger.info("✅ DeepSeek API client initialized")
        else:
            logger.warning("⚠️ DEEPSEEK_API_KEY not set - natural language chat disabled")
    
    def chat_completion(self, message: str, context: dict = None, 
                       donor_data: dict = None, templates_info: dict = None) -> Optional[str]:
        """Generate a response using DeepSeek API with donor and template context"""
        if not self.initialized:
            logger.warning("DeepSeek client not initialized")
            return None
            
        try:
            # Build enhanced system prompt with actual data
            system_prompt = self._build_system_prompt(donor_data, templates_info, context)
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}")
            return None
    
    def _build_system_prompt(self, donor_data: dict = None, 
                            templates_info: dict = None, 
                            context: dict = None) -> str:
        """Build system prompt with context"""
        system_prompt = """You are an AI assistant for the Diksha Foundation's fundraising team. 
        You help with donor relationship management, email generation, pipeline tracking, and fundraising strategy.
        
        You have access to:
        - Real-time donor database with organization information
        - Email template generation system
        - Pipeline status tracking
        - Grant proposal assistance
        - Historical donor profiles and interaction data"""
        
        # Add donor database context
        if donor_data:
            system_prompt += f"\n\nRELEVANT DONOR DATA:\n{json.dumps(donor_data, indent=2)}"
        
        # Add template information
        if templates_info:
            system_prompt += f"\n\nAVAILABLE EMAIL TEMPLATES:\n{json.dumps(templates_info, indent=2)}"
        
        # Add conversation context if available
        if context:
            system_prompt += f"\n\nCONVERSATION CONTEXT:\n{json.dumps(context, indent=2)}"
        
        system_prompt += "\n\nWhen discussing specific organizations, reference the actual data provided. When suggesting email generation, mention the appropriate templates and actual donor information available."
        
        return system_prompt
    
    def test_connection(self) -> bool:
        """Test DeepSeek API connectivity"""
        if not self.initialized:
            return False
            
        try:
            test_response = self.chat_completion("Hello", {})
            return bool(test_response)
        except Exception:
            return False
    
    def get_status(self) -> str:
        """Get DeepSeek API status"""
        if not self.initialized:
            return "not_configured"
        
        try:
            return "connected" if self.test_connection() else "failed"
        except Exception:
            return "failed"

# Global instance
deepseek_client = DeepSeekClient()

