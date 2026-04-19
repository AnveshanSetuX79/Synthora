import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

function MessagesPage() {
  const { freelancerId } = useParams()
  const navigate = useNavigate()
  const { user, token } = useAuthStore()
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const [freelancerInfo, setFreelancerInfo] = useState(null)

  useEffect(() => {
    fetchMessages()
    // Poll for new messages every 5 seconds
    const interval = setInterval(fetchMessages, 5000)
    return () => clearInterval(interval)
  }, [freelancerId])

  const fetchMessages = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/outreach/messages?freelancer_id=${freelancerId || ''}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      
      if (!response.ok) throw new Error('Failed to fetch messages')
      
      const data = await response.json()
      setMessages(data.messages || [])
      
      // Get freelancer info from first message
      if (data.messages && data.messages.length > 0) {
        const firstMsg = data.messages[0]
        setFreelancerInfo({
          name: firstMsg.sender_name || firstMsg.recipient_name,
          id: firstMsg.sender_id === user.user_id ? firstMsg.recipient_id : firstMsg.sender_id
        })
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!newMessage.trim()) return

    setSending(true)
    try {
      const response = await fetch('http://localhost:8000/api/outreach/send-message', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          recipient_id: freelancerId,
          message: newMessage,
          message_type: 'text'
        })
      })

      if (!response.ok) throw new Error('Failed to send message')

      setNewMessage('')
      fetchMessages()
    } catch (err) {
      alert(err.message)
    } finally {
      setSending(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading messages...</p>
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
            onClick={() => navigate(-1)}
            className="text-primary-600 hover:text-primary-700 mb-2 flex items-center"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold">
            {freelancerInfo ? `Chat with ${freelancerInfo.name}` : 'Messages'}
          </h1>
        </div>

        {/* Messages Container */}
        <div className="max-w-4xl mx-auto">
          <div className="card">
            {/* Messages List */}
            <div className="h-96 overflow-y-auto mb-4 space-y-4 p-4 bg-gray-50 rounded">
              {messages.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">💬</div>
                  <p className="text-gray-600">No messages yet</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Start the conversation by sending a message below
                  </p>
                </div>
              ) : (
                messages.map((message) => {
                  const isOwn = message.sender_id === user.user_id
                  return (
                    <div
                      key={message.id}
                      className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          isOwn
                            ? 'bg-primary-600 text-white'
                            : 'bg-white border border-gray-200'
                        }`}
                      >
                        <p className="text-sm">{message.message}</p>
                        <p
                          className={`text-xs mt-1 ${
                            isOwn ? 'text-primary-100' : 'text-gray-500'
                          }`}
                        >
                          {new Date(message.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  )
                })
              )}
            </div>

            {/* Message Input */}
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message..."
                className="input-field flex-1"
                disabled={sending}
              />
              <button
                type="submit"
                disabled={sending || !newMessage.trim()}
                className="btn-primary"
              >
                {sending ? 'Sending...' : 'Send'}
              </button>
            </form>
          </div>
        </div>

        {error && (
          <div className="max-w-4xl mx-auto mt-4">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MessagesPage

export default MessagesPage
