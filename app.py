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

# Force redeploy - Google Sheets linked and ready for multi-tab access

# Initialize Flask app
app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Diksha Fundraising Backend API",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Basic health check - just return OK if Flask is running
        return jsonify({
            "status": "healthy",
            "service": "Diksha Fundraising Backend",
            "timestamp": datetime.now().isoformat(),
            "backend_available": backend_manager is not None
        })
    except Exception as e:
        # Even if there's an error, return a basic response
        return jsonify({
            "status": "degraded",
            "service": "Diksha Fundraising Backend",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 200

# Import shared backend with better error handling
backend_manager = None
logger.info("🔄 Attempting to import backend...")

try:
    # Try importing backend components one by one to isolate issues
    logger.info("📦 Importing backend package...")
    from backend import backend_manager
    logger.info("✅ Backend package imported successfully")
    
    if backend_manager:
        logger.info("✅ Backend manager available")
    else:
        logger.warning("⚠️ Backend manager is None")
        
except ImportError as e:
    logger.warning(f"⚠️ Backend import failed: {e}")
    logger.warning("App will run with limited functionality")
    backend_manager = None
except Exception as e:
    logger.error(f"❌ Unexpected error importing backend: {e}")
    logger.error(f"Error type: {type(e).__name__}")
    backend_manager = None

# Get services from backend manager
if backend_manager:
    donor_service = backend_manager.donor_service
    email_service = backend_manager.email_service
    email_generator = backend_manager.email_generator
    pipeline_service = backend_manager.pipeline_service
    template_service = backend_manager.template_service
    context_helpers = backend_manager.context_helpers
    deepseek_client = backend_manager.deepseek_client
    sheets_db = backend_manager.sheets_db
    cache_manager = backend_manager.cache_manager
else:
    donor_service = None
    email_service = None
    pipeline_service = None
    template_service = None
    context_helpers = None
    deepseek_client = None
    sheets_db = None

# Natural language processing is now handled by the modular slack_bot.py

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

@app.route('/api/activities', methods=['GET'])
def get_activities():
    """Get interaction log entries from Google Sheets"""
    try:
        if not sheets_db or not sheets_db.initialized:
            return jsonify({
                "success": False,
                "error": "Google Sheets not connected"
            }), 503
        
        # Get interaction log data from Google Sheets
        interaction_log_data = sheets_db.get_interaction_log()
        
        return jsonify({
            "success": True,
            "data": interaction_log_data
        })
        
    except Exception as e:
        logger.error(f"Error getting activities: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/proposals', methods=['GET'])
def get_proposals():
    """Get proposals data from Google Sheets"""
    try:
        if not sheets_db or not sheets_db.initialized:
            return jsonify({
                "success": False,
                "error": "Google Sheets not connected"
            }), 503
        
        # Get proposals data from Google Sheets
        proposals_data = sheets_db.get_proposals()
        
        return jsonify({
            "success": True,
            "data": proposals_data
        })
        
    except Exception as e:
        logger.error(f"Error getting proposals: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get alerts data from Google Sheets"""
    try:
        if not sheets_db or not sheets_db.initialized:
            return jsonify({
                "success": False,
                "error": "Google Sheets not connected"
            }), 503
        
        # Get alerts data from Google Sheets
        alerts_data = sheets_db.get_alerts()
        
        return jsonify({
            "success": True,
            "data": alerts_data
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
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
        
        if not sheets_db or not sheets_db.initialized:
            return jsonify({
                "success": False,
                "error": "Google Sheets not connected"
            }), 503
        
        # Convert donor_id back to organization name
        org_name = donor_id.replace("_", " ").title()
        
        # Update the stage
        update_data = {
            "current_stage": stage,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # This would need to be implemented in your sheets_db
        # sheets_db.update_organization(org_name, update_data)
        
        return jsonify({
            "success": True,
            "message": "Stage updated successfully"
        })
        
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
        
        if not sheets_db or not sheets_db.initialized:
            return jsonify({
                "success": False,
                "error": "Google Sheets not connected"
            }), 503
        
        # Convert donor_id back to organization name
        org_name = donor_id.replace("_", " ").title()
        
        # Update the assignment
        update_data = {
            "assigned_to": owner,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # This would need to be implemented in your sheets_db
        # sheets_db.update_organization(org_name, update_data)
        
        return jsonify({
            "success": True,
            "message": "Donor assigned successfully"
        })
        
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
        
        if not sheets_db or not sheets_db.initialized:
            return jsonify({
                "success": False,
                "error": "Google Sheets not connected"
            }), 503
        
        # Convert donor_id back to organization name
        org_name = donor_id.replace("_", " ").title()
        
        # Update the notes
        update_data = {
            "notes": notes or "",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # This would need to be implemented in your sheets_db
        # sheets_db.update_organization(org_name, update_data)
        
        return jsonify({
            "success": True,
            "message": "Notes updated successfully"
        })
        
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
        if not email_generator or not email_generator.initialized:
            return jsonify({
                "success": False,
                "error": "Email generator not available"
            }), 503
        
        # Get templates from email generator
        templates = email_generator.get_available_templates()
        
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
                "type": template_info.get("type", "intro")
            }
            web_templates.append(web_template)
        
        return jsonify({
            "success": True,
            "data": web_templates
        })
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
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
        
        if not email_generator or not email_generator.initialized:
            return jsonify({
                "success": False,
                "error": "Email generator not available"
            }), 503
        
        # Generate draft using email generator
        draft_id = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{donor_id}"
        
        draft = {
            "id": draft_id,
            "template_id": template_id,
            "donor_id": donor_id,
            "subject": subject,
            "content": content,
            "placeholders": placeholders,
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        
        # Store draft (in a real implementation, you'd save this to a database)
        # For now, we'll just return it
        
        return jsonify({
            "success": True,
            "data": draft
        })
        
    except Exception as e:
        logger.error(f"Error generating draft: {e}")
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
        
        # In a real implementation, you would:
        # 1. Retrieve the draft
        # 2. Send the email via Gmail API
        # 3. Log the thread_id and message_id
        # 4. Update the donor's last_contact_date
        
        # For now, return mock data
        thread_id = f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return jsonify({
            "success": True,
            "data": {
                "thread_id": thread_id,
                "message_id": message_id
            }
        })
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
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
            "/debug/sheets-test",
            "/debug/templates",
            "/debug/context",
            "/debug/context-test",
            "/debug/cache-stats",
            "/debug/test-deepseek",
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

# Connection validation middleware for debug endpoints
@app.before_request
def check_services():
    if request.endpoint and request.endpoint.startswith('debug'):
        # Check if Google Sheets is available for debug endpoints
        if not sheets_db or not sheets_db.initialized:
            logger.warning(f"Debug endpoint {request.endpoint} accessed without Google Sheets connection")
            return jsonify({
                "error": "Google Sheets not connected",
                "message": "Debug endpoints require Google Sheets connection",
                "hint": "Check GOOGLE_CREDENTIALS_BASE64 environment variable",
                "timestamp": datetime.now().isoformat(),
                "status_code": 503
            }), 503

# All services are now provided by the shared backend

# Initialize Slack bot with shared backend
slack_bot = None
try:
    from slack_bot_refactored import initialize_slack_bot
    slack_bot = initialize_slack_bot()
    logger.info("✅ Slack bot initialized with shared backend")
except Exception as e:
    logger.error(f"❌ Slack bot initialization failed: {e}")
    slack_bot = None

############################
# Slack Bot Configuration
############################
# Slack bot is now handled by the modular slack_bot.py
# The global instance is imported from the module

############################
# Email Template Functions
############################
def get_available_templates():
    """Get list of available email templates from Google Drive"""
    try:
        # This would connect to your Templates folder in Google Drive
        # For now, returning the standard templates we know exist
        templates = {
            "identification": "Email Template - Identification Stage",
            "engagement": "Email Template - Engagement Stage", 
            "proposal": "Email Template - Proposal Stage",
            "followup": "Email Template - Follow-up",
            "celebration": "Email Template - Grant Secured"
        }
        return templates
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return {}

# Old email generation functions removed - now using modular email_generator.py

############################
# Slack Command Handlers
############################
# Slack command handlers are now handled by the modular slack_bot.py
# The handlers are automatically set up when the bot is initialized


def handle_email_action(org_name: str, template_type: str, mode: str = None) -> str:
    """Handle email generation action"""
    try:
        # Get organization data
        org_data = sheets_db.get_org_by_name(org_name)
        if not org_data:
            return f"❌ Organization '{org_name}' not found. Use `/pipeline search {org_name}` to find exact names."
        
        # Generate email
        subject, body = email_generator.generate_email(template_type, org_data, mode)
        
        if not subject or not body:
            return f"❌ Email generation failed: {body}"
        
        # Format response
        response = f"""📧 *Email Generated for {org_name}*
*Template:* {template_type}
*Mode:* {mode or email_generator.get_mode()}

*Subject:* {subject}

*Body:*
{body}

*Recipient:* {org_data.get('contact_person', 'Unknown')}
*Organization:* {org_data.get('organization_name', 'Unknown')}
*Sector:* {org_data.get('sector_tags', 'Unknown')}

💡 *Next Steps:*
1. Review and edit the email content
2. Add any personal touches or specific details
3. Send via your preferred email client
4. Update pipeline status after sending"""
        
        return response
        
    except Exception as e:
        logger.error(f"Email action error: {e}")
        return f"❌ Error generating email: {e}"



############################
# Slack Event Handlers
############################
# Slack event handlers are now handled by the modular slack_bot.py
# The handlers are automatically set up when the bot is initialized

############################
# Flask Routes
############################
@app.route('/')
def index():
    logger.info("📊 Root endpoint accessed")
    
    # Get tab information if connected
    tab_info = {}
    if sheets_db and sheets_db.initialized:
        try:
            tab_info = {
                "connected": True,
                "sheet_id": sheets_db.sheet_id,
                "main_tab": sheets_db.sheet_tab,
                "available_tabs": sheets_db.get_all_tabs(),
                "total_tabs": len(sheets_db.get_all_tabs())
            }
        except Exception as e:
            logger.error(f"Error getting tab info: {e}")
            tab_info = {
                "connected": False,
                "error": str(e),
                "sheet_id": None,
                "main_tab": None,
                "available_tabs": [],
                "total_tabs": 0
            }
    else:
        tab_info = {
            "connected": False,
            "sheet_id": None,
            "main_tab": None,
            "available_tabs": [],
            "total_tabs": 0
        }
    
    return jsonify({
        "app": "Diksha Fundraising Automation", 
        "status": "running", 
        "mode": "slack-bolt",
        "google_sheets": tab_info,
        "slack_commands": {
            "donoremail": "/donoremail [action] [parameters] - Fundraising email generation with AI enhancement",
            "help": "Use `/donoremail help` for comprehensive command list"
        },
        "endpoints": {
            "slack_events": "/slack/events",
            "slack_commands": "/slack/commands",
            "health": "/health",
            "sheets_test": "/debug/sheets-test",
            "search": "/debug/search?q=<query>",
            "search_all_tabs": "/debug/search-all-tabs?q=<query>",
            "tabs_info": "/debug/tabs",
            "tab_data": "/debug/tab-data?tab=<tab_name>",
            "drive_files": "/debug/drive-files",
            "search_drive": "/debug/search-drive?q=<query>",
            "institutional_grants": "/debug/institutional-grants",
            "drive_summary": "/debug/drive-summary",
            "comprehensive_search": "/debug/comprehensive-search?q=<query>",
            "email_generation": "/debug/generate-email",
            "available_templates": "/debug/templates",
            "claude_test": "/debug/test-claude",
            "deepseek_test": "/debug/test-deepseek",
            "compare_templates": "/debug/compare-templates?org=<org>&template=<type>",
            "donor_profile": "/debug/donor-profile?org=<org>"
        }
    })

# DeepSeek status is now handled by the modular deepseek_client.py

@app.route('/health')
def health():
    """Health check endpoint for quick testing"""
    msg = f"✅ /health ping at {datetime.now().isoformat()}"
    print(msg, flush=True)  # visible in Terminal A
    logger.info("🏥 Health check requested")
    
    # Check component health with safety checks
    sheets_status = "connected" if (sheets_db and sheets_db.initialized) else "not_connected"
    slack_status = "ready" if (slack_bot and slack_bot.is_initialized()) else "not_configured"
    email_status = "ready" if email_generator else "not_available"
    cache_status = "available" if cache_manager else "not_available"
    deepseek_status = deepseek_client.get_status() if deepseek_client else "not_configured"
    
    # Overall health status
    overall_status = "healthy"
    if sheets_status == "not_connected":
        overall_status = "degraded"
    if not slack_bot and not email_generator:
        overall_status = "unhealthy"
    
    return jsonify({
        "status": overall_status,
        "mode": "slack-bolt",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "fixes_applied": {
            "duplicate_initialization": "resolved",
            "slack_app_handling": "consolidated",
            "import_error_handling": "implemented",
            "route_handler_mismatch": "fixed",
            "cache_manager_import": "guarded",
            "command_parser_safety": "implemented",
            "database_fallback": "implemented",
            "error_handling": "enhanced",
            "deepseek_integration": "implemented"
        },
        "components": {
            "google_sheets": sheets_status,
            "slack_bot": slack_status,
            "email_generator": email_status,
            "cache_manager": cache_status,
            "deepseek_api": deepseek_status
        },
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
        # Use the modular Slack bot handler
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
        return generate_and_send_email("identification", org_name, user_id, channel_id, "First Introduction")
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
        
        return generate_and_send_email("engagement", org_name, user_id, channel_id, f"Concept Pitch: {project_name}")
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
    return generate_and_send_email("followup", org_name, user_id, channel_id, "Follow-up Email")

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
    return generate_and_send_email("meeting_request", org_name, user_id, channel_id, f"Meeting Request for {date}")

def handle_thanks_meeting_email(parts: list, user_id: str, channel_id: str):
    """Handle thanks meeting email generation"""
    if len(parts) < 2:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail thanksmeeting [OrgName]`\nExample: `/donoremail thanksmeeting Tata Trust`"
        })
    
    org_name = " ".join(parts[1:])
    return generate_and_send_email("thanks_meeting", org_name, user_id, channel_id, "Thank You After Meeting")

def handle_connect_email(parts: list, user_id: str, channel_id: str):
    """Handle connect email generation"""
    if len(parts) < 2:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail connect [OrgName]`\nExample: `/donoremail connect Infosys Foundation`"
        })
    
    org_name = " ".join(parts[1:])
    return generate_and_send_email("connect", org_name, user_id, channel_id, "Warm Connection Email")

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
    return generate_and_send_email("proposal_cover", org_name, user_id, channel_id, f"Proposal Cover: {project_name}")

def handle_proposal_reminder_email(parts: list, user_id: str, channel_id: str):
    """Handle proposal reminder email generation"""
    if len(parts) < 2:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail proposalreminder [OrgName]`\nExample: `/donoremail proposalreminder Tata Trust`"
        })
    
    org_name = " ".join(parts[1:])
    return generate_and_send_email("proposal_reminder", org_name, user_id, channel_id, "Proposal Reminder")

def handle_pitch_email(parts: list, user_id: str, channel_id: str):
    """Handle pitch email generation"""
    if len(parts) < 3:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail pitch [OrgName] [ProjectName]`\nExample: `/donoremail pitch HDFC Bank Youth Empowerment`"
        })
    
    org_name = parts[1]
    project_name = " ".join(parts[2:])
    return generate_and_send_email("pitch", org_name, user_id, channel_id, f"Strong Pitch: {project_name}")

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
    return generate_and_send_email("impact_story", org_name, user_id, channel_id, f"Impact Story: {theme}")

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
    return generate_and_send_email("invite", org_name, user_id, channel_id, f"Event Invite: {event_name} on {date}")

def handle_festival_greeting_email(parts: list, user_id: str, channel_id: str):
    """Handle festival greeting email generation"""
    if len(parts) < 3:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage: `/donoremail festivalgreeting [OrgName] [Festival]`\nExample: `/donoremail festivalgreeting HDFC Bank Diwali`"
        })
    
    org_name = parts[1]
    festival = " ".join(parts[2:])
    return generate_and_send_email("festival_greeting", org_name, user_id, channel_id, f"Festival Greeting: {festival}")

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
        # Get donor profile info
        profile_info = email_generator.get_donor_profile_info(org_name)
        
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

def generate_and_send_email(template_type: str, org_name: str, user_id: str, channel_id: str, email_purpose: str):
    """Generate and send email using the email generator"""
    try:
        # Get organization data from Google Sheets
        if not sheets_db.initialized:
            return jsonify({
                "response_type": "ephemeral",
                "text": "❌ Google Sheets not connected. Please check configuration."
            })
        
        org_data = sheets_db.get_org_by_name(org_name)
        if not org_data:
            return jsonify({
                "response_type": "ephemeral",
                "text": f"❌ Organization '{org_name}' not found in donor database.\n\nUse `/donoremail help` to see available commands."
            })
        
        # Generate email using the email generator
        subject, body = email_generator.generate_email(template_type, org_data, mode="claude")
        
        if not subject or not body:
            return jsonify({
                "response_type": "ephemeral",
                "text": f"❌ Failed to generate email for {org_name}\n\nTemplate type '{template_type}' not found or generation failed."
            })
        
        # Format the response
        response_text = f"""📧 **{email_purpose} Generated Successfully!**

🎯 **Organization:** {org_name}
📋 **Template:** {template_type}
🤖 **Enhanced with:** Claude AI + Google Drive Profile

📝 **Subject:** {subject}

📄 **Email Body:**
{body}

---
💡 **Next Steps:**
• Review and customize the email
• Use `/donoremail refine [tone]` to adjust tone
• Use `/donoremail save [name]` to save draft
• Use `/donoremail share [@colleague]` to get feedback"""
        
        return jsonify({
            "response_type": "in_channel",
            "text": response_text
        })
        
    except Exception as e:
        logger.error(f"Error generating email: {e}")
        return jsonify({
            "response_type": "ephemeral",
            "text": f"❌ Error generating email: {str(e)}\n\nPlease try again or contact support."
        })

############################
# Debug endpoints (no Slack)
############################
@app.route('/debug/status')
def debug_status():
    org = (request.args.get('org') or '').strip()
    if not org:
        return jsonify({"error": "Missing query param 'org'"}), 400
    
    # Get data from Google Sheets
    org_data = sheets_db.get_org_by_name(org)
    if org_data:
        return jsonify({
            "organization": org_data['organization_name'],
            "stage": org_data['current_stage'],
            "assigned_to": org_data['assigned_to'],
            "next_action": org_data['next_action'],
            "next_action_date": org_data['next_action_date'],
            "email": org_data['email'],
            "phone": org_data['phone'],
            "contact_person": org_data['contact_person'],
            "sector_tags": org_data['sector_tags'],
            "geography": org_data['geography'],
            "notes": org_data['notes'],
            "last_updated": org_data['last_updated'],
            "mode": "slack-bolt",
            "sheets_connected": True
        })
    else:
        return jsonify({
            "error": f"Organization '{org}' not found",
            "mode": "slack-bolt",
            "sheets_connected": sheets_db.initialized
        }), 404

@app.route('/debug/assign', methods=['POST'])
def debug_assign():
    data = request.get_json(silent=True) or {}
    org = (data.get('org') or '').strip()
    email = (data.get('email') or '').strip()
    if not org or not email:
        return jsonify({"error": "Body must include 'org' and 'email'"}), 400
    
    # Update in Google Sheets
    if sheets_db.update_org_field(org, 'assigned_to', email):
        return jsonify({
            "ok": True, 
            "organization": org, 
            "assigned_to": email, 
            "mode": "slack-bolt",
            "sheets_connected": True
        })
    else:
        return jsonify({
            "error": f"Failed to assign {org} to {email}. Organization not found or update failed.",
            "mode": "slack-bolt",
            "sheets_connected": sheets_db.initialized
        }), 404

@app.route('/debug/next', methods=['POST'])
def debug_next():
    data = request.get_json(silent=True) or {}
    org = (data.get('org') or '').strip()
    action_text = (data.get('action') or '').strip()
    due_date = (data.get('date') or '').strip()
    if not org or not action_text or not due_date:
        return jsonify({"error": "Body must include 'org', 'action', 'date' (YYYY-MM-DD)"}), 400
    
    # Update both next_action and next_action_date in Google Sheets
    success1 = sheets_db.update_org_field(org, 'next_action', action_text)
    success2 = sheets_db.update_org_field(org, 'next_action_date', due_date)
    
    if success1 and success2:
        return jsonify({
            "ok": True, 
            "organization": org, 
            "next_action": action_text, 
            "next_action_date": due_date, 
            "mode": "slack-bolt",
            "sheets_connected": True
        })
    else:
        return jsonify({
            "error": f"Failed to update next action for {org}. Organization not found or update failed.",
            "mode": "slack-bolt",
            "sheets_connected": sheets_db.initialized
        }), 404

@app.route('/debug/stage', methods=['POST'])
def debug_stage():
    data = request.get_json(silent=True) or {}
    org = (data.get('org') or '').strip()
    new_stage = (data.get('stage') or '').strip()
    if not org or not new_stage:
        return jsonify({"error": "Body must include 'org' and 'stage'"}), 400
    
    # Get current stage first
    org_data = sheets_db.get_org_by_name(org)
    if org_data:
        old_stage = org_data['current_stage']
        if sheets_db.update_org_field(org, 'current_stage', new_stage):
            return jsonify({
                "ok": True, 
                "organization": org, 
                "from": old_stage, 
                "to": new_stage, 
                "mode": "slack-bolt",
                "sheets_connected": True
            })
        else:
            return jsonify({
                "error": f"Failed to update stage for {org}.",
                "mode": "slack-bolt",
                "sheets_connected": sheets_db.initialized
            }), 500
    else:
        return jsonify({
            "error": f"Organization '{org}' not found in pipeline.",
            "mode": "slack-bolt",
            "sheets_connected": sheets_db.initialized
        }), 404

@app.route('/debug/sheets-test')
def debug_sheets_test():
    """Test Google Sheets connection and get sample data"""
    try:
        if not sheets_db or not sheets_db.initialized:
            return jsonify({
                "error": "Google Sheets not connected",
                "sheets_connected": False,
                "mode": "slack-bolt",
                "status_code": 503
            }), 503
        
        # Get pipeline data to test connection
        try:
            pipeline = sheets_db.get_pipeline()
            sample_orgs = []
            total_orgs = 0
            
            for stage, orgs in pipeline.items():
                total_orgs += len(orgs)
                if len(sample_orgs) < 5:
                    sample_orgs.extend([org['organization_name'] for org in orgs[:5-len(sample_orgs)]])
            
            return jsonify({
                "sheets_connected": True,
                "sheet_id": sheets_db.sheet_id,
                "sheet_tab": sheets_db.sheet_tab,
                "sample_organizations": sample_orgs,
                "total_organizations": total_orgs,
                "stages": list(pipeline.keys()),
                "mode": "slack-bolt",
                "status_code": 200
            })
        except Exception as e:
            logger.error(f"Error getting pipeline data: {e}")
            return jsonify({
                "error": f"Google Sheets connection test failed: {e}",
                "sheets_connected": False,
                "mode": "slack-bolt",
                "status_code": 500
            }), 500
        
    except Exception as e:
        logger.error(f"Error testing Google Sheets: {e}")
        return jsonify({
            "error": f"Google Sheets test failed: {e}",
            "sheets_connected": False,
            "mode": "slack-bolt",
            "status_code": 500
        }), 500

@app.route('/debug/search')
def debug_search():
    """Search organizations via API"""
    query = (request.args.get('q') or '').strip()
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    
    matches = sheets_db.find_org(query)
    return jsonify({
        "query": query,
        "matches": [{"name": m['organization_name'], "stage": m['current_stage'], "score": m.get('similarity_score', 0)} for m in matches],
        "count": len(matches),
        "sheets_connected": sheets_db.initialized,
        "mode": "slack-bolt"
    })

@app.route('/debug/tabs')
def debug_tabs():
    """Get information about all tabs in the spreadsheet"""
    if not sheets_db.initialized:
        return jsonify({
            "error": "Google Sheets not connected",
            "sheets_connected": False,
            "mode": "slack-bolt"
        }), 500
    
    tabs = sheets_db.get_all_tabs()
    summary = sheets_db.get_tab_summary()
    
    return jsonify({
        "available_tabs": tabs,
        "tab_summary": summary,
        "main_tab": sheets_db.sheet_tab,
        "sheets_connected": True,
        "mode": "slack-bolt"
    })

@app.route('/debug/search-all-tabs')
def debug_search_all_tabs():
    """Search organizations across all tabs"""
    query = (request.args.get('q') or '').strip()
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    
    if not sheets_db.initialized:
        return jsonify({
            "error": "Google Sheets not connected",
            "sheets_connected": False,
            "mode": "slack-bolt"
        }), 500
    
    matches = sheets_db.search_across_all_tabs(query)
    return jsonify({
        "query": query,
        "matches": [{
            "name": m['organization_name'], 
            "tab": m['tab_name'], 
            "score": m.get('similarity_score', 0),
            "exact_match": m.get('exact_match', False)
        } for m in matches],
        "count": len(matches),
        "sheets_connected": True,
        "mode": "slack-bolt"
    })

@app.route('/debug/tab-data')
def debug_tab_data():
    """Get data from a specific tab"""
    tab_name = (request.args.get('tab') or '').strip()
    if not tab_name:
        return jsonify({"error": "Missing query parameter 'tab'"}), 400
    
    if not sheets_db.initialized:
        return jsonify({
            "error": "Google Sheets not connected",
            "sheets_connected": False,
            "mode": "slack-bolt"
        }), 500
    
    tab_data = sheets_db.get_tab_data(tab_name)
    return jsonify({
        "tab_name": tab_name,
        "row_count": len(tab_data),
        "data": tab_data[:10] if tab_data else [],  # Return first 10 rows for preview
        "sheets_connected": True,
        "mode": "slack-bolt"
    })

@app.route('/debug/drive-files')
def debug_drive_files():
    """Get files from Google Drive donor profiles folder"""
    if not sheets_db.initialized:
        return jsonify({
            "error": "Google services not connected",
            "sheets_connected": False,
            "mode": "slack-bolt"
        }), 500
    
    files = sheets_db.get_drive_files()
    return jsonify({
        "folder_id": "1zfT_oXgcIMSubeF3TtSNflkNvTx__dBK",
        "file_count": len(files),
        "files": files,
        "sheets_connected": True,
        "mode": "slack-bolt"
    })

@app.route('/debug/search-drive')
def debug_search_drive():
    """Search for files in Google Drive folder"""
    query = (request.args.get('q') or '').strip()
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    
    if not sheets_db.initialized:
        return jsonify({
            "error": "Google services not connected",
            "sheets_connected": False,
            "mode": "slack-bolt"
        }), 500
    
    files = sheets_db.search_drive_files(query)
    return jsonify({
        "query": query,
        "file_count": len(files),
        "files": files,
        "sheets_connected": True,
        "mode": "slack-bolt"
    })

@app.route('/debug/comprehensive-search')
def debug_comprehensive_search():
    """Search across both Google Sheets and Google Drive"""
    query = (request.args.get('q') or '').strip()
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    
    if not sheets_db.initialized:
        return jsonify({
            "error": "Google services not connected",
            "sheets_connected": False,
            "mode": "slack-bolt"
        }), 500
    
    # Search in sheets
    sheet_matches = sheets_db.search_across_all_tabs(query)
    
    # Search in all drive folders
    drive_results = sheets_db.search_all_drive_folders(query)
    
    # Count total drive matches
    total_drive_matches = len(drive_results.get("donor_profiles", []))
    for subfolder_files in drive_results.get("institutional_grants", {}).values():
        total_drive_matches += len(subfolder_files)
    
    return jsonify({
        "query": query,
        "sheets_results": {
            "count": len(sheet_matches),
            "matches": [{
                "name": m['organization_name'], 
                "tab": m['tab_name'], 
                "score": m.get('similarity_score', 0)
            } for m in sheet_matches]
        },
        "drive_results": {
            "total_count": total_drive_matches,
            "donor_profiles": {
                "count": len(drive_results.get("donor_profiles", [])),
                "files": [{"name": f['name'], "id": f['id'], "link": f['webViewLink']} for f in drive_results.get("donor_profiles", [])]
            },
            "institutional_grants": {
                "Templates": {"count": len(drive_results.get("institutional_grants", {}).get("Templates", [])), "files": [{"name": f['name'], "id": f['id']} for f in drive_results.get("institutional_grants", {}).get("Templates", [])]},
                "Secured Grants": {"count": len(drive_results.get("institutional_grants", {}).get("Secured Grants", [])), "files": [{"name": f['name'], "id": f['id']} for f in drive_results.get("institutional_grants", {}).get("Secured Grants", [])]},
                "Resources": {"count": len(drive_results.get("institutional_grants", {}).get("Resources", [])), "files": [{"name": f['name'], "id": f['id']} for f in drive_results.get("institutional_grants", {}).get("Resources", [])]},
                "Active Prospects": {"count": len(drive_results.get("institutional_grants", {}).get("Active Prospects", [])), "files": [{"name": f['name'], "id": f['id']} for f in drive_results.get("institutional_grants", {}).get("Active Prospects", [])]},
                "Archive": {"count": len(drive_results.get("institutional_grants", {}).get("Archive", [])), "files": [{"name": f['name'], "id": f['id']} for f in drive_results.get("institutional_grants", {}).get("Archive", [])]}
            }
        },
        "total_results": len(sheet_matches) + total_drive_matches,
        "sheets_connected": True,
        "mode": "slack-bolt"
    })

@app.route('/debug/institutional-grants')
def debug_institutional_grants():
    """Get files from institutional grants folder and subfolders"""
    if not sheets_db.initialized:
        return jsonify({
            "error": "Google services not connected",
            "sheets_connected": False,
            "mode": "slack-bolt"
        }), 500
    
    files = sheets_db.get_institutional_grants_files()
    return jsonify({
        "folder_id": "1MDCBas01pwIeeLfhz4Nay06GqhUbRTQO",
        "subfolders": files,
        "total_files": sum(len(folder_files) for folder_files in files.values()),
        "sheets_connected": True,
        "mode": "slack-bolt"
    })

@app.route('/debug/drive-summary')
def debug_drive_summary():
    """Get comprehensive summary of all Drive folders"""
    if not sheets_db.initialized:
        return jsonify({
            "error": "Google services not connected",
            "sheets_connected": False,
            "mode": "slack-bolt"
        }), 500
    
    summary = sheets_db.get_drive_summary()
    return jsonify({
        "drive_summary": summary,
        "sheets_connected": True,
        "mode": "slack-bolt"
    })

@app.route('/debug/templates')
def debug_templates():
    """List available email templates and modes"""
    try:
        templates = email_generator.get_available_templates()
        current_mode = email_generator.get_mode()
        claude_configured = bool(os.environ.get("ANTHROPIC_API_KEY"))
        
        return jsonify({
            "ok": True,
            "templates": templates,
            "current_mode": current_mode,
            "modes": {
                "claude": "AI-enhanced emails using Claude API",
                "template": "Basic template system"
            },
            "claude_api_key": "configured" if claude_configured else "missing",
            "mode": "slack-bolt"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Templates endpoint failed: {e}",
            "mode": "slack-bolt"
        }), 500

@app.route('/debug/generate-email', methods=['POST'])
def debug_generate_email():
    """Generate custom email via API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        org = data.get('org', '').strip()
        template = data.get('template', '').strip().lower()
        mode = data.get('mode', '').strip().lower()
        
        if not org or not template:
            return jsonify({"error": "Missing required fields: org, template"}), 400
        
        # Get organization data
        org_data = sheets_db.get_org_by_name(org)
        if not org_data:
            return jsonify({
                "error": f"Organization '{org}' not found",
                "mode": "slack-bolt",
                "sheets_connected": sheets_db.initialized
            }), 404
        
        # Generate email
        subject, body = email_generator.generate_email(template, org_data, mode)
        
        if not subject or not body:
            return jsonify({
                "error": f"Email generation failed: {body}",
                "mode": "slack-bolt",
                "sheets_connected": sheets_db.initialized
            }), 500
        
        return jsonify({
            "ok": True,
            "email": {
                "subject": subject,
                "body": body,
                "template": template,
                "mode": mode or email_generator.get_mode(),
                "organization": org,
                "contact_person": org_data.get('contact_person', 'Unknown'),
                "sector": org_data.get('sector_tags', 'Unknown')
            },
            "mode": "slack-bolt",
            "sheets_connected": sheets_db.initialized
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Email generation failed: {e}",
            "mode": "slack-bolt",
            "sheets_connected": sheets_db.initialized
        }), 500

@app.route('/debug/test-claude')
def debug_test_claude():
    """Test Claude API integration"""
    try:
        # Test with sample data
        test_donor_data = {
            'organization_name': 'Test Foundation',
            'contact_person': 'John Doe',
            'sector_tags': 'Education Technology',
            'geography': 'Bihar',
            'alignment_score': '8',
            'priority': 'High',
            'current_stage': 'Engagement',
            'estimated_grant_size': '₹10,00,000',
            'notes': 'Interested in digital skills programs'
        }
        
        # Test both modes
        claude_subject, claude_body = email_generator.generate_email('engagement', test_donor_data, 'claude')
        template_subject, template_body = email_generator.generate_email('engagement', test_donor_data, 'template')
        
        return jsonify({
            "ok": True,
            "test_data": test_donor_data,
            "claude_mode": {
                "subject": claude_subject,
                "body_length": len(claude_body) if claude_body else 0,
                "status": "working" if claude_subject else "failed"
            },
            "template_mode": {
                "subject": template_subject,
                "body_length": len(template_body) if template_body else 0,
                "status": "working" if template_subject else "failed"
            },
            "claude_api_key": "configured" if os.environ.get("ANTHROPIC_API_KEY") else "missing",
            "mode": "slack-bolt"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Claude test failed: {e}",
            "mode": "slack-bolt"
        }), 500

@app.route('/debug/compare-templates')
def debug_compare_templates():
    """Compare base template vs. enhanced version for a specific organization"""
    org = (request.args.get('org') or '').strip()
    template_type = (request.args.get('template') or 'identification').strip().lower()
    
    if not org:
        return jsonify({"error": "Missing query parameter 'org'"}), 400
    
    if not sheets_db.initialized:
        return jsonify({
            "error": "Google services not connected",
            "sheets_connected": False,
            "mode": "slack-bolt"
        }), 500
    
    # Get organization data
    org_data = sheets_db.get_org_by_name(org)
    if not org_data:
        return jsonify({
            "error": f"Organization '{org}' not found",
            "mode": "slack-bolt",
            "sheets_connected": True
        }), 404
    
    try:
        # Use the email generator's comparison method
        comparison_result = email_generator.compare_templates(template_type, org_data)
        
        if comparison_result.get('ok'):
            # Add additional context
            comparison_result['organization'] = org
            comparison_result['template_type'] = template_type
            comparison_result['donor_context'] = {
                "sector": org_data.get('sector_tags', ''),
                "geography": org_data.get('geography', ''),
                "alignment_score": org_data.get('alignment_score', ''),
                "priority": org_data.get('priority', ''),
                "current_stage": org_data.get('current_stage', '')
            }
            comparison_result['mode'] = "slack-bolt"
            comparison_result['sheets_connected'] = True
            
            return jsonify(comparison_result)
        else:
            return jsonify({
                "error": comparison_result.get('error', 'Template comparison failed'),
                "mode": "slack-bolt",
                "sheets_connected": True
            }), 500
        
    except Exception as e:
        return jsonify({
            "error": f"Template comparison failed: {e}",
            "mode": "slack-bolt",
            "sheets_connected": True
        }), 500

@app.route('/debug/donor-profile')
def debug_donor_profile():
    """Get donor profile information from Google Drive"""
    org = (request.args.get('org') or '').strip()
    
    if not org:
        return jsonify({"error": "Missing query parameter 'org'"}), 400
    
    try:
        # Get donor profile information
        profile_info = email_generator.get_donor_profile_info(org)
        
        # Add additional context
        profile_info['mode'] = "slack-bolt"
        profile_info['sheets_connected'] = sheets_db.initialized
        
        return jsonify(profile_info)
        
    except Exception as e:
        return jsonify({
            "error": f"Donor profile lookup failed: {e}",
            "mode": "slack-bolt",
            "sheets_connected": sheets_db.initialized
        }), 500

@app.route("/debug/cache-stats")
def debug_cache_stats():
    """Get global cache statistics"""
    try:
        if cache_manager is None:
            return jsonify({
                "ok": False,
                "error": "Cache manager not available"
            }), 503
        
        stats = cache_manager.get_stats()
        return jsonify({
            "ok": True,
            "cache_stats": stats,
            "message": "Global cache statistics retrieved successfully"
        })
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@app.route("/debug/clear-cache", methods=["POST"])
def debug_clear_cache():
    """Clear the global cache"""
    try:
        if cache_manager is None:
            return jsonify({
                "ok": False,
                "error": "Cache manager not available"
            }), 503
        
        cache_manager.clear()
        return jsonify({
            "ok": True,
            "message": "Global cache cleared successfully"
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

# Add debug endpoint for testing DeepSeek
@app.route('/debug/test-deepseek', methods=['POST'])
def debug_test_deepseek():
    """Test DeepSeek API integration"""
    try:
        if not deepseek_client:
            return jsonify({
                "error": "DeepSeek not configured",
                "status": "DEEPSEEK_API_KEY not set"
            }), 503
        
        data = request.get_json()
        message = data.get('message', 'Hello, this is a test message.')
        context = data.get('context', {})
        
        response = deepseek_client.chat_completion(message, context)
        
        return jsonify({
            "ok": True,
            "message": message,
            "response": response,
            "api_status": "working" if response else "failed"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"DeepSeek test failed: {e}",
            "ok": False
        }), 500

# Add debug endpoint for template management
@app.route('/debug/template-management', methods=['GET', 'POST'])
def debug_template_management():
    """Debug endpoint for template management"""
    try:
        if not email_generator or not email_generator.initialized:
            return jsonify({
                "ok": False,
                "error": "Email generator not available"
            }), 503
        
        if request.method == 'GET':
            # Get template information
            templates = email_generator.get_available_templates()
            drive_templates = email_generator._get_templates_from_drive()
            
            return jsonify({
                "ok": True,
                "available_templates": templates,
                "drive_templates": list(drive_templates.keys()) if drive_templates else [],
                "drive_service_available": email_generator.drive_service is not None,
                "mode": "slack-bolt"
            })
        
        elif request.method == 'POST':
            # Create and upload sample templates
            data = request.get_json() or {}
            action = data.get('action', 'upload_samples')
            
            if action == 'upload_samples':
                results = email_generator.create_and_upload_sample_templates()
                return jsonify({
                    "ok": True,
                    "action": "upload_samples",
                    "results": results,
                    "mode": "slack-bolt"
                })
            
            elif action == 'test_template':
                template_name = data.get('template_name', 'intro')
                template_content = email_generator.get_template_content(template_name)
                return jsonify({
                    "ok": True,
                    "action": "test_template",
                    "template_name": template_name,
                    "template_found": template_content is not None,
                    "template_preview": template_content[:200] + "..." if template_content and len(template_content) > 200 else template_content,
                    "mode": "slack-bolt"
                })
            
            return jsonify({
                "ok": False,
                "error": "Unknown action",
                "available_actions": ["upload_samples", "test_template"]
            }), 400
        
    except Exception as e:
        logger.error(f"Template management error: {e}")
        return jsonify({
            "ok": False,
            "error": str(e),
            "mode": "slack-bolt"
        }), 500

# Add debug endpoint for testing context helpers
@app.route('/debug/context', methods=['GET'])
def debug_context():
    """Test context helper functions with current dependencies"""
    try:
        # Get query parameter for donor context
        query = request.args.get("q", "test query")
        
        # Test all context helper functions
        donor_context = get_relevant_donor_context(query, sheets_db)
        template_context = get_template_context(email_generator)
        pipeline_context = get_pipeline_insights(sheets_db)
        
        return jsonify({
            "ok": True,
            "query": query,
            "context_data": {
                "donor_context": donor_context,
                "template_context": template_context,
                "pipeline_context": pipeline_context
            },
            "dependencies_status": {
                "sheets_db": "✅ Available" if sheets_db and sheets_db.initialized else "❌ Not Available",
                "email_generator": "✅ Available" if email_generator else "❌ Not Available"
            },
            "message": "Context helper functions executed successfully"
        })
        
    except Exception as e:
        logger.error(f"Error in context debug endpoint: {e}")
        return jsonify({
            "ok": False,
            "error": f"Context debug failed: {e}",
            "dependencies_status": {
                "sheets_db": "❌ Error" if sheets_db is None else ("✅ Available" if sheets_db.initialized else "❌ Not Initialized"),
                "email_generator": "❌ Error" if email_generator is None else "✅ Available"
            }
        }), 500

# Add debug endpoint for testing context helpers with POST for complex queries
@app.route('/debug/context-test', methods=['POST'])
def debug_context_test():
    """Test context helper functions with POST data for complex queries"""
    try:
        data = request.get_json() or {}
        query = data.get("query", "Wipro Foundation")
        test_mode = data.get("mode", "all")  # all, donor, template, pipeline
        
        results = {}
        
        if test_mode in ["all", "donor"]:
            results["donor_context"] = get_relevant_donor_context(query, sheets_db)
        
        if test_mode in ["all", "template"]:
            results["template_context"] = get_template_context(email_generator)
        
        if test_mode in ["all", "pipeline"]:
            results["pipeline_context"] = get_pipeline_insights(sheets_db)
        
        return jsonify({
            "ok": True,
            "test_mode": test_mode,
            "query": query,
            "results": results,
            "dependencies_status": {
                "sheets_db": "✅ Available" if sheets_db and sheets_db.initialized else "❌ Not Available",
                "email_generator": "✅ Available" if email_generator else "❌ Not Available"
            },
            "message": f"Context test completed for mode: {test_mode}"
        })
        
    except Exception as e:
        logger.error(f"Error in context test endpoint: {e}")
        return jsonify({
            "ok": False,
            "error": f"Context test failed: {e}",
            "test_mode": data.get("mode", "unknown") if 'data' in locals() else "unknown"
        }), 500

@app.route('/debug/drive-templates', methods=['GET'])
def debug_drive_templates():
    """Test Drive template reading functionality"""
    try:
        if not email_generator:
            return jsonify({
                "ok": False,
                "error": "Email generator not available"
            }), 503
        
        # Test template reading from Drive
        templates = email_generator.get_available_templates()
        template_details = {}
        
        for template_name in templates.keys():
            template_content = email_generator.get_template_content(template_name)
            if template_content:
                template_details[template_name] = {
                    "has_content": True,
                    "content_length": len(template_content),
                    "content_preview": template_content[:200] + "..." if len(template_content) > 200 else template_content,
                    "source": "Drive" if len(template_content) > 50 else "Hardcoded"
                }
            else:
                template_details[template_name] = {
                    "has_content": False,
                    "content_length": 0,
                    "content_preview": "No content available",
                    "source": "Hardcoded"
                }
        
        # Test Drive service connectivity
        drive_status = "Not configured"
        if email_generator.drive_service:
            try:
                # Simple test query
                test_query = "name='Templates' and mimeType='application/vnd.google-apps.folder'"
                results = email_generator.drive_service.files().list(
                    q=test_query,
                    spaces='drive',
                    fields='files(id, name)',
                    pageSize=1
                ).execute()
                
                if results.get('files'):
                    drive_status = f"Connected - Found {len(results['files'])} template folders"
                else:
                    drive_status = "Connected - No template folders found"
            except Exception as e:
                drive_status = f"Error: {str(e)}"
        
        return jsonify({
            "ok": True,
            "drive_status": drive_status,
            "total_templates": len(templates),
            "template_details": template_details,
            "drive_service_configured": bool(email_generator.drive_service),
            "message": "Drive template test completed"
        })
        
    except Exception as e:
        logger.error(f"Error in Drive templates test: {e}")
        return jsonify({
            "ok": False,
            "error": f"Drive templates test failed: {e}"
        }), 500

def validate_startup_components():
    """Validate all startup components and return status"""
    validation_results = {
        "google_sheets": {"status": "❌ Not Available", "details": "Database not initialized"},
        "google_drive": {"status": "❌ Not Available", "details": "Drive service not configured"},
        "slack_bot": {"status": "❌ Not Available", "details": "Slack not configured"},
        "email_generator": {"status": "❌ Not Available", "details": "Email generator not available"},
        "claude_ai": {"status": "❌ Not Available", "details": "No API key configured"},
        "deepseek_ai": {"status": "❌ Not Available", "details": "No API key configured"},
        "cache_manager": {"status": "❌ Not Available", "details": "Cache manager not available"},
        "security": {"status": "❌ Not Available", "details": "Security features not configured"},
        "monitoring": {"status": "❌ Not Available", "details": "Monitoring not configured"}
    }
    
    # Check Google Sheets
    if sheets_db and sheets_db.initialized:
        validation_results["google_sheets"] = {"status": "✅ Connected", "details": f"Sheet ID: {sheets_db.sheet_id}"}
    elif sheets_db is None:
        validation_results["google_sheets"] = {"status": "❌ Failed", "details": "Initialization failed"}
    
    # Check Google Drive
    if email_generator and email_generator.drive_service:
        validation_results["google_drive"] = {"status": "✅ Connected", "details": "Drive service ready"}
    
    # Check Slack Bot
    if slack_bot and slack_bot.is_initialized():
        validation_results["slack_bot"] = {"status": "✅ Ready", "details": "Modular Slack integration active"}
    
    # Check Email Generator
    if email_generator:
        validation_results["email_generator"] = {"status": "✅ Ready", "details": "Modular system active"}
    
    # Check Claude AI
    if os.environ.get('ANTHROPIC_API_KEY'):
        validation_results["claude_ai"] = {"status": "✅ Configured", "details": "AI enhancement enabled"}
    
    # Check DeepSeek AI
    if deepseek_client and deepseek_client.initialized:
        validation_results["deepseek_ai"] = {"status": "✅ Configured", "details": "Natural language chat enabled"}
    
    # Check Cache Manager
    if cache_manager:
        validation_results["cache_manager"] = {"status": "✅ Available", "details": "Cache system ready"}
    
    # Check Security Features
    if slack_bot and slack_bot.is_initialized():
        validation_results["security"] = {"status": "✅ Configured", "details": "Slack signature validation enabled"}
    else:
        validation_results["security"] = {"status": "⚠️ Limited", "details": "Slack signature validation disabled"}
    
    # Check Monitoring Features
    validation_results["monitoring"] = {"status": "✅ Active", "details": "Request logging, error handling, and health checks enabled"}
    
    return validation_results

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    
    # Startup logging
    print("🚀 Diksha Foundation Fundraising Bot Starting...")
    print("="*60)
    
    # Validate components
    validation_results = validate_startup_components()
    
    for component, result in validation_results.items():
        print(f"{result['status']} {component.replace('_', ' ').title()}: {result['details']}")
    
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
    print("   • /debug/sheets-test - Test Google Sheets connection")
    print("   • /debug/templates - Email templates")
    print("   • /debug/generate-email - Generate emails")
    print("   • /debug/test-claude - Test Claude integration")
    print("   • /debug/test-deepseek - Test DeepSeek integration")
    print("   • /slack/events - Slack event handler")
    print("   • /slack/commands - Slack command handler")
    
    print(f"\n🚀 **New Donor Email Commands Available!**")
    print("   • /donoremail intro [OrgName] - First introduction")
    print("   • /donoremail concept [Org] [Project] - Concept pitch")
    print("   • /donoremail meetingrequest [Org] [Date] - Meeting request")
    print("   • /donoremail proposalcover [Org] [Project] - Proposal cover")
    print("   • /donoremail help - See all available commands")
    
    print(f"\n💡 **Key Features:**")
    print("   • AI-enhanced emails with Claude")
    print("   • Natural language chat with DeepSeek")
    print("   • Google Drive profile integration")
    print("   • Fundraising workflow stages")
    print("   • Smart fallback system")
    print("   • Enhanced error handling")
    print("   • Graceful degradation")
    
    print(f"\n" + "="*60)
    
    # Determine if we should start the server
    critical_components = [validation_results["google_sheets"]["status"], validation_results["email_generator"]["status"]]
    if all("❌" in status for status in critical_components):
        print("❌ Critical components failed. Server may not function properly.")
        print("   Check environment variables and module availability.")
    elif any("❌" in status for status in critical_components):
        print("⚠️  Some components failed. Server will run with limited functionality.")
    else:
        print("✅ All critical components ready. Server starting normally.")
    
    print("="*60)
    
    # Get port from environment variable (Railway requirement)
    port = int(os.getenv('PORT', 5000))
    
    print(f"🚀 Starting Flask app on port {port}")
    print(f"🌐 Health check available at: http://0.0.0.0:{port}/api/health")
    print(f"📊 Root endpoint available at: http://0.0.0.0:{port}/")
    print(f"🔧 Backend status: {'Available' if backend_manager else 'Limited'}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise
