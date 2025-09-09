# 🚀 Railway Deployment Guide - Shared Backend Architecture

## 📋 Prerequisites

- ✅ GitHub repository pushed with shared backend architecture
- ✅ Railway account connected to GitHub
- ✅ Environment variables prepared

## 🔧 Railway Deployment Steps

### 1. Connect Repository to Railway

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your repository**: `Diksha-Fundraising-Bot-`
5. **Select the main branch**

### 2. Configure Environment Variables

In Railway dashboard, go to your project → **Variables** tab and add:

#### 🔑 **Required Environment Variables**

```bash
# Google API Credentials (Base64 encoded service account JSON)
GOOGLE_CREDENTIALS_BASE64=eyJ0eXBlIjoic2VydmljZV9hY2NvdW50Iiwi...

# AI API Keys
ANTHROPIC_API_KEY=sk-ant-api03-...
DEEPSEEK_API_KEY=sk-...

# Slack Bot Credentials
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...

# Optional Configuration
CLAUDE_MODEL=claude-sonnet-4-20250514
MAX_REQUEST_SIZE=1000000
API_TIMEOUT=30
DEPLOYMENT_MODE=production
```

#### 📝 **How to Get Google Credentials**

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create/Select Project**
3. **Enable APIs**:
   - Google Sheets API
   - Google Drive API
4. **Create Service Account**:
   - Go to IAM & Admin → Service Accounts
   - Create new service account
   - Download JSON key file
5. **Encode to Base64**:
   ```bash
   # On Windows (PowerShell)
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("path/to/service-account.json"))
   
   # On Mac/Linux
   base64 -i service-account.json
   ```

### 3. Configure Railway Settings

#### 🐍 **Python Configuration**

Railway will auto-detect Python, but ensure:

1. **Runtime**: Python 3.11+
2. **Start Command**: `python app_refactored.py`
3. **Port**: Railway will set `PORT` environment variable automatically

#### 📦 **Dependencies**

Railway will automatically install from `requirements.txt`:

```txt
flask==2.3.3
slack-bolt==1.18.1
google-api-python-client==2.108.0
google-auth==2.23.4
anthropic==0.7.8
requests==2.31.0
python-dotenv==1.0.0
```

### 4. Deploy and Monitor

#### 🚀 **Deployment Process**

1. **Railway will automatically deploy** when you push to main branch
2. **Monitor deployment logs** in Railway dashboard
3. **Check for any errors** in the build process

#### 📊 **Expected Logs**

```
🚀 Diksha Foundation Fundraising Bot Starting...
============================================================
🔧 Backend Status: ✅ Initialized
📊 Services Available:
   ✅ Sheets Db
   ✅ Email Generator
   ✅ Deepseek Client
   ✅ Donor Service
   ✅ Email Service
   ✅ Pipeline Service
   ✅ Template Service
   ✅ Context Helpers

🌐 Server: Starting on port 3000
🔧 Debug Mode: ❌ Disabled

🔑 Environment Variables:
   GOOGLE_CREDENTIALS_BASE64: ✅ Set
   ANTHROPIC_API_KEY: ✅ Set
   DEEPSEEK_API_KEY: ✅ Set
   SLACK_BOT_TOKEN: ✅ Set
   SLACK_SIGNING_SECRET: ✅ Set

📋 Available Endpoints:
   • /health - Health check with detailed status
   • /api/pipeline - Get all donors
   • /api/donor/<id> - Get specific donor
   • /api/templates - Get email templates
   • /api/draft - Generate email draft
   • /api/send - Send email
   • /slack/events - Slack event handler
   • /slack/commands - Slack command handler

🚀 **New Donor Email Commands Available!**
   • /donoremail intro [OrgName] - First introduction
   • /donoremail concept [Org] [Project] - Concept pitch
   • /donoremail meetingrequest [Org] [Date] - Meeting request
   • /donoremail proposalcover [Org] [Project] - Proposal cover
   • /donoremail help - See all available commands

💡 **Key Features:**
   • Shared backend services
   • AI-enhanced emails with Claude
   • Natural language chat with DeepSeek
   • Google Drive profile integration
   • Fundraising workflow stages
   • Smart fallback system
   • Enhanced error handling
   • Graceful degradation

============================================================
✅ Backend initialized successfully. Server starting normally.
============================================================
```

### 5. Configure Slack App

#### 🔗 **Update Slack App Settings**

1. **Go to Slack API Dashboard**: https://api.slack.com/apps
2. **Select your app**
3. **Update Event Subscriptions**:
   - Request URL: `https://your-railway-app.railway.app/slack/events`
   - Subscribe to: `app_mention`, `message.channels`
4. **Update Slash Commands**:
   - Command: `/donoremail`
   - Request URL: `https://your-railway-app.railway.app/slack/commands`
5. **Update OAuth & Permissions**:
   - Scopes: `app_mentions:read`, `channels:history`, `chat:write`, `commands`

### 6. Test Deployment

#### 🧪 **Health Check**

```bash
curl https://your-railway-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "mode": "shared-backend",
  "timestamp": "2024-12-19T...",
  "version": "2.0.0",
  "backend_status": {
    "initialized": true,
    "services": {
      "sheets_db": {"available": true, "initialized": true},
      "email_generator": {"available": true, "mode": "claude"},
      "deepseek_client": {"available": true, "initialized": true}
    }
  }
}
```

#### 📊 **Test API Endpoints**

```bash
# Test pipeline endpoint
curl https://your-railway-app.railway.app/api/pipeline

# Test templates endpoint
curl https://your-railway-app.railway.app/api/templates
```

#### 💬 **Test Slack Integration**

1. **Invite bot to channel**: `/invite @your-bot-name`
2. **Test slash command**: `/donoremail help`
3. **Test natural language**: `@your-bot-name generate an intro email for Wipro Foundation`

## 🛠️ Troubleshooting

### ❌ **Common Issues**

#### **1. Google API Errors**
```
❌ Google API clients not available
```
**Solution**: Check `GOOGLE_CREDENTIALS_BASE64` is properly encoded

#### **2. Slack Connection Issues**
```
❌ Slack bot initialization failed
```
**Solution**: Verify `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET`

#### **3. AI API Errors**
```
❌ DeepSeek client not initialized
```
**Solution**: Check `DEEPSEEK_API_KEY` and `ANTHROPIC_API_KEY`

#### **4. Port Issues**
```
❌ Port already in use
```
**Solution**: Railway handles ports automatically, check if `PORT` env var is set

### 🔍 **Debug Commands**

```bash
# Check environment variables
railway variables

# View logs
railway logs

# Connect to shell
railway shell
```

## 📈 **Monitoring & Maintenance**

### 📊 **Health Monitoring**

- **Health Endpoint**: `/health` - Comprehensive status check
- **Railway Metrics**: Monitor CPU, memory, and response times
- **Log Monitoring**: Check Railway logs for errors

### 🔄 **Updates & Deployments**

- **Automatic Deployments**: Push to main branch triggers deployment
- **Manual Deployments**: Use Railway dashboard
- **Rollback**: Use Railway deployment history

### 🛡️ **Security**

- **Environment Variables**: All secrets stored securely in Railway
- **HTTPS**: Railway provides automatic SSL certificates
- **Rate Limiting**: Built into the application
- **Input Validation**: All endpoints validate input

## 🎯 **Success Criteria**

### ✅ **Deployment Successful When**

1. **Health Check Passes**: `/health` returns status "healthy"
2. **All Services Initialized**: Backend status shows all services available
3. **Slack Bot Responds**: `/donoremail help` works in Slack
4. **API Endpoints Work**: `/api/pipeline` returns donor data
5. **Google Integration**: Can access Sheets and Drive
6. **AI Features Work**: Email generation and natural language processing

### 🚀 **Next Steps After Deployment**

1. **Test all Slack commands**
2. **Verify Web UI endpoints**
3. **Test email generation**
4. **Monitor performance**
5. **Set up monitoring alerts**

## 📞 **Support**

- **Railway Documentation**: https://docs.railway.app/
- **Slack API Documentation**: https://api.slack.com/
- **Google API Documentation**: https://developers.google.com/sheets/api

---

**🎉 Congratulations! Your shared backend architecture is now deployed and ready for production use!**
