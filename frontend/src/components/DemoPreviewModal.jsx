import { useState } from 'react'
import { demosAPI } from '../services/api'

function DemoPreviewModal({ isOpen, onClose, demoUrl, businessName, businessId }) {
  const [copied, setCopied] = useState(false)

  if (!isOpen) return null

  const handleCopyLink = () => {
    navigator.clipboard.writeText(demoUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleSendToBusiness = () => {
    // Navigate to outreach page with pre-filled demo link
    window.location.href = `/outreach/send?businessId=${businessId}&demoUrl=${encodeURIComponent(demoUrl)}`
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold">Demo Preview</h2>
            <p className="text-gray-600">{businessName}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Demo Preview */}
        <div className="flex-1 overflow-hidden p-6">
          <div className="h-full border rounded-lg overflow-hidden">
            <iframe
              src={demoUrl}
              className="w-full h-full"
              title="Demo Preview"
              sandbox="allow-same-origin allow-scripts"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="p-6 border-t bg-gray-50 flex gap-3">
          <button
            onClick={handleCopyLink}
            className="btn-secondary flex-1"
          >
            {copied ? '✓ Copied!' : 'Copy Link'}
          </button>
          <button
            onClick={handleSendToBusiness}
            className="btn-primary flex-1"
          >
            Send to Business
          </button>
          <button
            onClick={onClose}
            className="btn-secondary"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default DemoPreviewModal
