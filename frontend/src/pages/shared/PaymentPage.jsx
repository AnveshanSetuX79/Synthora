import { useState, useEffect } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { paymentsAPI, dealsAPI } from '../../services/api'

// Load Razorpay script
const loadRazorpayScript = () => {
  return new Promise((resolve) => {
    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.onload = () => resolve(true)
    script.onerror = () => resolve(false)
    document.body.appendChild(script)
  })
}

function PaymentPage() {
  const { dealId } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  
  const milestoneId = searchParams.get('milestone')
  
  const [deal, setDeal] = useState(null)
  const [milestone, setMilestone] = useState(null)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState(null)
  const [razorpayLoaded, setRazorpayLoaded] = useState(false)

  // Load Razorpay script
  useEffect(() => {
    const loadScript = async () => {
      const loaded = await loadRazorpayScript()
      setRazorpayLoaded(loaded)
      if (!loaded) {
        setError('Failed to load Razorpay. Please refresh the page.')
      }
    }
    loadScript()
  }, [])

  // Fetch deal details
  useEffect(() => {
    const fetchDealDetails = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await dealsAPI.getDealDetails(dealId)
        setDeal(response.data.deal)
        
        // Find milestone if specified
        if (milestoneId && response.data.deal.milestones) {
          const ms = response.data.deal.milestones.find(m => m.id === milestoneId)
          setMilestone(ms)
        }
      } catch (err) {
        const errorMsg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to fetch deal details'
        setError(errorMsg)
      } finally {
        setLoading(false)
      }
    }

    if (dealId) {
      fetchDealDetails()
    }
  }, [dealId, milestoneId])

  // Calculate payment amount
  const getPaymentAmount = () => {
    if (milestone) {
      return milestone.amount
    }
    return deal?.amount || 0
  }

  // Handle payment
  const handlePayment = async () => {
    if (!razorpayLoaded) {
      setError('Razorpay is not loaded. Please refresh the page.')
      return
    }

    setProcessing(true)
    setError(null)

    try {
      // Create payment order
      const orderResponse = await paymentsAPI.createOrder({
        deal_id: dealId,
        amount: getPaymentAmount(),
        milestone_id: milestoneId || null
      })

      const { razorpay_order_id, amount, payment_id } = orderResponse.data

      // Razorpay options
      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID || 'rzp_test_dummy', // Replace with your Razorpay key
        amount: amount * 100, // Amount in paise
        currency: 'INR',
        name: 'LocalAI Leads',
        description: milestone ? `Payment for ${milestone.name}` : 'Deal Payment',
        order_id: razorpay_order_id,
        handler: async function (response) {
          try {
            // Verify payment
            await paymentsAPI.verifyPayment({
              payment_id: payment_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature
            })

            // Payment successful
            alert('Payment successful!')
            navigate(`/deals/${dealId}`)
          } catch (err) {
            const errorMsg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Payment verification failed'
            setError(errorMsg)
            setProcessing(false)
          }
        },
        prefill: {
          name: deal?.business_name || '',
          email: '',
          contact: ''
        },
        theme: {
          color: '#4F46E5' // primary-600
        },
        modal: {
          ondismiss: function() {
            setProcessing(false)
            setError('Payment cancelled by user')
          }
        }
      }

      // Open Razorpay checkout
      const razorpay = new window.Razorpay(options)
      razorpay.open()
    } catch (err) {
      const errorMsg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to create payment order'
      setError(errorMsg)
      setProcessing(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading payment details...</p>
        </div>
      </div>
    )
  }

  if (error && !deal) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
          <button onClick={() => navigate('/deals')} className="btn-secondary mt-4">
            Back to Deals
          </button>
        </div>
      </div>
    )
  }

  if (!deal) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <p className="text-gray-600">Deal not found</p>
          <button onClick={() => navigate('/deals')} className="btn-secondary mt-4">
            Back to Deals
          </button>
        </div>
      </div>
    )
  }

  // CORRECT PAYMENT CALCULATION:
  // Business owner pays: paymentAmount (e.g., ₹10,000)
  // Platform keeps: 15% commission (₹1,500)
  // Freelancer receives: 85% (₹8,500)
  const paymentAmount = getPaymentAmount()
  const platformCommission = Math.round(paymentAmount * 0.15)
  const freelancerReceives = paymentAmount - platformCommission

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate(`/deals/${dealId}`)}
            className="text-primary-600 hover:text-primary-700 mb-2 flex items-center"
          >
            ← Back to Deal
          </button>
          <h1 className="text-3xl font-bold">Payment</h1>
          <p className="text-gray-600">{deal.business_name}</p>
        </div>

        <div className="max-w-2xl mx-auto">
          {/* Payment Summary Card */}
          <div className="card mb-6">
            <h2 className="text-xl font-bold mb-6">Payment Summary</h2>

            <div className="space-y-4">
              {/* Deal Information */}
              <div className="pb-4 border-b">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Deal:</span>
                  <span className="font-medium">{deal.business_name}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Package:</span>
                  <span className="font-medium capitalize">{deal.package_type}</span>
                </div>
                {milestone && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Milestone:</span>
                    <span className="font-medium">{milestone.name}</span>
                  </div>
                )}
              </div>

              {/* Amount Breakdown */}
              <div className="space-y-3">
                <div className="flex justify-between text-xl font-bold">
                  <span>Total to Pay:</span>
                  <span className="text-primary-600">₹{paymentAmount.toLocaleString()}</span>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                  <div className="font-medium text-gray-700 mb-2">Payment Breakdown:</div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Project Amount:</span>
                    <span className="font-medium">₹{paymentAmount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Platform Fee (15%):</span>
                    <span className="text-gray-600">₹{platformCommission.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-gray-200">
                    <span className="text-gray-700 font-medium">Freelancer Receives:</span>
                    <span className="font-semibold text-green-600">₹{freelancerReceives.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Payment Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                <div className="flex items-start">
                  <span className="text-blue-600 mr-2">ℹ️</span>
                  <div className="text-sm text-blue-800">
                    <p className="font-medium mb-1">Secure Payment via Razorpay</p>
                    <p>Your payment is processed securely through Razorpay. We accept credit cards, debit cards, UPI, and net banking.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          {/* Payment Button */}
          <button
            onClick={handlePayment}
            disabled={processing || !razorpayLoaded}
            className="btn-primary w-full text-lg py-4"
          >
            {processing ? 'Processing...' : `Pay ₹${paymentAmount.toLocaleString()}`}
          </button>

          {/* Security Info */}
          <div className="mt-6 text-center text-sm text-gray-600">
            <p>🔒 Payments are secured by Razorpay</p>
            <p className="mt-1">Your payment information is encrypted and secure</p>
          </div>

          {/* Terms */}
          <div className="mt-6 text-xs text-gray-500 text-center">
            <p>By proceeding with payment, you agree to our Terms of Service and Privacy Policy.</p>
            <p className="mt-1">You pay ₹{paymentAmount.toLocaleString()}. Platform keeps 15% (₹{platformCommission.toLocaleString()}). Freelancer receives ₹{freelancerReceives.toLocaleString()}.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PaymentPage
