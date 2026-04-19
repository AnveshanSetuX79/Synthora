import { useState, useEffect, useRef } from 'react'
import { useAuthStore } from '../store/authStore'

function MessageThread({ leadContactId, businessName, onClose }) {
  const { user } = useAuthStore()
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [file, setFile] = useState(null)
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    fetchMessages()
    const interval = setInterval(fetchMessages, 3000) // Poll every 3 seconds
    return () => clearInterval(interval)
  }, [leadContactId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const fetchMessages = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/outreach/history/${leadContactId}`,
        {
          headers: {
            'Authorization': `Bearer ${useAuthStore.getState().token}`
          }
        }
      )
      
      if (response.ok) {
        const data = await response.json()
        setMessages(data.messages || [])
      }
    } catch (error) {
      console.error('Failed to fetch messages:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!newMessage.trim() && !file) return

    setSending(true)
    try {
      const formData = new FormData()
      formData.append('lead_contact_id', leadContactId)
      formData.append('message', newMessage)
      formData.append('channel', 'Email')
      
      if (file) {
        formData.append('attachment', file)
      }

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/outreach/send`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${useAuthStore.getState().token}`
          },
          body: formData
        }
      )

      if (response.ok) {
        setNewMessage('')
        setFile(null)
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
        fetchMessages()
      } else {
        const error = await response.json()
        alert(error.detail || 'Failed to send message')
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      alert('Failed to send message')
    } finally {
      setSending(false)
    }
  }

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      // Check file size (10MB max)
      if (selectedFile.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB')
        e.target.value = ''
        return
      }
      setFile(selectedFile)
    }
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
    
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-blue-600 text-white rounded-t-lg">
        <div>
          <h3 className="font-semibold text-lg">{businessName}</h3>
          <p className="text-sm text-blue-100">
            {messages.length} message{messages.length !== 1 ? 's' : ''}
          </p>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="text-white hover:text-blue-100 text-2xl"
          >
            ×
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: '500px' }}>
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p>No messages yet</p>
            <p className="text-sm mt-2">Start the conversation!</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  msg.sender_id === user?.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-900'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                <div className="flex items-center justify-between mt-1 space-x-2">
                  <span className="text-xs opacity-75">
                    {formatTimestamp(msg.sent_at)}
                  </span>
                  {msg.sender_id === user?.id && (
                    <span className="text-xs opacity-75">
                      {msg.delivery_status === 'delivered' && '✓✓'}
                      {msg.delivery_status === 'sent' && '✓'}
                      {msg.delivery_status === 'failed' && '✗'}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSendMessage} className="p-4 border-t bg-gray-50 rounded-b-lg">
        {file && (
          <div className="mb-2 flex items-center justify-between bg-blue-50 p-2 rounded">
            <span className="text-sm text-blue-900">📎 {file.name}</span>
            <button
              type="button"
              onClick={() => {
                setFile(null)
                if (fileInputRef.current) {
                  fileInputRef.current.value = ''
                }
              }}
              className="text-blue-600 hover:text-blue-800"
            >
              ✗
            </button>
          </div>
        )}
        <div className="flex space-x-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            accept="image/*,.pdf,.doc,.docx"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="px-3 py-2 text-gray-600 hover:text-gray-800 border rounded-lg"
            title="Attach file (max 10MB)"
          >
            📎
          </button>
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={sending}
          />
          <button
            type="submit"
            disabled={sending || (!newMessage.trim() && !file)}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {sending ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default MessageThread
