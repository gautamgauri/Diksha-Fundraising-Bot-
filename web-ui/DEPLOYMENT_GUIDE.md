# Funding Bot Web UI - Deployment Guide

This guide will help you deploy the Funding Bot Web UI to Railway alongside your existing Flask backend.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Google OAuth Setup**: Configure Google OAuth for web authentication
3. **PostgreSQL Database**: For user management (Railway provides this)
4. **Existing Flask Backend**: Your current Funding Bot backend

## Step 1: Google OAuth Configuration

### 1.1 Create Google OAuth App

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Choose "Web application"
6. Add authorized origins:
   - `http://localhost:3000` (for development)
   - `https://your-web-ui-domain.railway.app` (for production)
7. Add redirect URIs:
   - `http://localhost:3000/api/auth/callback/google`
   - `https://your-web-ui-domain.railway.app/api/auth/callback/google`

### 1.2 Get Credentials

Copy the Client ID and Client Secret - you'll need these for environment variables.

## Step 2: Railway Deployment

### 2.1 Create New Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Choose "Deploy from GitHub repo" or "Empty Project"

### 2.2 Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL instance
4. Copy the `DATABASE_URL` from the database service

### 2.3 Deploy Web UI

1. **Option A: Deploy from GitHub**
   - Connect your GitHub repository
   - Select the `web-ui` folder as the root directory
   - Railway will auto-detect it's a Next.js app

2. **Option B: Deploy from CLI**
   ```bash
   cd web-ui
   railway login
   railway init
   railway up
   ```

### 2.4 Configure Environment Variables

In Railway dashboard, go to your web UI service → Variables tab and add:

**Required Environment Variables:**
```env
# Authentication
NEXTAUTH_URL=https://your-web-ui-domain.railway.app
NEXTAUTH_SECRET=your-random-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Backend Integration
BACKEND_API_URL=https://your-flask-backend.railway.app
NEXT_PUBLIC_BACKEND_API_URL=https://your-flask-backend.railway.app

# Security
ALLOWED_EMAIL_DOMAINS=dikshafoundation.org,partner-org.com
NODE_ENV=production

# Feature Flags (Optional)
FEATURE_EMAIL_COMPOSER=true
FEATURE_BULK_OPS=true
FEATURE_OFFLINE_MODE=true
FEATURE_ACTIVITY_LOGGING=true

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn
```

**Environment Variable Security:**
- Variables prefixed with `NEXT_PUBLIC_` are accessible in the browser
- All other variables are server-side only
- Never expose secrets in client-side code

**Generate NEXTAUTH_SECRET**:
```bash
openssl rand -base64 32
```

## Step 3: Database Setup

### 3.1 Run Database Migrations

1. Connect to your Railway project via CLI:
   ```bash
   railway login
   railway link
   ```

2. Run Prisma setup and migrations:
   ```bash
   cd web-ui
   npm run db:generate
   npm run db:push
   npm run db:seed
   ```

3. Verify database connection:
   ```bash
   npx prisma studio
   ```

**Database Schema:**
The application uses Prisma with PostgreSQL and includes:
- User management with NextAuth.js integration
- Role-based access control (Admin, Fundraising, Viewer)
- Activity logging for audit trails
- Email templates and drafts management
- User permissions for granular access control

### 3.2 Verify Database Connection

Check that the database is properly connected by visiting your web UI and attempting to sign in.

## Step 4: Backend Integration

### 4.1 Update Flask Backend

Your Flask backend needs CORS configuration for the web UI. Add this to your Flask app:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:3000",
    "https://your-web-ui-domain.railway.app"
])
```

**Required Flask Backend Environment Variables:**
```env
GOOGLE_CREDENTIALS_BASE64=your-google-credentials
SLACK_BOT_TOKEN=your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
CORS_ORIGINS=https://your-web-ui-domain.railway.app
```

**Add Health Check Endpoint:**
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
```

### 4.2 Test API Connectivity

1. Visit your web UI
2. Try to load the pipeline page
3. Check Railway logs for any API errors

## Step 5: User Management

### 5.1 First Admin User

The first user to sign in will automatically get "viewer" role. To promote them to admin:

1. Connect to your PostgreSQL database
2. Run this SQL query:
   ```sql
   UPDATE "User" SET role = 'ADMIN' WHERE email = 'your-email@dikshafoundation.org';
   ```

### 5.2 User Roles

- **ADMIN**: Full access to all features
- **FUNDRAISING**: Can edit pipeline and send emails
- **VIEWER**: Read-only access

## Step 6: Production Monitoring & Security

### 6.1 Health Checks

The application includes health check endpoints for monitoring:

- **Web UI Health**: `https://your-web-ui-domain.railway.app/api/health`
- **Backend Health**: `https://your-flask-backend.railway.app/health`

### 6.2 Rate Limiting

Rate limiting is implemented for:
- Authentication attempts: 5 per 15 minutes
- API requests: 100 per 15 minutes  
- Email sending: 50 per hour

### 6.3 Security Headers

The application includes security headers:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: origin-when-cross-origin
- Permissions-Policy: camera=(), microphone=(), geolocation=()

### 6.4 Error Monitoring

For production error tracking, add Sentry:

```bash
npm install @sentry/nextjs
```

Configure in `sentry.client.config.js`:
```javascript
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
})
```

## Step 7: Backup & Recovery

### 7.1 Automated Backups

Set up automated database backups:

```bash
# Add to Railway cron job or external scheduler
node scripts/backup.js
```

### 7.2 Backup Storage

Configure cloud storage for backups:
```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BACKUP_BUCKET=your-backup-bucket
```

### 7.3 Recovery Process

To restore from backup:
```bash
# Download backup from S3
aws s3 cp s3://your-bucket/backup.sql.gz .

# Restore database
gunzip backup.sql.gz
psql $DATABASE_URL < backup.sql
```

## Step 8: User Management

### 8.1 Admin User Promotion

Promote first user to admin:
```sql
UPDATE "User" SET role = 'ADMIN' WHERE email = 'admin@dikshafoundation.org';
```

### 8.2 User Management API

The application includes user management endpoints:
- `GET /api/users` - List all users
- `PUT /api/users/[id]` - Update user role
- `DELETE /api/users/[id]` - Deactivate user

### 8.3 Role-Based Access

- **ADMIN**: Full system access, user management
- **FUNDRAISING**: Pipeline editing, email sending, template management
- **VIEWER**: Read-only access to pipeline and reports

## Step 9: Feature Flags

### 9.1 Environment-Based Features

Control feature rollout with environment variables:
```env
FEATURE_EMAIL_COMPOSER=true
FEATURE_BULK_OPS=true
FEATURE_OFFLINE_MODE=true
FEATURE_ACTIVITY_LOGGING=true
```

### 9.2 Gradual Rollout

Use feature flags for safe deployments:
```javascript
import { useFeature } from '@/lib/features'

function MyComponent() {
  const emailComposerEnabled = useFeature('emailComposer')
  
  return (
    <div>
      {emailComposerEnabled && <EmailComposer />}
    </div>
  )
}
```

## Step 10: Domain Configuration (Optional)

### 10.1 Custom Domain

1. In Railway dashboard, go to your web UI service
2. Click "Settings" → "Domains"
3. Add your custom domain (e.g., `funding-bot.dikshafoundation.org`)
4. Update DNS records as instructed by Railway

### 10.2 Update Google OAuth

After setting up custom domain, update your Google OAuth configuration:
- Add new authorized origins and redirect URIs
- Update `NEXTAUTH_URL` environment variable

## Step 11: Troubleshooting

### 11.1 Common Issues

**Database Connection Errors:**
```bash
# Check database connectivity
npx prisma db pull
npx prisma generate
```

**Authentication Issues:**
- Verify Google OAuth credentials
- Check `NEXTAUTH_URL` matches your domain
- Ensure `NEXTAUTH_SECRET` is set

**API Connection Issues:**
- Verify `BACKEND_API_URL` is correct
- Check CORS configuration in Flask backend
- Test backend health endpoint

### 11.2 Logs and Debugging

**View Railway Logs:**
```bash
railway logs --service web-ui
railway logs --service backend
```

**Debug Mode:**
```env
NODE_ENV=development
NEXTAUTH_DEBUG=true
```

### 11.3 Performance Issues

**Database Optimization:**
```sql
-- Add indexes for better performance
CREATE INDEX idx_user_email ON "User"(email);
CREATE INDEX idx_activity_timestamp ON "Activity"(timestamp);
CREATE INDEX idx_email_draft_status ON "EmailDraft"(status);
```

**Memory Issues:**
- Enable virtual scrolling for large datasets
- Use pagination for API responses
- Monitor memory usage in Railway dashboard

## Step 12: Maintenance

### 12.1 Regular Updates

**Update Dependencies:**
```bash
npm update
npm audit fix
```

**Database Migrations:**
```bash
npm run db:migrate
```

### 12.2 Monitoring

**Key Metrics to Monitor:**
- Response times
- Error rates
- Database connection pool
- Memory usage
- User activity

**Alerts to Set Up:**
- High error rates (>5%)
- Slow response times (>2s)
- Database connection failures
- Memory usage >80%

### 12.3 Security Updates

**Regular Security Tasks:**
- Update dependencies monthly
- Review user access quarterly
- Audit activity logs monthly
- Test backup recovery quarterly

## Conclusion

Your Funding Bot Web UI is now production-ready with:
- ✅ Secure authentication with Google OAuth
- ✅ Role-based access control
- ✅ Database management with Prisma
- ✅ API integration with Flask backend
- ✅ Health monitoring and error tracking
- ✅ Automated backups and recovery
- ✅ Feature flags for safe deployments
- ✅ Rate limiting and security headers

The application is designed to handle your fundraising operations securely and efficiently, with proper monitoring and maintenance procedures in place.
