# Donor Profile Generator Improvements

## 🚀 Enhanced Multi-Service Search System

### **Smart Quota Management & Service Fallback**

The donor profile generator now includes an intelligent search system that automatically manages free tier quotas across multiple search services:

#### **Priority-based Service Rotation:**
1. **🔥 ScaleSerp** (1000 free/month) - Best free tier, highest priority
2. **⚡ ValueSerp** (1000 free/month) - Primary backup
3. **🔍 Zenserp** (1000 free/month) - Secondary backup
4. **🚀 SerpAPI** (100 free/month) - Highest quality results
5. **📊 SearchAPI** (100 free/month) - Additional option
6. **⚡ RapidAPI Google** (500+ free/month) - Multiple providers
7. **⚠️ Bing API** (DEPRECATED) - Microsoft retiring service
8. **📚 Wikipedia** (FREE) - Enhanced foundation info extraction
9. **❌ DuckDuckGo** (DISABLED) - Too limited for foundation search

#### **Total Monthly Quota: 5500+ Free Searches**

## 🎯 Streamlit Frontend Improvements

### **Enhanced User Input Options**

Users can now:

- **Select from existing donors** - Choose from your current pipeline
- **Enter custom donor names** - Research any organization worldwide
- **Provide website hints** - Improve research accuracy
- **View detailed generation status** - See which services were used

### **Enhanced Result Display**

- **Search Services Status** - See which APIs are active/exhausted
- **Quality Evaluation Feedback** - Detailed AI assessment of profile quality
- **Research Details** - Which websites were found and scraped
- **Wikipedia Integration** - Comprehensive foundation background from Wikipedia
- **Service Usage Tracking** - Know which search services were used

## 🔧 Railway Environment Variables

Configure as many search services as desired for maximum coverage:

```bash
# Primary Services (Best Free Tiers)
SCALESERP_API_KEY=your-scaleserp-key     # 1000 free/month
VALUESERP_API_KEY=your-valueserp-key     # 1000 free/month
ZENSERP_API_KEY=your-zenserp-key         # 1000 free/month

# Quality Services
SERPAPI_KEY=your-serpapi-key             # 100 free/month (highest quality)
SEARCHAPI_KEY=your-searchapi-key         # 100 free/month

# Additional Options
RAPIDAPI_KEY=your-rapidapi-key           # 500+ free/month
BING_SEARCH_API_KEY=your-bing-key        # DEPRECATED - Microsoft retiring

# AI Models (at least one required)
ANTHROPIC_API_KEY=your-claude-api-key
OPENAI_API_KEY=your-openai-api-key

# Google Services (for Docs export)
GOOGLE_CREDENTIALS_BASE64=your-base64-encoded-service-account
```

## 🔄 Smart Features

### **Automatic Quota Management**
- Detects quota exhaustion via error codes and HTTP status
- Seamlessly switches to next available service
- Tracks service status in real-time
- Monthly reset functionality

### **Enhanced Error Handling**
- Retry logic for network failures
- Service-specific error detection
- Graceful degradation when services unavailable
- Detailed logging for debugging

### **Foundation URL Detection**
- Smart filtering for relevant results
- Identifies foundation websites automatically
- Domain guessing fallback when search fails

## 📝 Usage Examples

### **Research New Foundation:**
1. Go to Donor Profile page
2. Select "Enter custom donor"
3. Enter: "Ford Foundation"
4. Optional website: "www.fordfoundation.org"
5. Click "Generate Profile"

### **View Service Status:**
After generation, expand "Search Services Status" to see:
- Which services are active/exhausted
- Priority ordering
- Monthly quota limits
- Real-time availability

## 🎉 Benefits

- **5500+ monthly searches** across all free tiers
- **Automatic failover** when quotas hit
- **Custom donor research** capability
- **Enhanced result transparency**
- **Production-ready** for Railway deployment
- **Cost-effective** using free tiers efficiently

The system maximizes your research capabilities while staying within free tier limits!