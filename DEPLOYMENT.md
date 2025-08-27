# 🚀 Railway Deployment Guide

## Quick Setup for Railway

### 1. **Push to GitHub**
```bash
git add .
git commit -m "Add comprehensive Google Sheets integration"
git push origin main
```

### 2. **Set Environment Variables in Railway**

Go to your Railway project dashboard and add these environment variables:

```
MAIN_SHEET_ID=1yzwBj82QVm6pOYctGGC6-N-Q62J9bgdIjAks5Sor7wM
MAIN_SHEET_TAB=Pipeline Tracker
GOOGLE_CREDENTIALS_BASE64=<your-base64-encoded-credentials>
SLACK_BOT_TOKEN=<your-slack-bot-token>
SLACK_SIGNING_SECRET=<your-slack-signing-secret>
```

### 3. **Get Base64 Credentials**
Run this locally to get your base64 credentials:
```bash
python convert_credentials.py
```
Copy the base64 string and paste it as `GOOGLE_CREDENTIALS_BASE64` in Railway.

### 4. **Test the Deployment**

Once deployed, test these endpoints:

- **Health Check**: `https://your-app.railway.app/health`
- **Google Sheets Test**: `https://your-app.railway.app/debug/sheets-test`
- **Search Test**: `https://your-app.railway.app/debug/search?q=Wipro`

### 5. **Slack Commands**

Test these commands in Slack:
- `/pipeline status Wipro Foundation`
- `/pipeline search Wipro`
- `/pipeline assign Wipro Foundation gautam@dikshafoundation.org`

## 🔧 Troubleshooting

### If Google Sheets Connection Fails:
1. Check that `GOOGLE_CREDENTIALS_BASE64` is set correctly
2. Verify the service account has access to the sheet
3. Check Railway logs for detailed error messages

### If Slack Commands Don't Work:
1. Verify `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` are correct
2. Check that the Slack app is installed in your workspace
3. Ensure the bot has the necessary permissions

## 📊 Monitoring

Check Railway logs for:
- ✅ "Successfully connected to sheet"
- ✅ "Retrieved X organizations grouped by Y stages"
- ❌ Any error messages about authentication or sheet access
