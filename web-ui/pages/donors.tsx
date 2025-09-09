import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import Layout from '@/components/Layout'
import LoadingSpinner from '@/components/LoadingSpinner'
import { 
  MagnifyingGlassIcon, 
  UserGroupIcon,
  BuildingOfficeIcon,
  MapPinIcon
} from '@heroicons/react/24/outline'
import { Donor } from '@/types'
import { apiClient } from '@/lib/api'

export default function DonorsPage() {
  const { data: session } = useSession()
  const [donors, setDonors] = useState<Donor[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDonors()
  }, [])

  const loadDonors = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getPipeline()
      setDonors(data)
    } catch (err) {
      setError('Failed to load donors')
      console.error('Error loading donors:', err)
    } finally {
      setLoading(false)
    }
  }

  const filteredDonors = donors.filter(donor =>
    donor.organization_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    donor.contact_person?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    donor.sector_tags?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Donors</h1>
            <p className="text-gray-600 mt-1">
              Browse and search donor organizations
            </p>
          </div>
          <div className="text-sm text-gray-500">
            {filteredDonors.length} of {donors.length} organizations
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search organizations, contacts, or sectors..."
            className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="text-sm text-red-700">{error}</div>
          </div>
        )}

        {/* Donors Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDonors.map((donor) => (
            <div
              key={donor.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => window.location.href = `/donor/${donor.id}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <BuildingOfficeIcon className="h-6 w-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {donor.organization_name}
                    </h3>
                    <p className="text-sm text-gray-500 capitalize">
                      {donor.current_stage}
                    </p>
                  </div>
                </div>
                {donor.alignment_score && (
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">
                      {donor.alignment_score}/10
                    </div>
                    <div className="text-xs text-gray-500">Alignment</div>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                {donor.contact_person && (
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <UserGroupIcon className="h-4 w-4" />
                    <span>{donor.contact_person}</span>
                  </div>
                )}
                
                {donor.sector_tags && (
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <MapPinIcon className="h-4 w-4" />
                    <span>{donor.sector_tags}</span>
                  </div>
                )}
                
                {donor.assigned_to && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Assigned to:</span> {donor.assigned_to}
                  </div>
                )}
              </div>

              {donor.next_action && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Next:</span> {donor.next_action}
                  </div>
                  {donor.next_action_date && (
                    <div className="text-xs text-gray-500 mt-1">
                      Due: {new Date(donor.next_action_date).toLocaleDateString()}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {filteredDonors.length === 0 && (
          <div className="text-center py-12">
            <BuildingOfficeIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <div className="text-gray-500 text-lg">No donors found</div>
            <div className="text-gray-400 text-sm mt-2">
              Try adjusting your search query
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

