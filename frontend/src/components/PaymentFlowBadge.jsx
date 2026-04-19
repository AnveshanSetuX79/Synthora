import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'

function PaymentFlowBadge({ freelancerId }) {
  const [flowInfo, setFlowInfo] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (freelancerId) {
      fetchPaymentFlow()
    }
  }, [freelancerId])

  const fetchPaymentFlow = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/deals/payment-flow/${freelancerId}`,
        {
          headers: {
            'Authorization': `Bearer ${useAuthStore.getState().token}`
          }
        }
      )
      
      if (response.ok) {
        const data = await response.json()
        setFlowInfo(data)
      }
    } catch (error) {
      console.error('Failed to fetch payment flow:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading || !flowInfo) {
    return null
  }

  const isSimplified = flowInfo.payment_flow === 'simplified'
  const isUpgraded = flowInfo.payment_flow === 'full'

  return (
    <div className={`rounded-lg p-4 ${isSimplified ? 'bg-blue-50 border border-blue-200' : 'bg-purple-50 border border-purple-200'}`}>
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className={`text-lg font-bold ${isSimplified ? 'text-blue-900' : 'text-purple-900'}`}>
              {isSimplified ? '📊 Simplified Flow' : '🎯 Full Flow'}
            </span>
            {isUpgraded && (
              <span className="px-2 py-1 bg-purple-600 text-white text-xs rounded-full">
                UPGRADED
              </span>
            )}
          </div>
          <p className={`text-sm mt-1 ${isSimplified ? 'text-blue-700' : 'text-purple-700'}`}>
            {flowInfo.milestone_structure}
          </p>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold ${isSimplified ? 'text-blue-900' : 'text-purple-900'}`}>
            {flowInfo.completed_deals}
          </div>
          <p className={`text-xs ${isSimplified ? 'text-blue-600' : 'text-purple-600'}`}>
            Completed Deals
          </p>
        </div>
      </div>
      
      {isSimplified && flowInfo.deals_until_upgrade > 0 && (
        <div className="mt-3 pt-3 border-t border-blue-200">
          <div className="flex items-center justify-between text-sm">
            <span className="text-blue-700">
              Complete {flowInfo.deals_until_upgrade} more deal{flowInfo.deals_until_upgrade !== 1 ? 's' : ''} to unlock Full Flow
            </span>
            <span className="text-blue-900 font-semibold">
              {flowInfo.completed_deals}/{flowInfo.upgrade_threshold}
            </span>
          </div>
          <div className="mt-2 w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(flowInfo.completed_deals / flowInfo.upgrade_threshold) * 100}%` }}
            />
          </div>
        </div>
      )}
      
      {isUpgraded && (
        <div className="mt-3 pt-3 border-t border-purple-200">
          <p className="text-sm text-purple-700">
            ✨ You've unlocked the Full Flow with 3 milestones for better project management!
          </p>
        </div>
      )}
    </div>
  )
}

export default PaymentFlowBadge
