import { useState } from 'react'
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  UserIcon,
  CalendarIcon,
  TagIcon
} from '@heroicons/react/24/outline'
import { Donor, PipelineFilters } from '@/types'
import { useActivityLogger } from '@/lib/activity-logger'

interface MobilePipelineViewProps {
  donors: Donor[]
  loading: boolean
  onDonorClick: (donor: Donor) => void
  onUpdateDonor: (donorId: string, updates: Partial<Donor>) => Promise<void>
  canEdit: boolean
}

export default function MobilePipelineView({ 
  donors, 
  loading, 
  onDonorClick, 
  onUpdateDonor, 
  canEdit 
}: MobilePipelineViewProps) {
  const [filters, setFilters] = useState<PipelineFilters>({})
  const [showFilters, setShowFilters] = useState(false)
  const [expandedDonor, setExpandedDonor] = useState<string | null>(null)
  const { logPipelineView } = useActivityLogger()

  const filteredDonors = donors.filter(donor => {
    if (filters.search && !donor.organization_name.toLowerCase().includes(filters.search.toLowerCase())) {
      return false
    }
    if (filters.stage && filters.stage.length > 0 && !filters.stage.includes(donor.current_stage)) {
      return false
    }
    if (filters.sector && filters.sector.length > 0 && !filters.sector.some((s: string) => donor.sector_tags?.includes(s))) {
      return false
    }
    return true
  })

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'Initial Contact': return 'bg-blue-100 text-blue-800'
      case 'Intro Sent': return 'bg-yellow-100 text-yellow-800'
      case 'Follow-up Sent': return 'bg-orange-100 text-orange-800'
      case 'Proposal Sent': return 'bg-purple-100 text-purple-800'
      case 'Meeting Scheduled': return 'bg-indigo-100 text-indigo-800'
      case 'Negotiation': return 'bg-pink-100 text-pink-800'
      case 'Closed Won': return 'bg-green-100 text-green-800'
      case 'Closed Lost': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleFilterChange = (newFilters: PipelineFilters) => {
    setFilters(newFilters)
    logPipelineView(newFilters)
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="space-y-3">
          <div className="relative">
            <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search organizations..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              value={filters.search || ''}
              onChange={(e) => handleFilterChange({ ...filters, search: e.target.value })}
            />
          </div>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-50 border border-gray-300 rounded-md hover:bg-gray-100"
          >
            <FunnelIcon className="h-4 w-4 mr-2" />
            Filters
            {showFilters ? (
              <ChevronUpIcon className="h-4 w-4 ml-2" />
            ) : (
              <ChevronDownIcon className="h-4 w-4 ml-2" />
            )}
          </button>

          {showFilters && (
            <div className="space-y-3 pt-3 border-t border-gray-200">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Stage</label>
                <select
                  multiple
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  value={filters.stage || []}
                  onChange={(e) => {
                    const values = Array.from(e.target.selectedOptions, (option) => option.value)
                    handleFilterChange({ ...filters, stage: values })
                  }}
                >
                  <option value="Initial Contact">Initial Contact</option>
                  <option value="Intro Sent">Intro Sent</option>
                  <option value="Follow-up Sent">Follow-up Sent</option>
                  <option value="Proposal Sent">Proposal Sent</option>
                  <option value="Meeting Scheduled">Meeting Scheduled</option>
                  <option value="Negotiation">Negotiation</option>
                  <option value="Closed Won">Closed Won</option>
                  <option value="Closed Lost">Closed Lost</option>
                </select>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Donor Cards */}
      <div className="space-y-3">
        {filteredDonors.map((donor) => (
          <div
            key={donor.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
          >
            <div 
              className="p-4 cursor-pointer"
              onClick={() => onDonorClick(donor)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {donor.organization_name}
                  </h3>
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStageColor(donor.current_stage)}`}>
                      {donor.current_stage}
                    </span>
                    {donor.probability && (
                      <span className="text-sm text-gray-600">
                        {donor.probability}% probability
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setExpandedDonor(expandedDonor === donor.id ? null : donor.id)
                  }}
                  className="p-1 text-gray-400 hover:text-gray-600"
                >
                  {expandedDonor === donor.id ? (
                    <ChevronUpIcon className="h-5 w-5" />
                  ) : (
                    <ChevronDownIcon className="h-5 w-5" />
                  )}
                </button>
              </div>

              <div className="space-y-2 text-sm text-gray-600">
                {donor.assigned_to && (
                  <div className="flex items-center space-x-2">
                    <UserIcon className="h-4 w-4" />
                    <span>{donor.assigned_to}</span>
                  </div>
                )}
                
                {donor.next_action && (
                  <div className="flex items-center space-x-2">
                    <CalendarIcon className="h-4 w-4" />
                    <span>{donor.next_action}</span>
                    {donor.next_action_date && (
                      <span className="text-xs text-gray-500">
                        (Due: {new Date(donor.next_action_date).toLocaleDateString()})
                      </span>
                    )}
                  </div>
                )}
                
                {donor.sector_tags && (
                  <div className="flex items-center space-x-2">
                    <TagIcon className="h-4 w-4" />
                    <span>{donor.sector_tags}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Expanded Details */}
            {expandedDonor === donor.id && (
              <div className="px-4 pb-4 border-t border-gray-100">
                <div className="pt-3 space-y-3">
                  {donor.contact_person && (
                    <div>
                      <span className="text-sm font-medium text-gray-700">Contact:</span>
                      <span className="text-sm text-gray-600 ml-2">{donor.contact_person}</span>
                    </div>
                  )}
                  
                  {donor.contact_email && (
                    <div>
                      <span className="text-sm font-medium text-gray-700">Email:</span>
                      <span className="text-sm text-gray-600 ml-2">{donor.contact_email}</span>
                    </div>
                  )}
                  
                  {donor.last_contact_date && (
                    <div>
                      <span className="text-sm font-medium text-gray-700">Last Contact:</span>
                      <span className="text-sm text-gray-600 ml-2">
                        {new Date(donor.last_contact_date).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                  
                  {donor.notes && (
                    <div>
                      <span className="text-sm font-medium text-gray-700">Notes:</span>
                      <p className="text-sm text-gray-600 mt-1">{donor.notes}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredDonors.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">No organizations found</div>
          <div className="text-gray-400 text-sm mt-2">
            Try adjusting your search or filters
          </div>
        </div>
      )}
    </div>
  )
}

