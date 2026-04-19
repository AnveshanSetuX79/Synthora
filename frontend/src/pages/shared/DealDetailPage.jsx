import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { dealsAPI } from '../../services/api'
import MilestoneTracker from '../../components/MilestoneTracker'

function DealDetailPage() {
  const { dealId } = useParams()
  const navigate = useNavigate()
  
  const [deal, setDeal] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updating, setUpdating] = useState(false)

  // Fetch deal details
  const fetchDealDetails = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await dealsAPI.getDealDetails(dealId)
      setDeal(response.data.deal)
    } catch (err) {
      const errorMsg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to fetch deal details'
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (dealId) {
      fetchDealDetails()
    }
  }, [dealId])

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

  // Get milestone status badge
  const getMilestoneStatusBadge = (status) => {
    const statusLower = status?.toLowerCase() || 'pending'
    
    switch (statusLower) {
      case 'paid':
        return 'bg-green-100 text-green-800'
      case 'approved':
        return 'bg-blue-100 text-blue-800'
      case 'submitted':
        return 'bg-purple-100 text-purple-800'
      case 'inprogress':
        return 'bg-yellow-100 text-yellow-800'
      case 'pending':
        return 'bg-gray-100 text-gray-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
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

  // Handle status update
  const handleStatusUpdate = async (newStatus) => {
    if (!confirm(`Are you sure you want to change status to ${newStatus}?`)) {
      return
    }

    setUpdating(true)
    try {
      await dealsAPI.updateDealStatus(dealId, { status: newStatus })
      // Refresh deal details
      const response = await dealsAPI.getDealDetails(dealId)
      setDeal(response.data.deal)
      alert('Deal status updated successfully')
    } catch (err) {
      const errorMsg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to update status'
      alert(errorMsg)
    } finally {
      setUpdating(false)
    }
  }

  // Handle milestone update
  const handleMilestoneUpdate = async (milestoneId, newStatus) => {
    if (!confirm(`Are you sure you want to change milestone status to ${newStatus}?`)) {
      return
    }

    setUpdating(true)
    try {
      await dealsAPI.updateMilestone(dealId, milestoneId, { status: newStatus })
      // Refresh deal details
      const response = await dealsAPI.getDealDetails(dealId)
      setDeal(response.data.deal)
      alert('Milestone status updated successfully')
    } catch (err) {
      const errorMsg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to update milestone'
      alert(errorMsg)
    } finally {
      setUpdating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading deal details...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
          <button onClick={() => navigate('/deals')} className="btn-secondary mt-4">
            Back to Deals
          </button>
        </div>
      </div>
    )
  }

  if (!deal) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <p className="text-gray-600">Deal not found</p>
          <button onClick={() => navigate('/deals')} className="btn-secondary mt-4">
            Back to Deals
          </button>
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
            onClick={() => navigate('/deals')}
            className="text-primary-600 hover:text-primary-700 mb-2 flex items-center"
          >
            ← Back to Deals
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold">{deal.business_name || 'Deal Details'}</h1>
              <p className="text-gray-600">{deal.business_city || ''}</p>
            </div>
            <span className={`px-3 py-1 text-sm font-semibold rounded ${getStatusBadge(deal.status)}`}>
              {deal.status}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Deal Information */}
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Deal Information</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Package:</span>
                  <span className="font-medium capitalize">{deal.package_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Amount:</span>
                  <span className="font-medium">₹{(deal.amount || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Payment Flow:</span>
                  <span className="font-medium">{deal.payment_flow}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Created:</span>
                  <span className="font-medium">{formatDate(deal.created_at)}</span>
                </div>
                {deal.completed_at && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Completed:</span>
                    <span className="font-medium">{formatDate(deal.completed_at)}</span>
                  </div>
                )}
                {deal.description && (
                  <div className="pt-3 border-t">
                    <span className="text-gray-600 block mb-1">Description:</span>
                    <p className="text-gray-900">{deal.description}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Milestone Progress */}
            <MilestoneTracker deal={deal} onUpdate={fetchDealDetails} />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="card">
              <h3 className="text-lg font-bold mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-gray-600">Total Amount</span>
                  <div className="text-2xl font-bold text-primary-600">
                    ₹{(deal.amount || 0).toLocaleString()}
                  </div>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Your Earnings (85%)</span>
                  <div className="text-xl font-bold text-green-600">
                    ₹{((deal.amount || 0) * 0.85).toLocaleString()}
                  </div>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Platform Fee (15%)</span>
                  <div className="text-lg font-medium text-gray-600">
                    ₹{((deal.amount || 0) * 0.15).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="card">
              <h3 className="text-lg font-bold mb-4">Actions</h3>
              <div className="space-y-2">
                {deal.status === 'Pending' && (
                  <>
                    <button
                      onClick={() => navigate(`/payment/${dealId}`)}
                      className="btn-primary w-full"
                    >
                      Make Payment
                    </button>
                    <button
                      onClick={() => handleStatusUpdate('Active')}
                      disabled={updating}
                      className="btn-secondary w-full"
                    >
                      Activate Deal
                    </button>
                  </>
                )}
                {deal.status === 'Active' && (
                  <button
                    onClick={() => handleStatusUpdate('InProgress')}
                    disabled={updating}
                    className="btn-primary w-full"
                  >
                    Start Work
                  </button>
                )}
                {deal.status === 'InProgress' && (
                  <button
                    onClick={() => handleStatusUpdate('Completed')}
                    disabled={updating}
                    className="btn-primary w-full"
                  >
                    Mark as Completed
                  </button>
                )}
                <button
                  onClick={() => navigate(`/outreach/${deal.business_id}`)}
                  className="btn-secondary w-full"
                >
                  Contact Business
                </button>
              </div>
            </div>

            {/* Payment Status */}
            <div className="card">
              <h3 className="text-lg font-bold mb-4">Payment Status</h3>
              <div className="space-y-2 text-sm">
                {deal.milestones && deal.milestones.map((milestone, index) => (
                  <div key={milestone.id} className="flex justify-between">
                    <span className="text-gray-600">Milestone {index + 1}:</span>
                    <span className={`font-medium ${
                      milestone.status === 'Paid' ? 'text-green-600' : 'text-gray-600'
                    }`}>
                      {milestone.status === 'Paid' ? '✓ Paid' : 'Pending'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DealDetailPage
