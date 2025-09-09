# Migration Guide: Shared Backend Architecture

This guide explains how to migrate from the current architecture to the new shared backend system that allows both Slack and Web UI to use the same core functionality.

## Overview

The new architecture introduces a shared backend package (`backend/`) that contains all core functionality, making it available to both the Slack bot and Web UI through a unified service layer.

## Architecture Changes

### Before (Current)
```
├── slack_bot.py (uses email_generator.py, deepseek_client.py, etc.)
├── app.py (has its own API endpoints)
├── email_generator.py
├── deepseek_client.py
├── google_auth.py
├── sheets_sync.py
├── context_helpers.py
└── web-ui/ (separate frontend)
```

### After (New)
```
├── backend/
│   ├── __init__.py
│   ├── backend_manager.py (centralized initialization)
│   ├── core/
│   │   ├── email_generator.py
│   │   ├── deepseek_client.py
│   │   ├── google_auth.py
│   │   ├── sheets_db.py
│   │   └── cache_manager.py
│   ├── services/
│   │   ├── donor_service.py
│   │   ├── email_service.py
│   │   ├── pipeline_service.py
│   │   └── template_service.py
│   └── context/
│       └── context_helpers.py
├── slack_bot_refactored.py (uses shared backend)
├── app_refactored.py (uses shared backend)
└── web-ui/ (unchanged - works with refactored backend)
```

## Migration Steps

### 1. Update Imports

**Old way:**
```python
from email_generator import EmailGenerator
from deepseek_client import deepseek_client
from sheets_sync import SheetsDB
```

**New way:**
```python
from backend import backend_manager
# Or import specific services
from backend import EmailGenerator, DeepSeekClient, SheetsDB
```

### 2. Initialize Services

**Old way:**
```python
# Initialize each service separately
sheets_db = SheetsDB()
email_generator = EmailGenerator(drive_service=drive_service)
deepseek_client = DeepSeekClient()
```

**New way:**
```python
# Use the centralized backend manager
from backend import backend_manager

# All services are automatically initialized
donor_service = backend_manager.donor_service
email_service = backend_manager.email_service
pipeline_service = backend_manager.pipeline_service
template_service = backend_manager.template_service
context_helpers = backend_manager.context_helpers
```

### 3. Use Service Layer

**Old way:**
```python
# Direct access to core modules
org_data = sheets_db.get_org_by_name(org_name)
subject, body = email_generator.generate_email(template_type, org_data)
```

**New way:**
```python
# Use service layer for business logic
donor = donor_service.get_donor(donor_id)
result = email_service.generate_email(template_type, donor_id)
```

## Key Benefits

### 1. **Unified Interface**
Both Slack and Web UI now use the same backend services, ensuring consistent behavior.

### 2. **Centralized Initialization**
All services are initialized once in `backend_manager.py`, reducing duplication and ensuring proper dependency management.

### 3. **Service Layer**
Business logic is encapsulated in service classes, making the code more maintainable and testable.

### 4. **Better Error Handling**
Centralized error handling and status reporting across all services.

## File Changes

### New Files
- `backend/` - New shared backend package
- `slack_bot_refactored.py` - Refactored Slack bot using shared backend
- `app_refactored.py` - Refactored Flask app using shared backend
- `test_shared_backend.py` - Integration tests

### Files to Keep
- `web-ui/` - No changes needed, works with refactored backend
- Original files can be kept for reference during migration

## Testing the Migration

### 1. Run Integration Tests
```bash
python test_shared_backend.py
```

### 2. Test Slack Bot
```bash
python slack_bot_refactored.py
```

### 3. Test Web UI Backend
```bash
python app_refactored.py
```

### 4. Test Web UI Frontend
```bash
cd web-ui
npm run dev
```

## Environment Variables

No changes to environment variables are required. The same variables are used:
- `GOOGLE_CREDENTIALS_BASE64`
- `ANTHROPIC_API_KEY`
- `DEEPSEEK_API_KEY`
- `SLACK_BOT_TOKEN`
- `SLACK_SIGNING_SECRET`

## API Compatibility

The Web UI API endpoints remain the same:
- `GET /api/pipeline` - Get all donors
- `GET /api/donor/<id>` - Get specific donor
- `POST /api/moveStage` - Update donor stage
- `POST /api/assignDonor` - Assign donor
- `POST /api/notes` - Update notes
- `GET /api/templates` - Get email templates
- `POST /api/draft` - Generate email draft
- `POST /api/send` - Send email

## Slack Commands

Slack commands remain the same:
- `/donoremail intro [OrgName]`
- `/donoremail concept [Org] [Project]`
- `/donoremail meetingrequest [Org] [Date]`
- etc.

## Deployment

### Option 1: Gradual Migration
1. Deploy the new backend alongside the old one
2. Test thoroughly
3. Switch traffic to the new backend
4. Remove old files

### Option 2: Direct Replacement
1. Replace `app.py` with `app_refactored.py`
2. Replace `slack_bot.py` with `slack_bot_refactored.py`
3. Deploy and test

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure the `backend/` package is in your Python path
   - Check that all dependencies are installed

2. **Service Initialization Failures**
   - Check environment variables
   - Review backend manager logs
   - Use `backend_manager.get_status()` to diagnose issues

3. **API Endpoint Errors**
   - Verify that the refactored app is running
   - Check that services are properly initialized
   - Review error logs

### Debug Commands

```python
# Check backend status
from backend import backend_manager
status = backend_manager.get_status()
print(status)

# Test individual services
donors = backend_manager.donor_service.get_all_donors()
templates = backend_manager.email_service.get_available_templates()
```

## Support

If you encounter issues during migration:

1. Check the integration tests: `python test_shared_backend.py`
2. Review the backend status: Visit `/health` endpoint
3. Check logs for specific error messages
4. Verify environment variables are set correctly

The new architecture provides better maintainability, consistency, and extensibility while preserving all existing functionality.
