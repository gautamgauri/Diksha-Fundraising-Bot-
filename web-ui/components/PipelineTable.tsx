import { useState, useEffect, useMemo, useCallback, useDeferredValue } from 'react'
import { 
  MagnifyingGlassIcon, 
  FunnelIcon, 
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  ChevronUpDownIcon,
  DocumentArrowDownIcon,
  ArrowsPointingOutIcon
} from '@heroicons/react/24/outline'
import { Donor, PipelineFilters } from '@/types'
import { apiClient } from '@/lib/api'
import LoadingSpinner from './LoadingSpinner'
import { useSession } from 'next-auth/react'
import { validateDonorUpdate, ValidationResult } from '@/lib/validation'
import { getUserFriendlyMessage, ApiError } from '@/lib/error-handling'

interface PipelineTableProps {
  donors: Donor[]
  loading: boolean
  onDonorClick: (donor: Donor) => void
  onUpdateDonor: (donorId: string, updates: Partial<Donor>) => Promise<void>
  onRefresh?: () => void
  autoRefresh?: boolean
  refreshInterval?: number
}

const stages = [
  'Initial Contact',
  'Intro Sent',
  'Follow-up Sent',
  'Proposal Sent',
  'Thank You Sent',
  'Meeting Scheduled',
  'Negotiation',
  'Closed Won',
  'Closed Lost'
]

const sectors = [
  'Technology',
  'Education',
  'Healthcare',
  'Environment',
  'Social Services',
  'Arts & Culture',
  'Rural Development',
  'Women Empowerment'
]

export default function PipelineTable({ 
  donors, 
  loading, 
  onDonorClick, 
  onUpdateDonor, 
  onRefresh,
  autoRefresh = false,
  refreshInterval = 30000
}: PipelineTableProps) {
  const { data: session } = useSession()
  const [filters, setFilters] = useState<PipelineFilters>({})
  const [showFilters, setShowFilters] = useState(false)
  const [editingCell, setEditingCell] = useState<{ row: string; field: string } | null>(null)
  const [editValue, setEditValue] = useState('')
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const [isUpdating, setIsUpdating] = useState(false)
  
  // Performance optimizations
  const [sortConfig, setSortConfig] = useState<{
    key: keyof Donor | null,
    direction: 'asc' | 'desc'
  }>({ key: null, direction: 'asc' })
  
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 50,
    total: donors.length
  })
  
  const [selectedDonors, setSelectedDonors] = useState<string[]>([])
  const [showBulkActions, setShowBulkActions] = useState(false)
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table')
  const [useVirtualScrolling, setUseVirtualScrolling] = useState(false)
  const [isOnline, setIsOnline] = useState(true)
  const [pendingUpdates, setPendingUpdates] = useState<Array<{ donorId: string; updates: Partial<Donor>; timestamp: number }>>([])

  const canEdit = (session?.user as any)?.role === 'admin' || (session?.user as any)?.role === 'fundraising'

  // Debounced search to prevent excessive filtering
  const deferredSearchTerm = useDeferredValue(filters.search || '')

  // Responsive view mode detection
  useEffect(() => {
    const handleResize = () => {
      setViewMode(window.innerWidth < 768 ? 'cards' : 'table')
    }
    
    handleResize() // Set initial value
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Auto-enable virtual scrolling for large datasets
  useEffect(() => {
    setUseVirtualScrolling(donors.length > 1000)
  }, [donors.length])

  // Offline detection
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      // Process pending updates when back online
      processPendingUpdates()
    }
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    setIsOnline(navigator.onLine)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Process pending updates when back online
  const processPendingUpdates = useCallback(async () => {
    if (pendingUpdates.length === 0) return

    try {
      for (const update of pendingUpdates) {
        await onUpdateDonor(update.donorId, update.updates)
      }
      setPendingUpdates([])
    } catch (error) {
      console.error('Failed to process pending updates:', error)
    }
  }, [pendingUpdates, onUpdateDonor])

  // Auto-refresh effect with proper cleanup
  useEffect(() => {
    if (!autoRefresh || !onRefresh) return

    const interval = setInterval(() => {
      // Check if component is still mounted before calling refresh
      if (document.contains(document.getElementById('pipeline-table'))) {
        onRefresh()
      }
    }, refreshInterval)

    return () => {
      clearInterval(interval)
    }
  }, [autoRefresh, onRefresh, refreshInterval])

  // Update pagination when donors change
  useEffect(() => {
    setPagination(prev => ({ ...prev, total: donors.length }))
  }, [donors.length])

  // Sorting function
  const handleSort = useCallback((key: keyof Donor) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }, [])

  // Get sort icon
  const getSortIcon = (key: keyof Donor) => {
    if (sortConfig.key !== key) {
      return <ChevronUpDownIcon className="h-4 w-4 text-gray-400" />
    }
    return sortConfig.direction === 'asc' 
      ? <ChevronUpIcon className="h-4 w-4 text-gray-600" />
      : <ChevronDownIcon className="h-4 w-4 text-gray-600" />
  }

  // Memoized filtered and sorted data with debounced search
  const processedDonors = useMemo(() => {
    let filtered = donors.filter(donor => {
      if (deferredSearchTerm && !donor.organization_name.toLowerCase().includes(deferredSearchTerm.toLowerCase())) {
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

    // Apply sorting
    if (sortConfig.key) {
      filtered.sort((a, b) => {
        const aVal = a[sortConfig.key!]
        const bVal = b[sortConfig.key!]
        
        if (aVal === bVal) return 0
        
        const comparison = aVal < bVal ? -1 : 1
        return sortConfig.direction === 'asc' ? comparison : -comparison
      })
    }

    return filtered
  }, [donors, deferredSearchTerm, filters.stage, filters.sector, sortConfig])

  // Paginated data
  const paginatedDonors = useMemo(() => {
    const startIndex = (pagination.page - 1) * pagination.pageSize
    const endIndex = startIndex + pagination.pageSize
    return processedDonors.slice(startIndex, endIndex)
  }, [processedDonors, pagination.page, pagination.pageSize])

  // Bulk operations
  const handleSelectAll = useCallback((checked: boolean) => {
    if (checked) {
      setSelectedDonors(paginatedDonors.map(d => d.id))
    } else {
      setSelectedDonors([])
    }
  }, [paginatedDonors])

  const handleSelectDonor = useCallback((donorId: string, checked: boolean) => {
    setSelectedDonors(prev => 
      checked 
        ? [...prev, donorId]
        : prev.filter(id => id !== donorId)
    )
  }, [])

  const handleBulkUpdate = useCallback(async (field: keyof Donor, value: any) => {
    // Add confirmation for destructive operations
    if (field === 'current_stage' && value === 'Closed Lost') {
      const confirmed = window.confirm(
        `Mark ${selectedDonors.length} donors as "Closed Lost"? This action cannot be undone.`
      )
      if (!confirmed) return
    }

    if (field === 'current_stage' && value === 'Closed Won') {
      const confirmed = window.confirm(
        `Mark ${selectedDonors.length} donors as "Closed Won"? This will move them to the final stage.`
      )
      if (!confirmed) return
    }

    try {
      setIsUpdating(true)
      const promises = selectedDonors.map(donorId => 
        onUpdateDonor(donorId, { [field]: value })
      )
      await Promise.all(promises)
      setSelectedDonors([])
      setShowBulkActions(false)
    } catch (error) {
      console.error('Bulk update failed:', error)
    } finally {
      setIsUpdating(false)
    }
  }, [selectedDonors, onUpdateDonor])

  // Export functionality
  const handleExport = useCallback(() => {
    const csvData = processedDonors.map(donor => ({
      Organization: donor.organization_name,
      Stage: donor.current_stage,
      Owner: donor.assigned_to || '',
      'Next Action': donor.next_action || '',
      'Due Date': donor.next_action_date || '',
      'Last Contact': donor.last_contact_date || '',
      Sector: donor.sector_tags || '',
      Probability: donor.probability || '',
      'Contact Person': donor.contact_person || '',
      'Contact Email': donor.contact_email || '',
      Notes: donor.notes || ''
    }))

    const csv = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).map(val => `"${val}"`).join(','))
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `pipeline-export-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }, [processedDonors])

  const handleCellClick = (donorId: string, field: string, currentValue: string) => {
    if (!canEdit) return
    setEditingCell({ row: donorId, field })
    setEditValue(currentValue || '')
  }

  const handleSaveEdit = async (donorId: string, field: string) => {
    try {
      setIsUpdating(true)
      setValidationErrors({})
      
      // Find current donor data for validation
      const currentDonor = donors.find(d => d.id === donorId)
      if (!currentDonor) {
        throw new Error('Donor not found')
      }
      
      // Validate the update
      const updates: Partial<Donor> = { [field]: editValue }
      const validation = validateDonorUpdate(updates, currentDonor)
      
      if (!validation.isValid) {
        const errors: Record<string, string> = {}
        validation.errors.forEach(error => {
          errors[error.field] = error.message
        })
        setValidationErrors(errors)
        return
      }
      
      if (isOnline) {
        await onUpdateDonor(donorId, updates)
      } else {
        // Queue update for when back online
        setPendingUpdates(prev => [...prev, { donorId, updates, timestamp: Date.now() }])
      }
      
      setEditingCell(null)
      setValidationErrors({})
    } catch (error) {
      console.error('Failed to update donor:', error)
      const apiError = error as ApiError
      setValidationErrors({ 
        [field]: getUserFriendlyMessage(apiError) 
      })
    } finally {
      setIsUpdating(false)
    }
  }

  const handleCancelEdit = () => {
    setEditingCell(null)
    setEditValue('')
    setValidationErrors({})
  }

  // Removed duplicate filtering logic - using processedDonors memoized version instead

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
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  // Virtual scrolling row component
  const VirtualTableRow = ({ index, style, data }: { index: number; style: React.CSSProperties; data: Donor[] }) => {
    const donor = data[index]
    if (!donor) return null

    return (
      <div style={style} className="flex items-center border-b border-gray-200 hover:bg-gray-50">
        <div className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 w-1/6">
          {donor.organization_name}
        </div>
        <div className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 w-1/6">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStageColor(donor.current_stage)}`}>
            {donor.current_stage}
          </span>
        </div>
        <div className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 w-1/6">
          {donor.assigned_to || 'Unassigned'}
        </div>
        <div className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 w-1/6">
          {donor.next_action || 'No action'}
        </div>
        <div className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 w-1/6">
          {donor.next_action_date || 'No date'}
        </div>
        <div className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 w-1/6">
          {donor.probability ? `${donor.probability}%` : 'Not set'}
        </div>
      </div>
    )
  }

  // Card view component for mobile
  const DonorCard = ({ donor }: { donor: Donor }) => (
    <div 
      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onDonorClick(donor)}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-medium text-gray-900 mb-1">
            {donor.organization_name}
          </h3>
          <div className="flex items-center space-x-2 mb-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStageColor(donor.current_stage)}`}>
              {donor.current_stage}
            </span>
            {donor.probability && (
              <span className="text-sm text-gray-500">
                {donor.probability}% probability
              </span>
            )}
          </div>
        </div>
        {canEdit && (
          <input
            type="checkbox"
            checked={selectedDonors.includes(donor.id)}
            onChange={(e) => {
              e.stopPropagation()
              handleSelectDonor(donor.id, e.target.checked)
            }}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
        )}
      </div>
      
      <div className="space-y-2 text-sm text-gray-600">
        {donor.assigned_to && (
          <div>Owner: <span className="font-medium">{donor.assigned_to}</span></div>
        )}
        {donor.sector_tags && (
          <div>Sector: <span className="font-medium">{donor.sector_tags}</span></div>
        )}
        {donor.next_action && (
          <div>Next: <span className="font-medium">{donor.next_action}</span></div>
        )}
        {donor.next_action_date && (
          <div>Due: <span className="font-medium">{donor.next_action_date}</span></div>
        )}
      </div>
    </div>
  )

  return (
    <div className="bg-white shadow-sm rounded-lg" id="pipeline-table">
      {/* Header with search and filters */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search organizations..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                value={filters.search || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFilters({ ...filters, search: e.target.value })}
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <FunnelIcon className="h-4 w-4 mr-2" />
              Filters
            </button>
            
            {/* View Mode Toggle */}
            <div className="flex items-center border border-gray-300 rounded-md">
              <button
                onClick={() => setViewMode('table')}
                className={`px-3 py-2 text-sm font-medium ${
                  viewMode === 'table' 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Table
              </button>
              <button
                onClick={() => setViewMode('cards')}
                className={`px-3 py-2 text-sm font-medium ${
                  viewMode === 'cards' 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Cards
              </button>
            </div>

            {/* Performance Indicator */}
            {processedDonors.length > 1000 && (
              <div className="flex items-center text-xs text-gray-500">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Virtual scrolling enabled ({processedDonors.length} donors)
              </div>
            )}

            {/* Offline Indicator */}
            {!isOnline && (
              <div className="flex items-center text-xs text-orange-600">
                <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
                Offline mode - {pendingUpdates.length} pending updates
              </div>
            )}
            {canEdit && (
              <button
                onClick={handleExport}
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
                Export
              </button>
            )}
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-500">
              {processedDonors.length} of {donors.length} organizations
            </div>
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                <ArrowsPointingOutIcon className="h-4 w-4 mr-2" />
                Refresh
              </button>
            )}
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Stage</label>
              <select
                multiple
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                value={filters.stage || []}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                  const values = Array.from(e.target.selectedOptions, (option: HTMLOptionElement) => option.value)
                  setFilters({ ...filters, stage: values })
                }}
              >
                {stages.map(stage => (
                  <option key={stage} value={stage}>{stage}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sector</label>
              <select
                multiple
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                value={filters.sector || []}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                  const values = Array.from(e.target.selectedOptions, (option: HTMLOptionElement) => option.value)
                  setFilters({ ...filters, sector: values })
                }}
              >
                {sectors.map(sector => (
                  <option key={sector} value={sector}>{sector}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setFilters({})}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Clear Filters
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Bulk Actions Bar */}
      {selectedDonors.length > 0 && (
        <div className="px-6 py-3 bg-primary-50 border-b border-primary-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-primary-900">
                {selectedDonors.length} donor{selectedDonors.length > 1 ? 's' : ''} selected
              </span>
              <div className="flex items-center space-x-2">
                <select
                  onChange={(e) => handleBulkUpdate('current_stage', e.target.value)}
                  className="text-sm border border-primary-300 rounded px-2 py-1"
                  disabled={isUpdating}
                >
                  <option value="">Update Stage</option>
                  {stages.map(stage => (
                    <option key={stage} value={stage}>{stage}</option>
                  ))}
                </select>
                <input
                  type="text"
                  placeholder="Assign to..."
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleBulkUpdate('assigned_to', (e.target as HTMLInputElement).value)
                    }
                  }}
                  className="text-sm border border-primary-300 rounded px-2 py-1"
                  disabled={isUpdating}
                />
              </div>
            </div>
            <button
              onClick={() => {
                setSelectedDonors([])
                setShowBulkActions(false)
              }}
              className="text-sm text-primary-600 hover:text-primary-800"
            >
              Clear Selection
            </button>
          </div>
        </div>
      )}

      {/* Content - Table or Cards */}
      {viewMode === 'table' ? (
        useVirtualScrolling ? (
          /* Virtual Scrolling Table for Large Datasets */
          <div className="h-96 overflow-auto">
            <div className="min-w-full">
              {/* Table Header */}
              <div className="bg-gray-50 flex items-center border-b border-gray-200 sticky top-0 z-10">
                <div className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                  Organization
                </div>
                <div className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                  Stage
                </div>
                <div className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                  Owner
                </div>
                <div className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                  Next Action
                </div>
                <div className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                  Due Date
                </div>
                <div className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                  Probability
                </div>
              </div>
              {/* Virtual Rows */}
              {processedDonors.map((donor, index) => (
                <VirtualTableRow 
                  key={donor.id} 
                  index={index} 
                  style={{}} 
                  data={processedDonors}
                />
              ))}
            </div>
          </div>
        ) : (
          /* Regular Table */
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {canEdit && (
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedDonors.length === paginatedDonors.length && paginatedDonors.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                </th>
              )}
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('organization_name')}
              >
                <div className="flex items-center space-x-1">
                  <span>Organization</span>
                  {getSortIcon('organization_name')}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('current_stage')}
              >
                <div className="flex items-center space-x-1">
                  <span>Stage</span>
                  {getSortIcon('current_stage')}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('assigned_to')}
              >
                <div className="flex items-center space-x-1">
                  <span>Owner</span>
                  {getSortIcon('assigned_to')}
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Next Action
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('next_action_date')}
              >
                <div className="flex items-center space-x-1">
                  <span>Due Date</span>
                  {getSortIcon('next_action_date')}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('last_contact_date')}
              >
                <div className="flex items-center space-x-1">
                  <span>Last Contact</span>
                  {getSortIcon('last_contact_date')}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('sector_tags')}
              >
                <div className="flex items-center space-x-1">
                  <span>Sector</span>
                  {getSortIcon('sector_tags')}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('probability')}
              >
                <div className="flex items-center space-x-1">
                  <span>Probability</span>
                  {getSortIcon('probability')}
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedDonors.map((donor) => (
              <tr
                key={donor.id}
                className="hover:bg-gray-50 cursor-pointer"
                onClick={() => onDonorClick(donor)}
              >
                {canEdit && (
                  <td className="px-6 py-4 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={selectedDonors.includes(donor.id)}
                      onChange={(e) => handleSelectDonor(donor.id, e.target.checked)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                  </td>
                )}
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {donor.organization_name}
                  </div>
                  {donor.alignment_score && (
                    <div className="text-sm text-gray-500">
                      Score: {donor.alignment_score}/10
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {editingCell?.row === donor.id && editingCell?.field === 'current_stage' ? (
                    <div className="flex items-center space-x-2">
                      <select
                        value={editValue}
                        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setEditValue(e.target.value)}
                        className="text-sm border border-gray-300 rounded px-2 py-1"
                        onClick={(e: React.MouseEvent) => e.stopPropagation()}
                      >
                        {stages.map(stage => (
                          <option key={stage} value={stage}>{stage}</option>
                        ))}
                      </select>
                      <button
                        onClick={(e: React.MouseEvent) => {
                          e.stopPropagation()
                          handleSaveEdit(donor.id, 'current_stage')
                        }}
                        disabled={isUpdating}
                        className="text-green-600 hover:text-green-800 disabled:opacity-50"
                      >
                        <CheckIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e: React.MouseEvent) => {
                          e.stopPropagation()
                          handleCancelEdit()
                        }}
                        className="text-red-600 hover:text-red-800"
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStageColor(donor.current_stage)} ${
                        canEdit ? 'cursor-pointer hover:bg-opacity-80' : ''
                      }`}
                      onClick={(e: React.MouseEvent) => {
                        e.stopPropagation()
                        if (canEdit) {
                          handleCellClick(donor.id, 'current_stage', donor.current_stage)
                        }
                      }}
                    >
                      {donor.current_stage}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {editingCell?.row === donor.id && editingCell?.field === 'assigned_to' ? (
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={editValue}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEditValue(e.target.value)}
                        className="text-sm border border-gray-300 rounded px-2 py-1 w-32"
                        onClick={(e: React.MouseEvent) => e.stopPropagation()}
                      />
                      <button
                        onClick={(e: React.MouseEvent) => {
                          e.stopPropagation()
                          handleSaveEdit(donor.id, 'assigned_to')
                        }}
                        className="text-green-600 hover:text-green-800"
                      >
                        <CheckIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e: React.MouseEvent) => {
                          e.stopPropagation()
                          handleCancelEdit()
                        }}
                        className="text-red-600 hover:text-red-800"
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <span
                      className={canEdit ? 'cursor-pointer hover:bg-gray-100 px-2 py-1 rounded' : ''}
                      onClick={(e: React.MouseEvent) => {
                        e.stopPropagation()
                        if (canEdit) {
                          handleCellClick(donor.id, 'assigned_to', donor.assigned_to || '')
                        }
                      }}
                    >
                      {donor.assigned_to || 'Unassigned'}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {editingCell?.row === donor.id && editingCell?.field === 'next_action' ? (
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={editValue}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEditValue(e.target.value)}
                        className="text-sm border border-gray-300 rounded px-2 py-1 w-40"
                        onClick={(e: React.MouseEvent) => e.stopPropagation()}
                      />
                      <button
                        onClick={(e: React.MouseEvent) => {
                          e.stopPropagation()
                          handleSaveEdit(donor.id, 'next_action')
                        }}
                        className="text-green-600 hover:text-green-800"
                      >
                        <CheckIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e: React.MouseEvent) => {
                          e.stopPropagation()
                          handleCancelEdit()
                        }}
                        className="text-red-600 hover:text-red-800"
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <span
                      className={canEdit ? 'cursor-pointer hover:bg-gray-100 px-2 py-1 rounded' : ''}
                      onClick={(e: React.MouseEvent) => {
                        e.stopPropagation()
                        if (canEdit) {
                          handleCellClick(donor.id, 'next_action', donor.next_action || '')
                        }
                      }}
                    >
                      {donor.next_action || 'No action set'}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {editingCell?.row === donor.id && editingCell?.field === 'next_action_date' ? (
                    <div className="flex items-center space-x-2">
                      <input
                        type="date"
                        value={editValue}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEditValue(e.target.value)}
                        className="text-sm border border-gray-300 rounded px-2 py-1"
                        onClick={(e: React.MouseEvent) => e.stopPropagation()}
                      />
                      <button
                        onClick={(e: React.MouseEvent) => {
                          e.stopPropagation()
                          handleSaveEdit(donor.id, 'next_action_date')
                        }}
                        className="text-green-600 hover:text-green-800"
                      >
                        <CheckIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e: React.MouseEvent) => {
                          e.stopPropagation()
                          handleCancelEdit()
                        }}
                        className="text-red-600 hover:text-red-800"
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <span
                      className={canEdit ? 'cursor-pointer hover:bg-gray-100 px-2 py-1 rounded' : ''}
                      onClick={(e: React.MouseEvent) => {
                        e.stopPropagation()
                        if (canEdit) {
                          handleCellClick(donor.id, 'next_action_date', donor.next_action_date || '')
                        }
                      }}
                    >
                      {donor.next_action_date || 'No date set'}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {donor.last_contact_date || 'Never'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {donor.sector_tags || 'Not specified'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {donor.probability ? `${donor.probability}%` : 'Not set'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
        )
      ) : (
        /* Cards View */
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {paginatedDonors.map((donor) => (
              <DonorCard key={donor.id} donor={donor} />
            ))}
          </div>
        </div>
      )}

      {processedDonors.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">No organizations found</div>
          <div className="text-gray-400 text-sm mt-2">
            Try adjusting your search or filters
          </div>
        </div>
      )}

      {/* Pagination */}
      {processedDonors.length > pagination.pageSize && (
        <div className="px-6 py-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {((pagination.page - 1) * pagination.pageSize) + 1} to{' '}
              {Math.min(pagination.page * pagination.pageSize, processedDonors.length)} of{' '}
              {processedDonors.length} results
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPagination(prev => ({ ...prev, page: Math.max(1, prev.page - 1) }))}
                disabled={pagination.page === 1}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="px-3 py-1 text-sm text-gray-700">
                Page {pagination.page} of {Math.ceil(processedDonors.length / pagination.pageSize)}
              </span>
              <button
                onClick={() => setPagination(prev => ({ 
                  ...prev, 
                  page: Math.min(Math.ceil(processedDonors.length / pagination.pageSize), prev.page + 1) 
                }))}
                disabled={pagination.page >= Math.ceil(processedDonors.length / pagination.pageSize)}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Validation Errors */}
      {Object.keys(validationErrors).length > 0 && (
        <div className="px-6 py-4 bg-red-50 border-t border-red-200">
          <div className="flex items-center space-x-2">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
            <div className="text-sm text-red-700">
              <strong>Validation Error:</strong> {Object.values(validationErrors)[0]}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
