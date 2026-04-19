import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { dealsAPI, leadsAPI } from '../../services/api'

const PACKAGE_OPTIONS = [
  {
    type: 'starter',
    name: 'Starter Package',
    priceRange: '₹2,999 - ₹4,999',
    minPrice: 2999,
    maxPrice: 4999,
    features: [
      'Single page website',
      'Mobile responsive',
      'Contact form',
      'Basic SEO',
      '1 month support'
    ]
  },
  {
    type: 'standard',
    name: 'Standard Package',
    priceRange: '₹12,000',
    minPrice: 12000,
    maxPrice: 12000,
    features: [
      'Multi-page website (up to 5 pages)',
      'Mobile responsive',
      'Contact form & WhatsApp integration',
      'Advanced SEO',
      'Google My Business setup',
      '3 months support'
    ]
  },
  {
    type: 'premium',
    name: 'Premium Package',
    priceRange: '₹40,000',
    minPrice: 40000,
    maxPrice: 40000,
    features: [
      'Custom website (unlimited pages)',
      'Mobile responsive',
      'Advanced features (booking, payments, etc.)',
      'Premium SEO & Analytics',
      'Social media integration',
      '6 months support',
      'Content management system'
    ]
  }
]

const PAYMENT_FLOWS = [
  {
    value: 'Simplified',
    name: 'Simplified (2 Milestones)',
    description: '50% advance + 50% on delivery'
  },
  {
    value: 'Full',
    name: 'Full (3 Milestones)',
    description: '30% advance + 40% mid-project + 30% on delivery'
  }
]

function CreateDealPage() {
  const { businessId } = useParams()
  const navigate = useNavigate()
  
  const [business, setBusiness] = useState(null)
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState(null)
  
  const [formData, setFormData] = useState({
    packageType: 'starter',
    amount: 2999,
    paymentFlow: 'Simplified',
    description: ''
  })

  // Fetch business details
  useEffect(() => {
    const fetchBusiness = async () => {
      setLoading(true)
      setError(null)

      try {
        // Try to get business from lead details
        const response = await leadsAPI.getLeads({ business_id: businessId })
        if (response.data.leads && response.data.leads.length > 0) {
          setBusiness(response.data.leads[0].business)
        }
      } catch (err) {
        setError('Failed to fetch business details')
      } finally {
        setLoading(false)
      }
    }

    if (businessId) {
      fetchBusiness()
    }
  }, [businessId])

  const handlePackageChange = (packageType) => {
    const pkg = PACKAGE_OPTIONS.find(p => p.type === packageType)
    setFormData(prev => ({
      ...prev,
      packageType,
      amount: pkg.minPrice
    }))
  }

  const handleAmountChange = (amount) => {
    const pkg = PACKAGE_OPTIONS.find(p => p.type === formData.packageType)
    const numAmount = parseInt(amount) || pkg.minPrice
    
    // Validate amount is within package range
    if (numAmount < pkg.minPrice) {
      setFormData(prev => ({ ...prev, amount: pkg.minPrice }))
    } else if (numAmount > pkg.maxPrice) {
      setFormData(prev => ({ ...prev, amount: pkg.maxPrice }))
    } else {
      setFormData(prev => ({ ...prev, amount: numAmount }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    setCreating(true)
    setError(null)

    try {
      const response = await dealsAPI.createDeal({
        business_id: businessId,
        package_type: formData.packageType,
        amount: formData.amount,
        payment_flow: formData.paymentFlow,
        description: formData.description || null
      })

      // Navigate to deal details page
      navigate(`/deals/${response.data.deal_id}`)
    } catch (err) {
      const errorMsg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to create deal'
      setError(errorMsg)
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading...</p>
        </div>
      </div>
    )
  }

  const selectedPackage = PACKAGE_OPTIONS.find(p => p.type === formData.packageType)

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/my-leads')}
            className="text-primary-600 hover:text-primary-700 mb-2 flex items-center"
          >
            ← Back to My Leads
          </button>
          <h1 className="text-3xl font-bold">Create Deal</h1>
          {business && (
            <p className="text-gray-600">{business.name} • {business.city}</p>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Form */}
          <div className="lg:col-span-2">
            <form onSubmit={handleSubmit} className="card">
              <h2 className="text-xl font-bold mb-6">Deal Details</h2>

              {/* Package Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Select Package
                </label>
                <div className="space-y-3">
                  {PACKAGE_OPTIONS.map((pkg) => (
                    <label
                      key={pkg.type}
                      className={`block p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                        formData.packageType === pkg.type
                          ? 'border-primary-600 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="packageType"
                        value={pkg.type}
                        checked={formData.packageType === pkg.type}
                        onChange={(e) => handlePackageChange(e.target.value)}
                        className="sr-only"
                      />
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-semibold text-gray-900">{pkg.name}</div>
                          <div className="text-sm text-gray-600 mt-1">{pkg.priceRange}</div>
                        </div>
                        {formData.packageType === pkg.type && (
                          <span className="text-primary-600">✓</span>
                        )}
                      </div>
                      <ul className="mt-3 space-y-1">
                        {pkg.features.map((feature, idx) => (
                          <li key={idx} className="text-sm text-gray-600 flex items-start">
                            <span className="mr-2">•</span>
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </label>
                  ))}
                </div>
              </div>

              {/* Amount */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Deal Amount (₹)
                </label>
                <input
                  type="number"
                  value={formData.amount}
                  onChange={(e) => handleAmountChange(e.target.value)}
                  min={selectedPackage.minPrice}
                  max={selectedPackage.maxPrice}
                  className="input-field"
                  required
                />
                <p className="text-sm text-gray-500 mt-1">
                  Range: ₹{selectedPackage.minPrice.toLocaleString()} - ₹{selectedPackage.maxPrice.toLocaleString()}
                </p>
              </div>

              {/* Payment Flow */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Payment Flow
                </label>
                <div className="space-y-2">
                  {PAYMENT_FLOWS.map((flow) => (
                    <label
                      key={flow.value}
                      className={`block p-3 border rounded-lg cursor-pointer transition-colors ${
                        formData.paymentFlow === flow.value
                          ? 'border-primary-600 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="paymentFlow"
                        value={flow.value}
                        checked={formData.paymentFlow === flow.value}
                        onChange={(e) => setFormData(prev => ({ ...prev, paymentFlow: e.target.value }))}
                        className="sr-only"
                      />
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="font-medium text-gray-900">{flow.name}</div>
                          <div className="text-sm text-gray-600">{flow.description}</div>
                        </div>
                        {formData.paymentFlow === flow.value && (
                          <span className="text-primary-600">✓</span>
                        )}
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Description */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  className="input-field min-h-[100px]"
                  placeholder="Add any special requirements or notes..."
                />
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={creating}
                className="btn-primary w-full"
              >
                {creating ? 'Creating Deal...' : 'Create Deal'}
              </button>
            </form>
          </div>

          {/* Summary */}
          <div>
            <div className="card sticky top-4">
              <h3 className="text-lg font-bold mb-4">Deal Summary</h3>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Package:</span>
                  <span className="font-medium">{selectedPackage.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Amount:</span>
                  <span className="font-medium">₹{formData.amount.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Payment Flow:</span>
                  <span className="font-medium">{formData.paymentFlow}</span>
                </div>
                
                <div className="pt-3 border-t">
                  <div className="font-medium mb-2">Milestones:</div>
                  {formData.paymentFlow === 'Simplified' ? (
                    <>
                      <div className="flex justify-between text-gray-600">
                        <span>1. Advance (50%)</span>
                        <span>₹{(formData.amount * 0.5).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-gray-600">
                        <span>2. Delivery (50%)</span>
                        <span>₹{(formData.amount * 0.5).toLocaleString()}</span>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="flex justify-between text-gray-600">
                        <span>1. Advance (30%)</span>
                        <span>₹{(formData.amount * 0.3).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-gray-600">
                        <span>2. Mid-project (40%)</span>
                        <span>₹{(formData.amount * 0.4).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-gray-600">
                        <span>3. Delivery (30%)</span>
                        <span>₹{(formData.amount * 0.3).toLocaleString()}</span>
                      </div>
                    </>
                  )}
                </div>

                <div className="pt-3 border-t">
                  <div className="flex justify-between text-gray-600">
                    <span>Platform Fee (15%):</span>
                    <span>₹{(formData.amount * 0.15).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between font-medium text-lg mt-2">
                    <span>Your Earnings:</span>
                    <span className="text-primary-600">₹{(formData.amount * 0.85).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CreateDealPage
