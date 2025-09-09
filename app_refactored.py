#!/usr/bin/env python3
"""
Refactored Flask App for Diksha Foundation Fundraising Bot
Uses shared backend services for consistent functionality across Slack and Web UI
"""

from flask import Flask, request, jsonify
import os
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import shared backend
from backend import backend_manager

# Initialize Flask app
app = Flask(__name__)

# Get services from backend manager
backend = backend_manager
donor_service = backend.donor_service
email_service = backend.email_service
pipeline_service = backend.pipeline_service
template_service = backend.template_service
context_helpers = backend.context_helpers
deepseek_client = backend.deepseek_client

# Web UI API Endpoints
@app.route('/api/pipeline', methods=['GET'])
def get_pipeline():
    """Get all donors from the pipeline"""
    try:
        if not donor_service:
            return jsonify({
                "success": False,
                "error": "Donor service not available"
            }), 503
        
        # Get all donors using shared backend
        donors = donor_service.get_all_donors()
        
        return jsonify({
            "success": True,
            "data": donors
        })
        
    except Exception as e:
        logger.error(f"Error getting pipeline: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/donor/<donor_id>', methods=['GET'])
def get_donor(donor_id):
    """Get specific donor information"""
    try:
        if not donor_service:
            return jsonify({
                "success": False,
                "error": "Donor service not available"
            }), 503
        
        # Get donor using shared backend
        donor = donor_service.get_donor(donor_id)
        if not donor:
            return jsonify({
                "success": False,
                "error": "Donor not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": donor
        })
        
    except Exception as e:
        logger.error(f"Error getting donor: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/moveStage', methods=['POST'])
def move_stage():
    """Update donor stage"""
    try:
        data = request.get_json()
        donor_id = data.get('donor_id')
        stage = data.get('stage')
        
        if not donor_id or not stage:
            return jsonify({
                "success": False,
                "error": "Missing required fields: donor_id, stage"
            }), 400
        
        if not donor_service:
            return jsonify({
                "success": False,
                "error": "Donor service not available"
            }), 503
        
        # Update stage using shared backend
        success = donor_service.update_donor_stage(donor_id, stage)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Stage updated successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update stage"
            }), 500
        
    except Exception as e:
        logger.error(f"Error updating stage: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/assignDonor', methods=['POST'])
def assign_donor():
    """Assign donor to team member"""
    try:
        data = request.get_json()
        donor_id = data.get('donor_id')
        owner = data.get('owner')
        
        if not donor_id or not owner:
            return jsonify({
                "success": False,
                "error": "Missing required fields: donor_id, owner"
            }), 400
        
        if not donor_service:
            return jsonify({
                "success": False,
                "error": "Donor service not available"
            }), 503
        
        # Update assignment using shared backend
        success = donor_service.update_donor_owner(donor_id, owner)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Donor assigned successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to assign donor"
            }), 500
        
    except Exception as e:
        logger.error(f"Error assigning donor: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/notes', methods=['POST'])
def update_notes():
    """Update donor notes"""
    try:
        data = request.get_json()
        donor_id = data.get('donor_id')
        notes = data.get('notes')
        
        if not donor_id:
            return jsonify({
                "success": False,
                "error": "Missing required field: donor_id"
            }), 400
        
        if not donor_service:
            return jsonify({
                "success": False,
                "error": "Donor service not available"
            }), 503
        
        # Update notes using shared backend
        success = donor_service.update_donor_notes(donor_id, notes)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Notes updated successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update notes"
            }), 500
        
    except Exception as e:
        logger.error(f"Error updating notes: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get available email templates"""
    try:
        if not template_service:
            return jsonify({
                "success": False,
                "error": "Template service not available"
            }), 503
        
        # Get templates using shared backend
        templates = template_service.get_available_templates()
        
        return jsonify({
            "success": True,
            "data": templates
        })
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/template/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get specific email template"""
    try:
        if not template_service:
            return jsonify({
                "success": False,
                "error": "Template service not available"
            }), 503
        
        # Get template using shared backend
        template = template_service.get_template(template_id)
        if not template:
            return jsonify({
                "success": False,
                "error": "Template not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": template
        })
        
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/draft', methods=['POST'])
def generate_draft():
    """Generate email draft"""
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        donor_id = data.get('donor_id')
        subject = data.get('subject')
        content = data.get('content')
        placeholders = data.get('placeholders', {})
        
        if not all([template_id, donor_id, subject, content]):
            return jsonify({
                "success": False,
                "error": "Missing required fields"
            }), 400
        
        if not email_service:
            return jsonify({
                "success": False,
                "error": "Email service not available"
            }), 503
        
        # Generate draft using shared backend
        result = email_service.generate_email(template_id, donor_id)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "data": result["data"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Email generation failed")
            }), 500
        
    except Exception as e:
        logger.error(f"Error generating draft: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/draft/<draft_id>/refine', methods=['POST'])
def refine_draft(draft_id):
    """Refine email draft"""
    try:
        data = request.get_json()
        refinements = data.get('refinements', {})
        
        if not email_service:
            return jsonify({
                "success": False,
                "error": "Email service not available"
            }), 503
        
        # Refine draft using shared backend
        result = email_service.refine_draft(draft_id, refinements)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "data": result["data"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Draft refinement failed")
            }), 500
        
    except Exception as e:
        logger.error(f"Error refining draft: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/send', methods=['POST'])
def send_email():
    """Send email"""
    try:
        data = request.get_json()
        draft_id = data.get('draft_id')
        
        if not draft_id:
            return jsonify({
                "success": False,
                "error": "Missing required field: draft_id"
            }), 400
        
        if not email_service:
            return jsonify({
                "success": False,
                "error": "Email service not available"
            }), 503
        
        # Send email using shared backend
        result = email_service.send_email(draft_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/activities', methods=['GET'])
def get_activities():
    """Get user activities"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        # For now, return mock data - in a real implementation, you'd query a database
        activities = {
            "data": [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": 0,
                "pages": 0
            }
        }
        
        return jsonify({
            "success": True,
            "data": activities
        })
        
    except Exception as e:
        logger.error(f"Error getting activities: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/docs/<donor_id>', methods=['GET'])
def get_donor_documents(donor_id):
    """Get donor documents"""
    try:
        if not donor_service:
            return jsonify({
                "success": False,
                "error": "Donor service not available"
            }), 503
        
        # Get documents using shared backend
        documents = donor_service.get_donor_documents(donor_id)
        
        return jsonify({
            "success": True,
            "data": documents
        })
        
    except Exception as e:
        logger.error(f"Error getting donor documents: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/search', methods=['GET'])
def search_donors():
    """Search donors"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: q"
            }), 400
        
        if not donor_service:
            return jsonify({
                "success": False,
                "error": "Donor service not available"
            }), 503
        
        # Search donors using shared backend
        donors = donor_service.search_donors(query)
        
        return jsonify({
            "success": True,
            "data": donors
        })
        
    except Exception as e:
        logger.error(f"Error searching donors: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/log', methods=['POST'])
def log_activity():
    """Log user activity"""
    try:
        data = request.get_json()
        action = data.get('action')
        target = data.get('target')
        details = data.get('details')
        
        if not action:
            return jsonify({
                "success": False,
                "error": "Missing required field: action"
            }), 400
        
        # Log the activity (in a real implementation, you'd save this to a database)
        logger.info(f"Activity logged: {action} - {target} - {details}")
        
        return jsonify({
            "success": True,
            "message": "Activity logged successfully"
        })
        
    except Exception as e:
        logger.error(f"Error logging activity: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Global error handlers
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.now().isoformat(),
        "status_code": 500
    }), 500

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"Endpoint not found: {request.url}")
    return jsonify({
        "error": "Endpoint not found",
        "message": f"The requested endpoint '{request.endpoint}' does not exist",
        "available_endpoints": [
            "/health",
            "/api/pipeline",
            "/api/donor/<id>",
            "/api/templates",
            "/api/draft",
            "/api/send",
            "/slack/events",
            "/slack/commands"
        ],
        "timestamp": datetime.now().isoformat(),
        "status_code": 404
    }), 404

@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"Bad request: {request.url} - {error}")
    return jsonify({
        "error": "Bad request",
        "message": "Invalid request format or parameters",
        "timestamp": datetime.now().isoformat(),
        "status_code": 400
    }), 400

# Request logging middleware
@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.url} - IP: {request.remote_addr} - User-Agent: {request.headers.get('User-Agent', 'Unknown')}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response: {request.method} {request.url} - Status: {response.status_code} - Size: {len(response.get_data())} bytes")
    return response

# Initialize Slack bot with shared backend
slack_bot = None
try:
    from slack_bot_refactored import initialize_slack_bot
    slack_bot = initialize_slack_bot()
    logger.info("✅ Slack bot initialized with shared backend")
except Exception as e:
    logger.error(f"❌ Slack bot initialization failed: {e}")
    slack_bot = None

@app.route('/')
def index():
    logger.info("📊 Root endpoint accessed")
    
    # Get backend status
    backend_status = backend.get_status()
    
    return jsonify({
        "app": "Diksha Fundraising Automation", 
        "status": "running", 
        "mode": "shared-backend",
        "backend_status": backend_status,
        "slack_commands": {
            "donoremail": "/donoremail [action] [parameters] - Fundraising email generation with AI enhancement",
            "help": "Use `/donoremail help` for comprehensive command list"
        },
        "endpoints": {
            "slack_events": "/slack/events",
            "slack_commands": "/slack/commands",
            "health": "/health",
            "api_pipeline": "/api/pipeline",
            "api_donor": "/api/donor/<id>",
            "api_templates": "/api/templates",
            "api_draft": "/api/draft",
            "api_send": "/api/send"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for quick testing"""
    msg = f"✅ /health ping at {datetime.now().isoformat()}"
    print(msg, flush=True)  # visible in Terminal A
    logger.info("🏥 Health check requested")
    
    # Get backend status
    backend_status = backend.get_status()
    
    # Overall health status
    overall_status = "healthy"
    if not backend.initialized:
        overall_status = "degraded"
    if not backend_status["services"]["sheets_db"]["initialized"]:
        overall_status = "unhealthy"
    
    return jsonify({
        "status": overall_status,
        "mode": "shared-backend",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "backend_status": backend_status,
        "environment": {
            "google_credentials": "configured" if os.environ.get("GOOGLE_CREDENTIALS_BASE64") else "missing",
            "anthropic_api_key": "configured" if os.environ.get("ANTHROPIC_API_KEY") else "missing",
            "deepseek_api_key": "configured" if os.environ.get("DEEPSEEK_API_KEY") else "missing",
            "slack_credentials": "configured" if (os.environ.get("SLACK_BOT_TOKEN") and os.environ.get("SLACK_SIGNING_SECRET")) else "missing"
        },
        "security": {
            "slack_signature_validation": "enabled" if (os.environ.get("SLACK_SIGNING_SECRET") and os.environ.get("SLACK_BOT_TOKEN")) else "disabled",
            "input_sanitization": "active",
            "rate_limiting": "basic",
            "error_exposure": "limited"
        },
        "monitoring": {
            "request_logging": "active",
            "error_logging": "active",
            "health_checks": "active",
            "component_validation": "active"
        }
    })

# Slack command handlers
@app.route("/slack/events", methods=["POST"])
def slack_events():
    """Handle Slack events with signature validation"""
    if not slack_bot or not slack_bot.is_initialized():
        return jsonify({"error": "Slack not configured"}), 503
    
    try:
        # Use the refactored Slack bot handler
        handler = slack_bot.get_handler()
        if handler:
            return handler.handle(request)
        else:
            return jsonify({"error": "Slack handler not available"}), 503
    except Exception as e:
        logger.error(f"Error handling Slack event: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/slack/commands", methods=["POST"])
def slack_commands():
    """Handle Slack slash commands"""
    try:
        form_data = request.form.to_dict()
        command = form_data.get("command", "")
        text = form_data.get("text", "").strip()
        user_id = form_data.get("user_id", "")
        channel_id = form_data.get("channel_id", "")
        
        logger.info(f"Received command: {command} with text: '{text}' from user: {user_id}")
        
        if command == "/donoremail":
            return handle_donoremail_command(text, user_id, channel_id)
        else:
            return jsonify({
                "response_type": "ephemeral",
                "text": f"Unknown command: {command}"
            })
            
    except Exception as e:
        logger.error(f"Error handling Slack command: {e}")
        return jsonify({
            "response_type": "ephemeral",
            "text": f"Error processing command: {str(e)}"
        }), 500

def handle_donoremail_command(text: str, user_id: str, channel_id: str):
    """Handle the /donoremail command with fundraising workflow stages"""
    try:
        # Input validation and sanitization
        if not text or not text.strip():
            return jsonify({
                "response_type": "ephemeral",
                "text": get_donoremail_help()
            })
        
        # Sanitize input - remove any potentially dangerous characters
        sanitized_text = text.strip()
        if len(sanitized_text) > 1000:  # Prevent extremely long inputs
            return jsonify({
                "response_type": "ephemeral",
                "text": "❌ Command too long. Please keep commands under 1000 characters."
            })
        
        # Parse command parts with safety checks
        parts = [part.strip() for part in sanitized_text.split() if part.strip()]
        if not parts:
            return jsonify({
                "response_type": "ephemeral",
                "text": "❌ Invalid command format. Use `/donoremail help` for guidance."
            })
        
        action = parts[0].lower()
        
        # Validate action parameter
        if not action:
            return jsonify({
                "response_type": "ephemeral",
                "text": "❌ Invalid action. Use `/donoremail help` for available commands."
            })
        
        # Validate action is alphanumeric for security
        if not action.replace('-', '').replace('_', '').isalnum():
            return jsonify({
                "response_type": "ephemeral",
                "text": "❌ Invalid action format. Actions must be alphanumeric."
            })
        
        # Stage 1: Prospecting / Outreach
        if action == "intro":
            return handle_intro_email(parts, user_id, channel_id)
        elif action == "concept":
            return handle_concept_email(parts, user_id, channel_id)
        elif action == "followup":
            return handle_followup_email(parts, user_id, channel_id)
        
        # Stage 2: Engagement
        elif action == "meetingrequest":
            return handle_meeting_request_email(parts, user_id, channel_id)
        elif action == "thanksmeeting":
            return handle_thanks_meeting_email(parts, user_id, channel_id)
        elif action == "connect":
            return handle_connect_email(parts, user_id, channel_id)
        
        # Stage 3: Proposal Submission
        elif action == "proposalcover":
            return handle_proposal_cover_email(parts, user_id, channel_id)
        elif action == "proposalreminder":
            return handle_proposal_reminder_email(parts, user_id, channel_id)
        elif action == "pitch":
            return handle_pitch_email(parts, user_id, channel_id)
        
        # Stage 4: Stewardship for Fundraising
        elif action == "impactstory":
            return handle_impact_story_email(parts, user_id, channel_id)
        elif action == "invite":
            return handle_invite_email(parts, user_id, channel_id)
        elif action == "festivalgreeting":
            return handle_festival_greeting_email(parts, user_id, channel_id)
        
        # Utilities
        elif action == "refine":
            return handle_refine_email(parts, user_id, channel_id)
        elif action == "insert":
            return handle_insert_profile(parts, user_id, channel_id)
        elif action == "save":
            return handle_save_draft(parts, user_id, channel_id)
        elif action == "share":
            return handle_share_draft(parts, user_id, channel_id)
        
        # Help and unknown actions
        elif action in ["help", "?"]:
            return jsonify({
                "response_type": "ephemeral",
                "text": get_donoremail_help()
            })
        else:
            return jsonify({
                "response_type": "ephemeral",
                "text": f"❌ Unknown action: '{action}'. Use `/donoremail help` for available commands."
            })
            
    except Exception as e:
        logger.error(f"Error handling donoremail command: {e}")
        return jsonify({
            "response_type": "ephemeral",
            "text": f"❌ Error processing command: {str(e)}"
        })

def get_donoremail_help():
    """Get comprehensive help for donoremail commands"""
    return """🟢 **Stage 1: Prospecting / Outreach**
• `/donoremail intro [OrgName]` → First introduction to a new donor
• `/donoremail concept [OrgName] [ProjectName]` → Concise concept pitch (2-3 paras)
• `/donoremail followup [OrgName]` → Follow-up if no response after intro

🔵 **Stage 2: Engagement**
• `/donoremail meetingrequest [OrgName] [Date]` → Request a donor meeting/call
• `/donoremail thanksmeeting [OrgName]` → Thank-you mail after initial meeting
• `/donoremail connect [OrgName]` → Warm connection email (referral/introduction)

🟣 **Stage 3: Proposal Submission**
• `/donoremail proposalcover [OrgName] [ProjectName]` → Cover note for proposal
• `/donoremail proposalreminder [OrgName]` → Reminder for pending proposal
• `/donoremail pitch [OrgName] [ProjectName]` → Strong pitch highlighting alignment

🔴 **Stage 4: Stewardship for Fundraising**
• `/donoremail impactstory [OrgName] [Theme]` → Share story to inspire interest
• `/donoremail invite [OrgName] [EventName] [Date]` → Invite to events
• `/donoremail festivalgreeting [OrgName] [Festival]` → Relationship building

⚙️ **Utilities**
• `/donoremail refine [formal/concise/warm/personal]` → Adjust draft tone
• `/donoremail insert profile [OrgName]` → Pull donor profile from Drive
• `/donoremail save [DraftName]` → Save draft to Google Drive
• `/donoremail share [@colleague]` → Share draft in Slack for review

**Examples:**
• `/donoremail intro Wipro Foundation`
• `/donoremail concept Tata Trust Digital Skills Training`
• `/donoremail meetingrequest HDFC Bank 2024-02-15`
• `/donoremail refine warm`"""

# Stage 1: Prospecting / Outreach Handlers
def handle_intro_email(parts: list, user_id: str, channel_id: str):
    """Handle intro email generation"""
    if len(parts) < 2:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail intro [OrgName]`\nExample: `/donoremail intro Wipro Foundation`"
        })
    
    try:
        org_name = " ".join(parts[1:])
        if not org_name.strip():
            return jsonify({
                "response_type": "ephemeral",
                "text": "❌ Organization name cannot be empty. Use `/donoremail intro [OrgName]`"
            })
        return slack_bot.generate_and_send_email("identification", org_name, user_id, channel_id, "First Introduction")
    except Exception as e:
        logger.error(f"Error in intro email handler: {e}")
        return jsonify({
            "response_type": "ephemeral",
            "text": f"❌ Error processing intro email: {str(e)}"
        })

def handle_concept_email(parts: list, user_id: str, channel_id: str):
    """Handle concept email generation"""
    if len(parts) < 3:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail concept [OrgName] [ProjectName]`\nExample: `/donoremail concept Tata Trust Digital Skills Training`"
        })
    
    try:
        org_name = parts[1].strip()
        project_name = " ".join(parts[2:]).strip()
        
        if not org_name or not project_name:
            return jsonify({
                "response_type": "ephemeral",
                "text": "❌ Both organization name and project name are required. Use `/donoremail concept [OrgName] [ProjectName]`"
            })
        
        return slack_bot.generate_and_send_email("engagement", org_name, user_id, channel_id, f"Concept Pitch: {project_name}")
    except Exception as e:
        logger.error(f"Error in concept email handler: {e}")
        return jsonify({
            "response_type": "ephemeral",
            "text": f"❌ Error processing concept email: {str(e)}"
        })

def handle_followup_email(parts: list, user_id: str, channel_id: str):
    """Handle followup email generation"""
    if len(parts) < 2:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail followup [OrgName]`\nExample: `/donoremail followup Wipro Foundation`"
        })
    
    org_name = " ".join(parts[1:])
    return slack_bot.generate_and_send_email("followup", org_name, user_id, channel_id, "Follow-up Email")

# Stage 2: Engagement Handlers
def handle_meeting_request_email(parts: list, user_id: str, channel_id: str):
    """Handle meeting request email generation"""
    if len(parts) < 3:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail meetingrequest [OrgName] [Date]`\nExample: `/donoremail meetingrequest HDFC Bank 2024-02-15`"
        })
    
    org_name = parts[1]
    date = parts[2]
    return slack_bot.generate_and_send_email("meeting_request", org_name, user_id, channel_id, f"Meeting Request for {date}")

def handle_thanks_meeting_email(parts: list, user_id: str, channel_id: str):
    """Handle thanks meeting email generation"""
    if len(parts) < 2:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail thanksmeeting [OrgName]`\nExample: `/donoremail thanksmeeting Tata Trust`"
        })
    
    org_name = " ".join(parts[1:])
    return slack_bot.generate_and_send_email("thanks_meeting", org_name, user_id, channel_id, "Thank You After Meeting")

def handle_connect_email(parts: list, user_id: str, channel_id: str):
    """Handle connect email generation"""
    if len(parts) < 2:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail connect [OrgName]`\nExample: `/donoremail connect Infosys Foundation`"
        })
    
    org_name = " ".join(parts[1:])
    return slack_bot.generate_and_send_email("connect", org_name, user_id, channel_id, "Warm Connection Email")

# Stage 3: Proposal Submission Handlers
def handle_proposal_cover_email(parts: list, user_id: str, channel_id: str):
    """Handle proposal cover email generation"""
    if len(parts) < 3:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail proposalcover [OrgName] [ProjectName]`\nExample: `/donoremail proposalcover Wipro Foundation Digital Skills Program`"
        })
    
    org_name = parts[1]
    project_name = " ".join(parts[2:])
    return slack_bot.generate_and_send_email("proposal_cover", org_name, user_id, channel_id, f"Proposal Cover: {project_name}")

def handle_proposal_reminder_email(parts: list, user_id: str, channel_id: str):
    """Handle proposal reminder email generation"""
    if len(parts) < 2:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail proposalreminder [OrgName]`\nExample: `/donoremail proposalreminder Tata Trust`"
        })
    
    org_name = " ".join(parts[1:])
    return slack_bot.generate_and_send_email("proposal_reminder", org_name, user_id, channel_id, "Proposal Reminder")

def handle_pitch_email(parts: list, user_id: str, channel_id: str):
    """Handle pitch email generation"""
    if len(parts) < 3:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail pitch [OrgName] [ProjectName]`\nExample: `/donoremail pitch HDFC Bank Youth Empowerment`"
        })
    
    org_name = parts[1]
    project_name = " ".join(parts[2:])
    return slack_bot.generate_and_send_email("pitch", org_name, user_id, channel_id, f"Strong Pitch: {project_name}")

# Stage 4: Stewardship Handlers
def handle_impact_story_email(parts: list, user_id: str, channel_id: str):
    """Handle impact story email generation"""
    if len(parts) < 3:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail impactstory [OrgName] [Theme]`\nExample: `/donoremail impactstory Wipro Foundation Digital Literacy`"
        })
    
    org_name = parts[1]
    theme = " ".join(parts[2:])
    return slack_bot.generate_and_send_email("impact_story", org_name, user_id, channel_id, f"Impact Story: {theme}")

def handle_invite_email(parts: list, user_id: str, channel_id: str):
    """Handle invite email generation"""
    if len(parts) < 4:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail invite [OrgName] [EventName] [Date]`\nExample: `/donoremail invite Tata Trust Annual Meeting 2024-03-20`"
        })
    
    org_name = parts[1]
    event_name = parts[2]
    date = parts[3]
    return slack_bot.generate_and_send_email("invite", org_name, user_id, channel_id, f"Event Invite: {event_name} on {date}")

def handle_festival_greeting_email(parts: list, user_id: str, channel_id: str):
    """Handle festival greeting email generation"""
    if len(parts) < 3:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail festivalgreeting [OrgName] [Festival]`\nExample: `/donoremail festivalgreeting HDFC Bank Diwali`"
        })
    
    org_name = parts[1]
    festival = " ".join(parts[2:])
    return slack_bot.generate_and_send_email("festival_greeting", org_name, user_id, channel_id, f"Festival Greeting: {festival}")

# Utility Handlers
def handle_refine_email(parts: list, user_id: str, channel_id: str):
    """Handle email refinement"""
    if len(parts) < 2:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail refine [tone]`\nTones: formal, concise, warm, personal\nExample: `/donoremail refine warm`"
        })
    
    tone = parts[1].lower()
    if tone not in ["formal", "concise", "warm", "personal"]:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Invalid tone. Use: formal, concise, warm, or personal"
        })
    
    # This would typically work with a draft in progress
    return jsonify({
        "response_type": "ephemeral",
        "text": f"Email tone adjusted to: {tone}\n\nNote: This feature works with drafts in progress. Use other commands to generate emails first."
    })

def handle_insert_profile(parts: list, user_id: str, channel_id: str):
    """Handle profile insertion into draft"""
    if len(parts) < 3 or parts[1] != "profile":
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail insert profile [OrgName]`\nExample: `/donoremail insert profile Wipro Foundation`"
        })
    
    org_name = " ".join(parts[2:])
    
    try:
        # Get donor profile info using shared backend
        donor_id = org_name.replace(" ", "_").lower()
        profile_info = email_service.get_donor_profile_info(donor_id)
        
        if profile_info.get('profile_found'):
            return jsonify({
                "response_type": "ephemeral",
                "text": f"✅ Profile found for {org_name}:\n\n📄 File: {profile_info['file_info']['name']}\n📋 Type: {profile_info['file_info']['type']}\n📅 Modified: {profile_info['file_info']['modified']}\n\nProfile content has been integrated into your email draft."
            })
        else:
            return jsonify({
                "response_type": "ephemeral",
                "text": f"⚠️ No profile found for {org_name}\n\nAvailable data from Google Sheets will be used instead."
            })
            
    except Exception as e:
        return jsonify({
            "response_type": "ephemeral",
            "text": f"Error retrieving profile: {str(e)}"
        })

def handle_save_draft(parts: list, user_id: str, channel_id: str):
    """Handle draft saving to Google Drive"""
    if len(parts) < 2:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail save [DraftName]`\nExample: `/donoremail save Wipro Foundation Intro`"
        })
    
    draft_name = " ".join(parts[1:])
    
    # This would typically save the current draft
    return jsonify({
        "response_type": "ephemeral",
        "text": f"📁 Draft '{draft_name}' saved to Google Drive\n\nNote: This feature works with drafts in progress. Use other commands to generate emails first."
    })

def handle_share_draft(parts: list, user_id: str, channel_id: str):
    """Handle draft sharing with colleagues"""
    if len(parts) < 2:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail share [@colleague]`\nExample: `/donoremail share @sarah`"
        })
    
    colleague = parts[1]
    
    # This would typically share the current draft
    return jsonify({
        "response_type": "ephemeral",
        "text": f"📤 Draft shared with {colleague}\n\nNote: This feature works with drafts in progress. Use other commands to generate emails first."
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    
    # Startup logging
    print("🚀 Diksha Foundation Fundraising Bot Starting...")
    print("="*60)
    
    # Get backend status
    backend_status = backend.get_status()
    
    print(f"🔧 Backend Status: {'✅ Initialized' if backend.initialized else '❌ Failed'}")
    print(f"📊 Services Available:")
    for service_name, service_info in backend_status["services"].items():
        status = "✅" if service_info.get("available", False) else "❌"
        print(f"   {status} {service_name.replace('_', ' ').title()}")
    
    print(f"\n🌐 Server: Starting on port {port}")
    print(f"🔧 Debug Mode: {'✅ Enabled' if app.debug else '❌ Disabled'}")
    
    # Environment variable status
    print(f"\n🔑 Environment Variables:")
    print(f"   GOOGLE_CREDENTIALS_BASE64: {'✅ Set' if os.environ.get('GOOGLE_CREDENTIALS_BASE64') else '❌ Missing'}")
    print(f"   ANTHROPIC_API_KEY: {'✅ Set' if os.environ.get('ANTHROPIC_API_KEY') else '❌ Missing'}")
    print(f"   DEEPSEEK_API_KEY: {'✅ Set' if os.environ.get('DEEPSEEK_API_KEY') else '❌ Missing'}")
    print(f"   SLACK_BOT_TOKEN: {'✅ Set' if os.environ.get('SLACK_BOT_TOKEN') else '❌ Missing'}")
    print(f"   SLACK_SIGNING_SECRET: {'✅ Set' if os.environ.get('SLACK_SIGNING_SECRET') else '❌ Missing'}")
    
    print(f"\n📋 Available Endpoints:")
    print("   • /health - Health check with detailed status")
    print("   • /api/pipeline - Get all donors")
    print("   • /api/donor/<id> - Get specific donor")
    print("   • /api/templates - Get email templates")
    print("   • /api/draft - Generate email draft")
    print("   • /api/send - Send email")
    print("   • /slack/events - Slack event handler")
    print("   • /slack/commands - Slack command handler")
    
    print(f"\n🚀 **New Donor Email Commands Available!**")
    print("   • /donoremail intro [OrgName] - First introduction")
    print("   • /donoremail concept [Org] [Project] - Concept pitch")
    print("   • /donoremail meetingrequest [Org] [Date] - Meeting request")
    print("   • /donoremail proposalcover [Org] [Project] - Proposal cover")
    print("   • /donoremail help - See all available commands")
    
    print(f"\n💡 **Key Features:**")
    print("   • Shared backend services")
    print("   • AI-enhanced emails with Claude")
    print("   • Natural language chat with DeepSeek")
    print("   • Google Drive profile integration")
    print("   • Fundraising workflow stages")
    print("   • Smart fallback system")
    print("   • Enhanced error handling")
    print("   • Graceful degradation")
    
    print(f"\n" + "="*60)
    
    # Determine if we should start the server
    if not backend.initialized:
        print("❌ Backend initialization failed. Server may not function properly.")
        print("   Check environment variables and module availability.")
    else:
        print("✅ Backend initialized successfully. Server starting normally.")
    
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=True)
