# Funding Bot Web UI

A modern web interface for the Diksha Foundation Fundraising Bot, built with Next.js, TypeScript, and Tailwind CSS.

## Features

### ✅ Implemented
- **Authentication**: Google OAuth with role-based access (Admin, Fundraising, Viewer)
- **Pipeline Management**: Table view with filtering, searching, and inline editing
- **Donor Profiles**: Detailed donor information with contact details and notes
- **Email Composer**: Template-based email generation with AI refinement
- **Responsive Design**: Mobile-friendly interface with modern UI components

### 🚧 In Progress
- **Templates Page**: Drive integration and placeholder detection
- **Activity Log**: User action tracking and accountability
- **Gmail Integration**: Direct email sending and thread logging

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS, Headless UI
- **Authentication**: NextAuth.js with Google OAuth
- **State Management**: React Query for server state
- **Database**: PostgreSQL with Prisma (for user management)
- **Backend Integration**: RESTful APIs with your existing Flask backend

## Project Structure

```
web-ui/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout wrapper
│   ├── Navigation.tsx  # Top navigation bar
│   ├── PipelineTable.tsx # Pipeline data table
│   ├── EmailComposer.tsx # Email composition interface
│   └── LoadingSpinner.tsx # Loading states
├── pages/              # Next.js pages
│   ├── index.tsx       # Pipeline page (main dashboard)
│   ├── donor/[id].tsx  # Individual donor profile
│   ├── auth/           # Authentication pages
│   └── api/            # API routes
├── lib/                # Utility libraries
│   ├── auth.ts         # NextAuth configuration
│   ├── api.ts          # Backend API client
│   └── prisma/         # Database schema
├── types/              # TypeScript type definitions
└── styles/             # Global styles
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- PostgreSQL database (for user management)
- Google OAuth credentials
- Access to your Flask backend API

### Installation

1. **Clone and install dependencies**:
   ```bash
   cd web-ui
   npm install
   ```

2. **Set up environment variables**:
   ```bash
   cp env.example .env.local
   ```
   
   Fill in the required values:
   ```env
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=your-secret-key-here
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   BACKEND_API_URL=http://localhost:5000
   DATABASE_URL=postgresql://username:password@localhost:5432/funding_bot_web
   ```

3. **Set up the database**:
   ```bash
   npx prisma generate
   npx prisma db push
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

5. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## User Roles

### Admin
- Full access to all features
- Can manage users and settings
- Can edit all donor information
- Can send emails and manage templates

### Fundraising Staff
- Can view and edit pipeline
- Can send emails and manage their assigned donors
- Cannot access admin features
- Cannot manage other users

### Viewer
- Read-only access to pipeline and donor profiles
- Cannot edit or send emails
- Can view activity logs (if implemented)

## API Integration

The web UI communicates with your existing Flask backend through these endpoints:

- `GET /api/pipeline` - Fetch all donors
- `GET /api/donor/:id` - Get specific donor details
- `POST /api/moveStage` - Update donor stage
- `POST /api/assignDonor` - Assign donor to team member
- `POST /api/notes` - Update donor notes
- `GET /api/templates` - Get email templates
- `POST /api/draft` - Generate email draft
- `POST /api/send` - Send email
- `POST /api/log` - Log user activity

## Deployment

### Railway Deployment

1. **Connect to Railway**:
   ```bash
   railway login
   railway link
   ```

2. **Set environment variables** in Railway dashboard:
   - `NEXTAUTH_URL` - Your production URL
   - `NEXTAUTH_SECRET` - Random secret key
   - `GOOGLE_CLIENT_ID` - Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
   - `BACKEND_API_URL` - Your Flask backend URL
   - `DATABASE_URL` - PostgreSQL connection string

3. **Deploy**:
   ```bash
   railway up
   ```

### Environment Setup

Make sure your Google OAuth app is configured with:
- Authorized JavaScript origins: `http://localhost:3000` (dev), `https://your-domain.com` (prod)
- Authorized redirect URIs: `http://localhost:3000/api/auth/callback/google` (dev), `https://your-domain.com/api/auth/callback/google` (prod)

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Code Style

- TypeScript for type safety
- Tailwind CSS for styling
- ESLint for code quality
- Prettier for code formatting (recommended)

## Integration with Existing System

This web UI is designed to work alongside your existing Slack bot:

- **Slack Bot**: Handles notifications, quick queries, and natural language processing
- **Web UI**: Handles detailed pipeline management, email composition, and bulk operations
- **Shared Backend**: Both interfaces use the same Flask API and Google Sheets database

## Future Enhancements

- **Dashboard Analytics**: Charts and metrics for fundraising performance
- **Bulk Operations**: Mass email campaigns and bulk updates
- **Mobile App**: React Native app for mobile access
- **Advanced Reporting**: Export capabilities and custom reports
- **Integration Hub**: Connect with CRM systems and other tools

## Support

For issues or questions:
1. Check the existing Flask backend logs
2. Verify Google OAuth configuration
3. Ensure database connectivity
4. Check Railway deployment logs

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test with different user roles
4. Update documentation for new features

