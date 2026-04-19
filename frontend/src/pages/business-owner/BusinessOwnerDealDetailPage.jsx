import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import MilestoneTracker from '../../components/MilestoneTracker'

function BusinessOwnerDealDetailPage() {
  const { dealId } = useParams()
  const navigate = useNavigate()
  const { token } = useAuthStore()
  const [deal, setDeal] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDeal()
  }, [dealId])

  const fetchDeal = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/deals/${dealId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) throw new Error('Failed to fetch deal')
      
      const data = await response.json()
      setDeal(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'inprogress':
        return 'bg-blue-100 text-blue-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'disputed':
        return 'bg-red-100 text-red-800'
      case 'cancelled':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-yellow-100 text-yellow-800'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading deal...</p>
        </div>
      </div>
    )
  }

  if (error || !deal) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error || 'Deal not found'}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/business-dashboard')}
            className="text-primary-600 hover:text-primary-700 mb-2 flex items-center"
          >
            ← Back to Dashboard
          </button>
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold">Deal Details</h1>
            <span className={`px-3 py-1 text-sm font-semibold rounded ${getStatusColor(deal.status)}`}>
              {deal.status}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Deal Info */}
          <div className="lg:col-span-1">
            <div className="card mb-6">
              <h2 className="text-xl font-bold mb-4">Deal Information</h2>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="font-medium text-gray-600">Total Amount:</span>
                  <p className="text-2xl font-bold text-primary-600">
                    ₹{(deal.amount / 100).toFixed(2)}
                  </p>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Payment Flow:</span>
                  <p className="text-gray-900">{deal.payment_flow}</p>
                </div>
                {deal.package_type && (
                  <div>
                    <span className="font-medium text-gray-600">Package:</span>
                    <p className="text-gray-900">{deal.package_type}</p>
                  </div>
                )}
                <div>
                  <span className="font-medium text-gray-600">Created:</span>
                  <p className="text-gray-900">
                    {new Date(deal.created_at).toLocaleDateString()}
                  </p>
                </div>
                {deal.completed_at && (
                  <div>
                    <span className="font-medium text-gray-600">Completed:</span>
                    <p className="text-gray-900">
                      {new Date(deal.completed_at).toLocaleDateString()}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {deal.description && (
              <div className="card">
                <h2 className="text-xl font-bold mb-3">Description</h2>
                <p className="text-gray-700 text-sm">{deal.description}</p>
              </div>
            )}
          </div>

          {/* Milestones */}
          <div className="lg:col-span-2">
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Project Milestones</h2>
              <MilestoneTracker dealId={dealId} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BusinessOwnerDealDetailPage
