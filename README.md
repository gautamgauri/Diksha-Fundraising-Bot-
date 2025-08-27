# Diksha Fundraising Bot

A Slack bot for managing Diksha Foundation's fundraising pipeline with live Google Sheets integration.

## Features

- **Live Google Sheets Integration**: Connects to `Diksha_Donor_Pipeline_2025_v2` sheet
- **Slack Commands**: Manage pipeline directly from Slack
- **Real-time Updates**: All changes sync immediately to Google Sheets
- **Search Functionality**: Find organizations quickly
- **Health Monitoring**: Built-in health checks and debugging endpoints

## Slack Commands

### `/pipeline status <organization>`
Get the current status of an organization in the pipeline.

**Example:**
```
/pipeline status Wipro Foundation
```

### `/pipeline assign <organization> <email>`
Assign an organization to a team member.

**Example:**
```
/pipeline assign Wipro Foundation gautam@dikshafoundation.org
```

### `/pipeline next <organization> | <action> | <YYYY-MM-DD>`
Set the next action and due date for an organization.

**Example:**
```
/pipeline next Wipro Foundation | Send proposal | 2025-01-15
```

### `/pipeline stage <organization> | <stage>`
Update the pipeline stage for an organization.

**Example:**
```
/pipeline stage Wipro Foundation | Proposal Sent
```

### `/pipeline search <query>`
Search for organizations by name.

**Example:**
```
/pipeline search Wipro
```

## Google Sheets Structure

The bot expects the following column structure in your Google Sheet:

| Column | Field | Description |
|--------|-------|-------------|
| A | Organization Name | Name of the organization |
| B | Contact Person | Primary contact at the organization |
| C | Email | Organization contact email |
| D | Phone | Organization phone number |
| E | Current Stage | Current stage in pipeline |
| F | Previous Stage | Previous stage in pipeline |
| G | Sector Tags | Industry/sector tags |
| H | Geography | Geographic location |
| I | Assigned To | Team member assigned |
| J | Next Action | Next action to take |
| K | Next Action Date | Due date for next action |
| L | Notes | Additional notes |
| M | Last Updated | Timestamp of last update |

## Setup

### 1. Google Sheets Setup

1. Create a Google Service Account
2. Download the credentials JSON file
3. Share your Google Sheet with the service account email
4. Convert credentials to base64:
   ```bash
   python convert_credentials.py
   ```
5. Copy the base64 string to use as environment variable

### 2. Environment Variables

Set these environment variables in Railway:

```
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_SIGNING_SECRET=your_slack_signing_secret
GOOGLE_CREDENTIALS_BASE64=your_base64_encoded_credentials
MAIN_SHEET_ID=your_google_sheet_id
MAIN_SHEET_TAB=Pipeline Tracker
```

### 3. Deploy to Railway

The app is configured to deploy automatically to Railway. The credentials file will be included in the deployment.

## Testing

### Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Convert credentials to base64:
```bash
python convert_credentials.py
```

3. Test Google Sheets connection:
```bash
python test_comprehensive.py
```

4. Run the app locally:
```bash
python app.py
```

### API Endpoints

- `GET /` - App status and Google Sheets connection info
- `GET /health` - Health check
- `GET /debug/sheets-test` - Test Google Sheets connection
- `GET /debug/search?q=<query>` - Search organizations via API
- `GET /debug/status?org=<organization>` - Get organization status
- `POST /debug/assign` - Assign organization (JSON body)
- `POST /debug/next` - Set next action (JSON body)
- `POST /debug/stage` - Update stage (JSON body)

## Troubleshooting

### Google Sheets Connection Issues

1. Check that the `GOOGLE_CREDENTIALS_BASE64` environment variable is set correctly
2. Verify the service account has access to the Google Sheet
3. Ensure the `MAIN_SHEET_ID` and `MAIN_SHEET_TAB` are correct
4. Check that the sheet has the expected column structure

### Slack Integration Issues

1. Verify Slack environment variables are set correctly
2. Check that the Slack app is properly configured with the correct permissions
3. Ensure the Slack app is installed in your workspace

### Common Error Messages

- **"Organization not found"**: The organization name doesn't match exactly. Use `/pipeline search` to find the correct name.
- **"Google Sheets not connected"**: Check credentials file and service account permissions.
- **"Failed to update"**: The organization may not exist or there may be a permissions issue.

## Development

### Adding New Features

1. The `SheetsDB` class in `app/modules/sheets_sync.py` handles all Google Sheets operations
2. Google authentication is handled in `app/modules/google_auth.py`
3. Slack commands are defined in the `@slack_app.command` decorators
4. Debug endpoints provide API access for testing

### Logging

The app uses Python's logging module. Check Railway logs for debugging information.

## Security Notes

- Google Sheets credentials are stored as base64 environment variables (not in files)
- All API endpoints include proper error handling
- Slack commands validate input before processing
- Credentials are automatically excluded from version control
