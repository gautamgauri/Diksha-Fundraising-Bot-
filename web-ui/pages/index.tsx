import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { useSession } from 'next-auth/react'
import Layout from '../components/Layout'
import PipelineTable from '../components/PipelineTable'
import MobilePipelineView from '../components/MobilePipelineView'
import { Donor } from '../types'
import { apiClient } from '../lib/api'
import LoadingSpinner from '../components/LoadingSpinner'
import { useActivityLogger } from '../lib/activity-logger'

export default function PipelinePage() {
  const { data: session } = useSession()
  const router = useRouter()
  const [donors, setDonors] = useState<Donor[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isMobile, setIsMobile] = useState(false)
  const { logDonorUpdate, logBulkUpdate, logExport } = useActivityLogger()

  useEffect(() => {
    loadDonors()
    
    // Check if mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const loadDonors = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getPipeline()
      setDonors(data)
    } catch (err) {
      setError('Failed to load pipeline data')
      console.error('Error loading donors:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDonorClick = (donor: Donor) => {
    router.push(`/donor/${donor.id}`)
  }

  const handleUpdateDonor = async (donorId: string, updates: Partial<Donor>) => {
    try {
      const originalDonor = donors.find(d => d.id === donorId)
      if (!originalDonor) return

      // Update locally first for immediate feedback (optimistic update)
      setDonors(prev => prev.map(donor => 
        donor.id === donorId ? { ...donor, ...updates } : donor
      ))

      // Make API call based on the field being updated
      if (updates.current_stage) {
        await apiClient.updateDonorStage(donorId, updates.current_stage)
        await logDonorUpdate(donorId, 'current_stage', originalDonor.current_stage, updates.current_stage)
      }
      if (updates.assigned_to) {
        await apiClient.updateDonorOwner(donorId, updates.assigned_to)
        await logDonorUpdate(donorId, 'assigned_to', originalDonor.assigned_to, updates.assigned_to)
      }
      if (updates.notes) {
        await apiClient.updateDonorNotes(donorId, updates.notes)
        await logDonorUpdate(donorId, 'notes', originalDonor.notes, updates.notes)
      }
      if (updates.next_action) {
        await apiClient.updateDonorNextAction(donorId, updates.next_action)
        await logDonorUpdate(donorId, 'next_action', originalDonor.next_action, updates.next_action)
      }
      if (updates.next_action_date) {
        await apiClient.updateDonorNextActionDate(donorId, updates.next_action_date)
        await logDonorUpdate(donorId, 'next_action_date', originalDonor.next_action_date, updates.next_action_date)
      }

    } catch (error) {
      console.error('Failed to update donor:', error)
      // Revert local changes on error
      loadDonors()
      throw error
    }
  }

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Donor Pipeline</h1>
            <p className="text-gray-600 mt-1">
              Manage your fundraising pipeline and track donor relationships
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={loadDonors}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Refresh
            </button>
            {(session.user.role === 'admin' || session.user.role === 'fundraising') && (
              <button
                onClick={() => router.push('/donor/new')}
                className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700"
              >
                Add Donor
              </button>
            )}
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Pipeline Table */}
        {isMobile ? (
          <MobilePipelineView
            donors={donors}
            loading={loading}
            onDonorClick={handleDonorClick}
            onUpdateDonor={handleUpdateDonor}
            canEdit={(session.user as any)?.role === 'admin' || (session.user as any)?.role === 'fundraising'}
          />
        ) : (
          <PipelineTable
            donors={donors}
            loading={loading}
            onDonorClick={handleDonorClick}
            onUpdateDonor={handleUpdateDonor}
            onRefresh={loadDonors}
            autoRefresh={true}
            refreshInterval={30000}
          />
        )}

        {/* Pipeline Stats */}
        {!loading && donors.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-2xl font-bold text-gray-900">{donors.length}</div>
              <div className="text-sm text-gray-600">Total Organizations</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-2xl font-bold text-blue-600">
                {donors.filter(d => ['Intro Sent', 'Follow-up Sent', 'Proposal Sent'].includes(d.current_stage)).length}
              </div>
              <div className="text-sm text-gray-600">Active Prospects</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-2xl font-bold text-green-600">
                {donors.filter(d => d.current_stage === 'Closed Won').length}
              </div>
              <div className="text-sm text-gray-600">Closed Won</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-2xl font-bold text-orange-600">
                {donors.filter(d => d.next_action_date && new Date(d.next_action_date) <= new Date()).length}
              </div>
              <div className="text-sm text-gray-600">Overdue Actions</div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
