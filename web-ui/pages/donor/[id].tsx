import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { useSession } from 'next-auth/react'
import Layout from '@/components/Layout'
import EmailComposer from '@/components/EmailComposer'
import LoadingSpinner from '@/components/LoadingSpinner'
import { 
  ArrowLeftIcon, 
  PencilIcon, 
  DocumentTextIcon,
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline'
import { Donor } from '@/types'
import { apiClient } from '@/lib/api'

export default function DonorProfilePage() {
  const { data: session } = useSession()
  const router = useRouter()
  const { id } = router.query
  const [donor, setDonor] = useState<Donor | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editingNotes, setEditingNotes] = useState(false)
  const [notes, setNotes] = useState('')

  useEffect(() => {
    if (id) {
      loadDonor()
    }
  }, [id])

  const loadDonor = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getDonor(id as string)
      setDonor(data)
      setNotes(data.notes || '')
    } catch (err) {
      setError('Failed to load donor information')
      console.error('Error loading donor:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveNotes = async () => {
    if (!donor) return

    try {
      await apiClient.updateDonorNotes(donor.id, notes)
      setDonor({ ...donor, notes })
      setEditingNotes(false)
      
      // Log the activity
      await apiClient.logActivity(
        'Updated donor notes',
        `Donor: ${donor.organization_name}`,
        'Notes updated via web UI'
      )
    } catch (err) {
      console.error('Failed to save notes:', err)
    }
  }

  const handleEmailSent = async (threadId: string, messageId: string) => {
    if (!donor) return

    // Update donor's last contact date
    const updatedDonor = {
      ...donor,
      last_contact_date: new Date().toISOString().split('T')[0]
    }
    setDonor(updatedDonor)

    // Log the activity
    await apiClient.logActivity(
      'Email sent',
      `Donor: ${donor.organization_name}`,
      `Thread ID: ${threadId}, Message ID: ${messageId}`
    )
  }

  const getStageColor = (stage: string) => {
    const colors: Record<string, string> = {
      'Initial Contact': 'bg-gray-100 text-gray-800',
      'Intro Sent': 'bg-blue-100 text-blue-800',
      'Follow-up Sent': 'bg-yellow-100 text-yellow-800',
      'Proposal Sent': 'bg-purple-100 text-purple-800',
      'Thank You Sent': 'bg-green-100 text-green-800',
      'Meeting Scheduled': 'bg-indigo-100 text-indigo-800',
      'Negotiation': 'bg-orange-100 text-orange-800',
      'Closed Won': 'bg-green-100 text-green-800',
      'Closed Lost': 'bg-red-100 text-red-800'
    }
    return colors[stage] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </Layout>
    )
  }

  if (error || !donor) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="text-red-600 text-lg">{error || 'Donor not found'}</div>
          <button
            onClick={() => router.back()}
            className="mt-4 text-primary-600 hover:text-primary-800"
          >
            Go back
          </button>
        </div>
      </Layout>
    )
  }

  const canEdit = session?.user?.role === 'admin' || session?.user?.role === 'fundraising'

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.back()}
              className="flex items-center text-gray-600 hover:text-gray-800"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-2" />
              Back to Pipeline
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{donor.organization_name}</h1>
              <div className="flex items-center space-x-4 mt-1">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStageColor(donor.current_stage)}`}>
                  {donor.current_stage}
                </span>
                {donor.alignment_score && (
                  <span className="text-sm text-gray-600">
                    Alignment Score: {donor.alignment_score}/10
                  </span>
                )}
              </div>
            </div>
          </div>
          {canEdit && (
            <button
              onClick={() => router.push(`/donor/${donor.id}/edit`)}
              className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <PencilIcon className="h-4 w-4 mr-2" />
              Edit Profile
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Donor Information */}
          <div className="lg:col-span-1 space-y-6">
            {/* Contact Information */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Contact Information</h3>
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <UserIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {donor.contact_person || 'Not specified'}
                    </div>
                    <div className="text-sm text-gray-500">Contact Person</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <BuildingOfficeIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {donor.contact_email || 'Not specified'}
                    </div>
                    <div className="text-sm text-gray-500">Email</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <UserIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {donor.contact_role || 'Not specified'}
                    </div>
                    <div className="text-sm text-gray-500">Role</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Pipeline Information */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Pipeline Information</h3>
              <div className="space-y-4">
                <div>
                  <div className="text-sm font-medium text-gray-900">Assigned To</div>
                  <div className="text-sm text-gray-600">{donor.assigned_to || 'Unassigned'}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900">Next Action</div>
                  <div className="text-sm text-gray-600">{donor.next_action || 'No action set'}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900">Due Date</div>
                  <div className="text-sm text-gray-600">{donor.next_action_date || 'No date set'}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900">Last Contact</div>
                  <div className="text-sm text-gray-600">{donor.last_contact_date || 'Never'}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900">Sector</div>
                  <div className="text-sm text-gray-600">{donor.sector_tags || 'Not specified'}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900">Probability</div>
                  <div className="text-sm text-gray-600">{donor.probability ? `${donor.probability}%` : 'Not set'}</div>
                </div>
              </div>
            </div>

            {/* Notes */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Notes</h3>
                {canEdit && !editingNotes && (
                  <button
                    onClick={() => setEditingNotes(true)}
                    className="text-primary-600 hover:text-primary-800 text-sm"
                  >
                    Edit
                  </button>
                )}
              </div>
              {editingNotes ? (
                <div className="space-y-3">
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={6}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Add notes about this donor..."
                  />
                  <div className="flex justify-end space-x-2">
                    <button
                      onClick={() => {
                        setEditingNotes(false)
                        setNotes(donor.notes || '')
                      }}
                      className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveNotes}
                      className="px-3 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700"
                    >
                      Save
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-gray-600">
                  {donor.notes || 'No notes added yet.'}
                </div>
              )}
            </div>

            {/* Documents */}
            {donor.documents && donor.documents.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Documents</h3>
                <div className="space-y-2">
                  {donor.documents.map((doc) => (
                    <a
                      key={doc.id}
                      href={doc.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-3 p-2 rounded-md hover:bg-gray-50"
                    >
                      <DocumentTextIcon className="h-5 w-5 text-gray-400" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{doc.name}</div>
                        <div className="text-xs text-gray-500">{doc.type}</div>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Email Composer */}
          <div className="lg:col-span-2">
            <EmailComposer donor={donor} onEmailSent={handleEmailSent} />
          </div>
        </div>
      </div>
    </Layout>
  )
}

