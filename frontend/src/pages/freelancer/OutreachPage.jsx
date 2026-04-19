import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { leadsAPI } from '../../services/api'
import MessageComposer from '../../components/MessageComposer'
import MessageHistory from '../../components/MessageHistory'
import FollowUpManager from '../../components/FollowUpManager'

function OutreachPage() {
  const { leadId } = useParams()
  const navigate = useNavigate()
  
  const [lead, setLead] = useState(null)
  const [leadContactId, setLeadContactId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshHistory, setRefreshHistory] = useState(0)

  // Fetch lead details
  useEffect(() => {
    const fetchLeadDetails = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await leadsAPI.getLeadDetails(leadId)
        setLead(response.data)
        
        // Get lead contact ID (assuming it's in the lead data)
        // If not, we'll need to create a lead contact first
        setLeadContactId(response.data.lead_contact_id || leadId)
      } catch (err) {
        setError(err.response?.data?.detail?.message || 'Failed to fetch lead details')
      } finally {
        setLoading(false)
      }
    }

    if (leadId) {
      fetchLeadDetails()
    }
  }, [leadId])

  const handleMessageSent = () => {
    // Refresh message history after sending
    setRefreshHistory(prev => prev + 1)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading...</p>
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
          <button onClick={() => navigate('/my-leads')} className="btn-secondary mt-4">
            Back to My Leads
          </button>
        </div>
      </div>
    )
  }

  if (!lead) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <p className="text-gray-600">Lead not found</p>
          <button onClick={() => navigate('/my-leads')} className="btn-secondary mt-4">
            Back to My Leads
          </button>
        </div>
      </div>
    )
  }

  const business = lead.business || {}

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/my-leads')}
            className="text-primary-600 hover:text-primary-700 mb-2 flex items-center"
          >
            ← Back to My Leads
          </button>
          <h1 className="text-3xl font-bold">{business.name}</h1>
          <p className="text-gray-600">{business.category} • {business.city}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Message Composer */}
          <div>
            <MessageComposer
              leadContactId={leadContactId}
              businessName={business.name}
              onMessageSent={handleMessageSent}
            />
          </div>

          {/* Message History */}
          <div>
            <MessageHistory
              leadContactId={leadContactId}
              refresh={refreshHistory}
            />
          </div>
        </div>

        {/* Follow-Up Manager */}
        <div className="mt-6">
          <FollowUpManager />
        </div>
      </div>
    </div>
  )
}

export default OutreachPage
