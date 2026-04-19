import { useState, useEffect } from 'react'
import { kycAPI, payoutAPI } from '../../services/api'
import { useNavigate } from 'react-router-dom'

export default function KYCPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [kycStatus, setKycStatus] = useState(null)
  const [errors, setErrors] = useState({})
  const [step, setStep] = useState(1) // Multi-step form
  const [formData, setFormData] = useState({
    document_type: 'PAN',
    document_number: '',
    document_url: '',
    bank_account_number: '',
    bank_account_number_confirm: '',
    bank_ifsc_code: '',
    bank_account_holder_name: '',
  })

  useEffect(() => {
    fetchKYCStatus()
  }, [])

  const fetchKYCStatus = async () => {
    try {
      setLoading(true)
      const response = await kycAPI.getKYCStatus()
      setKycStatus(response.data.kyc_status)
    } catch (error) {
      console.error('Error fetching KYC status:', error)
    } finally {
      setLoading(false)
    }
  }

  // Validation functions
  const validatePAN = (pan) => {
    const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/
    return panRegex.test(pan)
  }

  const validateAadhaar = (aadhaar) => {
    const aadhaarRegex = /^\d{12}$/
    return aadhaarRegex.test(aadhaar.replace(/\s/g, ''))
  }

  const validateIFSC = (ifsc) => {
    const ifscRegex = /^[A-Z]{4}0[A-Z0-9]{6}$/
    return ifscRegex.test(ifsc)
  }

  const validateAccountNumber = (accNum) => {
    return /^\d{9,18}$/.test(accNum)
  }

  const validateStep1 = () => {
    const newErrors = {}
    
    if (!formData.document_number) {
      newErrors.document_number = 'Document number is required'
    } else {
      if (formData.document_type === 'PAN' && !validatePAN(formData.document_number)) {
        newErrors.document_number = 'Invalid PAN format (e.g., ABCDE1234F)'
      } else if (formData.document_type === 'Aadhaar' && !validateAadhaar(formData.document_number)) {
        newErrors.document_number = 'Invalid Aadhaar format (12 digits)'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const validateStep2 = () => {
    const newErrors = {}

    if (!formData.bank_account_holder_name) {
      newErrors.bank_account_holder_name = 'Account holder name is required'
    } else if (formData.bank_account_holder_name.length < 3) {
      newErrors.bank_account_holder_name = 'Name must be at least 3 characters'
    }

    if (!formData.bank_account_number) {
      newErrors.bank_account_number = 'Account number is required'
    } else if (!validateAccountNumber(formData.bank_account_number)) {
      newErrors.bank_account_number = 'Invalid account number (9-18 digits)'
    }

    if (!formData.bank_account_number_confirm) {
      newErrors.bank_account_number_confirm = 'Please confirm account number'
    } else if (formData.bank_account_number !== formData.bank_account_number_confirm) {
      newErrors.bank_account_number_confirm = 'Account numbers do not match'
    }

    if (!formData.bank_ifsc_code) {
      newErrors.bank_ifsc_code = 'IFSC code is required'
    } else if (!validateIFSC(formData.bank_ifsc_code)) {
      newErrors.bank_ifsc_code = 'Invalid IFSC code format'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (step === 1 && validateStep1()) {
      setStep(2)
    }
  }

  const handleBack = () => {
    setStep(1)
    setErrors({})
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateStep2()) {
      return
    }

    try {
      setSubmitting(true)
      const submitData = {
        document_type: formData.document_type,
        document_number: formData.document_number,
        document_url: formData.document_url,
        bank_account_number: formData.bank_account_number,
        bank_ifsc_code: formData.bank_ifsc_code,
        bank_account_holder_name: formData.bank_account_holder_name,
      }
      
      await kycAPI.submitKYC(submitData)
      await fetchKYCStatus()
      setStep(3) // Success step
    } catch (error) {
      console.error('Error submitting KYC:', error)
      setErrors({ submit: error.response?.data?.detail?.message || 'Failed to submit KYC. Please try again.' })
    } finally {
      setSubmitting(false)
    }
  }

  const handleCreateLinkedAccount = async () => {
    try {
      setSubmitting(true)
      await payoutAPI.createLinkedAccount()
      await fetchKYCStatus()
    } catch (error) {
      console.error('Error creating linked account:', error)
      setErrors({ submit: error.response?.data?.detail?.message || 'Failed to create linked account' })
    } finally {
      setSubmitting(false)
    }
  }

  const maskAccountNumber = (accNum) => {
    if (!accNum || accNum.length < 4) return accNum
    return 'X'.repeat(accNum.length - 4) + accNum.slice(-4)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading KYC status...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="text-primary-600 hover:text-primary-700 mb-4 flex items-center"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold text-gray-900">KYC Verification</h1>
          <p className="mt-2 text-gray-600">Secure verification for receiving payouts</p>
        </div>

        {/* Security Badge */}
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start">
          <div className="text-2xl mr-3">🔒</div>
          <div>
            <h4 className="text-sm font-semibold text-blue-900 mb-1">Your data is secure</h4>
            <p className="text-xs text-blue-800">
              All information is encrypted and stored securely. We comply with RBI guidelines and never share your data.
            </p>
          </div>
        </div>

        {/* KYC Status Card */}
        {kycStatus && kycStatus.status !== 'Pending' && (
          <div className={`mb-6 rounded-lg border-2 overflow-hidden ${
            kycStatus.status === 'Approved' ? 'bg-green-50 border-green-200' :
            kycStatus.status === 'Rejected' ? 'bg-red-50 border-red-200' :
            'bg-yellow-50 border-yellow-200'
          }`}>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Verification Status</h3>
                <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
                  kycStatus.status === 'Approved' ? 'bg-green-100 text-green-800' :
                  kycStatus.status === 'Rejected' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {kycStatus.status}
                </span>
              </div>

              {kycStatus.status === 'Approved' && (
                <div className="space-y-3">
                  <div className="flex items-center text-green-700">
                    <span className="text-xl mr-2">✓</span>
                    <span className="text-sm font-medium">Identity verified</span>
                  </div>
                  {kycStatus.has_bank_details && (
                    <div className="flex items-center text-green-700">
                      <span className="text-xl mr-2">✓</span>
                      <span className="text-sm font-medium">Bank details verified</span>
                    </div>
                  )}
                  {kycStatus.has_linked_account ? (
                    <div className="flex items-center text-green-700">
                      <span className="text-xl mr-2">✓</span>
                      <span className="text-sm font-medium">Ready for payouts</span>
                    </div>
                  ) : (
                    <div className="mt-4 pt-4 border-t border-green-200">
                      <p className="text-sm text-gray-700 mb-3">Final step: Create linked account for payouts</p>
                      <button
                        onClick={handleCreateLinkedAccount}
                        disabled={submitting}
                        className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium"
                      >
                        {submitting ? 'Creating...' : 'Create Payout Account'}
                      </button>
                    </div>
                  )}
                </div>
              )}

              {kycStatus.status === 'Rejected' && (
                <div>
                  <p className="text-sm text-red-700 mb-2 font-medium">Verification failed</p>
                  {kycStatus.rejection_reason && (
                    <div className="bg-red-100 border border-red-200 rounded p-3 mb-3">
                      <p className="text-sm text-red-800"><strong>Reason:</strong> {kycStatus.rejection_reason}</p>
                    </div>
                  )}
                  <p className="text-sm text-gray-600">Please review and resubmit with correct information</p>
                </div>
              )}

              {kycStatus.status === 'Submitted' && (
                <div>
                  <p className="text-sm text-yellow-700 mb-2">Your documents are under review</p>
                  <p className="text-xs text-gray-600">Verification typically takes 1-2 business days. We'll notify you once complete.</p>
                </div>
              )}

              {kycStatus.submitted_at && (
                <p className="text-xs text-gray-500 mt-4 pt-4 border-t">
                  Submitted: {new Date(kycStatus.submitted_at).toLocaleString('en-IN', { 
                    dateStyle: 'medium', 
                    timeStyle: 'short' 
                  })}
                </p>
              )}
            </div>
          </div>
        )}

        {/* KYC Form */}
        {(!kycStatus || kycStatus.status === 'Pending' || kycStatus.status === 'Rejected') && step < 3 && (
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Progress Bar */}
            <div className="bg-gray-100 px-6 py-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Step {step} of 2</span>
                <span className="text-sm text-gray-600">
                  {step === 1 ? 'Identity Verification' : 'Bank Details'}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(step / 2) * 100}%` }}
                />
              </div>
            </div>

            <form onSubmit={step === 2 ? handleSubmit : (e) => { e.preventDefault(); handleNext(); }} className="p-6">
              {/* Step 1: Identity Verification */}
              {step === 1 && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Identity Verification</h3>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Document Type <span className="text-red-500">*</span>
                        </label>
                        <select
                          value={formData.document_type}
                          onChange={(e) => {
                            setFormData({ ...formData, document_type: e.target.value, document_number: '' })
                            setErrors({})
                          }}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          required
                        >
                          <option value="PAN">PAN Card (Recommended)</option>
                          <option value="Aadhaar">Aadhaar Card</option>
                          <option value="DrivingLicense">Driving License</option>
                          <option value="Passport">Passport</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {formData.document_type} Number <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.document_number}
                          onChange={(e) => {
                            setFormData({ ...formData, document_number: e.target.value.toUpperCase().replace(/\s/g, '') })
                            setErrors({ ...errors, document_number: '' })
                          }}
                          placeholder={
                            formData.document_type === 'PAN' ? 'ABCDE1234F' :
                            formData.document_type === 'Aadhaar' ? '123456789012' :
                            'Enter document number'
                          }
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                            errors.document_number ? 'border-red-300' : 'border-gray-300'
                          }`}
                          required
                        />
                        {errors.document_number && (
                          <p className="text-red-500 text-sm mt-1">{errors.document_number}</p>
                        )}
                        <p className="text-xs text-gray-500 mt-1">
                          {formData.document_type === 'PAN' && 'Format: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F)'}
                          {formData.document_type === 'Aadhaar' && '12-digit number without spaces'}
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Document Upload (Optional)
                        </label>
                        <input
                          type="url"
                          value={formData.document_url}
                          onChange={(e) => setFormData({ ...formData, document_url: e.target.value })}
                          placeholder="https://drive.google.com/..."
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Upload to Google Drive/Dropbox and paste the shareable link
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      type="button"
                      onClick={() => navigate(-1)}
                      className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium"
                    >
                      Continue to Bank Details →
                    </button>
                  </div>
                </div>
              )}

              {/* Step 2: Bank Details */}
              {step === 2 && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Bank Account Details</h3>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Account Holder Name <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.bank_account_holder_name}
                          onChange={(e) => {
                            setFormData({ ...formData, bank_account_holder_name: e.target.value })
                            setErrors({ ...errors, bank_account_holder_name: '' })
                          }}
                          placeholder="As per bank records"
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                            errors.bank_account_holder_name ? 'border-red-300' : 'border-gray-300'
                          }`}
                          required
                        />
                        {errors.bank_account_holder_name && (
                          <p className="text-red-500 text-sm mt-1">{errors.bank_account_holder_name}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Account Number <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.bank_account_number}
                          onChange={(e) => {
                            setFormData({ ...formData, bank_account_number: e.target.value.replace(/\D/g, '') })
                            setErrors({ ...errors, bank_account_number: '' })
                          }}
                          placeholder="Enter account number"
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                            errors.bank_account_number ? 'border-red-300' : 'border-gray-300'
                          }`}
                          required
                        />
                        {errors.bank_account_number && (
                          <p className="text-red-500 text-sm mt-1">{errors.bank_account_number}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Confirm Account Number <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.bank_account_number_confirm}
                          onChange={(e) => {
                            setFormData({ ...formData, bank_account_number_confirm: e.target.value.replace(/\D/g, '') })
                            setErrors({ ...errors, bank_account_number_confirm: '' })
                          }}
                          placeholder="Re-enter account number"
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                            errors.bank_account_number_confirm ? 'border-red-300' : 'border-gray-300'
                          }`}
                          required
                        />
                        {errors.bank_account_number_confirm && (
                          <p className="text-red-500 text-sm mt-1">{errors.bank_account_number_confirm}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          IFSC Code <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.bank_ifsc_code}
                          onChange={(e) => {
                            setFormData({ ...formData, bank_ifsc_code: e.target.value.toUpperCase().replace(/\s/g, '') })
                            setErrors({ ...errors, bank_ifsc_code: '' })
                          }}
                          placeholder="SBIN0001234"
                          maxLength={11}
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                            errors.bank_ifsc_code ? 'border-red-300' : 'border-gray-300'
                          }`}
                          required
                        />
                        {errors.bank_ifsc_code && (
                          <p className="text-red-500 text-sm mt-1">{errors.bank_ifsc_code}</p>
                        )}
                        <p className="text-xs text-gray-500 mt-1">
                          11-character code (e.g., SBIN0001234). Find it on your cheque or passbook.
                        </p>
                      </div>
                    </div>
                  </div>

                  {errors.submit && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                      {errors.submit}
                    </div>
                  )}

                  <div className="flex gap-3 pt-4">
                    <button
                      type="button"
                      onClick={handleBack}
                      className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                    >
                      ← Back
                    </button>
                    <button
                      type="submit"
                      disabled={submitting}
                      className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium"
                    >
                      {submitting ? 'Submitting...' : 'Submit for Verification'}
                    </button>
                  </div>
                </div>
              )}
            </form>
          </div>
        )}

        {/* Success Step */}
        {step === 3 && (
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">KYC Submitted Successfully!</h2>
            <p className="text-gray-600 mb-6">
              Your documents are under review. We'll notify you within 1-2 business days.
            </p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium"
              >
                Go to Dashboard
              </button>
              <button
                onClick={() => navigate('/profile')}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                View Profile
              </button>
            </div>
          </div>
        )}

        {/* Info Box */}
        <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Why we need this information</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
            <div className="flex items-start">
              <span className="text-primary-600 mr-2">•</span>
              <span>Required by RBI for financial transactions</span>
            </div>
            <div className="flex items-start">
              <span className="text-primary-600 mr-2">•</span>
              <span>Ensures secure payout processing</span>
            </div>
            <div className="flex items-start">
              <span className="text-primary-600 mr-2">•</span>
              <span>Prevents fraud and identity theft</span>
            </div>
            <div className="flex items-start">
              <span className="text-primary-600 mr-2">•</span>
              <span>One-time verification process</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
