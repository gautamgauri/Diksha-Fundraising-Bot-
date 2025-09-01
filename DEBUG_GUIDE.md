# Diksha Foundation Fundraising Bot - Debug Guide

## 🚨 Critical Issues Identified & Fixed

### 1. **Missing Dependencies** ✅ RESOLVED
**Problem:** The app requires `slack-bolt`, Google API libraries, and custom modules that may not be present.

**Solution Applied:**
- Added comprehensive import guards with try-catch blocks
- Graceful degradation when optional modules are missing
- Clear error messages for missing critical modules

**Code Example:**
```python
try:
    from sheets_sync import SheetsDB
    from email_generator import EmailGenerator
    logger.info("✅ Required modules imported successfully")
except ImportError as e:
    logger.error(f"❌ Missing required module: {e}")
    logger.error("Please ensure sheets_sync.py and email_generator.py exist in the same directory")
    sys.exit(1)

# Optional import for cache manager
try:
    from cache_manager import cache_manager
    logger.info("✅ Cache manager imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Cache manager not available: {e}")
    cache_manager = None
```

### 2. **Environment Variables** ✅ VALIDATED
**Problem:** Missing required keys like `SLACK_BOT_TOKEN`, `ANTHROPIC_API_KEY`, `GOOGLE_CREDENTIALS_BASE64`.

**Solution Applied:**
- Enhanced health check endpoint shows environment variable status
- Startup validation checks all required variables
- Clear indication of what's missing and what's configured

**Required Environment Variables:**
```bash
# Required for basic functionality
GOOGLE_CREDENTIALS_BASE64=base64_encoded_credentials
ANTHROPIC_API_KEY=your_claude_api_key

# Optional for Slack integration
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_SIGNING_SECRET=your_slack_signing_secret

# Optional for custom port
PORT=3000
```

### 3. **Error Handling** ✅ ENHANCED
**Problem:** Several routes lacked proper exception handling and input validation.

**Solution Applied:**
- Added comprehensive error handling to all command handlers
- Proper HTTP status codes (503 for service unavailable, 500 for server errors)
- Input validation and sanitization for all user inputs
- Graceful degradation when services are unavailable

## 🔧 High Priority Issues Fixed

### 1. **Slack Command Parser Safety** ✅ IMPLEMENTED
**Problem:** The `handle_donoremail_command` function assumed `text.split()` would always have elements, causing IndexError.

**Solution Applied:**
```python
def handle_donoremail_command(text: str, user_id: str, channel_id: str):
    try:
        if not text or not text.strip():
            return jsonify({
                "response_type": "ephemeral",
                "text": get_donoremail_help()
            })
        
        # Parse command parts with safety checks
        parts = [part.strip() for part in text.split() if part.strip()]
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
        
        # ... rest of the function with proper error handling
```

### 2. **Database Initialization Fallback** ✅ IMPLEMENTED
**Problem:** No fallback if Google Sheets connection fails during startup.

**Solution Applied:**
```python
# Initialize Google Sheets database (ONCE) with fallback
try:
    sheets_db = SheetsDB()
    if not sheets_db.initialized:
        logger.warning("⚠️ Google Sheets connection failed during initialization")
        sheets_db = None
    else:
        logger.info("✅ Google Sheets database initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Google Sheets database: {e}")
    logger.warning("⚠️ Application will run with limited functionality")
    sheets_db = None
```

### 3. **Route Error Responses** ✅ IMPLEMENTED
**Problem:** Many endpoints returned errors without proper HTTP status codes.

**Solution Applied:**
- Added proper HTTP status codes (503 for service unavailable)
- Consistent error response format
- Detailed error messages with status codes
- Graceful handling of missing services

## 🚀 Quick Debug Steps

### Step 1: Check Basic Connectivity
```bash
curl http://localhost:3000/health
```

**Expected Response:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "components": {
    "google_sheets": "connected|not_connected",
    "slack_bot": "ready|not_configured",
    "email_generator": "ready|not_available"
  },
  "environment": {
    "google_credentials": "configured|missing",
    "anthropic_api_key": "configured|missing",
    "slack_credentials": "configured|missing"
  }
}
```

### Step 2: Test Google Sheets Connection
```bash
curl http://localhost:3000/debug/sheets-test
```

**Success Response:**
```json
{
  "sheets_connected": true,
  "sheet_id": "your_sheet_id",
  "sample_organizations": ["Org1", "Org2"],
  "total_organizations": 25,
  "status_code": 200
}
```

**Failure Response:**
```json
{
  "error": "Google Sheets not connected",
  "sheets_connected": false,
  "status_code": 503
}
```

### Step 3: Check Module Availability
Look for these log messages during startup:
- ✅ Required modules imported successfully
- ✅ Google Sheets database initialized successfully
- ✅ Google Drive service configured for donor profiles
- ✅ Slack app initialized with credentials

### Step 4: Verify Environment Variables
Check if these are set in your environment:
```bash
echo $GOOGLE_CREDENTIALS_BASE64
echo $ANTHROPIC_API_KEY
echo $SLACK_BOT_TOKEN
echo $SLACK_SIGNING_SECRET
```

## 🐛 Most Likely Causes of Failure

### 1. **Import Errors on Startup**
**Symptoms:** Application crashes immediately with ImportError
**Causes:** Missing `sheets_sync.py`, `email_generator.py`, or `cache_manager.py`
**Solution:** Ensure all required modules exist in the same directory

### 2. **Google Sheets Connection Failures**
**Symptoms:** Health check shows `google_sheets: "not_connected"`
**Causes:** Invalid credentials, network issues, or missing permissions
**Solution:** Verify `GOOGLE_CREDENTIALS_BASE64` and check Google Sheets API access

### 3. **Slack Verification Failures**
**Symptoms:** Slack commands return errors or don't work
**Causes:** Wrong signing secret, invalid bot token, or misconfigured Slack app
**Solution:** Verify `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` in Slack app settings

### 4. **Runtime Errors in Command Parsing**
**Symptoms:** Slack commands fail with IndexError or similar
**Causes:** Malformed input or edge cases in command parsing
**Solution:** All command handlers now have comprehensive error handling

## 🔍 Debugging Commands

### Health Check with Detailed Status
```bash
curl http://localhost:3000/health
```

### Test Google Sheets Connection
```bash
curl http://localhost:3000/debug/sheets-test
```

### Test Email Generation
```bash
curl -X POST http://localhost:3000/debug/generate-email \
  -H "Content-Type: application/json" \
  -d '{"org": "Test Org", "template": "identification", "mode": "template"}'
```

### Test Claude Integration
```bash
curl http://localhost:3000/debug/test-claude
```

### Check Available Templates
```bash
curl http://localhost:3000/debug/templates
```

## 📋 Startup Validation

The application now includes comprehensive startup validation:

1. **Component Health Check** - Validates all major components
2. **Environment Variable Check** - Shows what's configured and what's missing
3. **Service Availability** - Checks Google Sheets, Drive, Slack, and AI services
4. **Graceful Degradation** - Application continues with limited functionality if non-critical services fail

## 🚨 Error Response Codes

- **200** - Success
- **400** - Bad Request (invalid input)
- **404** - Not Found (organization not found)
- **500** - Internal Server Error
- **503** - Service Unavailable (Google Sheets, Slack not configured)

## 💡 Troubleshooting Tips

### If Google Sheets Won't Connect:
1. Verify `GOOGLE_CREDENTIALS_BASE64` is set correctly
2. Check if the service account has access to the spreadsheet
3. Ensure the spreadsheet ID is correct in `sheets_sync.py`

### If Slack Commands Don't Work:
1. Verify `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET`
2. Check if the Slack app is properly configured
3. Ensure the bot is added to the workspace

### If Email Generation Fails:
1. Check if `ANTHROPIC_API_KEY` is set for AI enhancement
2. Verify the email generator module is working
3. Check logs for specific error messages

### If the App Won't Start:
1. Check for missing Python modules
2. Verify all required files exist in the directory
3. Check Python version compatibility

## 🎯 Next Steps for Production

1. **Set all required environment variables**
2. **Test the health endpoint** to verify all components
3. **Test Google Sheets connection** with `/debug/sheets-test`
4. **Test Slack integration** with a simple command
5. **Monitor logs** for any remaining issues

## 📞 Support

If you continue to experience issues:
1. Check the application logs for specific error messages
2. Use the `/health` endpoint to identify which components are failing
3. Verify all environment variables are set correctly
4. Test individual endpoints to isolate the problem

The application is now much more robust with comprehensive error handling, graceful degradation, and detailed debugging information!
