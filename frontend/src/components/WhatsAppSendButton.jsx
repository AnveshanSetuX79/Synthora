import { useState } from 'react'
import api from '../services/api'

function WhatsAppSendButton({ leadContactId, businessName, className = '' }) {
  const [sending, setSending] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleSendWhatsApp = async () => {
    setSending(true)
    setSuccess(false)

    try {
      const response = await api.post('/api/outreach/whatsapp/generate-link', {
        lead_contact_id: leadContactId,
        template_type: 'first_contact'
      })

      const { whatsapp_link, message_preview, instructions } = response.data

      // Open WhatsApp in new tab
      window.open(whatsapp_link, '_blank')

      // Show success
      setSuccess(true)
      
      // Auto-hide success message after 10 seconds
      setTimeout(() => setSuccess(false), 10000)

    } catch (err) {
      const errorMsg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to generate WhatsApp link'
      alert(`❌ ${errorMsg}`)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className={className}>
      {/* WhatsApp Section */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg p-4">
        <div className="flex items-start gap-3 mb-3">
          <span className="text-3xl">💚</span>
          <div className="flex-1">
            <h3 className="font-bold text-green-900 mb-1">Send Demo via WhatsApp</h3>
            <p className="text-sm text-green-700">
              FREE • Instant • 10x Better Open Rates
            </p>
            <p className="text-xs text-green-600 mt-1">
              No SMS costs. Message opens in WhatsApp with demo link pre-filled!
            </p>
          </div>
        </div>
        
        <button
          onClick={handleSendWhatsApp}
          disabled={sending}
          className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-4 px-6 rounded-lg flex items-center justify-center gap-2 shadow-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span className="text-2xl">📱</span>
          <span className="text-lg">
            {sending ? 'Opening WhatsApp...' : 'Send via WhatsApp'}
          </span>
          <span className="bg-white text-green-600 text-xs font-bold px-2 py-1 rounded-full ml-2">
            FREE
          </span>
        </button>
        
        {success && (
          <div className="mt-3 bg-green-100 border border-green-300 rounded-lg p-3 animate-pulse">
            <div className="flex items-center gap-2">
              <span className="text-green-600">✅</span>
              <span className="text-sm font-medium text-green-900">
                WhatsApp opened! Just click "Send" in WhatsApp.
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-4">
        <p className="text-xs text-blue-800">
          💡 <strong>Pro Tip:</strong> WhatsApp has 98% open rate vs 20% for SMS. 
          Business owners are more likely to respond!
        </p>
      </div>
    </div>
  )
}

export default WhatsAppSendButton
