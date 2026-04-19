import { useState, useEffect } from 'react'
import { payoutAPI } from '../services/api'
import { useNavigate } from 'react-router-dom'

export default function PayoutButton({ milestone, onSuccess }) {
  const navigate = useNavigate()
  const [processing, setProcessing] = useState(false)
  const [eligibility, setEligibility] = useState(null)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    checkEligibility()
  }, [])

  const checkEligibility = async () => {
    try {
      const response = await payoutAPI.checkEligibility()
      setEligibility(response.data.eligibility)
    } catch (error) {
      console.error('Error checking eligibility:', error)
    }
  }

  const handleRequestPayout = async () => {
    if (!eligibility?.eligible) {
      if (eligibility?.reason === 'KYC not approved') {
        if (confirm('KYC verification required. Go to KYC page?')) {
          navigate('/kyc')
        }
      } else {
        alert(eligibility?.reason || 'Not eligible for payout')
      }
      return
    }

    try {
      setProcessing(true)
      await payoutAPI.processPayout({ milestone_id: milestone.id })
      alert('Payout processed successfully! Funds will be transferred to your account.')
      setShowModal(false)
      if (onSuccess) {
        await onSuccess()
      }
    } catch (error) {
      console.error('Error processing payout:', error)
      alert(error.response?.data?.detail?.message || 'Failed to process payout')
    } finally {
      setProcessing(false)
    }
  }

  if (!milestone || milestone.status !== 'Approved' || milestone.paid_at) {
    return null
  }

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700"
      >
        Request Payout
      </button>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Request Payout
            </h3>

            <div className="mb-6 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Milestone:</span>
                <span className="font-medium text-gray-900">{milestone.name}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Amount:</span>
                <span className="font-medium text-gray-900">₹{(milestone.amount / 100).toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Platform Fee (10%):</span>
                <span className="font-medium text-gray-900">₹{(milestone.amount * 0.1 / 100).toLocaleString()}</span>
              </div>
              <div className="border-t pt-3 flex justify-between">
                <span className="text-sm font-semibold text-gray-900">You'll Receive:</span>
                <span className="text-lg font-bold text-green-600">₹{(milestone.amount * 0.9 / 100).toLocaleString()}</span>
              </div>
            </div>

            {eligibility && !eligibility.eligible && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">
                  <span className="font-semibold">Not Eligible:</span> {eligibility.reason}
                </p>
                {eligibility.reason === 'KYC not approved' && (
                  <button
                    onClick={() => navigate('/kyc')}
                    className="mt-2 text-sm text-red-600 underline hover:text-red-700"
                  >
                    Complete KYC Verification →
                  </button>
                )}
              </div>
            )}

            {eligibility?.eligible && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">
                  ✓ You're eligible for payout
                </p>
                <p className="text-xs text-green-600 mt-1">
                  Funds will be transferred to your linked account
                </p>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={handleRequestPayout}
                disabled={processing || !eligibility?.eligible}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {processing ? 'Processing...' : 'Confirm Payout'}
              </button>
              <button
                onClick={() => setShowModal(false)}
                disabled={processing}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
