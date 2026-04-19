import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

function BusinessOwnerDashboard() {
  const navigate = useNavigate()
  const { user, token } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [dashboard, setDashboard] = useState(null)
  const [freelancers, setFreelancers] = useState([])
  const [deals, setDeals] = useState([])

  useEffect(() => {
    // Check if onboarding is complete
    const onboardingComplete = localStorage.getItem('businessOwnerOnboardingComplete')
    if (!onboardingComplete) {
      navigate('/business-onboarding')
      return
    }
    
    fetchDashboard()
    fetchFreelancers()
    fetchDeals()
  }, [])

  const fetchDashboard = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/business-owners/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) throw new Error('Failed to fetch dashboard')
      
      const data = await response.json()
      setDashboard(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchFreelancers = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/business-owners/freelancers', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) throw new Error('Failed to fetch freelancers')
      
      const data = await response.json()
      setFreelancers(data)
    } catch (err) {
      console.error('Error fetching freelancers:', err)
    }
  }

  const fetchDeals = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/deals', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) throw new Error('Failed to fetch deals')
      
      const data = await response.json()
      setDeals(data.filter(deal => deal.status.toLowerCase() !== 'cancelled'))
    } catch (err) {
      console.error('Error fetching deals:', err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading dashboard...</p>
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
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Welcome, {dashboard?.owner_name}!</h1>
          <p className="text-gray-600">Manage your business and connect with freelancers</p>
        </div>

        {/* Business Info Card */}
        {dashboard?.business_id && (
          <div className="card mb-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h2 className="text-2xl font-bold mb-2">{dashboard.business_name}</h2>
                <p className="text-gray-600 mb-1">
                  <span className="font-medium">Category:</span> {dashboard.business_category}
                </p>
                <p className="text-gray-600">
                  <span className="font-medium">Address:</span> {dashboard.business_address}
                </p>
              </div>
              {dashboard.demo_url && (
                <button
                  onClick={() => window.open(dashboard.demo_url, '_blank')}
                  className="btn-primary"
                >
                  🌐 View Demo Website
                </button>
              )}
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="card">
            <div className="text-sm text-gray-600 mb-1">Active Deals</div>
            <div className="text-3xl font-bold text-primary-600">
              {dashboard?.active_deals || 0}
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600 mb-1">Messages</div>
            <div className="text-3xl font-bold text-blue-600">
              {dashboard?.total_messages || 0}
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600 mb-1">Freelancers Contacted</div>
            <div className="text-3xl font-bold text-green-600">
              {dashboard?.freelancers_contacted || 0}
            </div>
          </div>
        </div>

        {/* Freelancers Who Contacted You */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold mb-4">Freelancers Who Contacted You</h2>
          
          {freelancers.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">👋</div>
              <p className="text-gray-600">No freelancers have contacted you yet</p>
              <p className="text-sm text-gray-500 mt-2">
                When freelancers send you demos or messages, they'll appear here
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {freelancers.map((freelancer) => (
                <div
                  key={freelancer.freelancer_id}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-bold">{freelancer.freelancer_name}</h3>
                        <span className={`px-2 py-1 text-xs font-semibold rounded ${
                          freelancer.tier === 'top_rated' ? 'bg-purple-100 text-purple-800' :
                          freelancer.tier === 'verified' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {freelancer.tier === 'top_rated' ? 'Top Rated' :
                           freelancer.tier === 'verified' ? 'Verified' : 'New'}
                        </span>
                        {freelancer.demo_sent && (
                          <span className="px-2 py-1 text-xs font-semibold rounded bg-green-100 text-green-800">
                            ✓ Demo Sent
                          </span>
                        )}
                      </div>
                      
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>
                          <span className="font-medium">Messages:</span> {freelancer.message_count}
                        </p>
                        <p>
                          <span className="font-medium">Last Contact:</span>{' '}
                          {new Date(freelancer.last_contact).toLocaleDateString()}
                        </p>
                        {freelancer.portfolio_url && (
                          <p>
                            <span className="font-medium">Portfolio:</span>{' '}
                            <a
                              href={freelancer.portfolio_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-primary-600 hover:underline"
                            >
                              View Portfolio
                            </a>
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <button
                        onClick={() => navigate(`/messages/${freelancer.freelancer_id}`)}
                        className="btn-secondary text-sm"
                      >
                        💬 Chat
                      </button>
                      <button
                        onClick={() => navigate(`/deals/create/${dashboard.business_id}?freelancer=${freelancer.freelancer_id}`)}
                        className="btn-primary text-sm"
                      >
                        📝 Create Deal
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Active Deals */}
        {deals.length > 0 && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Your Deals</h2>
            <div className="space-y-4">
              {deals.map((deal) => (
                <div
                  key={deal.id}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition cursor-pointer"
                  onClick={() => navigate(`/business-deals/${deal.id}`)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-bold">
                          {deal.package_type || 'Website Project'}
                        </h3>
                        <span className={`px-2 py-1 text-xs font-semibold rounded ${
                          deal.status.toLowerCase() === 'completed' ? 'bg-green-100 text-green-800' :
                          deal.status.toLowerCase() === 'active' || deal.status.toLowerCase() === 'inprogress' ? 'bg-blue-100 text-blue-800' :
                          deal.status.toLowerCase() === 'disputed' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {deal.status}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>
                          <span className="font-medium">Amount:</span> ₹{(deal.amount / 100).toFixed(2)}
                        </p>
                        <p>
                          <span className="font-medium">Payment Flow:</span> {deal.payment_flow}
                        </p>
                        <p>
                          <span className="font-medium">Created:</span>{' '}
                          {new Date(deal.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        navigate(`/business-deals/${deal.id}`)
                      }}
                      className="btn-primary text-sm"
                    >
                      View Details →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Business Warning */}
        {!dashboard?.business_id && (
          <div className="card bg-yellow-50 border-yellow-200">
            <div className="flex items-start">
              <span className="text-2xl mr-3">⚠️</span>
              <div>
                <h3 className="font-semibold text-yellow-900 mb-1">No Business Linked</h3>
                <p className="text-sm text-yellow-800">
                  Your account is not linked to a business yet. This usually happens when a freelancer
                  invites you to the platform. Contact support if you need assistance.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default BusinessOwnerDashboard
