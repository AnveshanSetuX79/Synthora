import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import api from '../../services/api'

function ProfilePage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState('profile')
  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    phone: '',
    portfolio_url: '',
    tier: 'new',
    daily_limit: 3,
    remaining_contacts: 0,
  })
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [errors, setErrors] = useState({})
  const [success, setSuccess] = useState('')

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/auth/profile')
      setProfileData(response.data)
    } catch (error) {
      console.error('Error fetching profile:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleProfileUpdate = async (e) => {
    e.preventDefault()
    setErrors({})
    setSuccess('')

    // Validation
    const newErrors = {}
    if (!profileData.name) newErrors.name = 'Name is required'
    if (profileData.portfolio_url && !/^https?:\/\/.+/.test(profileData.portfolio_url)) {
      newErrors.portfolio_url = 'Invalid URL format'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    try {
      setSaving(true)
      await api.put('/api/auth/profile', {
        name: profileData.name,
        portfolio_url: profileData.portfolio_url,
      })
      setSuccess('Profile updated successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (error) {
      setErrors({ submit: error.response?.data?.detail?.message || 'Failed to update profile' })
    } finally {
      setSaving(false)
    }
  }

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    setErrors({})
    setSuccess('')

    // Validation
    const newErrors = {}
    if (!passwordData.current_password) newErrors.current_password = 'Current password is required'
    if (!passwordData.new_password) newErrors.new_password = 'New password is required'
    else if (passwordData.new_password.length < 8) {
      newErrors.new_password = 'Password must be at least 8 characters'
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(passwordData.new_password)) {
      newErrors.new_password = 'Password must contain uppercase, lowercase, and number'
    }
    if (passwordData.new_password !== passwordData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    try {
      setSaving(true)
      await api.put('/api/auth/change-password', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      })
      setSuccess('Password changed successfully!')
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' })
      setTimeout(() => setSuccess(''), 3000)
    } catch (error) {
      setErrors({ submit: error.response?.data?.detail?.message || 'Failed to change password' })
    } finally {
      setSaving(false)
    }
  }

  const getTierInfo = (tier) => {
    const tiers = {
      new: {
        name: 'New',
        limit: 3,
        color: 'gray',
        next: 'verified',
        requirements: 'Complete 5 deals to unlock Verified tier',
      },
      verified: {
        name: 'Verified',
        limit: 10,
        color: 'blue',
        next: 'top_rated',
        requirements: 'Complete 20 deals with 80%+ win rate to unlock Top Rated',
      },
      top_rated: {
        name: 'Top Rated',
        limit: 20,
        color: 'purple',
        next: null,
        requirements: 'You are at the highest tier!',
      },
    }
    return tiers[tier] || tiers.new
  }

  const tierInfo = getTierInfo(profileData.tier)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Profile Settings</h1>
          <p className="text-gray-600">Manage your account and preferences</p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {success}
          </div>
        )}

        {/* Error Message */}
        {errors.submit && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {errors.submit}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="card">
              {/* User Info */}
              <div className="text-center pb-6 border-b">
                <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-3xl font-bold text-primary-600">
                    {profileData.name?.charAt(0)?.toUpperCase() || 'U'}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900">{profileData.name}</h3>
                <p className="text-sm text-gray-600">{profileData.email}</p>
              </div>

              {/* Tier Badge */}
              <div className="py-6 border-b">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Current Tier</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold bg-${tierInfo.color}-100 text-${tierInfo.color}-800`}>
                    {tierInfo.name}
                  </span>
                </div>
                <div className="text-sm text-gray-600 mb-3">
                  {profileData.daily_limit} leads per day
                </div>
                <div className="text-xs text-gray-500">
                  {profileData.remaining_contacts} contacts remaining today
                </div>
              </div>

              {/* Navigation */}
              <nav className="pt-6 space-y-1">
                <button
                  onClick={() => setActiveTab('profile')}
                  className={`w-full text-left px-4 py-2 rounded ${
                    activeTab === 'profile'
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Profile Information
                </button>
                <button
                  onClick={() => setActiveTab('tier')}
                  className={`w-full text-left px-4 py-2 rounded ${
                    activeTab === 'tier'
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Tier Progress
                </button>
                <button
                  onClick={() => setActiveTab('password')}
                  className={`w-full text-left px-4 py-2 rounded ${
                    activeTab === 'password'
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Change Password
                </button>
                <button
                  onClick={() => navigate('/kyc')}
                  className="w-full text-left px-4 py-2 rounded text-gray-700 hover:bg-gray-50"
                >
                  KYC Verification
                </button>
                <button
                  onClick={logout}
                  className="w-full text-left px-4 py-2 rounded text-red-600 hover:bg-red-50"
                >
                  Logout
                </button>
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="card">
                <h2 className="text-xl font-semibold mb-6">Profile Information</h2>
                <form onSubmit={handleProfileUpdate} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Full Name
                    </label>
                    <input
                      type="text"
                      value={profileData.name}
                      onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                      className="input-field"
                    />
                    {errors.name && (
                      <p className="text-red-500 text-sm mt-1">{errors.name}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email
                    </label>
                    <input
                      type="email"
                      value={profileData.email}
                      disabled
                      className="input-field bg-gray-50 cursor-not-allowed"
                    />
                    <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={profileData.phone}
                      disabled
                      className="input-field bg-gray-50 cursor-not-allowed"
                    />
                    <p className="text-xs text-gray-500 mt-1">Phone cannot be changed</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Portfolio URL
                    </label>
                    <input
                      type="url"
                      value={profileData.portfolio_url || ''}
                      onChange={(e) => setProfileData({ ...profileData, portfolio_url: e.target.value })}
                      className="input-field"
                      placeholder="https://yourportfolio.com"
                    />
                    {errors.portfolio_url && (
                      <p className="text-red-500 text-sm mt-1">{errors.portfolio_url}</p>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={saving}
                    className="btn-primary"
                  >
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                </form>
              </div>
            )}

            {/* Tier Progress Tab */}
            {activeTab === 'tier' && (
              <div className="card">
                <h2 className="text-xl font-semibold mb-6">Tier Progress</h2>
                
                {/* Current Tier */}
                <div className="bg-gradient-to-r from-primary-50 to-primary-100 rounded-lg p-6 mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-2xl font-bold text-primary-900">{tierInfo.name} Tier</h3>
                      <p className="text-primary-700">{profileData.daily_limit} leads per day</p>
                    </div>
                    <div className="text-5xl">
                      {tierInfo.name === 'New' && '🌱'}
                      {tierInfo.name === 'Verified' && '✅'}
                      {tierInfo.name === 'Top Rated' && '⭐'}
                    </div>
                  </div>
                  <p className="text-sm text-primary-800">{tierInfo.requirements}</p>
                </div>

                {/* Tier Comparison */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900">All Tiers</h3>
                  
                  {['new', 'verified', 'top_rated'].map((tier) => {
                    const info = getTierInfo(tier)
                    const isCurrent = tier === profileData.tier
                    
                    return (
                      <div
                        key={tier}
                        className={`border-2 rounded-lg p-4 ${
                          isCurrent
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold text-gray-900">{info.name}</h4>
                          {isCurrent && (
                            <span className="px-2 py-1 bg-primary-600 text-white text-xs rounded-full">
                              Current
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>• {info.limit} leads per day</p>
                          <p>• 6-hour exclusivity window</p>
                          <p>• Full platform access</p>
                          {tier === 'verified' && <p>• Priority support</p>}
                          {tier === 'top_rated' && <p>• Premium badge</p>}
                          {tier === 'top_rated' && <p>• Featured in marketplace</p>}
                        </div>
                      </div>
                    )
                  })}
                </div>

                {/* Upgrade Tips */}
                {tierInfo.next && (
                  <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-900 mb-2">💡 Tips to Upgrade</h4>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>• Close more deals successfully</li>
                      <li>• Maintain high response rates</li>
                      <li>• Get positive client feedback</li>
                      <li>• Complete KYC verification</li>
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Password Tab */}
            {activeTab === 'password' && (
              <div className="card">
                <h2 className="text-xl font-semibold mb-6">Change Password</h2>
                <form onSubmit={handlePasswordChange} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Password
                    </label>
                    <input
                      type="password"
                      value={passwordData.current_password}
                      onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                      className="input-field"
                      placeholder="••••••••"
                    />
                    {errors.current_password && (
                      <p className="text-red-500 text-sm mt-1">{errors.current_password}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      New Password
                    </label>
                    <input
                      type="password"
                      value={passwordData.new_password}
                      onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                      className="input-field"
                      placeholder="••••••••"
                    />
                    {errors.new_password && (
                      <p className="text-red-500 text-sm mt-1">{errors.new_password}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">
                      Must be 8+ characters with uppercase, lowercase, and number
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      value={passwordData.confirm_password}
                      onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                      className="input-field"
                      placeholder="••••••••"
                    />
                    {errors.confirm_password && (
                      <p className="text-red-500 text-sm mt-1">{errors.confirm_password}</p>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={saving}
                    className="btn-primary"
                  >
                    {saving ? 'Changing...' : 'Change Password'}
                  </button>
                </form>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
