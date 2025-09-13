# Diksha Fundraising Bot - Streamlit App

A modern, multi-page Streamlit application for managing fundraising activities, donor relationships, and email communications.

## 🚀 Features

### 📊 Pipeline Management
- View fundraising pipeline with key metrics
- Track donor stages and progress
- Export pipeline data
- Add new prospects

### 🏷️ Donor Profiles
- Comprehensive donor information
- Donation history tracking
- Engagement scoring
- Communication preferences

### ✉️ AI-Powered Email Composer
- AI-generated email content
- Multiple email templates
- Email scheduling and tracking
- Integration with Gmail API

### 🧩 Template Management
- Email template library
- Custom template creation
- Template categorization
- Usage analytics

### 📝 Activity Log
- Complete activity tracking
- Filterable activity history
- Export capabilities
- Real-time updates

## 🏗️ Architecture

```
streamlit-app/
├── streamlit_app.py          # Main application entry point
├── pages/                    # Multi-page application structure
│   ├── 1_📊_Pipeline.py      # Pipeline management
│   ├── 2_🏷️_Donor_Profile.py # Donor profiles
│   ├── 3_✉️_Composer.py      # Email composer
│   ├── 4_🧩_Templates.py     # Template management
│   └── 5_📝_Activity_Log.py  # Activity tracking
├── lib/                      # Utility libraries
│   ├── api.py               # Backend API integration
│   └── auth.py              # Authentication
├── requirements.txt         # Python dependencies
├── Procfile                # Railway deployment
└── railway.json            # Railway configuration
```

## 🔧 Setup

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export API_BASE="http://localhost:5000"  # Your Node.js backend URL
   export ALLOWED_USERS="your.email@dikshafoundation.org"
   ```

3. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

### Railway Deployment

1. **Connect to Railway:**
   - Link your GitHub repository
   - Select the `streamlit-app` directory

2. **Set environment variables in Railway:**
   - `API_BASE`: Your Node.js backend URL
   - `ALLOWED_USERS`: Comma-separated list of allowed emails

3. **Deploy:**
   - Railway will automatically build and deploy
   - Access your app at the provided Railway URL

## 🔌 Backend Integration

The Streamlit app connects to your existing Node.js backend via REST API:

### API Endpoints Used:
- `GET /api/donors` - Fetch donor list
- `GET /api/pipeline` - Get pipeline data
- `GET /api/donors/{id}` - Get donor details
- `POST /api/email/send` - Send emails
- `GET /api/activities` - Get activity log
- `POST /api/log` - Log activities

### Authentication:
- Simple email-based authentication
- Role-based access control
- Configurable allowlist

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop and mobile
- **Dark/Light Mode**: Automatic theme detection
- **Real-time Updates**: Live data synchronization
- **Interactive Components**: Charts, tables, and forms
- **Error Handling**: Graceful fallbacks and error messages

## 📱 Pages Overview

### 1. Pipeline (📊)
- Pipeline metrics and KPIs
- Donor stage tracking
- Export and filtering options

### 2. Donor Profile (🏷️)
- Individual donor management
- Donation history
- Engagement scoring
- Communication preferences

### 3. Email Composer (✉️)
- AI-powered content generation
- Template selection
- Email scheduling
- Tracking and analytics

### 4. Templates (🧩)
- Template library management
- Custom template creation
- Usage analytics
- Template categorization

### 5. Activity Log (📝)
- Complete activity tracking
- Filterable history
- Export capabilities
- Real-time updates

## 🔒 Security

- Email-based authentication
- Role-based access control
- API key management
- Secure environment variables

## 🚀 Deployment

### Railway (Recommended)
- Automatic builds from GitHub
- Environment variable management
- SSL certificates
- Custom domains

### Other Platforms
- Heroku
- Streamlit Cloud
- AWS/GCP/Azure

## 📊 Monitoring

- Application logs
- Error tracking
- Performance metrics
- User activity logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ for Diksha Foundation**




