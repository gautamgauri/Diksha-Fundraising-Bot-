# DeepSeek Integration for Diksha Foundation Fundraising Bot

## Overview

The DeepSeek integration adds natural language processing capabilities to the Diksha Foundation fundraising bot, enabling users to have conversational interactions about fundraising strategy, donor management, and email generation.

## Features

### 🤖 Natural Language Chat
- **Context-aware responses**: The bot understands fundraising context and provides relevant information
- **Donor database integration**: References actual donor data when answering questions
- **Template awareness**: Knows about available email templates and can suggest appropriate ones
- **Pipeline insights**: Provides real-time pipeline status and statistics

### 📧 Enhanced Email Assistance
- **Smart email generation**: Understands natural language requests for email creation
- **Template recommendations**: Suggests appropriate templates based on context
- **Organization matching**: Automatically finds relevant organizations mentioned in queries

### 🔍 Intelligent Query Processing
- **Keyword detection**: Recognizes fundraising-related terms and provides helpful guidance
- **Command suggestions**: Offers relevant slash commands for specific tasks
- **Context gathering**: Collects relevant donor and template information for better responses

## Configuration

### Environment Variables

Set the following environment variable to enable DeepSeek:

```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key-here"
```

### API Configuration

The integration uses the DeepSeek Chat API with the following settings:
- **Model**: `deepseek-chat`
- **Temperature**: 0.7 (balanced creativity and consistency)
- **Max Tokens**: 1000
- **Timeout**: 30 seconds

## Usage

### Natural Language Queries

Users can now ask questions in natural language:

```
@bot How do I generate an intro email for Wipro Foundation?
@bot What's the status of Tata Trust in our pipeline?
@bot Show me available email templates
@bot Tell me about our fundraising strategy
```

### Direct Messages

Users can also send direct messages to the bot for private conversations about fundraising topics.

### Context-Aware Responses

The bot automatically:
1. **Analyzes queries** for fundraising-related keywords
2. **Gathers relevant context** from donor database and templates
3. **Provides personalized responses** with actual data
4. **Suggests appropriate commands** for specific actions

## API Endpoints

### Health Check
```
GET /health
```
Includes DeepSeek API status in the health check response.

### DeepSeek Test
```
POST /debug/test-deepseek
```
Test the DeepSeek integration with custom messages and context.

**Request Body:**
```json
{
  "message": "Your test message here",
  "context": {
    "user_id": "user123",
    "channel_id": "channel456"
  }
}
```

## Integration Points

### Slack Events
- **App Mentions**: Enhanced with natural language processing
- **Direct Messages**: Full conversational support
- **Context Gathering**: Automatic donor and template data collection

### Helper Functions
- `get_relevant_donor_context()`: Extracts donor information from queries
- `get_template_context()`: Provides available email template information
- `get_pipeline_insights()`: Gathers current pipeline statistics

### Natural Language Handlers
- `handle_natural_language_query_with_context()`: Processes queries with real data
- `handle_natural_language_query()`: Fallback handler for general queries

## Error Handling

### Graceful Degradation
- If DeepSeek API is unavailable, falls back to command-based responses
- Maintains functionality even when AI features are disabled
- Provides helpful error messages and alternative suggestions

### API Error Handling
- Network timeout protection (30 seconds)
- HTTP status code validation
- Comprehensive error logging

## Testing

### Test Script
Run the included test script to verify integration:

```bash
python test_deepseek.py
```

### Manual Testing
1. Set `DEEPSEEK_API_KEY` environment variable
2. Start the Flask application
3. Test natural language queries in Slack
4. Verify health endpoint shows DeepSeek status

## Monitoring

### Health Checks
- DeepSeek API connectivity status
- Response time monitoring
- Error rate tracking

### Logging
- API call success/failure logging
- Response quality monitoring
- Context gathering statistics

## Security

### API Key Protection
- Environment variable storage
- No hardcoded credentials
- Secure API communication

### Input Validation
- Message length limits
- Context data sanitization
- Rate limiting considerations

## Performance

### Optimization Features
- **Context caching**: Reuses gathered context for related queries
- **Smart fallbacks**: Reduces API calls for simple queries
- **Efficient data gathering**: Limits context data to relevant information

### Resource Management
- **Timeout handling**: Prevents hanging API calls
- **Memory efficiency**: Limits context data size
- **Connection pooling**: Reuses HTTP connections

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   - Error: "DEEPSEEK_API_KEY not set"
   - Solution: Set the environment variable

2. **API Connection Failed**
   - Error: "DeepSeek API call failed"
   - Solution: Check network connectivity and API key validity

3. **Context Gathering Errors**
   - Error: "Error getting donor context"
   - Solution: Verify Google Sheets connection

### Debug Commands

```bash
# Check DeepSeek status
curl http://localhost:3000/health

# Test DeepSeek API
curl -X POST http://localhost:3000/debug/test-deepseek \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

## Future Enhancements

### Planned Features
- **Conversation memory**: Remember previous interactions
- **Advanced context**: Include more donor relationship data
- **Multi-language support**: Handle queries in multiple languages
- **Learning capabilities**: Improve responses based on user feedback

### Integration Opportunities
- **Analytics dashboard**: Track conversation quality and usage
- **Feedback system**: Collect user satisfaction ratings
- **A/B testing**: Compare different response strategies

## Support

For issues with the DeepSeek integration:

1. Check the application logs for error details
2. Verify the API key is correctly set
3. Test the `/debug/test-deepseek` endpoint
4. Review the health check for component status

## Changelog

### v1.0.0 (Current)
- Initial DeepSeek integration
- Natural language processing for fundraising queries
- Context-aware responses with donor data
- Enhanced Slack event handling
- Comprehensive error handling and fallbacks

