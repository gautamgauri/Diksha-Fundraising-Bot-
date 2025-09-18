#!/usr/bin/env python3
"""
WhatsApp Message Generator Module
Diksha Foundation Fundraising Bot
"""

import os
import logging
import re
import time
from typing import Tuple, Dict, Any, Optional, List
from functools import wraps, lru_cache
from collections import defaultdict

# Import configuration
from config import (
    EMAIL_CONFIG, DIKSHA_INFO, CACHE_CONFIG, 
    API_CONFIG, SECURITY_CONFIG, DEPLOYMENT_MODE
)
from cache_manager import cache_manager

# Configure logging
logger = logging.getLogger(__name__)

def retry_on_failure(max_retries=None, delay=None):
    """Retry decorator with exponential backoff"""
    max_retries = max_retries or EMAIL_CONFIG['max_retries']
    delay = delay or EMAIL_CONFIG['retry_delay']
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
                        logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    else:
                        logger.error(f"All {max_retries} attempts failed: {e}")
            
            raise last_exception
        return wrapper
    return decorator

class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, max_calls=10, time_window=60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        now = time.time()
        # Clean old entries
        self.calls[identifier] = [
            call_time for call_time in self.calls[identifier] 
            if now - call_time < self.time_window
        ]
        
        if len(self.calls[identifier]) < self.max_calls:
            self.calls[identifier].append(now)
            return True
        return False

class WhatsAppGenerator:
    """WhatsApp message generator with template-based enhancement and AI integration"""
    
    def __init__(self):
        """Initialize the WhatsApp generator"""
        self.claude_api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.enhancement_mode = "claude"  # Default mode
        
        # Configuration from config file
        self.max_tokens = EMAIL_CONFIG['max_tokens']
        self.temperature = EMAIL_CONFIG['temperature']
        self.similarity_threshold = EMAIL_CONFIG['similarity_threshold']
        self.content_length_limit = 1000  # WhatsApp messages should be shorter
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            max_calls=EMAIL_CONFIG.get('max_calls_per_minute', 10),
            time_window=60
        )
        
        # Initialize Claude client if available
        self._initialize_claude()
        
        logger.info(f"WhatsAppGenerator initialized in {self.enhancement_mode} mode")
    
    def _initialize_claude(self):
        """Initialize Claude API client"""
        try:
            if self.claude_api_key:
                import anthropic
                self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)
                logger.info("Claude API client initialized successfully")
            else:
                self.claude_client = None
                logger.warning("Claude API key not found - using template mode only")
        except ImportError:
            self.claude_client = None
            logger.warning("Anthropic library not installed - using template mode only")
        except Exception as e:
            self.claude_client = None
            logger.error(f"Failed to initialize Claude client: {e}")
    
    def _sanitize_input(self, text: str) -> str:
        """Sanitize input text for security"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters and patterns
        text = re.sub(r'[<>]', '', text)
        text = text.replace('\x00', '')  # Remove null bytes
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)
        
        return text
    
    def set_mode(self, mode: str) -> str:
        """Set the message generation mode"""
        if mode in ["claude", "template"]:
            self.enhancement_mode = mode
            logger.info(f"WhatsApp generation mode set to: {mode}")
            return f"WhatsApp generation mode set to: {mode}"
        else:
            return f"Invalid mode '{mode}'. Use 'claude' or 'template'."
    
    def get_mode(self) -> str:
        """Get current message generation mode"""
        return self.enhancement_mode
    
    def get_available_templates(self) -> Dict[str, str]:
        """Get available WhatsApp message templates"""
        return {
            "initial_intro": "Friendly introduction and organization overview",
            "quick_connect": "Brief connection request for busy contacts",
            "program_highlight": "Showcase specific program with impact",
            "meeting_request": "Request for call or meeting",
            "follow_up": "Follow-up after initial contact",
            "thank_you": "Appreciation and next steps",
            "milestone_share": "Share achievements and milestones",
            "event_invite": "Invitation to events or webinars",
            "partnership_proposal": "Partnership opportunity discussion",
            "impact_update": "Regular impact and progress updates",
            "urgent_connect": "Time-sensitive opportunity sharing",
            "festival_greeting": "Festival wishes with organization context"
        }
    
    def get_template_content(self, template_type: str) -> str:
        """Get template content for a specific template type"""
        templates = {
            "initial_intro": """Hi {contact_person}! 👋

I'm reaching out from Diksha Foundation, a non-profit working on digital literacy and skill development across India.

We're making significant impact in {geography} and similar regions, and I believe {organization_name} might be interested in our work in {sector_tags}.

Would love to share more about our programs. Are you available for a brief chat this week?

Best regards,
Team Diksha Foundation 🌟""",

            "quick_connect": """Hi {contact_person}! 

Quick intro - I'm from Diksha Foundation, working on digital skills in rural India. 

Noticed {organization_name}'s work in {sector_tags} - would love to explore potential collaboration.

Can we connect for 10 mins this week?

Thanks! 🙏""",

            "program_highlight": """Hello {contact_person}!

Excited to share our latest milestone - we've trained 10,000+ students in digital skills across rural India! 📱💻

Our programs in {geography} are creating real employment opportunities. Given {organization_name}'s focus on {sector_tags}, thought you'd appreciate seeing our impact.

Would you be interested in learning more about partnership opportunities?

Warm regards,
Diksha Foundation Team""",

            "meeting_request": """Hi {contact_person},

Hope you're doing well! 

I'm from Diksha Foundation and would love to discuss how we can collaborate with {organization_name} on digital literacy initiatives.

Our work in {geography} aligns well with your {sector_tags} focus. 

Would you have 15-20 minutes for a call this week to explore synergies?

Looking forward to hearing from you! 📞""",

            "follow_up": """Hi {contact_person},

Following up on our previous conversation about Diksha Foundation's work in digital literacy.

As discussed, we're seeing great results in {geography} and would love {organization_name}'s support in scaling our impact.

When would be a good time to continue our discussion?

Best,
Team Diksha 🚀""",

            "thank_you": """Dear {contact_person},

Thank you so much for taking the time to learn about Diksha Foundation! 🙏

Your insights about {organization_name}'s approach to {sector_tags} were really valuable.

As next steps, I'll share our detailed proposal and impact metrics. 

Looking forward to a meaningful partnership!

Gratefully,
Diksha Foundation""",

            "milestone_share": """🎉 Exciting news, {contact_person}!

Diksha Foundation just reached a major milestone - 50,000+ lives impacted through our digital literacy programs!

Our work in {geography} continues to create sustainable livelihoods. 

Thought {organization_name} would appreciate seeing the progress in {sector_tags} space.

Would love to share more details if you're interested! 📊""",

            "event_invite": """Hi {contact_person}! 

Diksha Foundation is hosting a virtual impact showcase next week showcasing our work in digital skills and rural development.

Given {organization_name}'s interest in {sector_tags}, thought this might be relevant for you.

Would you like to join us? I can send the details.

Hope to see you there! 🎪""",

            "partnership_proposal": """Hello {contact_person},

I hope this message finds you well!

Diksha Foundation has an exciting partnership opportunity that aligns perfectly with {organization_name}'s mission in {sector_tags}.

We're looking to expand our digital literacy programs in {geography} and believe your expertise could make a huge difference.

Could we schedule a call to discuss this further?

Warm regards! 🤝""",

            "impact_update": """Hi {contact_person}! 📈

Quick update from Diksha Foundation:
• 2,500+ new students trained this quarter
• 85% job placement rate in {geography}
• New partnerships in {sector_tags} sector

Thought {organization_name} would appreciate seeing the progress!

Always here to discuss collaboration opportunities.

Best wishes! ✨""",

            "urgent_connect": """Hi {contact_person}! ⏰

Hope you're well! 

We have a time-sensitive opportunity at Diksha Foundation that could be perfect for {organization_name}.

A major funding window for {sector_tags} initiatives in {geography} is closing soon, and we'd love to discuss joint participation.

Could we connect today or tomorrow?

Thanks! 🚀""",

            "festival_greeting": """🎊 Happy Diwali, {contact_person}!

May this festival of lights bring prosperity and joy to you and the entire {organization_name} team!

As we celebrate, we're grateful for partners who share our vision of digital empowerment in {geography}.

Wishing you a bright year ahead filled with impactful collaborations! ✨

Warm regards,
Team Diksha Foundation"""
        }
        
        return templates.get(template_type, "")
    
    @retry_on_failure()
    def _enhance_with_claude(self, template_message: str, donor_data: Dict[str, Any]) -> str:
        """Enhance WhatsApp message using Claude AI"""
        if not self.claude_client:
            return template_message
        
        if not self.rate_limiter.is_allowed("claude_whatsapp"):
            logger.warning("Rate limit exceeded for Claude WhatsApp API")
            return template_message
        
        try:
            # Create WhatsApp-specific enhancement prompt
            enhancement_prompt = f"""
Please enhance this WhatsApp message for fundraising outreach. Keep it:
- Conversational and friendly (WhatsApp style)
- Under 300 words (optimal for mobile reading)
- Professional yet approachable
- Include relevant emojis naturally
- Maintain the personal touch

Donor Context:
- Organization: {donor_data.get('organization_name', 'N/A')}
- Sector: {donor_data.get('sector_tags', 'N/A')}
- Geography: {donor_data.get('geography', 'N/A')}
- Stage: {donor_data.get('current_stage', 'N/A')}
- Priority: {donor_data.get('priority', 'Medium')}
- Grant Size: {donor_data.get('estimated_grant_size', 'N/A')}
- Notes: {donor_data.get('notes', 'N/A')}

Current message:
{template_message}

Enhanced WhatsApp message:"""

            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{
                    "role": "user", 
                    "content": enhancement_prompt
                }]
            )
            
            enhanced_message = response.content[0].text.strip()
            
            # Validate message length for WhatsApp
            if len(enhanced_message) > 1500:  # WhatsApp practical limit
                enhanced_message = enhanced_message[:1400] + "..."
            
            logger.info("Successfully enhanced WhatsApp message with Claude")
            return enhanced_message
            
        except Exception as e:
            logger.error(f"Claude enhancement failed: {e}")
            return template_message
    
    def generate_message(self, template_type: str, donor_data: Dict[str, Any], mode: str = None) -> str:
        """Generate a WhatsApp message based on template and donor data"""
        try:
            # Use instance mode if not specified
            mode = mode or self.enhancement_mode
            
            # Sanitize inputs
            template_type = self._sanitize_input(template_type)
            
            # Get base template
            template_content = self.get_template_content(template_type)
            if not template_content:
                logger.error(f"Template '{template_type}' not found")
                return "Template not found"
            
            # Fill in donor data
            try:
                formatted_message = template_content.format(
                    contact_person=donor_data.get('contact_person', 'there'),
                    organization_name=donor_data.get('organization_name', 'your organization'),
                    sector_tags=donor_data.get('sector_tags', 'social impact'),
                    geography=donor_data.get('geography', 'India'),
                    current_stage=donor_data.get('current_stage', 'initial contact'),
                    estimated_grant_size=donor_data.get('estimated_grant_size', 'TBD'),
                    alignment_score=donor_data.get('alignment_score', '7'),
                    priority=donor_data.get('priority', 'Medium')
                )
            except KeyError as e:
                logger.warning(f"Missing template variable: {e}")
                formatted_message = template_content
            
            # Enhance with AI if in Claude mode
            if mode == "claude" and self.claude_client:
                formatted_message = self._enhance_with_claude(formatted_message, donor_data)
            
            # Final validation
            if len(formatted_message) > 1600:
                formatted_message = formatted_message[:1500] + "..."
                logger.warning("Message truncated to WhatsApp length limit")
            
            return formatted_message
            
        except Exception as e:
            logger.error(f"Error generating WhatsApp message: {e}")
            return f"Error generating message: {str(e)}"
    
    def get_message_analytics(self, message: str) -> Dict[str, Any]:
        """Analyze WhatsApp message for effectiveness"""
        if not message:
            return {}
        
        words = len(message.split())
        chars = len(message)
        lines = len(message.split('\n'))
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF]', message))
        
        # Calculate readability score
        readability = "Good"
        if words < 20:
            readability = "Too Short"
        elif words > 100:
            readability = "Too Long"
        elif chars > 1000:
            readability = "Consider Shortening"
        
        # WhatsApp effectiveness score
        effectiveness = min(100, max(0,
            (min(words / 50, 1) * 30) +  # Optimal length factor
            (min(emoji_count / 3, 1) * 20) +  # Emoji engagement factor
            (30 if lines > 1 else 20) +  # Structure factor
            (20)  # Base score
        ))
        
        return {
            'word_count': words,
            'character_count': chars,
            'line_count': lines,
            'emoji_count': emoji_count,
            'readability': readability,
            'effectiveness_score': effectiveness,
            'platform_optimized': chars <= 1000 and words <= 80
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health information"""
        return {
            'mode': self.enhancement_mode,
            'claude_available': self.claude_client is not None,
            'api_key_configured': bool(self.claude_api_key),
            'templates_count': len(self.get_available_templates()),
            'rate_limit_status': 'OK',
            'cache_enabled': bool(cache_manager),
            'timestamp': time.time()
        }

# Global instance for easy access
whatsapp_generator = WhatsAppGenerator()

if __name__ == "__main__":
    # Test the WhatsApp generator
    generator = WhatsAppGenerator()
    
    sample_donor = {
        'organization_name': 'Tech Foundation',
        'contact_person': 'Priya Sharma',
        'sector_tags': 'Education Technology',
        'geography': 'Karnataka',
        'alignment_score': '9',
        'priority': 'High',
        'current_stage': 'Initial Contact',
        'estimated_grant_size': '₹15,00,000',
        'notes': 'Interested in digital literacy programs for rural students'
    }
    
    print("🧪 Testing WhatsApp Generator")
    print("=" * 50)
    
    # Test templates
    templates = generator.get_available_templates()
    print(f"\n📱 Available Templates: {len(templates)}")
    for template_type, description in templates.items():
        print(f"   • {template_type}: {description}")
    
    # Test message generation
    print(f"\n📝 Testing Message Generation")
    message = generator.generate_message('initial_intro', sample_donor, 'template')
    print(f"Generated message:\n{message}")
    
    # Test analytics
    analytics = generator.get_message_analytics(message)
    print(f"\n📊 Message Analytics: {analytics}")
