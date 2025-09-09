#!/usr/bin/env python3
"""
Refactored Slack Bot Integration for Diksha Foundation Fundraising Bot
Uses shared backend services for consistent functionality
"""

import os
import logging
import json
import re
import time
import hashlib
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Import shared backend
from backend import backend_manager

# Import dependencies
try:
    from slack_bolt import App as SlackApp
    from slack_bolt.adapter.flask import SlackRequestHandler
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    logger.warning("⚠️ slack-bolt not available - Slack integration disabled")

class SlackBot:
    """Slack bot with shared backend services"""
    
    def __init__(self, bot_token: str = None, signing_secret: str = None):
        """Initialize Slack bot with shared backend"""
        self.bot_token = bot_token or os.environ.get("SLACK_BOT_TOKEN")
        self.signing_secret = signing_secret or os.environ.get("SLACK_SIGNING_SECRET")
        self.app = None
        self.handler = None
        self.initialized = False
        
        # Get services from backend manager
        self.backend = backend_manager
        self.donor_service = self.backend.donor_service
        self.email_service = self.backend.email_service
        self.pipeline_service = self.backend.pipeline_service
        self.template_service = self.backend.template_service
        self.context_helpers = self.backend.context_helpers
        self.deepseek_client = self.backend.deepseek_client
        
        # Enhanced tracking and configuration
        self.pending_approvals = {}  # channel_id -> {thread_ts: approval_data}
        self.request_cache = {}  # Simple in-memory cache
        self.rate_limits = {}  # user_id -> {requests: [], window_start: timestamp}
        self.session_contexts = {}  # thread_ts -> conversation context
        
        # Configuration
        self.max_requests_per_minute = 10
        self.cache_ttl = 300  # 5 minutes
        self.max_context_length = 5  # Remember last 5 exchanges
        
        if SLACK_AVAILABLE and self.bot_token and self.signing_secret:
            try:
                self.app = SlackApp(
                    token=self.bot_token,
                    signing_secret=self.signing_secret,
                    process_before_response=True  # Enable async processing
                )
                self.handler = SlackRequestHandler(self.app)
                self.initialized = True
                self._setup_event_handlers()
                logger.info("✅ Slack bot initialized with shared backend")
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
                thread_ts = event.get("thread_ts") or event.get("ts")
                
                # Rate limiting check
                if not self._check_rate_limit(user_id):
                    say("You're sending requests too quickly. Please wait a moment before trying again.", 
                        thread_ts=thread_ts)
                    return
                
                # Remove bot mention from text
                bot_user_id = self.app.client.auth_test()["user_id"]
                text = text.replace(f"<@{bot_user_id}>", "").strip()
                
                # Update conversation context
                self._update_context(thread_ts, "user", text)
                
                if not text:
                    response = self._get_help_message()
                    say(response, thread_ts=thread_ts)
                    return
                
                # Process natural language query
                response = self._process_natural_language_query(text, user_id, channel_id, thread_ts)
                say(response, thread_ts=thread_ts)
                self._update_context(thread_ts, "assistant", response)
                
            except Exception as e:
                logger.error(f"Error handling app mention: {e}")
                say("Sorry, I encountered an error. Please try again or use the slash commands.")

        @self.app.event("message")
        def handle_message(event, say):
            """Handle all messages for approval workflow and follow-ups"""
            # Only respond to messages in threads where we have pending approvals
            thread_ts = event.get("thread_ts")
            if not thread_ts:
                return  # Only handle threaded messages
            
            text = event.get("text", "").lower().strip()
            user_id = event.get("user")
            channel_id = event.get("channel")
            
            # Skip bot messages
            if event.get("bot_id"):
                return
            
            # Handle approval workflow
            if self._has_pending_approval(channel_id, thread_ts):
                response = self._handle_approval_response(channel_id, thread_ts, user_id, text)
                if response:
                    say(response, thread_ts=thread_ts)
            
            # Update context for ongoing conversations
            self._update_context(thread_ts, "user", text)
    
    def _process_natural_language_query(self, text: str, user_id: str, 
                                      channel_id: str = None, thread_ts: str = None) -> str:
        """Process natural language queries with context using shared backend"""
        try:
            # Get conversation context if available
            context = self._get_context_for_processing(thread_ts) if thread_ts else ""
            
            # Check if it's a command-like request and gather relevant context
            if any(keyword in text.lower() for keyword in ["email", "generate", "donor", "pipeline", "status", "search", "organization", "foundation", "trust"]):
                # Get relevant context using shared backend
                donor_context = self.context_helpers.get_relevant_donor_context(text)
                template_context = self.context_helpers.get_template_context()
                
                # Try to provide helpful guidance with real data
                response = self._handle_natural_language_query_with_context(text, user_id, channel_id, donor_context, template_context)
                return response
            
            # Try DeepSeek for broader conversations
            if self.deepseek_client and self.deepseek_client.initialized:
                # Get general context for broader conversations
                donor_context = self.context_helpers.get_relevant_donor_context(text)
                template_context = self.context_helpers.get_template_context()
                pipeline_context = self.context_helpers.get_pipeline_insights()
                
                combined_context = {
                    **donor_context,
                    **template_context,
                    **pipeline_context
                }
                
                # Use DeepSeek with full context
                response = self.deepseek_client.chat_completion(text, context=combined_context, 
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
            pipeline_insights = self.context_helpers.get_pipeline_insights()
            
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
            if self.deepseek_client and self.deepseek_client.initialized:
                response = self.deepseek_client.chat_completion(text)
                if response:
                    return response
            
            return """I can help with fundraising emails and pipeline management. Try asking:

• "How do I generate an intro email?"
• "Show me pipeline commands"  
• "What email templates are available?"

Or use `/donoremail help` and `/pipeline` for specific commands."""
    
    def generate_and_send_email(self, template_type: str, org_name: str, user_id: str, channel_id: str, email_purpose: str):
        """Generate and send email using the shared backend email service"""
        try:
            # Convert org_name to donor_id format
            donor_id = org_name.replace(" ", "_").lower()
            
            # Use shared backend email service
            result = self.email_service.generate_email(template_type, donor_id, mode="claude")
            
            if not result.get("success"):
                return {
                    "response_type": "ephemeral",
                    "text": f"❌ {result.get('error', 'Email generation failed')}"
                }
            
            draft = result["data"]
            
            # Format the response
            response_text = f"""📧 **{email_purpose} Generated Successfully!**

🎯 **Organization:** {org_name}
📋 **Template:** {template_type}
🤖 **Enhanced with:** Claude AI + Google Drive Profile

📝 **Subject:** {draft['subject']}

📄 **Email Body:**
{draft['content']}

---
💡 **Next Steps:**
• Review and customize the email
• Use `/donoremail refine [tone]` to adjust tone
• Use `/donoremail save [name]` to save draft
• Use `/donoremail share [@colleague]` to get feedback"""
            
            return {
                "response_type": "in_channel",
                "text": response_text
            }
            
        except Exception as e:
            logger.error(f"Error generating email: {e}")
            return {
                "response_type": "ephemeral",
                "text": f"❌ Error generating email: {str(e)}\n\nPlease try again or contact support."
            }
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Enhanced rate limiting with sliding window"""
        now = time.time()
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = {"requests": [], "window_start": now}
        
        user_limits = self.rate_limits[user_id]
        
        # Clean old requests (sliding window)
        user_limits["requests"] = [req_time for req_time in user_limits["requests"] 
                                 if now - req_time < 60]  # 1-minute window
        
        # Check limit
        if len(user_limits["requests"]) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        user_limits["requests"].append(now)
        return True
    
    def _update_context(self, thread_ts: str, role: str, content: str):
        """Update conversation context for better continuity"""
        if thread_ts not in self.session_contexts:
            self.session_contexts[thread_ts] = []
        
        context = self.session_contexts[thread_ts]
        context.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
        
        # Keep only recent context
        if len(context) > self.max_context_length * 2:  # *2 for user+assistant pairs
            context = context[-self.max_context_length * 2:]
            self.session_contexts[thread_ts] = context
    
    def _get_context_for_processing(self, thread_ts: str) -> str:
        """Get conversation context for enhanced processing"""
        if thread_ts not in self.session_contexts:
            return ""
        
        context_parts = []
        for exchange in self.session_contexts[thread_ts][-4:]:  # Last 2 exchanges
            role = exchange["role"]
            content = exchange["content"][:100]  # Truncate for brevity
            context_parts.append(f"{role}: {content}")
        
        return "; ".join(context_parts) if context_parts else ""
    
    def _has_pending_approval(self, channel_id: str, thread_ts: str) -> bool:
        """Check if there's a pending approval in this thread"""
        return (channel_id in self.pending_approvals and 
                thread_ts in self.pending_approvals[channel_id])
    
    def _handle_approval_response(self, channel_id: str, thread_ts: str, user_id: str, text: str) -> Optional[str]:
        """Handle user approval responses"""
        try:
            if text in ["approve", "yes", "send", "ok"]:
                response = self._process_approval(channel_id, thread_ts, user_id)
                # Clean up pending approval
                if channel_id in self.pending_approvals and thread_ts in self.pending_approvals[channel_id]:
                    del self.pending_approvals[channel_id][thread_ts]
                return response
            
            elif text.startswith("edit ") or text.startswith("change "):
                changes = text.replace("edit ", "").replace("change ", "")
                return self._handle_edit_request(channel_id, thread_ts, user_id, changes)
            
            elif text in ["cancel", "no", "stop"]:
                # Clean up pending approval
                if channel_id in self.pending_approvals and thread_ts in self.pending_approvals[channel_id]:
                    del self.pending_approvals[channel_id][thread_ts]
                return "Email generation cancelled. No changes were made to the pipeline."
            
            elif text.startswith("help") or text.startswith("?"):
                return """**Approval Options:**
• `approve` - Send email and update pipeline
• `edit [changes]` - Modify the email (e.g., \"edit make it warmer\")
• `cancel` - Don't send anything

**Examples:**
• `edit make it more formal`
• `edit add mention of rural development`
• `edit shorter and more direct`"""
            
            return None
            
        except Exception as e:
            logger.error(f"Error handling approval response: {e}")
            return "I encountered an error while processing your approval. Please try again."
    
    def _process_approval(self, channel_id: str, thread_ts: str, user_id: str) -> str:
        """Process approved email and update pipeline"""
        try:
            approval_data = self.pending_approvals[channel_id][thread_ts]
            org_name = approval_data["org_data"]["organization_name"]
            email_type = approval_data["nlu_result"]["email_variant"]
            
            # Determine new stage based on email type
            stage_mapping = {
                "intro": "Intro Sent",
                "followup": "Follow-up Sent", 
                "proposal_cover": "Proposal Sent",
                "thankyou": "Thank You Sent"
            }
            new_stage = stage_mapping.get(email_type, "Communication Sent")
            
            # Update pipeline using shared backend
            donor_id = org_name.replace(" ", "_").lower()
            success = self.donor_service.update_donor_stage(donor_id, new_stage)
            
            if success:
                return f"""✅ **Email approved and pipeline updated!**

**Organization:** {org_name}
**New Stage:** {new_stage}
**Email Type:** {email_type}

**Next Actions:**
• Email draft is ready for your review
• Pipeline has been updated
• Next follow-up scheduled for TBD

**Thread Link:** N/A"""
            else:
                return f"""⚠️ **Pipeline update failed**

**Organization:** {org_name}
**Error:** Failed to update pipeline

The email was approved but I couldn't update the pipeline. Please update it manually or contact support."""
            
        except Exception as e:
            logger.error(f"Error processing approval: {e}")
            return "I encountered an error while updating the pipeline. The email was approved but the pipeline update failed. Please contact support."
    
    def _handle_edit_request(self, channel_id: str, thread_ts: str, user_id: str, changes: str) -> str:
        """Handle edit requests for email content"""
        try:
            if not changes:
                return "Please specify what changes you'd like me to make. For example:\n• \"edit make it warmer\"\n• \"edit shorter and more direct\"\n• \"edit add mention of rural development\""
            
            # For now, return a simple response
            # In a full implementation, you'd regenerate the email with the changes
            return f"""I understand you want to make these changes: "{changes}"

**Note:** Email regeneration with changes is not yet implemented in this version.

**Current options:**
• `approve` - Use the current email as-is
• `cancel` - Don't send anything
• Contact support for custom modifications"""
            
        except Exception as e:
            logger.error(f"Error handling edit request: {e}")
            return "I encountered an error while processing your edit request. Please try again."
    
    def _get_help_message(self) -> str:
        """Get comprehensive help message"""
        return """Hi! I'm your Diksha Foundation fundraising assistant. I can help you:

**📧 Email Generation:**
• "intro email to HDFC about KHEL program"
• "followup with Tata Trust regarding digital skills"
• "thank you email to Wipro Foundation"

**📊 Status & Pipeline:**
• "what's our status with Infosys Foundation?"
• "when did we last contact HDFC?"
• "show me pipeline information"

**📁 Asset Management:**
• "show me Tata Trust assets"
• "find documents for Wipro Foundation"
• "locate proposal files"

**💡 Tips:**
• Be specific about organization names
• Mention programs or focus areas
• Specify tone preferences (warm, formal, urgent)

**Need help?** Just ask "help" or "what can you do?" """
    
    def get_handler(self):
        """Get Flask request handler"""
        return self.handler
    
    def is_initialized(self):
        """Check if Slack bot is initialized"""
        return self.initialized

# Global instance - will be initialized with shared backend
slack_bot = None

def initialize_slack_bot():
    """Initialize the global Slack bot instance with shared backend"""
    global slack_bot
    slack_bot = SlackBot()
    return slack_bot
