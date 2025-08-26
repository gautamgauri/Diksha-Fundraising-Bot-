# Diksha Fundraising Bot

**Copyright (c) 2025 Diksha Foundation - All Rights Reserved**

A Slack bot for managing Diksha Foundation's fundraising pipeline with automated donor tracking and communication.

## Features

- **Slack Integration**: Slash commands for pipeline management
- **Health Monitoring**: Built-in health check endpoints
- **Debug Logging**: Comprehensive logging for troubleshooting
- **Railway Ready**: Configured for Railway deployment

## Commands

- `/pipeline status <org>` - Check organization status
- `/pipeline assign <org> <email>` - Assign to team member
- `/pipeline next <org> | <action> | <YYYY-MM-DD>` - Set next action
- `/pipeline stage <org> | <stage>` - Update pipeline stage

## Deployment

### Railway Deployment

1. **Fork/Clone** this repository to your GitHub account
2. **Connect to Railway**:
   - Go to [Railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked repository
3. **Set Environment Variables**:
   - `SLACK_BOT_TOKEN` - Your Slack bot token
   - `SLACK_SIGNING_SECRET` - Your Slack app signing secret
4. **Deploy** - Railway will automatically build and deploy

### Environment Variables

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Test health endpoint
curl http://localhost:3000/health
```

## Endpoints

- `GET /` - Root endpoint with app info
- `GET /health` - Health check with timestamp
- `POST /slack/events` - Slack events webhook

## Slack App Configuration

1. Create a Slack app at https://api.slack.com/apps
2. Add slash commands pointing to your Railway URL
3. Set Event Subscriptions URL to: `https://your-app.railway.app/slack/events`
4. Install the app to your workspace

## Debug Mode

The app includes debug prints that show in Railway logs:
- `✅ /health ping` - When health endpoint is hit
- `🌐 /slack/events called` - When Slack sends events
- `📊 /pipeline hit` - When pipeline commands are used

## Support

For issues or questions, check the Railway logs or contact the development team.
