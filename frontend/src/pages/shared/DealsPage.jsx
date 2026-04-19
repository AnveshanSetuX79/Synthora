import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { dealsAPI } from '../../services/api'

function DealsPage() {
  const navigate = useNavigate()
  
  const [deals, setDeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [statusFilter, setStatusFilter] = useState('all')

  // Fetch deals
  useEffect(() => {
    const fetchDeals = async () => {
      setLoading(true)
      setError(null)

      try {
        const params = statusFilter !== 'all' ? { status: statusFilter } : {}
        const response = await dealsAPI.getMyDeals(params)
        setDeals(response.data.deals || [])
      } catch (err) {
        const errorMsg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to fetch deals'
        setError(errorMsg)
      } finally {
        setLoading(false)
      }
    }

    fetchDeals()
  }, [statusFilter])

  // Get status badge color
  const getStatusBadge = (status) => {
    const statusLower = status?.toLowerCase() || 'pending'
    
    switch (statusLower) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'active':
      case 'inprogress':
        return 'bg-blue-100 text-blue-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'disputed':
        return 'bg-red-100 text-red-800'
      case 'cancelled':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading deals...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Deals</h1>
        </div>

        {/* Status Filter */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          <button
            onClick={() => setStatusFilter('all')}
            className={`px-4 py-2 rounded whitespace-nowrap ${
              statusFilter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border'
            }`}
          >
            All ({deals.length})
          </button>
          <button
            onClick={() => setStatusFilter('Pending')}
            className={`px-4 py-2 rounded whitespace-nowrap ${
              statusFilter === 'Pending'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setStatusFilter('Active')}
            className={`px-4 py-2 rounded whitespace-nowrap ${
              statusFilter === 'Active'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border'
            }`}
          >
            Active
          </button>
          <button
            onClick={() => setStatusFilter('InProgress')}
            className={`px-4 py-2 rounded whitespace-nowrap ${
              statusFilter === 'InProgress'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border'
            }`}
          >
            In Progress
          </button>
          <button
            onClick={() => setStatusFilter('Completed')}
            className={`px-4 py-2 rounded whitespace-nowrap ${
              statusFilter === 'Completed'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border'
            }`}
          >
            Completed
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Deals Table */}
        {deals.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-600">No deals found</p>
            <p className="text-sm text-gray-500 mt-1">
              Create your first deal from a claimed lead
            </p>
          </div>
        ) : (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Business
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Package
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {deals.map((deal) => (
                    <tr key={deal.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">
                          {deal.business_name || 'Unknown Business'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {deal.business_city || ''}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900 capitalize">
                          {deal.package_type || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">
                          ₹{(deal.amount || 0).toLocaleString()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded ${getStatusBadge(deal.status)}`}>
                          {deal.status || 'Pending'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(deal.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => navigate(`/deals/${deal.id}`)}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DealsPage
