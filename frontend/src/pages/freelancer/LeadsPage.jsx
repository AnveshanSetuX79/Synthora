import { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { leadsAPI } from '../../services/api'
import { useLeadsStore } from '../../store/leadsStore'
import { useAuthStore } from '../../store/authStore'
import MapView from '../../components/MapView'
import InsightPanel from '../../components/InsightPanel'

function LeadsPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuthStore()
  const { leads, setLeads, filters, updateFilters, clearFilters } = useLeadsStore()
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [view, setView] = useState('available') // 'available' or 'my-leads'
  const [viewMode, setViewMode] = useState('table') // 'table' or 'map'
  const [selectedLead, setSelectedLead] = useState(null)
  const [sortBy, setSortBy] = useState('score') // 'score', 'freshness', 'date'
  const [sortOrder, setSortOrder] = useState('desc')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [claiming, setClaiming] = useState(null)
  const [userLocation, setUserLocation] = useState(null)
  const [locationSuggestion, setLocationSuggestion] = useState(null)
  const [remainingContacts, setRemainingContacts] = useState(null)
  const [dailyLimit, setDailyLimit] = useState(null)
  const initialFetchDone = useRef(false)

  // Detect user location on mount
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          setUserLocation({ lat: latitude, lng: longitude })
          // You can use reverse geocoding here to get city name
          setLocationSuggestion(`Detected location: ${latitude.toFixed(2)}, ${longitude.toFixed(2)}`)
        },
        (error) => {
          // Silently handle location denial - it's a normal user choice
          if (error.code === 1) {
            // User denied permission
            setLocationSuggestion('Enable location to see nearby leads')
          } else {
            // Other errors (timeout, unavailable)
            setLocationSuggestion('Location unavailable')
          }
        }
      )
    }
  }, [])

  // Fetch leads
  const fetchLeads = async () => {
    setLoading(true)
    setError(null)

    try {
      const params = {
        ...filters,
        sort_by: sortBy,
        sort_order: sortOrder,
        page,
        limit: 20,
      }

      const response = view === 'available' 
        ? await leadsAPI.getAvailableLeads(params)
        : await leadsAPI.getMyLeads(params)

      setLeads(response.data.leads || [])
      setTotalPages(response.data.total_pages || 1)
      
      // Store remaining contacts info from available leads response
      if (view === 'available' && response.data.remaining_allocations !== undefined) {
        setRemainingContacts(response.data.remaining_allocations)
        setDailyLimit(response.data.daily_limit)
      }
    } catch (err) {
      setError(err.response?.data?.detail?.message || 'Failed to fetch leads')
    } finally {
      setLoading(false)
    }
  }

  // Initial fetch only
  useEffect(() => {
    if (!initialFetchDone.current) {
      fetchLeads()
      initialFetchDone.current = true
    }
  }, [])

  // Fetch when returning from discover page
  useEffect(() => {
    if (location.state?.fromDiscover) {
      fetchLeads()
      // Clear the state so it doesn't refetch on every render
      window.history.replaceState({}, document.title)
    }
  }, [location])

  // Fetch when view changes
  useEffect(() => {
    if (initialFetchDone.current) {
      setPage(1)
      fetchLeads()
    }
  }, [view])

  // Handle claim lead
  const handleClaimLead = async (leadId) => {
    setClaiming(leadId)
    try {
      await leadsAPI.claimLead(leadId)
      fetchLeads() // Refresh list
      alert('Lead claimed successfully! You have 6 hours of exclusivity.')
    } catch (err) {
      alert(err.response?.data?.detail?.message || 'Failed to claim lead')
    } finally {
      setClaiming(null)
    }
  }

  // Handle filter change (don't fetch immediately)
  const handleFilterChange = (key, value) => {
    updateFilters({ [key]: value })
  }

  // Apply filters and fetch
  const applyFilters = () => {
    setPage(1) // Reset to first page
    fetchLeads()
  }

  // Clear filters and fetch
  const handleClearFilters = () => {
    clearFilters()
    setPage(1)
    fetchLeads()
  }

  // Handle sort change
  const handleSortChange = (newSortBy) => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(newSortBy)
      setSortOrder('desc')
    }
    setPage(1)
    fetchLeads() // Fetch immediately on sort change
  }

  // Handle page change
  const handlePageChange = (newPage) => {
    setPage(newPage)
    fetchLeads() // Fetch immediately on page change
  }

  // Get score badge color
  const getScoreBadge = (score) => {
    if (score >= 80) return 'bg-green-100 text-green-800'
    if (score >= 50) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  // Get freshness badge color
  const getFreshnessBadge = (freshness) => {
    if (freshness === 'High') return 'bg-green-100 text-green-800'
    if (freshness === 'Medium') return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Leads</h1>
          <div className="flex gap-2">
            {/* View Mode Toggle */}
            <div className="flex border rounded overflow-hidden">
              <button
                onClick={() => setViewMode('table')}
                className={`px-4 py-2 ${
                  viewMode === 'table'
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700'
                }`}
                title="Table View"
              >
                📋 Table
              </button>
              <button
                onClick={() => setViewMode('map')}
                className={`px-4 py-2 ${
                  viewMode === 'map'
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700'
                }`}
                title="Map View"
              >
                🗺️ Map
              </button>
            </div>
            
            <button
              onClick={() => navigate('/leads/discover')}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              🔍 Discover New Leads
            </button>
            <button
              onClick={() => { setView('available'); setPage(1); }}
              className={`px-4 py-2 rounded ${
                view === 'available'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 border'
              }`}
            >
              Available Leads
            </button>
            <button
              onClick={() => { setView('my-leads'); setPage(1); }}
              className={`px-4 py-2 rounded ${
                view === 'my-leads'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 border'
              }`}
            >
              My Leads
            </button>
          </div>
        </div>

        {/* Daily Limit Banner - Only show for available leads */}
        {view === 'available' && remainingContacts !== null && (
          <div className={`card mb-6 ${remainingContacts === 0 ? 'bg-red-50 border-red-200' : 'bg-blue-50 border-blue-200'}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className={`font-semibold ${remainingContacts === 0 ? 'text-red-900' : 'text-blue-900'}`}>
                  {remainingContacts === 0 ? '⚠️ Daily Limit Reached' : '📊 Daily Contact Limit'}
                </h3>
                <p className={`text-sm mt-1 ${remainingContacts === 0 ? 'text-red-700' : 'text-blue-700'}`}>
                  {remainingContacts === 0 
                    ? `You've used all ${dailyLimit} of your daily lead contacts. Your limit will reset at midnight.`
                    : `You have ${remainingContacts} of ${dailyLimit} lead contacts remaining today.`
                  }
                </p>
              </div>
              {remainingContacts === 0 && (
                <button
                  onClick={() => navigate('/profile')}
                  className="btn-primary"
                >
                  Upgrade Tier
                </button>
              )}
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="card mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={filters.category || ''}
                onChange={(e) => handleFilterChange('category', e.target.value || null)}
                className="input-field"
              >
                <option value="">All Categories</option>
                <option value="restaurant">Restaurant</option>
                <option value="school">School</option>
                <option value="retail">Retail</option>
                <option value="healthcare">Healthcare</option>
              </select>
            </div>

            {/* Score Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Score
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={filters.scoreMin || ''}
                onChange={(e) => handleFilterChange('scoreMin', e.target.value ? parseInt(e.target.value) : null)}
                className="input-field"
                placeholder="0-100"
              />
            </div>

            {/* Freshness Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Freshness
              </label>
              <select
                value={filters.freshness || ''}
                onChange={(e) => handleFilterChange('freshness', e.target.value || null)}
                className="input-field"
              >
                <option value="">All</option>
                <option value="High">High (&lt;7 days)</option>
                <option value="Medium">Medium (7-30 days)</option>
                <option value="Low">Low (&gt;30 days)</option>
              </select>
            </div>

            {/* Status Filter (for My Leads) */}
            {view === 'my-leads' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => handleFilterChange('status', e.target.value || null)}
                  className="input-field"
                >
                  <option value="">All</option>
                  <option value="claimed">Claimed</option>
                  <option value="contacted">Contacted</option>
                  <option value="demo_sent">Demo Sent</option>
                  <option value="in_negotiation">In Negotiation</option>
                  <option value="closed">Closed</option>
                  <option value="cold">Cold</option>
                </select>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-end gap-2">
              <button
                onClick={applyFilters}
                className="btn-primary flex-1"
              >
                Apply Filters
              </button>
              <button
                onClick={handleClearFilters}
                className="btn-secondary flex-1"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Location Suggestion */}
          {locationSuggestion && (
            <div className="mt-4 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-2 rounded text-sm">
              📍 {locationSuggestion}
              {userLocation && (
                <button
                  onClick={() => navigate(`/leads/discover?lat=${userLocation.lat}&lng=${userLocation.lng}`)}
                  className="ml-2 text-blue-800 underline hover:text-blue-900"
                >
                  Discover leads near you
                </button>
              )}
            </div>
          )}
        </div>

        {/* Sort Controls */}
        <div className="flex justify-between items-center mb-4">
          <div className="flex gap-2">
            <button
              onClick={() => handleSortChange('score')}
              className={`px-3 py-1 text-sm rounded ${
                sortBy === 'score' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100'
              }`}
            >
              Score {sortBy === 'score' && (sortOrder === 'asc' ? '↑' : '↓')}
            </button>
            <button
              onClick={() => handleSortChange('freshness')}
              className={`px-3 py-1 text-sm rounded ${
                sortBy === 'freshness' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100'
              }`}
            >
              Freshness {sortBy === 'freshness' && (sortOrder === 'asc' ? '↑' : '↓')}
            </button>
            <button
              onClick={() => handleSortChange('date')}
              className={`px-3 py-1 text-sm rounded ${
                sortBy === 'date' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100'
              }`}
            >
              Date {sortBy === 'date' && (sortOrder === 'asc' ? '↑' : '↓')}
            </button>
          </div>
          <p className="text-sm text-gray-600">
            {leads.length} leads found
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="card text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading leads...</p>
          </div>
        ) : leads.length === 0 ? (
          <div className="card text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-gray-600 text-lg mb-2">No leads found</p>
            <p className="text-gray-500 text-sm mb-6">
              {view === 'available' 
                ? remainingContacts === 0
                  ? 'You have reached your daily contact limit. Come back tomorrow or upgrade your tier.'
                  : 'Discover new leads to get started'
                : "You haven't claimed any leads yet"}
            </p>
            {view === 'available' && remainingContacts !== 0 && (
              <button
                onClick={() => navigate('/leads/discover')}
                className="btn-primary"
              >
                🔍 Discover New Leads
              </button>
            )}
          </div>
        ) : viewMode === 'map' ? (
          /* Map View */
          <div className="flex gap-4" style={{ minHeight: '600px' }}>
            <div className={`${selectedLead ? 'w-2/3' : 'w-full'} transition-all duration-300`}>
              <MapView
                leads={leads}
                onLeadSelect={setSelectedLead}
                selectedLeadId={selectedLead?.lead_id}
                userLocation={userLocation}
                className="h-full"
              />
            </div>
            {selectedLead && (
              <div className="w-1/3">
                <InsightPanel
                  lead={selectedLead}
                  onClose={() => setSelectedLead(null)}
                  onClaim={view === 'available' ? handleClaimLead : null}
                  onViewDetails={() => navigate(`/leads/${selectedLead.lead_id}`)}
                  claiming={claiming === selectedLead.lead_id}
                  canClaim={view === 'available' && remainingContacts > 0}
                />
              </div>
            )}
          </div>
        ) : (
          <>
            {/* Leads Table */}
            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Business
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Category
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Score
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Freshness
                      </th>
                      {view === 'my-leads' && (
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                      )}
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {leads.map((lead) => (
                      <tr key={lead.lead_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {lead.business_name || lead.business?.name || 'Unknown Business'}
                            </div>
                            <div className="text-sm text-gray-500">
                              📍 {lead.address || lead.business?.address || lead.city || lead.business?.city || 'Unknown Location'}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-gray-900 capitalize">
                            {lead.category || lead.business?.category || 'N/A'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-semibold rounded ${getScoreBadge(lead.score)}`}>
                            {lead.score}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-semibold rounded ${getFreshnessBadge(lead.freshness)}`}>
                            {lead.freshness}
                          </span>
                        </td>
                        {view === 'my-leads' && (
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-sm text-gray-900 capitalize">
                              {lead.status?.replace('_', ' ') || 'N/A'}
                            </span>
                          </td>
                        )}
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => navigate(`/leads/${lead.lead_id}`)}
                            className="text-primary-600 hover:text-primary-900 mr-4"
                          >
                            View Details
                          </button>
                          {view === 'available' && (
                            <button
                              onClick={() => handleClaimLead(lead.lead_id)}
                              disabled={claiming === lead.lead_id || remainingContacts === 0}
                              className={`btn-primary text-sm py-1 px-3 ${remainingContacts === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
                              title={remainingContacts === 0 ? 'Daily limit reached' : 'Claim this lead'}
                            >
                              {claiming === lead.lead_id ? 'Claiming...' : remainingContacts === 0 ? 'Limit Reached' : 'Claim Lead'}
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-6">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className="px-4 py-2 border rounded disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page === totalPages}
                  className="px-4 py-2 border rounded disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default LeadsPage
