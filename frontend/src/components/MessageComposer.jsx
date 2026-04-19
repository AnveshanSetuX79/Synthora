import { useState } from 'react'
import { outreachAPI } from '../services/api'

const MESSAGE_TEMPLATES = {
  first_contact: {
    name: 'First Contact',
    whatsapp: 'Hi {business_name}! 👋\n\nI noticed your business doesn\'t have a website yet. I\'ve created a FREE demo website for you to see how it could look.\n\nCheck it out: {demo_link}\n\nNo obligations - just wanted to show you the potential! Let me know what you think.',
    sms: 'Hi {business_name}! I created a FREE demo website for you. Check it: {demo_link}. No obligations!'
  },
  follow_up: {
    name: 'Follow Up',
    whatsapp: 'Hi {business_name}! 👋\n\nJust following up on the demo website I shared earlier. Did you get a chance to check it out?\n\n{demo_link}\n\nHappy to answer any questions!',
    sms: 'Hi {business_name}! Following up on the demo website. Any questions? {demo_link}'
  },
  demo_link: {
    name: 'Demo Link Only',
    whatsapp: 'Hi {business_name}! 👋\n\nHere\'s your demo website: {demo_link}\n\nLet me know if you\'d like to discuss taking it live!',
    sms: 'Hi {business_name}! Your demo: {demo_link}. Let me know if interested!'
  },
  custom: {
    name: 'Custom Message',
    whatsapp: '',
    sms: ''
  }
}

const MAX_SMS_LENGTH = 160
const MAX_WHATSAPP_LENGTH = 4096

function MessageComposer({ leadContactId, businessName, onMessageSent }) {
  const [channel, setChannel] = useState('WhatsApp')
  const [templateType, setTemplateType] = useState('first_contact')
  const [message, setMessage] = useState(MESSAGE_TEMPLATES.first_contact.whatsapp)
  const [demoLink, setDemoLink] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  const maxLength = channel === 'SMS' ? MAX_SMS_LENGTH : MAX_WHATSAPP_LENGTH
  const charCount = message.length

  // Update message when template or channel changes
  const handleTemplateChange = (newTemplate) => {
    setTemplateType(newTemplate)
    const template = MESSAGE_TEMPLATES[newTemplate]
    const channelKey = channel.toLowerCase()
    let newMessage = template[channelKey] || template.whatsapp
    
    // Replace placeholders
    newMessage = newMessage.replace('{business_name}', businessName || '[Business Name]')
    newMessage = newMessage.replace('{demo_link}', demoLink || '[Demo Link]')
    
    setMessage(newMessage)
  }

  const handleChannelChange = (newChannel) => {
    setChannel(newChannel)
    const template = MESSAGE_TEMPLATES[templateType]
    const channelKey = newChannel.toLowerCase()
    let newMessage = template[channelKey] || template.whatsapp
    
    // Replace placeholders
    newMessage = newMessage.replace('{business_name}', businessName || '[Business Name]')
    newMessage = newMessage.replace('{demo_link}', demoLink || '[Demo Link]')
    
    setMessage(newMessage)
  }

  const handleDemoLinkChange = (link) => {
    setDemoLink(link)
    // Update message with new demo link
    const updatedMessage = message.replace(/\[Demo Link\]|https?:\/\/[^\s]+/g, link || '[Demo Link]')
    setMessage(updatedMessage)
  }

  const handleSendMessage = async () => {
    if (!message.trim()) {
      setError('Message cannot be empty')
      return
    }

    if (charCount > maxLength) {
      setError(`Message exceeds ${maxLength} character limit`)
      return
    }

    setSending(true)
    setError(null)
    setSuccess(false)

    try {
      await outreachAPI.sendMessage({
        lead_contact_id: leadContactId,
        template_type: templateType,
        channel: channel,
        custom_message: templateType === 'custom' ? message : null
      })

      setSuccess(true)
      setMessage('')
      
      // Notify parent component
      if (onMessageSent) {
        onMessageSent()
      }

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      const errorMsg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to send message'
      setError(errorMsg)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4">Send Message</h2>

      {/* Channel Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Channel
        </label>
        <div className="flex gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              name="channel"
              value="WhatsApp"
              checked={channel === 'WhatsApp'}
              onChange={(e) => handleChannelChange(e.target.value)}
              className="mr-2"
            />
            WhatsApp
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="channel"
              value="SMS"
              checked={channel === 'SMS'}
              onChange={(e) => handleChannelChange(e.target.value)}
              className="mr-2"
            />
            SMS
          </label>
        </div>
      </div>

      {/* Template Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Template
        </label>
        <select
          value={templateType}
          onChange={(e) => handleTemplateChange(e.target.value)}
          className="input-field"
        >
          {Object.entries(MESSAGE_TEMPLATES).map(([key, template]) => (
            <option key={key} value={key}>
              {template.name}
            </option>
          ))}
        </select>
      </div>

      {/* Demo Link Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Demo Link (Optional)
        </label>
        <div className="flex gap-2">
          <input
            type="url"
            value={demoLink}
            onChange={(e) => handleDemoLinkChange(e.target.value)}
            className="input-field flex-1"
            placeholder="https://example.com/demo/123"
          />
          <button
            onClick={() => handleDemoLinkChange(demoLink)}
            className="btn-secondary"
            title="Insert demo link into message"
          >
            Insert
          </button>
        </div>
      </div>

      {/* Message Text Area */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Message
        </label>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="input-field min-h-[150px]"
          placeholder="Type your message here..."
          maxLength={maxLength}
        />
        <div className="flex justify-between items-center mt-1">
          <span className={`text-sm ${charCount > maxLength ? 'text-red-600' : 'text-gray-500'}`}>
            {charCount} / {maxLength} characters
          </span>
          {channel === 'SMS' && charCount > MAX_SMS_LENGTH && (
            <span className="text-xs text-orange-600">
              Will be sent as {Math.ceil(charCount / MAX_SMS_LENGTH)} messages
            </span>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
          Message sent successfully via {channel}!
        </div>
      )}

      {/* Send Button */}
      <button
        onClick={handleSendMessage}
        disabled={sending || !message.trim() || charCount > maxLength}
        className="btn-primary w-full"
      >
        {sending ? 'Sending...' : `Send via ${channel}`}
      </button>
    </div>
  )
}

export default MessageComposer
