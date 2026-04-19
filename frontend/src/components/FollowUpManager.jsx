import { useState, useEffect } from 'react'
import { followUpAPI } from '../services/api'
import { useNavigate } from 'react-router-dom'

export default function FollowUpManager() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [scheduling, setScheduling] = useState(false)
  const [leadsNeedingFollowUp, setLeadsNeedingFollowUp] = useState([])

  useEffect(() => {
    fetchLeadsNeedingFollowUp()
  }, [])

  const fetchLeadsNeedingFollowUp = async () => {
    try {
      setLoading(true)
      const response = await followUpAPI.getLeadsNeedingFollowUp()
      setLeadsNeedingFollowUp(response.data.leads || [])
      setLoading(false)
    } catch (error) {
      console.error('Error fetching leads needing follow-up:', error)
      setLoading(false)
    }
  }

  const handleScheduleFollowUps = async () => {
    if (!confirm('Schedule automatic follow-ups for all eligible leads?')) {
      return
    }

    try {
      setScheduling(true)
      const response = await followUpAPI.scheduleFollowUps()
      alert(`Successfully scheduled ${response.data.followups_sent} follow-up messages!`)
      await fetchLeadsNeedingFollowUp()
    } catch (error) {
      console.error('Error scheduling follow-ups:', error)
      alert(error.response?.data?.detail?.message || 'Failed to schedule follow-ups')
    } finally {
      setScheduling(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Auto Follow-Ups</h3>
          <p className="text-sm text-gray-600 mt-1">
            Leads contacted 48+ hours ago with no response
          </p>
        </div>
        <button
          onClick={handleScheduleFollowUps}
          disabled={scheduling || leadsNeedingFollowUp.length === 0}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {scheduling ? 'Scheduling...' : `Schedule Follow-Ups (${leadsNeedingFollowUp.length})`}
        </button>
      </div>

      {leadsNeedingFollowUp.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-3">✅</div>
          <p className="text-gray-600">No leads need follow-up right now</p>
          <p className="text-sm text-gray-500 mt-1">
            All your leads are either recently contacted or have responded
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {leadsNeedingFollowUp.map((lead) => (
            <div
              key={lead.lead_contact_id}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors cursor-pointer"
              onClick={() => navigate(`/outreach/${lead.lead_contact_id}`)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{lead.business_name}</h4>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                    <span>
                      Last contact: {lead.hours_since_contact}h ago
                    </span>
                    <span>•</span>
                    <span>
                      Follow-ups: {lead.follow_up_count}/2
                    </span>
                    <span>•</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      lead.status === 'Contacted' ? 'bg-blue-100 text-blue-800' :
                      lead.status === 'Interested' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {lead.status}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-500">
                    {new Date(lead.last_contact_at).toLocaleDateString()}
                  </div>
                  {lead.follow_up_count >= 1 && (
                    <div className="mt-1 text-xs text-orange-600 font-medium">
                      {2 - lead.follow_up_count} follow-up{2 - lead.follow_up_count !== 1 ? 's' : ''} left
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">How Auto Follow-Ups Work</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Automatically sends follow-up after 48 hours of no response</li>
          <li>• Maximum 2 follow-ups per lead</li>
          <li>• Leads marked as "Cold" after 2 failed follow-ups</li>
          <li>• Respects opt-out preferences</li>
        </ul>
      </div>
    </div>
  )
}
