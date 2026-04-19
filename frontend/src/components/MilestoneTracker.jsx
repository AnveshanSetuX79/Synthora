import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'

function MilestoneTracker({ dealId }) {
  const { token } = useAuthStore()
  const [milestones, setMilestones] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedMilestone, setSelectedMilestone] = useState(null)
  const [feedback, setFeedback] = useState('')
  const [rejectionReason, setRejectionReason] = useState('')

  useEffect(() => {
    fetchMilestones()
  }, [dealId])

  const fetchMilestones = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/business-owners/deals/${dealId}/milestones`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      
      if (!response.ok) throw new Error('Failed to fetch milestones')
      
      const data = await response.json()
      setMilestones(data)
    } catch (err) {
      console.error('Error fetching milestones:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (milestoneId) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/business-owners/milestones/${milestoneId}/approve`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ feedback })
        }
      )

      if (!response.ok) throw new Error('Failed to approve milestone')

      alert('Milestone approved successfully!')
      setSelectedMilestone(null)
      setFeedback('')
      fetchMilestones()
    } catch (err) {
      alert(err.message)
    }
  }

  const handleReject = async (milestoneId) => {
    if (!rejectionReason.trim()) {
      alert('Please provide a reason for rejection')
      return
    }

    try {
      const response = await fetch(
        `http://localhost:8000/api/business-owners/milestones/${milestoneId}/reject`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ rejection_reason: rejectionReason })
        }
      )

      if (!response.ok) throw new Error('Failed to reject milestone')

      alert('Milestone rejected. Freelancer has been notified.')
      setSelectedMilestone(null)
      setRejectionReason('')
      fetchMilestones()
    } catch (err) {
      alert(err.message)
    }
  }

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'approved':
        return 'bg-green-100 text-green-800'
      case 'submitted':
        return 'bg-yellow-100 text-yellow-800'
      case 'inprogress':
      case 'in_progress':
        return 'bg-blue-100 text-blue-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      case 'paid':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'approved':
        return '✓'
      case 'submitted':
        return '⏳'
      case 'inprogress':
      case 'in_progress':
        return '🔨'
      case 'rejected':
        return '✗'
      case 'paid':
        return '💰'
      default:
        return '○'
    }
  }

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <p className="text-gray-600 mt-2">Loading milestones...</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {milestones.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-600">No milestones yet</p>
        </div>
      ) : (
        <>
          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Project Progress</span>
              <span className="text-sm text-gray-600">
                {milestones.filter(m => m.status.toLowerCase() === 'approved' || m.status.toLowerCase() === 'paid').length} / {milestones.length} completed
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-primary-600 h-3 rounded-full transition-all duration-300"
                style={{
                  width: `${(milestones.filter(m => m.status.toLowerCase() === 'approved' || m.status.toLowerCase() === 'paid').length / milestones.length) * 100}%`
                }}
              ></div>
            </div>
          </div>

          {/* Milestone List */}
          {milestones.map((milestone) => (
            <div
              key={milestone.id}
              className="border rounded-lg p-4 hover:bg-gray-50 transition"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{getStatusIcon(milestone.status)}</span>
                    <h3 className="text-lg font-semibold">{milestone.name}</h3>
                    <span className={`px-2 py-1 text-xs font-semibold rounded ${getStatusColor(milestone.status)}`}>
                      {milestone.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p>
                      <span className="font-medium">Amount:</span> ₹{(milestone.amount / 100).toFixed(2)} ({milestone.percentage}%)
                    </p>
                    {milestone.due_date && (
                      <p>
                        <span className="font-medium">Due:</span>{' '}
                        {new Date(milestone.due_date).toLocaleDateString()}
                      </p>
                    )}
                    {milestone.submitted_at && (
                      <p>
                        <span className="font-medium">Submitted:</span>{' '}
                        {new Date(milestone.submitted_at).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>

                {milestone.status.toLowerCase() === 'submitted' && (
                  <button
                    onClick={() => setSelectedMilestone(milestone)}
                    className="btn-primary text-sm"
                  >
                    Review
                  </button>
                )}
              </div>

              {/* Deliverables */}
              {milestone.deliverables && milestone.deliverables.length > 0 && (
                <div className="mt-3 p-3 bg-gray-50 rounded">
                  <p className="text-sm font-medium mb-2">Deliverables:</p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {milestone.deliverables.map((item, idx) => (
                      <li key={idx}>• {item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Feedback */}
              {milestone.feedback && (
                <div className="mt-3 p-3 bg-blue-50 rounded">
                  <p className="text-sm font-medium mb-1">Your Feedback:</p>
                  <p className="text-sm text-gray-700">{milestone.feedback}</p>
                </div>
              )}

              {/* Rejection Reason */}
              {milestone.rejection_reason && (
                <div className="mt-3 p-3 bg-red-50 rounded">
                  <p className="text-sm font-medium mb-1">Rejection Reason:</p>
                  <p className="text-sm text-gray-700">{milestone.rejection_reason}</p>
                </div>
              )}
            </div>
          ))}
        </>
      )}

      {/* Review Modal */}
      {selectedMilestone && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">Review Milestone</h2>
              
              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-2">{selectedMilestone.name}</h3>
                <p className="text-gray-600">
                  Amount: ₹{(selectedMilestone.amount / 100).toFixed(2)} ({selectedMilestone.percentage}%)
                </p>
              </div>

              {selectedMilestone.deliverables && selectedMilestone.deliverables.length > 0 && (
                <div className="mb-4 p-4 bg-gray-50 rounded">
                  <p className="font-medium mb-2">Deliverables:</p>
                  <ul className="space-y-1">
                    {selectedMilestone.deliverables.map((item, idx) => (
                      <li key={idx} className="text-gray-700">• {item}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  Feedback (Optional)
                </label>
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Provide feedback on the work..."
                  className="input-field"
                  rows="3"
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  Rejection Reason (Required if rejecting)
                </label>
                <textarea
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  placeholder="Explain what needs to be fixed..."
                  className="input-field"
                  rows="3"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => handleApprove(selectedMilestone.id)}
                  className="btn-primary flex-1"
                >
                  ✓ Approve Milestone
                </button>
                <button
                  onClick={() => handleReject(selectedMilestone.id)}
                  className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 flex-1"
                >
                  ✗ Request Changes
                </button>
                <button
                  onClick={() => {
                    setSelectedMilestone(null)
                    setFeedback('')
                    setRejectionReason('')
                  }}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MilestoneTracker
