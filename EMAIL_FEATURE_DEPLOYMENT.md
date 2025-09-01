# 📧 Email Generation Feature - Deployment Guide

## 🚀 What's New

The Diksha Foundation Fundraising Bot now includes **custom email generation** based on your Google Drive templates and donor data from Google Sheets.

## ✨ New Features

### 1. Slack Command: `/pipeline email`
- **Usage**: `/pipeline email <organization> | <template> | [mode]`
- **Example**: `/pipeline email Wipro Foundation | identification | claude`
- **What it does**: Generates customized emails using donor data and stage-appropriate templates
- **Modes**: 
  - `claude` - AI-enhanced emails using Claude API (default)
  - `template` - Basic template system

### 2. Available Templates
- **`identification`** - Initial outreach and introduction
- **`engagement`** - Relationship building and deeper discussion  
- **`proposal`** - Formal proposal submission
- **`followup`** - Follow-up messages
- **`celebration`** - Grant secured celebrations

### 3. API Endpoints
- **`GET /debug/templates`** - List available templates and modes
- **`POST /debug/generate-email`** - Generate custom email via API
- **`GET /debug/test-claude`** - Test Claude API integration

### 4. Mode Management
- **`/pipeline mode [claude|template]`** - Set email generation mode
- **Automatic fallback** - If Claude fails, falls back to template system

## 🔧 Deployment Steps

### Step 1: Deploy to Railway
```bash
# Commit your changes
git add .
git commit -m "Add email generation feature with Claude AI integration"
git push origin main

# Railway will automatically deploy
```

### Step 2: Configure Claude API
1. **Get Claude API Key**: 
   - Visit [Anthropic Console](https://console.anthropic.com/)
   - Create API key for Claude 3 Sonnet
   
2. **Set Environment Variable in Railway**:
   - Go to your Railway project dashboard
   - Add environment variable: `ANTHROPIC_API_KEY`
   - Value: Your Claude API key

3. **Verify Configuration**:
   - Check Railway logs for "✅ Claude API key configured"
   - Test endpoint: `https://your-app.railway.app/debug/test-claude`

### Step 3: Verify Deployment
1. Check Railway dashboard for successful deployment
2. Test health endpoint: `https://your-app.railway.app/health`
3. Test templates endpoint: `https://your-app.railway.app/debug/templates`
4. Test Claude integration: `https://your-app.railway.app/debug/test-claude`

### Step 4: Test in Slack
1. Go to your Slack workspace
2. Test Claude mode: `/pipeline email Wipro Foundation | identification | claude`
3. Test template mode: `/pipeline email Wipro Foundation | identification | template`
4. Compare the quality difference!

## 🧪 Testing

### Local Testing
```bash
# Run the test suite
python test_email_generation.py

# Test individual endpoints
curl http://localhost:3000/debug/templates
curl -X POST http://localhost:3000/debug/generate-email \
  -H "Content-Type: application/json" \
  -d '{"org":"Wipro Foundation","template":"identification"}'
```

### Production Testing
```bash
# Test templates endpoint
curl https://your-app.railway.app/debug/templates

# Test email generation
curl -X POST https://your-app.railway.app/debug/generate-email \
  -H "Content-Type: application/json" \
  -d '{"org":"Wipro Foundation","template":"identification"}'
```

## 📊 How It Works

### 1. Template-Based Enhancement (NEW!)
- **Base Template First**: System starts with your proven email templates
- **AI Enhancement**: Claude API enhances language, personalization, and engagement
- **Quality Validation**: Checks enhancement quality and similarity to base
- **Smart Fallback**: If enhancement is insufficient, applies manual improvements
- **Comparison Metrics**: Shows improvement percentage and length changes

### 2. Template Selection
- User specifies template type (e.g., `identification`)
- System loads your existing base template
- AI enhances while maintaining core structure and key points

### 3. Data Integration
- Pulls organization data from Google Sheets
- Uses fields like: organization name, contact person, sector, geography
- Incorporates estimated grant size for budget calculations

### 4. AI Enhancement Process
- **Context Analysis**: Analyzes donor data and sector alignment
- **Language Enhancement**: Makes content more engaging and professional
- **Personalization**: Adds organization-specific references and achievements
- **Stage Optimization**: Applies stage-specific improvements
- **Quality Control**: Validates enhancement quality and similarity

### 5. Output
- Generates enhanced subject line and body text
- Provides recipient information and donor context
- Shows enhancement metrics and comparison data
- Suggests next steps for review and sending

## 🎯 Use Cases

### Initial Outreach
```
/pipeline email Tata Trust | identification
```
- Generates introduction email
- Includes Diksha Foundation overview
- Requests initial meeting

### Relationship Building
```
/pipeline email HDFC Bank | engagement
```
- Deepens existing relationship
- Highlights alignment opportunities
- Requests detailed discussion

### Proposal Submission
```
/pipeline email Wipro Foundation | proposal
```
- Formal proposal format
- Includes budget breakdown
- Requests presentation meeting

## 🔍 Troubleshooting

### Common Issues

1. **"Template type not found"**
   - Use exact template names: identification, engagement, proposal, followup, celebration
   - Check spelling and case sensitivity

2. **"Organization not found"**
   - Verify organization name in Google Sheets
   - Use `/pipeline search` to find exact names

3. **"Template generation failed"**
   - Check Google Sheets connection
   - Verify organization data is complete
   - Check Railway logs for detailed errors

### Debug Commands

```bash
# Check available templates
/debug/templates

# Test email generation
/debug/generate-email

# Verify organization data
/pipeline status <organization>
```

## 🚀 Next Steps

### Immediate Actions
1. ✅ Deploy to Railway
2. ✅ Test basic functionality
3. ✅ Verify Slack integration

### Future Enhancements
1. **Template Management**: Add/edit templates via Slack
2. **Email History**: Track generated emails
3. **Auto-send**: Direct email sending capability
4. **Template Customization**: User-defined template fields
5. **Multi-language**: Support for Hindi and other languages

## 📞 Support

If you encounter issues:
1. Check Railway logs for error messages
2. Verify Google Sheets connection
3. Test individual endpoints
4. Review organization data completeness

---

**🎉 Your fundraising bot now generates professional, customized emails automatically!**
