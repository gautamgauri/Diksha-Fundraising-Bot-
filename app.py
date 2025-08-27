from flask import Flask, request, jsonify
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Slack Bolt for easier Slack integration
from slack_bolt import App as SlackApp
from slack_bolt.adapter.flask import SlackRequestHandler

# Google Sheets integration
from sheets_sync import SheetsDB

# Force redeploy - Google Sheets linked and ready for multi-tab access

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

############################
# Google Sheets Database
############################
# Initialize Google Sheets database
sheets_db = SheetsDB()

############################
# Slack App Configuration
############################
slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")

# Initialize Slack app (only if credentials are available)
slack_app = None
slack_handler = None

if slack_bot_token and slack_signing_secret:
    slack_app = SlackApp(
        token=slack_bot_token,
        signing_secret=slack_signing_secret
    )
    # Create Flask handler
    slack_handler = SlackRequestHandler(slack_app)
    logger.info("✅ Slack app initialized with credentials")
else:
    logger.warning("⚠️  Slack credentials not found. Running in test mode.")
    logger.info("Set SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET environment variables for full Slack integration.")

############################
# Slack Command Handlers
############################
if slack_app:
    @slack_app.command("/pipeline")
    def pipeline_command(ack, respond, command):
        """Handle /pipeline slash command"""
        ack()
        print(f"📊 /pipeline hit | user={command.get('user_name', 'unknown')} | text={command.get('text', '')}", flush=True)
        text = (command.get("text", "") or "").strip()
    
        if not text:
            respond("🎯 *Diksha Fundraising Bot*\n\nUsage:\n• `/pipeline status <org>` - Check organization status\n• `/pipeline assign <org> <email>` - Assign to team member\n• `/pipeline next <org> | <action> | <YYYY-MM-DD>` - Set next action\n• `/pipeline stage <org> | <stage>` - Update pipeline stage\n• `/pipeline search <query>` - Search organizations\n\n*Connected to live Google Sheets data*")
            return

        parts = text.split()
        action = parts[0].lower()
        args = parts[1:]

        try:
            if action == "status":
                # /pipeline status <org>
                if not args:
                    respond("Usage: /pipeline status <organization>")
                    return
                org_query = " ".join(args)
                
                # Get data from Google Sheets
                org_data = sheets_db.get_org_by_name(org_query)
                if org_data:
                    respond(f"🏢 *{org_data['organization_name']}*\n📊 Stage: {org_data['current_stage']}\n👤 Assigned: {org_data['assigned_to']}\n📅 Next: {org_data['next_action']} on {org_data['next_action_date']}\n📧 Email: {org_data['email']}\n📞 Phone: {org_data['phone']}\n👥 Contact: {org_data['contact_person']}\n🏷️ Sector: {org_data['sector_tags']}\n🌍 Geography: {org_data['geography']}\n📝 Notes: {org_data['notes']}")
                else:
                    # Try to find similar organizations
                    matches = sheets_db.find_org(org_query)
                    if matches:
                        respond(f"❌ Organization '{org_query}' not found. Similar organizations:\n" + "\n".join([f"• {match['organization_name']}" for match in matches]))
                    else:
                        respond(f"❌ Organization '{org_query}' not found in pipeline.")
                return

            if action == "assign":
                # /pipeline assign <org> <email>
                if len(args) < 2:
                    respond("Usage: /pipeline assign <organization> <email>")
                    return
                org_query = " ".join(args[:-1])
                email = args[-1]
                
                # Update in Google Sheets
                if sheets_db.update_org_field(org_query, 'assigned_to', email):
                    respond(f"✅ Assigned *{org_query}* to {email}")
                else:
                    respond(f"❌ Failed to assign {org_query}. Organization not found or update failed.")
                return

            if action == "next":
                # /pipeline next <org> | <action> | <YYYY-MM-DD>
                rest = " ".join(args)
                parts2 = [p.strip() for p in rest.split("|")]
                if len(parts2) < 3:
                    respond("Usage: /pipeline next <org> | <action> | <YYYY-MM-DD>")
                    return
                org_query, action_text, due_date = parts2[0], parts2[1], parts2[2]
                
                # Update both next_action and next_action_date
                success1 = sheets_db.update_org_field(org_query, 'next_action', action_text)
                success2 = sheets_db.update_org_field(org_query, 'next_action_date', due_date)
                
                if success1 and success2:
                    respond(f"📅 Updated next action for *{org_query}*:\n• Action: {action_text}\n• Due: {due_date}")
                else:
                    respond(f"❌ Failed to update next action for {org_query}. Organization not found or update failed.")
                return

            if action == "stage":
                # /pipeline stage <org> | <stage>
                rest = " ".join(args)
                parts2 = [p.strip() for p in rest.split("|")]
                if len(parts2) < 2:
                    respond("Usage: /pipeline stage <org> | <stage>")
                    return
                org_query, new_stage = parts2[0], parts2[1]
                
                # Get current stage first
                org_data = sheets_db.get_org_by_name(org_query)
                if org_data:
                    old_stage = org_data['current_stage']
                    if sheets_db.update_org_field(org_query, 'current_stage', new_stage):
                        respond(f"🔄 Stage updated for *{org_query}*:\n• From: {old_stage}\n• To: {new_stage}")
                    else:
                        respond(f"❌ Failed to update stage for {org_query}.")
                else:
                    respond(f"❌ Organization '{org_query}' not found in pipeline.")
                return

            if action == "search":
                # /pipeline search <query>
                if not args:
                    respond("Usage: /pipeline search <query>")
                    return
                query = " ".join(args)
                matches = sheets_db.find_org(query)
                if matches:
                    respond(f"🔍 Organizations matching '{query}':\n" + "\n".join([f"• {match['organization_name']} ({match['current_stage']})" for match in matches]))
                else:
                    respond(f"🔍 No organizations found matching '{query}'")
                return

            respond("Unknown action. Use one of: status, assign, next, stage, search")
        except Exception as e:
            logger.error(f"Error in pipeline command: {e}")
            respond(f"Error: {e}")

############################
# Slack Event Handlers
############################
if slack_app:
    @slack_app.event("app_mention")
    def handle_app_mention(event, say):
        """Handle when the bot is mentioned"""
        say(f"Hello! I'm the Diksha Fundraising Bot. Use `/pipeline` to manage your fundraising pipeline.")

    @slack_app.event("message")
    def handle_message(event, say):
        """Handle general messages (optional)"""
        # Only respond to messages in specific channels if needed
        pass

############################
# Flask Routes
############################
@app.route('/')
def index():
    logger.info("📊 Root endpoint accessed")
    
    # Get tab information if connected
    tab_info = {}
    if sheets_db.initialized:
        tab_info = {
            "connected": True,
            "sheet_id": sheets_db.sheet_id,
            "main_tab": sheets_db.sheet_tab,
            "available_tabs": sheets_db.get_all_tabs(),
            "total_tabs": len(sheets_db.get_all_tabs())
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
        "endpoints": {
            "slack_events": "/slack/events",
            "health": "/health",
            "sheets_test": "/debug/sheets-test",
            "search": "/debug/search?q=<query>",
            "search_all_tabs": "/debug/search-all-tabs?q=<query>",
            "tabs_info": "/debug/tabs",
            "tab_data": "/debug/tab-data?tab=<tab_name>"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for quick testing"""
    msg = f"✅ /health ping at {datetime.now().isoformat()}"
    print(msg, flush=True)  # visible in Terminal A
    logger.info("🏥 Health check requested")
    return jsonify({
        "status": "healthy",
        "mode": "slack-bolt",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route("/slack/events", methods=["POST"])
def slack_events():
    """Handle all Slack events through Bolt"""
    print(f"🌐 /slack/events called at {datetime.now().isoformat()}", flush=True)
    logger.info("🤖 Slack event received")
    if slack_handler:
        return slack_handler.handle(request)
    else:
        logger.warning("❌ Slack handler not available")
        return jsonify({"error": "Slack integration not configured"}), 500

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
        if not sheets_db.initialized:
            return jsonify({
                "error": "Google Sheets not connected",
                "sheets_connected": False,
                "mode": "slack-bolt"
            }), 500
        
        # Get pipeline data to test connection
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
            "mode": "slack-bolt"
        })
        
    except Exception as e:
        logger.error(f"Error testing Google Sheets: {e}")
        return jsonify({
            "error": f"Google Sheets test failed: {e}",
            "sheets_connected": False,
            "mode": "slack-bolt"
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    logger.info(f"🚀 Starting Diksha Fundraising Bot on port {port}...")
    logger.info(f"📡 Health check: http://localhost:{port}/health")
    logger.info(f"🌐 Root endpoint: http://localhost:{port}/")
    logger.info(f"🤖 Slack events: http://localhost:{port}/slack/events")
    app.run(host='0.0.0.0', port=port, debug=False)
