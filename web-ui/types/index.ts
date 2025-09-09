// User and Authentication Types
export interface User {
  id: string
  name?: string
  email: string
  image?: string
  role: 'admin' | 'fundraising' | 'viewer'
  createdAt?: string
  updatedAt?: string
  lastLoginAt?: string
  permissions?: {
    canViewPipeline: boolean
    canEditPipeline: boolean
    canSendEmails: boolean
    canManageTemplates: boolean
    canViewLogs: boolean
    canManageUsers: boolean
  }
}

export interface Session {
  user: User
  expires: string
}

// Donor and Pipeline Types
export interface Donor {
  id: string
  organization_name: string
  current_stage: string
  assigned_to?: string
  next_action?: string
  next_action_date?: string
  last_contact_date?: string
  sector_tags?: string
  probability?: number
  updated_at?: string
  alignment_score?: number
  contact_person?: string
  contact_email?: string
  contact_role?: string
  notes?: string
  documents?: Document[]
}

export interface Document {
  id: string
  name: string
  type: string
  url: string
  drive_id: string
  created_at: string
}

// Email Types
export interface EmailTemplate {
  id: string
  name: string
  description: string
  subject: string
  content: string
  placeholders: string[]
  type: 'intro' | 'followup' | 'proposal_cover' | 'thankyou' | 'meeting_request'
}

export interface EmailDraft {
  id: string
  template_id: string
  donor_id: string
  subject: string
  content: string
  placeholders: Record<string, string>
  status: 'draft' | 'sent' | 'failed'
  created_at: string
  sent_at?: string
  thread_id?: string
  message_id?: string
}

// Activity Log Types
export interface Activity {
  id: string
  user_id: string
  user_name: string
  action: string
  target?: string
  details?: string
  timestamp: string
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  hasMore: boolean
}

// Pipeline Filter Types
export interface PipelineFilters {
  stage?: string[]
  owner?: string[]
  sector?: string[]
  search?: string
}

// Email Composer Types
export interface EmailComposerData {
  template_id: string
  donor_id: string
  subject: string
  content: string
  placeholders: Record<string, string>
  ai_refinements?: {
    tone?: 'formal' | 'warm' | 'urgent' | 'casual'
    length?: 'short' | 'medium' | 'long'
    cta?: string
  }
}

// Error Types
export interface EmailError {
  type: 'validation' | 'network' | 'permission' | 'quota' | 'template' | 'ai_service' | 'gmail_api'
  message: string
  details?: string
  code?: string
}

export interface EmailErrorResponse {
  success: false
  error: EmailError
}