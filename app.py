from flask import Flask, request, jsonify
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Slack Bolt for easier Slack integration
from slack_bolt import App as SlackApp
from slack_bolt.adapter.flask import SlackRequestHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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
            respond("🎯 *Diksha Fundraising Bot*\n\nUsage:\n• `/pipeline status <org>` - Check organization status\n• `/pipeline assign <org> <email>` - Assign to team member\n• `/pipeline next <org> | <action> | <YYYY-MM-DD>` - Set next action\n• `/pipeline stage <org> | <stage>` - Update pipeline stage\n\n*Note: Google Sheets integration disabled for testing*")
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
                respond(f"🏢 *{org_query}*\n📊 Stage: Identified\n👤 Assigned: team@dikshafoundation.org\n📅 Next: Initial outreach on 2025-07-15\n\n*Note: This is test data - Google Sheets integration disabled*")
                return

            if action == "assign":
                # /pipeline assign <org> <email>
                if len(args) < 2:
                    respond("Usage: /pipeline assign <organization> <email>")
                    return
                org_query = " ".join(args[:-1])
                email = args[-1]
                respond(f"✅ Assigned *{org_query}* to {email}\n\n*Note: This is test data - Google Sheets integration disabled*")
                return

            if action == "next":
                # /pipeline next <org> | <action> | <YYYY-MM-DD>
                rest = " ".join(args)
                parts2 = [p.strip() for p in rest.split("|")]
                if len(parts2) < 3:
                    respond("Usage: /pipeline next <org> | <action> | <YYYY-MM-DD>")
                    return
                org_query, action_text, due_date = parts2[0], parts2[1], parts2[2]
                respond(f"📅 Updated next action for *{org_query}*:\n• Action: {action_text}\n• Due: {due_date}\n\n*Note: This is test data - Google Sheets integration disabled*")
                return

            if action == "stage":
                # /pipeline stage <org> | <stage>
                rest = " ".join(args)
                parts2 = [p.strip() for p in rest.split("|")]
                if len(parts2) < 2:
                    respond("Usage: /pipeline stage <org> | <stage>")
                    return
                org_query, new_stage = parts2[0], parts2[1]
                respond(f"🔄 Stage updated for *{org_query}*:\n• From: Identified\n• To: {new_stage}\n\n*Note: This is test data - Google Sheets integration disabled*")
                return

            respond("Unknown action. Use one of: status, assign, next, stage")
        except Exception as e:
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
    return jsonify({
        "app": "Diksha Fundraising Automation", 
        "status": "running", 
        "mode": "slack-bolt",
        "endpoints": {
            "slack_events": "/slack/events",
            "health": "/health"
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
    return jsonify({
        "organization": org,
        "stage": "Identified (test mode)",
        "assigned_to": "team@dikshafoundation.org",
        "next_action": "Initial outreach",
        "next_action_date": "2025-07-15",
        "mode": "slack-bolt"
    })

@app.route('/debug/assign', methods=['POST'])
def debug_assign():
    data = request.get_json(silent=True) or {}
    org = (data.get('org') or '').strip()
    email = (data.get('email') or '').strip()
    if not org or not email:
        return jsonify({"error": "Body must include 'org' and 'email'"}), 400
    return jsonify({"ok": True, "organization": org, "assigned_to": email, "mode": "slack-bolt"})

@app.route('/debug/next', methods=['POST'])
def debug_next():
    data = request.get_json(silent=True) or {}
    org = (data.get('org') or '').strip()
    action_text = (data.get('action') or '').strip()
    due_date = (data.get('date') or '').strip()
    if not org or not action_text or not due_date:
        return jsonify({"error": "Body must include 'org', 'action', 'date' (YYYY-MM-DD)"}), 400
    return jsonify({"ok": True, "organization": org, "next_action": action_text, "next_action_date": due_date, "mode": "slack-bolt"})

@app.route('/debug/stage', methods=['POST'])
def debug_stage():
    data = request.get_json(silent=True) or {}
    org = (data.get('org') or '').strip()
    new_stage = (data.get('stage') or '').strip()
    if not org or not new_stage:
        return jsonify({"error": "Body must include 'org' and 'stage'"}), 400
    return jsonify({"ok": True, "organization": org, "from": "Identified", "to": new_stage, "mode": "slack-bolt"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    logger.info(f"🚀 Starting Diksha Fundraising Bot on port {port}...")
    logger.info(f"📡 Health check: http://localhost:{port}/health")
    logger.info(f"🌐 Root endpoint: http://localhost:{port}/")
    logger.info(f"🤖 Slack events: http://localhost:{port}/slack/events")
    app.run(host='0.0.0.0', port=port, debug=False)
