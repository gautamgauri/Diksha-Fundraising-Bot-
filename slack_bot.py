#!/usr/bin/env python3
"""
Slack Bot Integration for Diksha Foundation Fundraising Bot
Handles Slack events, commands, and natural language processing with DeepSeek
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Import dependencies
try:
    from slack_bolt import App as SlackApp
    from slack_bolt.adapter.flask import SlackRequestHandler
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    logger.warning("⚠️ slack-bolt not available - Slack integration disabled")

class SlackBot:
    """Slack bot with DeepSeek natural language processing"""
    
    def __init__(self, bot_token: str = None, signing_secret: str = None, 
                 sheets_db=None, email_generator=None):
        """Initialize Slack bot"""
        self.bot_token = bot_token or os.environ.get("SLACK_BOT_TOKEN")
        self.signing_secret = signing_secret or os.environ.get("SLACK_SIGNING_SECRET")
        self.sheets_db = sheets_db
        self.email_generator = email_generator
        self.app = None
        self.handler = None
        self.initialized = False
        
        if SLACK_AVAILABLE and self.bot_token and self.signing_secret:
            try:
                self.app = SlackApp(
                    token=self.bot_token,
                    signing_secret=self.signing_secret
                )
                self.handler = SlackRequestHandler(self.app)
                self.initialized = True
                self._setup_event_handlers()
                logger.info("✅ Slack bot initialized successfully")
            except Exception as e:
                logger.error(f"❌ Slack initialization failed: {e}")
                self.app = None
                self.handler = None
        else:
            logger.warning("⚠️ Slack credentials not found. Running in test mode.")
    
    def _setup_event_handlers(self):
        """Setup Slack event handlers"""
        if not self.app:
            return
            
        @self.app.event("app_mention")
        def handle_app_mention(event, say):
            """Handle when the bot is mentioned with natural language processing"""
            try:
                # Extract the message text, removing the bot mention
                text = event.get("text", "")
                user_id = event.get("user")
                channel_id = event.get("channel")
                
                # Remove bot mention from text
                bot_user_id = self.app.client.auth_test()["user_id"]
                text = text.replace(f"<@{bot_user_id}>", "").strip()
                
                if not text:
                    say("Hi! I'm the Diksha Foundation fundraising bot. You can ask me questions about donors, email generation, or pipeline management. Try asking something like 'How do I generate an intro email?' or use `/donoremail help` for commands.")
                    return
                
                # Process natural language query
                response = self._process_natural_language_query(text, user_id, channel_id)
                say(response)
                
            except Exception as e:
                logger.error(f"Error handling app mention: {e}")
                say("Sorry, I encountered an error. Please try again or use the slash commands.")

        @self.app.event("message")
        def handle_direct_message(event, say):
            """Handle direct messages to the bot"""
            # Only respond to direct messages, not channel messages
            if event.get("channel_type") == "im":
                text = event.get("text", "")
                user_id = event.get("user")
                
                if text:
                    response = self._process_natural_language_query(text, user_id, None, is_dm=True)
                    if response:
                        say(response)
                    else:
                        say("I'm having trouble right now. Try using `/donoremail help` for specific commands.")
                else:
                    say("Hi! I can help with fundraising tasks. Use `/donoremail help` or `/pipeline` to get started.")
    
    def _process_natural_language_query(self, text: str, user_id: str, 
                                      channel_id: str = None, is_dm: bool = False) -> str:
        """Process natural language queries with context"""
        try:
            # Import context helpers (avoid circular imports)
            from context_helpers import get_relevant_donor_context, get_template_context, get_pipeline_insights
            
            # Check if it's a command-like request and gather relevant context
            donor_context = {}
            template_context = {}
            
            if any(keyword in text.lower() for keyword in ["email", "generate", "donor", "pipeline", "status", "search", "organization", "foundation", "trust"]):
                # Get relevant donor data based on the query
                donor_context = get_relevant_donor_context(text, self._get_sheets_db())
                template_context = get_template_context(self._get_email_generator())
                
                # Try to provide helpful guidance with real data
                response = self._handle_natural_language_query_with_context(text, user_id, channel_id, donor_context, template_context)
                return response
            
            # Try DeepSeek for broader conversations
            from deepseek_client import deepseek_client
            if deepseek_client and deepseek_client.initialized:
                # Get general context for broader conversations
                donor_context = get_relevant_donor_context(text, self._get_sheets_db())
                template_context = get_template_context(self._get_email_generator())
                pipeline_context = get_pipeline_insights(self._get_sheets_db())
                
                combined_context = {
                    **donor_context,
                    **template_context,
                    **pipeline_context
                }
                
                # Use DeepSeek with full context
                response = deepseek_client.chat_completion(text, context=combined_context, 
                                                         donor_data=donor_context, 
                                                         templates_info=template_context)
                if response:
                    return response
            
            # Fallback without DeepSeek
            return self._handle_natural_language_query(text, user_id, channel_id)
            
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return "I can help with fundraising tasks! Use `/donoremail help` to see email generation commands or `/pipeline` for donor management."
    
    def _handle_natural_language_query_with_context(self, text: str, user_id: str, 
                                                   channel_id: str, donor_context: dict, 
                                                   template_context: dict) -> str:
        """Process natural language queries with real donor and template data"""
        text_lower = text.lower()
        
        # If specific organizations are mentioned, provide detailed info
        if donor_context.get('mentioned_organizations'):
            orgs = donor_context['mentioned_organizations']
            org_info = []
            for org in orgs:
                org_info.append(f"• **{org['organization_name']}**: Stage - {org['current_stage']}, Sector - {org.get('sector_tags', 'N/A')}")
            
            if "status" in text_lower or "pipeline" in text_lower:
                return f"Here are the organizations I found:\n" + "\n".join(org_info) + f"\n\nFor detailed status, use: `/pipeline status [Organization Name]`"
            
            elif "email" in text_lower:
                templates = template_context.get('available_templates', {})
                template_list = "\n".join([f"• `{k}` - {v}" for k, v in templates.items()])
                
                return f"I found these organizations:\n" + "\n".join(org_info) + f"\n\n**Available email templates:**\n{template_list}\n\nTo generate an email, use: `/donoremail [template] [Organization Name]`"
        
        # Email generation with template context
        if "email" in text_lower and ("generate" in text_lower or "create" in text_lower):
            templates = template_context.get('available_templates', {})
            current_mode = template_context.get('current_mode', 'template')
            
            if templates:
                template_list = "\n".join([f"• `/donoremail {k} [Org]` - {desc}" 
                                         for k, desc in template_context.get('template_descriptions', {}).items()
                                         if k in templates])
                
                response = f"**Available email templates** (Mode: {current_mode}):\n{template_list}"
                
                # Add sector examples if available
                if donor_context.get('sector_examples'):
                    examples = donor_context['sector_examples'][:3]
                    example_list = "\n".join([f"• {ex['name']} ({ex['sector']})" for ex in examples])
                    response += f"\n\n**Example organizations in your pipeline:**\n{example_list}"
                
                return response + "\n\nExample: `/donoremail identification Wipro Foundation`"
        
        # Pipeline queries with real data
        elif "pipeline" in text_lower or "donor" in text_lower:
            from context_helpers import get_pipeline_insights
            pipeline_insights = get_pipeline_insights(self._get_sheets_db())
            
            if pipeline_insights:
                total_orgs = pipeline_insights.get('total_organizations', 0)
                active_prospects = pipeline_insights.get('active_prospects', [])
                
                response = f"**Current Pipeline Status:**\n• Total organizations: {total_orgs}"
                
                if active_prospects:
                    prospect_list = "\n".join([f"• {p['name']} - {p['stage']} ({p['sector']})" for p in active_prospects[:5]])
                    response += f"\n\n**Active prospects:**\n{prospect_list}"
                
                return response + "\n\nUse `/pipeline status [Org]` for detailed information."
        
        # Fallback with available data context
        available_data = []
        if donor_context.get('mentioned_organizations'):
            available_data.append(f"{len(donor_context['mentioned_organizations'])} organizations found")
        if template_context.get('available_templates'):
            available_data.append(f"{len(template_context['available_templates'])} email templates")
        
        if available_data:
            context_info = " and ".join(available_data)
            return f"I have access to {context_info} that might help. Try asking:\n• 'Generate an email for [organization]'\n• 'What's the status of [organization]?'\n• 'Show me pipeline information'\n\nOr use `/donoremail help` and `/pipeline` for specific commands."
        
        return self._handle_natural_language_query(text, user_id, channel_id)
    
    def _handle_natural_language_query(self, text: str, user_id: str, channel_id: str) -> str:
        """Process natural language queries and provide helpful responses"""
        text_lower = text.lower()
        
        # Email generation queries
        if "email" in text_lower and ("generate" in text_lower or "create" in text_lower or "write" in text_lower):
            if "intro" in text_lower or "introduction" in text_lower:
                return """To generate an introduction email, use:
`/donoremail intro [Organization Name]`

Example: `/donoremail intro Wipro Foundation`

This will create a personalized introduction email using our AI system and donor database."""
            
            elif "concept" in text_lower or "pitch" in text_lower:
                return """To generate a concept pitch email, use:
`/donoremail concept [Organization] [Project Name]`

Example: `/donoremail concept Tata Trust Digital Skills Training`

This creates a focused 2-3 paragraph concept presentation."""
            
            elif "meeting" in text_lower:
                return """To request a meeting, use:
`/donoremail meetingrequest [Organization] [Date]`

Example: `/donoremail meetingrequest HDFC Bank 2024-02-15`

This generates a professional meeting request email."""
            
            else:
                return """I can help generate various types of fundraising emails:

• `/donoremail intro [Org]` - Introduction emails
• `/donoremail concept [Org] [Project]` - Concept pitches  
• `/donoremail meetingrequest [Org] [Date]` - Meeting requests
• `/donoremail proposalcover [Org] [Project]` - Proposal covers
• `/donoremail help` - See all options"""
        
        # Pipeline/donor queries
        elif "pipeline" in text_lower or "status" in text_lower or "donor" in text_lower:
            if "search" in text_lower or "find" in text_lower:
                return """To search for organizations in your pipeline:
`/pipeline search [query]`

Example: `/pipeline search Wipro`

This searches across all donor records and shows matching organizations."""
            
            elif "status" in text_lower:
                return """To check an organization's status:
`/pipeline status [Organization Name]`

Example: `/pipeline status Tata Trust`

This shows current stage, assigned team member, next actions, and contact details."""
            
            else:
                return """I can help with pipeline management:

• `/pipeline status [Org]` - Check organization status
• `/pipeline search [query]` - Find organizations
• `/pipeline assign [Org] | [Member]` - Assign prospects
• `/pipeline stage [Org] | [Stage]` - Update stage
• `/pipeline` - See all commands"""
        
        # General help
        elif "help" in text_lower or "command" in text_lower:
            return """Here are the main commands I support:

**Email Generation:**
• `/donoremail help` - Full email command list
• `/donoremail intro [Org]` - Introduction emails
• `/donoremail concept [Org] [Project]` - Concept pitches

**Pipeline Management:**
• `/pipeline status [Org]` - Organization status
• `/pipeline search [query]` - Find organizations
• `/pipeline assign [Org] | [Member]` - Assign prospects

Ask me questions like:
• "How do I generate an intro email for Wipro?"
• "Show me pipeline commands"
• "What's the status of Tata Trust?"

I can also have natural conversations about fundraising strategy and donor management!"""
        
        else:
            # Use DeepSeek for complex queries if available
            from deepseek_client import deepseek_client
            if deepseek_client and deepseek_client.initialized:
                response = deepseek_client.chat_completion(text)
                if response:
                    return response
            
            return """I can help with fundraising emails and pipeline management. Try asking:

• "How do I generate an intro email?"
• "Show me pipeline commands"  
• "What email templates are available?"

Or use `/donoremail help` and `/pipeline` for specific commands."""
    
    def get_handler(self):
        """Get Flask request handler"""
        return self.handler
    
    def is_initialized(self):
        """Check if Slack bot is initialized"""
        return self.initialized
    
    def _get_sheets_db(self):
        """Get sheets database instance"""
        return self.sheets_db
    
    def _get_email_generator(self):
        """Get email generator instance"""
        return self.email_generator

# Global instance - will be initialized with dependencies from main app
slack_bot = None

def initialize_slack_bot(sheets_db=None, email_generator=None):
    """Initialize the global Slack bot instance with dependencies"""
    global slack_bot
    slack_bot = SlackBot(sheets_db=sheets_db, email_generator=email_generator)
    return slack_bot
