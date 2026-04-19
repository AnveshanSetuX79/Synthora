import { useState, useEffect } from 'react'
import { authAPI } from '../services/api'

function OTPModal({ userId, phone, onSuccess, onClose }) {
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [resendTimer, setResendTimer] = useState(60)

  // Countdown timer for resend
  useEffect(() => {
    if (resendTimer > 0) {
      const timer = setTimeout(() => setResendTimer(resendTimer - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [resendTimer])

  const handleOTPChange = (e) => {
    const value = e.target.value.replace(/\D/g, '') // Only digits
    if (value.length <= 6) {
      setOtp(value)
      setError('')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (otp.length !== 6) {
      setError('Please enter a 6-digit OTP')
      return
    }

    setLoading(true)
    setError('')

    try {
      await authAPI.verifyOTP({
        phone: phone,
        otp_code: otp,
      })

      setSuccess(true)
      
      // Auto-close after 1.5 seconds
      setTimeout(() => {
        onSuccess()
      }, 1500)
    } catch (err) {
      const errorMessage = err.response?.data?.detail?.message || 'Invalid OTP'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    if (resendTimer > 0) return

    setLoading(true)
    setError('')

    try {
      // In production, call resend OTP API
      // await authAPI.resendOTP({ user_id: userId })
      
      setResendTimer(60)
      setOtp('')
    } catch (err) {
      setError('Failed to resend OTP')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
        {success ? (
          <div className="text-center">
            <div className="text-6xl mb-4">✓</div>
            <h3 className="text-2xl font-bold text-green-600 mb-2">
              Verification Successful!
            </h3>
            <p className="text-gray-600">Redirecting to login...</p>
          </div>
        ) : (
          <>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold">Verify Phone Number</h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            <p className="text-gray-600 mb-6">
              We've sent a 6-digit OTP to <strong>{phone}</strong>
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Enter OTP
                </label>
                <input
                  type="text"
                  value={otp}
                  onChange={handleOTPChange}
                  className="input-field text-center text-2xl tracking-widest"
                  placeholder="000000"
                  maxLength={6}
                  autoFocus
                />
                {error && (
                  <p className="text-red-500 text-sm mt-2">{error}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading || otp.length !== 6}
                className="btn-primary w-full"
              >
                {loading ? 'Verifying...' : 'Verify OTP'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-600 text-sm">
                Didn't receive the code?{' '}
                {resendTimer > 0 ? (
                  <span className="text-gray-400">
                    Resend in {resendTimer}s
                  </span>
                ) : (
                  <button
                    onClick={handleResend}
                    disabled={loading}
                    className="text-primary-600 hover:text-primary-700 font-medium"
                  >
                    Resend OTP
                  </button>
                )}
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default OTPModal
