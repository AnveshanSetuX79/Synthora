import { useState, useEffect } from 'react'
import { outreachAPI } from '../services/api'

function MessageHistory({ leadContactId, refresh }) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch message history
  useEffect(() => {
    const fetchHistory = async () => {
      if (!leadContactId) return

      setLoading(true)
      setError(null)

      try {
        const response = await outreachAPI.getMessageHistory(leadContactId)
        setMessages(response.data.messages || [])
      } catch (err) {
        const errorMsg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to fetch message history'
        setError(errorMsg)
      } finally {
        setLoading(false)
      }
    }

    fetchHistory()
  }, [leadContactId, refresh])

  // Get status badge color
  const getStatusBadge = (status) => {
    const statusLower = status?.toLowerCase() || 'sent'
    
    switch (statusLower) {
      case 'delivered':
        return 'bg-green-100 text-green-800'
      case 'sent':
        return 'bg-blue-100 text-blue-800'
      case 'read':
        return 'bg-purple-100 text-purple-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  // Get channel icon
  const getChannelIcon = (channel) => {
    switch (channel?.toLowerCase()) {
      case 'whatsapp':
        return '💬'
      case 'sms':
        return '📱'
      case 'email':
        return '📧'
      default:
        return '💬'
    }
  }

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown'
    
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    })
  }

  if (loading) {
    return (
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Message History</h2>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Loading messages...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4">Message History</h2>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {messages.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-600">No messages sent yet</p>
          <p className="text-sm text-gray-500 mt-1">
            Send your first message to start the conversation
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {messages.map((msg, index) => (
            <div
              key={msg.id || index}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              {/* Message Header */}
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{getChannelIcon(msg.channel)}</span>
                  <span className="font-medium text-gray-900">
                    {msg.channel || 'WhatsApp'}
                  </span>
                </div>
                <span className={`px-2 py-1 text-xs font-semibold rounded ${getStatusBadge(msg.delivery_status)}`}>
                  {msg.delivery_status || 'Sent'}
                </span>
              </div>

              {/* Message Content */}
              <div className="mb-3">
                <p className="text-gray-700 whitespace-pre-wrap break-words">
                  {msg.content}
                </p>
              </div>

              {/* Message Footer */}
              <div className="flex justify-between items-center text-sm text-gray-500">
                <span>{formatTimestamp(msg.sent_at)}</span>
                
                {/* Additional Status Info */}
                <div className="flex gap-3">
                  {msg.delivered_at && (
                    <span title={`Delivered: ${new Date(msg.delivered_at).toLocaleString()}`}>
                      ✓ Delivered
                    </span>
                  )}
                  {msg.viewed_at && (
                    <span title={`Viewed: ${new Date(msg.viewed_at).toLocaleString()}`}>
                      👁 Viewed
                    </span>
                  )}
                  {msg.replied_at && (
                    <span title={`Replied: ${new Date(msg.replied_at).toLocaleString()}`}>
                      ↩ Replied
                    </span>
                  )}
                </div>
              </div>

              {/* Template Type */}
              {msg.template_id && (
                <div className="mt-2 pt-2 border-t border-gray-100">
                  <span className="text-xs text-gray-500">
                    Template: {msg.template_id.replace('_', ' ')}
                  </span>
                </div>
              )}

              {/* Opted Out Warning */}
              {msg.opted_out && (
                <div className="mt-2 pt-2 border-t border-gray-100">
                  <span className="text-xs text-red-600 font-medium">
                    ⚠ Business opted out after this message
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Follow-up Schedule (if applicable) */}
      {messages.length > 0 && messages.length < 3 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            💡 Tip: Follow up in 48 hours if no response (max 2 follow-ups)
          </p>
        </div>
      )}
    </div>
  )
}

export default MessageHistory
