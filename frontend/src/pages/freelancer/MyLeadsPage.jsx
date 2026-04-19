import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { leadsAPI } from '../../services/api'

function MyLeadsPage() {
  const navigate = useNavigate()
  
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [statusFilter, setStatusFilter] = useState('all')

  // Fetch my leads
  useEffect(() => {
    const fetchMyLeads = async () => {
      setLoading(true)
      setError(null)

      try {
        const params = statusFilter !== 'all' ? { status: statusFilter } : {}
        const response = await leadsAPI.getMyLeads(params)
        setLeads(response.data.leads || [])
      } catch (err) {
        setError(err.response?.data?.detail?.message || 'Failed to fetch your leads')
      } finally {
        setLoading(false)
      }
    }

    fetchMyLeads()
  }, [statusFilter])

  // Group leads by status
  const groupedLeads = {
    active: leads.filter(l => l.status === 'claimed' && l.exclusivity_active),
    contacted: leads.filter(l => l.status === 'contacted'),
    demo_sent: leads.filter(l => l.status === 'demo_sent'),
    in_negotiation: leads.filter(l => l.status === 'in_negotiation'),
    closed: leads.filter(l => l.status === 'closed'),
    cold: leads.filter(l => l.status === 'cold'),
  }

  // Calculate exclusivity timer
  const getExclusivityTimer = (expiresAt) => {
    if (!expiresAt) return null
    
    const now = new Date()
    const expires = new Date(expiresAt)
    const diff = expires - now

    if (diff <= 0) return 'Expired'

    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

    return `${hours}h ${minutes}m`
  }

  // Render lead card
  const renderLeadCard = (lead) => {
    const timer = getExclusivityTimer(lead.exclusivity_expires_at)

    return (
      <div key={lead.lead_id} className="card hover:shadow-lg transition-shadow">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h3 className="text-lg font-bold">{lead.business_name}</h3>
            <p className="text-sm text-gray-600">{lead.category} • 📍 {lead.address || lead.city}</p>
          </div>
          <span className={`px-2 py-1 text-xs font-semibold rounded ${
            lead.score >= 80 ? 'bg-green-100 text-green-800' :
            lead.score >= 50 ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            Score: {lead.score}
          </span>
        </div>

        {timer && timer !== 'Expired' && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-3 py-2 rounded text-sm mb-3">
            Exclusivity: {timer}
          </div>
        )}

        <div className="flex gap-2 mt-4">
          <button
            type="button"
            onClick={() => navigate(`/leads/${lead.lead_id}`)}
            className="btn-secondary text-sm flex-1"
          >
            View Details
          </button>
          <button
            type="button"
            onClick={() => navigate(`/leads/${lead.lead_id}`)}
            className="btn-primary text-sm flex-1"
          >
            Manage Lead
          </button>
          <button
            type="button"
            onClick={() => navigate(`/outreach/${lead.lead_id}`)}
            className="btn-secondary text-sm flex-1"
          >
            Send Message
          </button>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading your leads...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">My Leads</h1>
          <button
            onClick={() => navigate('/leads')}
            className="btn-primary"
          >
            Browse Available Leads
          </button>
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
            All ({leads.length})
          </button>
          <button
            onClick={() => setStatusFilter('claimed')}
            className={`px-4 py-2 rounded whitespace-nowrap ${
              statusFilter === 'claimed'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border'
            }`}
          >
            Active ({groupedLeads.active.length})
          </button>
          <button
            onClick={() => setStatusFilter('contacted')}
            className={`px-4 py-2 rounded whitespace-nowrap ${
              statusFilter === 'contacted'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border'
            }`}
          >
            Contacted ({groupedLeads.contacted.length})
          </button>
          <button
            onClick={() => setStatusFilter('demo_sent')}
            className={`px-4 py-2 rounded whitespace-nowrap ${
              statusFilter === 'demo_sent'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border'
            }`}
          >
            Demo Sent ({groupedLeads.demo_sent.length})
          </button>
          <button
            onClick={() => setStatusFilter('in_negotiation')}
            className={`px-4 py-2 rounded whitespace-nowrap ${
              statusFilter === 'in_negotiation'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border'
            }`}
          >
            Negotiating ({groupedLeads.in_negotiation.length})
          </button>
          <button
            onClick={() => setStatusFilter('closed')}
            className={`px-4 py-2 rounded whitespace-nowrap ${
              statusFilter === 'closed'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border'
            }`}
          >
            Closed ({groupedLeads.closed.length})
          </button>
          <button
            onClick={() => setStatusFilter('cold')}
            className={`px-4 py-2 rounded whitespace-nowrap ${
              statusFilter === 'cold'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border'
            }`}
          >
            Cold ({groupedLeads.cold.length})
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Leads Grid */}
        {statusFilter === 'all' ? (
          // Show grouped by status
          <div className="space-y-8">
            {Object.entries(groupedLeads).map(([status, statusLeads]) => (
              statusLeads.length > 0 && (
                <div key={status}>
                  <h2 className="text-xl font-bold mb-4 capitalize">
                    {status.replace('_', ' ')} ({statusLeads.length})
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {statusLeads.map(renderLeadCard)}
                  </div>
                </div>
              )
            ))}
            {leads.length === 0 && (
              <div className="card text-center py-12">
                <p className="text-gray-600">You haven't claimed any leads yet</p>
                <button
                  onClick={() => navigate('/leads')}
                  className="btn-primary mt-4"
                >
                  Browse Available Leads
                </button>
              </div>
            )}
          </div>
        ) : (
          // Show filtered leads
          <div>
            {leads.filter(l => statusFilter === 'all' || l.status === statusFilter).length === 0 ? (
              <div className="card text-center py-12">
                <p className="text-gray-600">No leads in this status</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {leads
                  .filter(l => statusFilter === 'all' || l.status === statusFilter)
                  .map(renderLeadCard)}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default MyLeadsPage
