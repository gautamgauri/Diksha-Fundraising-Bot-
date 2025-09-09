import { useState, useEffect } from 'react'
import { 
  PaperAirplaneIcon, 
  SparklesIcon, 
  DocumentTextIcon,
  EyeIcon,
  PencilIcon
} from '@heroicons/react/24/outline'
import { EmailTemplate, EmailDraft, Donor, EmailError } from '@/types'
import { apiClient } from '@/lib/api'
import { useActivityLogger } from '@/lib/activity-logger'
import LoadingSpinner from './LoadingSpinner'

interface EmailComposerProps {
  donor: Donor
  onEmailSent: (threadId: string, messageId: string) => void
}

export default function EmailComposer({ donor, onEmailSent }: EmailComposerProps) {
  const [templates, setTemplates] = useState<EmailTemplate[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<EmailTemplate | null>(null)
  const [draft, setDraft] = useState<EmailDraft | null>(null)
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [previewMode, setPreviewMode] = useState(false)
  const [error, setError] = useState<EmailError | null>(null)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [previewTemplate, setPreviewTemplate] = useState<EmailTemplate | null>(null)
  const [showSendConfirmation, setShowSendConfirmation] = useState(false)
  
  const { logEmailSent, logActivity } = useActivityLogger()

  useEffect(() => {
    loadTemplates()
  }, [])

  // Auto-save draft functionality
  useEffect(() => {
    if (draft && !sending) {
      const timeoutId = setTimeout(() => {
        saveDraftToLocal(draft)
      }, 1000)
      return () => clearTimeout(timeoutId)
    }
  }, [draft?.content, draft?.subject, sending])

  const saveDraftToLocal = (draft: EmailDraft) => {
    try {
      localStorage.setItem(`draft_${draft.id}`, JSON.stringify(draft))
      setLastSaved(new Date())
    } catch (err) {
      console.warn('Failed to save draft locally:', err)
    }
  }

  const loadDraftFromLocal = (draftId: string): EmailDraft | null => {
    try {
      const saved = localStorage.getItem(`draft_${draftId}`)
      return saved ? JSON.parse(saved) : null
    } catch (err) {
      console.warn('Failed to load draft from local storage:', err)
      return null
    }
  }

  const getEmailErrorMessage = (error: EmailError): string => {
    switch (error.type) {
      case 'quota':
        return 'Daily email limit reached. Try again tomorrow.'
      case 'permission':
        return 'Gmail access permissions needed. Please reconnect your account.'
      case 'network':
        return 'Network error. Please check your connection and try again.'
      case 'validation':
        return `Validation error: ${error.message}`
      case 'template':
        return `Template error: ${error.message}`
      case 'ai_service':
        return 'AI service temporarily unavailable. Using template mode.'
      case 'gmail_api':
        return 'Gmail API error. Please try again later.'
      default:
        return error.message || 'An unexpected error occurred.'
    }
  }

  const handleError = (err: any, context: string): void => {
    console.error(`Error in ${context}:`, err)
    
    let emailError: EmailError
    
    if (err.response?.status === 429) {
      emailError = {
        type: 'quota',
        message: 'Rate limit exceeded',
        details: 'Too many requests. Please wait before trying again.'
      }
    } else if (err.response?.status === 403) {
      emailError = {
        type: 'permission',
        message: 'Permission denied',
        details: 'Gmail access permissions may have expired.'
      }
    } else if (err.code === 'NETWORK_ERROR' || !navigator.onLine) {
      emailError = {
        type: 'network',
        message: 'Network error',
        details: 'Please check your internet connection.'
      }
    } else if (err.message?.includes('validation')) {
      emailError = {
        type: 'validation',
        message: err.message,
        details: err.details
      }
    } else if (err.message?.includes('template')) {
      emailError = {
        type: 'template',
        message: err.message,
        details: err.details
      }
    } else {
      emailError = {
        type: 'network',
        message: err.message || 'An unexpected error occurred',
        details: context
      }
    }
    
    setError(emailError)
  }

  const loadTemplates = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getTemplates()
      setTemplates(data)
    } catch (err) {
      handleError(err, 'loading templates')
    } finally {
      setLoading(false)
    }
  }

  const handleTemplateSelect = async (template: EmailTemplate) => {
    try {
      setLoading(true)
      setError(null)
      
      // Generate draft with placeholders filled
      const placeholders = {
        org_name: donor.organization_name,
        contact_person: donor.contact_person || 'Team',
        focus_area: donor.sector_tags || 'social impact',
        alignment_score: donor.alignment_score?.toString() || 'high',
        last_contact: donor.last_contact_date || 'recently'
      }

      // Validate placeholders in template content
      const missingPlaceholders = validatePlaceholders(template.content, placeholders)
      if (missingPlaceholders.length > 0) {
        setError({
          type: 'validation',
          message: `Template contains missing placeholders: ${missingPlaceholders.join(', ')}`,
          details: 'Please ensure all template placeholders have corresponding donor data.'
        })
        return
      }

      const draftData = {
        template_id: template.id,
        donor_id: donor.id,
        subject: template.subject,
        content: template.content,
        placeholders
      }

      const newDraft = await apiClient.generateDraft(draftData)
      
      // Check for existing local draft
      const existingDraft = loadDraftFromLocal(newDraft.id)
      if (existingDraft) {
        setDraft(existingDraft)
        setLastSaved(new Date(existingDraft.created_at))
      } else {
        setDraft(newDraft)
        setLastSaved(new Date())
      }
      
      setSelectedTemplate(template)
      
      // Log draft creation activity
      await logActivity(
        'draft_created',
        donor.id,
        `Created email draft using ${template.name} template`,
        {
          template: template.name,
          donor_name: donor.organization_name
        }
      )
    } catch (err) {
      handleError(err, 'generating draft')
    } finally {
      setLoading(false)
    }
  }

  const handleRefineDraft = async (refinements: { tone?: 'formal' | 'warm' | 'urgent' | 'casual'; length?: 'short' | 'medium' | 'long'; cta?: string }) => {
    if (!draft) return

    try {
      setLoading(true)
      setError(null)
      const refinedDraft = await apiClient.refineDraft(draft.id, refinements)
      setDraft(refinedDraft)
      
      // Log draft refinement activity
      await logActivity(
        'draft_refined',
        donor.id,
        `Refined email draft with AI: ${Object.keys(refinements).join(', ')}`,
        {
          refinements,
          donor_name: donor.organization_name
        }
      )
    } catch (err) {
      handleError(err, 'refining draft')
    } finally {
      setLoading(false)
    }
  }

  const handleSendEmail = async () => {
    if (!draft) return

    // Show confirmation for important email types
    if (selectedTemplate?.type === 'proposal_cover' || selectedTemplate?.type === 'intro') {
      setShowSendConfirmation(true)
      return
    }

    await sendEmail()
  }

  const sendEmail = async () => {
    if (!draft) return

    try {
      setSending(true)
      setError(null)
      setShowSendConfirmation(false)
      
      const result = await apiClient.sendEmail(draft.id)
      
      if (result.success) {
        // Log the email send activity
        await logEmailSent(
          donor.id,
          selectedTemplate?.name || 'unknown',
          draft.subject
        )
        
        // Log additional activity details
        await logActivity(
          'email_sent',
          donor.id,
          `Sent ${selectedTemplate?.name || 'unknown'} email to ${donor.organization_name}`,
          {
            template: selectedTemplate?.name,
            subject: draft.subject,
            thread_id: result.data!.thread_id,
            message_id: result.data!.message_id,
            donor_name: donor.organization_name
          }
        )
        
        onEmailSent(result.data!.thread_id, result.data!.message_id)
        setDraft(null)
        setSelectedTemplate(null)
      } else {
        setError({
          type: 'gmail_api',
          message: result.error || 'Failed to send email',
          details: 'The email could not be sent through Gmail API.'
        })
      }
    } catch (err) {
      handleError(err, 'sending email')
    } finally {
      setSending(false)
    }
  }

  const fillPlaceholders = (content: string, placeholders: Record<string, string>) => {
    let filledContent = content
    Object.entries(placeholders).forEach(([key, value]: [string, string]) => {
      const placeholder = `{{${key}}}`
      filledContent = filledContent.replace(new RegExp(placeholder, 'g'), value)
    })
    return filledContent
  }

  const validatePlaceholders = (content: string, available: Record<string, string>) => {
    const placeholderPattern = /\{\{([^}]+)\}\}/g
    const matches = content.match(placeholderPattern)
    const missing = matches?.filter(match => {
      const key = match.replace(/[{}]/g, '')
      return !available[key]
    }) || []
    return missing
  }

  const extractPlaceholders = (content: string) => {
    const regex = /\{\{([^}]+)\}\}/g
    const placeholders = []
    let match
    while ((match = regex.exec(content)) !== null) {
      placeholders.push(match[1])
    }
    return placeholders
  }

  if (loading && !draft) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Template Selection */}
      {!selectedTemplate && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Select Email Template</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <div
                key={template.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 hover:shadow-md transition-all"
              >
                <div className="flex items-center space-x-3 mb-2">
                  <DocumentTextIcon className="h-5 w-5 text-primary-600" />
                  <h4 className="font-medium text-gray-900">{template.name}</h4>
                </div>
                <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                <div className="text-xs text-gray-500 mb-3">
                  <div className="font-medium">Subject:</div>
                  <div className="truncate">{template.subject}</div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setPreviewTemplate(template as EmailTemplate)}
                    className="flex-1 px-3 py-2 text-xs font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                  >
                    Preview
                  </button>
                  <button
                    onClick={() => handleTemplateSelect(template as EmailTemplate)}
                    className="flex-1 px-3 py-2 text-xs font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700"
                  >
                    Use Template
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Email Composer */}
      {selectedTemplate && draft && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">Email Composer</h3>
                  <div className="flex items-center space-x-4">
                    <p className="text-sm text-gray-600">Template: {selectedTemplate.name}</p>
                    {lastSaved && (
                      <p className="text-xs text-gray-500">
                        Last saved: {lastSaved.toLocaleTimeString()}
                      </p>
                    )}
                  </div>
                </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setPreviewMode(!previewMode)}
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  <EyeIcon className="h-4 w-4 mr-2" />
                  {previewMode ? 'Edit' : 'Preview'}
                </button>
                <button
                  onClick={() => {
                    setSelectedTemplate(null)
                    setDraft(null)
                    setPreviewMode(false)
                  }}
                  className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* AI Refinement Options */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-900 mb-3">AI Refinements</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tone</label>
                  <select
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                    onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleRefineDraft({ tone: e.target.value as 'formal' | 'warm' | 'urgent' | 'casual' })}
                  >
                    <option value="">Select tone...</option>
                    <option value="formal">Formal</option>
                    <option value="warm">Warm</option>
                    <option value="urgent">Urgent</option>
                    <option value="casual">Casual</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Length</label>
                  <select
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                    onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleRefineDraft({ length: e.target.value as 'short' | 'medium' | 'long' })}
                  >
                    <option value="">Select length...</option>
                    <option value="short">Short</option>
                    <option value="medium">Medium</option>
                    <option value="long">Long</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Custom CTA</label>
                  <input
                    type="text"
                    placeholder="Enter custom call-to-action..."
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleRefineDraft({ cta: e.target.value })}
                  />
                </div>
              </div>
            </div>

            {/* Subject Line */}
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">Subject Line</label>
              <input
                type="text"
                value={fillPlaceholders(draft.subject, draft.placeholders)}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDraft({ ...draft, subject: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-primary-500 focus:border-primary-500"
                disabled={previewMode}
              />
            </div>

            {/* Email Content */}
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">Email Content</label>
              {previewMode ? (
                <div className="border border-gray-300 rounded-md p-4 bg-gray-50 min-h-[300px]">
                  <div className="prose prose-sm max-w-none">
                    {fillPlaceholders(draft.content, draft.placeholders).split('\n').map((line, index) => (
                      <p key={index} className="mb-2">{line}</p>
                    ))}
                  </div>
                </div>
              ) : (
                <textarea
                  value={fillPlaceholders(draft.content, draft.placeholders)}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setDraft({ ...draft, content: e.target.value })}
                  rows={12}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-primary-500 focus:border-primary-500"
                />
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">
                      {getEmailErrorMessage(error)}
                    </h3>
                    {error.details && (
                      <div className="mt-2 text-sm text-red-700">
                        {error.details}
                      </div>
                    )}
                    <div className="mt-4">
                      <div className="-mx-2 -my-1.5 flex">
                        <button
                          type="button"
                          onClick={() => setError(null)}
                          className="bg-red-50 px-2 py-1.5 rounded-md text-sm font-medium text-red-800 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-red-50 focus:ring-red-600"
                        >
                          Dismiss
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Send Button */}
            <div className="flex justify-end">
              <button
                onClick={handleSendEmail}
                disabled={sending || loading}
                className="flex items-center px-6 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {sending ? (
                  <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    Sending...
                  </>
                ) : (
                  <>
                    <PaperAirplaneIcon className="h-4 w-4 mr-2" />
                    Send Email
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Template Preview Modal */}
      {previewTemplate && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Preview: {previewTemplate.name}
                </h3>
                <button
                  onClick={() => setPreviewTemplate(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <p className="text-sm text-gray-600">{previewTemplate.description}</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Subject Line</label>
                  <div className="p-3 bg-gray-50 rounded-md text-sm">
                    {fillPlaceholders(previewTemplate.subject, {
                      org_name: donor.organization_name,
                      contact_person: donor.contact_person || 'Team',
                      focus_area: donor.sector_tags || 'social impact',
                      alignment_score: donor.alignment_score?.toString() || 'high',
                      last_contact: donor.last_contact_date || 'recently'
                    })}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email Content</label>
                  <div className="p-3 bg-gray-50 rounded-md text-sm max-h-64 overflow-y-auto">
                    <div className="prose prose-sm max-w-none">
                      {fillPlaceholders(previewTemplate.content, {
                        org_name: donor.organization_name,
                        contact_person: donor.contact_person || 'Team',
                        focus_area: donor.sector_tags || 'social impact',
                        alignment_score: donor.alignment_score?.toString() || 'high',
                        last_contact: donor.last_contact_date || 'recently'
                      }).split('\n').map((line, index) => (
                        <p key={index} className="mb-2">{line}</p>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    onClick={() => setPreviewTemplate(null)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => {
                      handleTemplateSelect(previewTemplate)
                      setPreviewTemplate(null)
                    }}
                    className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700"
                  >
                    Use This Template
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Send Confirmation Modal */}
      {showSendConfirmation && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 lg:w-1/3 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-center w-12 h-12 mx-auto bg-yellow-100 rounded-full mb-4">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Confirm Email Send
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  You're about to send a <strong>{selectedTemplate?.type}</strong> email to{' '}
                  <strong>{donor.organization_name}</strong>. This is an important communication.
                </p>
                
                <div className="bg-gray-50 rounded-md p-3 mb-4 text-left">
                  <div className="text-sm">
                    <div className="font-medium text-gray-900 mb-1">Subject:</div>
                    <div className="text-gray-700 mb-2">{draft?.subject}</div>
                    <div className="font-medium text-gray-900 mb-1">Recipient:</div>
                    <div className="text-gray-700">{donor.organization_name}</div>
                  </div>
                </div>
                
                <p className="text-xs text-gray-500 mb-6">
                  This action will be logged and cannot be undone.
                </p>
              </div>
              
              <div className="flex justify-center space-x-3">
                <button
                  onClick={() => setShowSendConfirmation(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={sendEmail}
                  className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700"
                >
                  Send Email
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
