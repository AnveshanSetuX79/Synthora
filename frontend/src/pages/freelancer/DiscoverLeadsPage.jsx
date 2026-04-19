import { useState, useEffect } from 'react'
import { leadsAPI } from '../../services/api'
import { useNavigate, useSearchParams } from 'react-router-dom'

function DiscoverLeadsPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [discovering, setDiscovering] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [formData, setFormData] = useState({
    location: 'Pune, India',
    category: 'restaurant',
    limit: 20
  })
  const [detectedLocation, setDetectedLocation] = useState(null)

  // Check for lat/lng in URL params (from "Discover leads near you" link)
  useEffect(() => {
    const lat = searchParams.get('lat')
    const lng = searchParams.get('lng')
    
    if (lat && lng) {
      const locationStr = `${parseFloat(lat).toFixed(4)}, ${parseFloat(lng).toFixed(4)}`
      setDetectedLocation({ lat: parseFloat(lat), lng: parseFloat(lng) })
      setFormData(prev => ({
        ...prev,
        location: locationStr
      }))
    }
  }, [searchParams])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'limit' ? (value ? parseInt(value) : 20) : value
    }))
  }

  const handleDiscover = async (e) => {
    e.preventDefault()
    setDiscovering(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await leadsAPI.discoverLeads(formData)
      const discovered = response.data.discovered || 0
      const stored = response.data.stored || 0
      setSuccess(`Successfully discovered ${discovered} businesses and stored ${stored} new leads!`)
      
      // Don't auto-redirect, let user choose
      // Show button to view leads instead
    } catch (err) {
      console.error('Discover error:', err)
      const errorMsg = err.response?.data?.detail?.message 
        || err.response?.data?.detail 
        || err.message 
        || 'Failed to discover leads'
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
    } finally {
      setDiscovering(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Discover New Leads</h1>
          <p className="text-gray-600">
            Use Google Places API to discover businesses in your target location
          </p>
        </div>

        {/* Discovery Form */}
        <div className="max-w-2xl mx-auto">
          {/* Detected Location Banner */}
          {detectedLocation && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <div className="flex items-start">
                <span className="text-2xl mr-3">📍</span>
                <div className="flex-1">
                  <h3 className="font-semibold text-green-900 mb-1">Location Detected!</h3>
                  <p className="text-sm text-green-800">
                    We've detected your location at coordinates: {detectedLocation.lat.toFixed(4)}, {detectedLocation.lng.toFixed(4)}
                  </p>
                  <p className="text-xs text-green-700 mt-1">
                    The search will use these coordinates to find businesses near you.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <span className="text-2xl mr-3">💡</span>
              <div className="flex-1">
                <h3 className="font-semibold text-blue-900 mb-2">How to Get Best Results</h3>
                <div className="grid md:grid-cols-2 gap-3 text-sm text-blue-800">
                  <div>
                    <p className="font-medium mb-1">📍 Location Tips:</p>
                    <ul className="space-y-0.5 ml-4">
                      <li>• Use specific areas (e.g., "Koregaon Park, Pune")</li>
                      <li>• Major cities have better coverage</li>
                      <li>• Tier 1 & 2 cities work best</li>
                    </ul>
                  </div>
                  <div>
                    <p className="font-medium mb-1">🏢 Category Tips:</p>
                    <ul className="space-y-0.5 ml-4">
                      <li>• Restaurant: Best coverage</li>
                      <li>• School: Good in urban areas</li>
                      <li>• Healthcare: Hospitals & clinics</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <form onSubmit={handleDiscover} className="space-y-6">
              {/* Location Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="e.g., Koregaon Park, Pune or Andheri, Mumbai"
                  required
                />
                <p className="text-sm text-gray-500 mt-1">
                  Enter city name, area name, or coordinates (lat,lng) for precise results
                </p>
                
                {/* Major Cities */}
                <div className="mt-3">
                  <span className="text-xs font-medium text-gray-700">Major Cities:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {['Pune, India', 'Mumbai, India', 'Bangalore, India', 'Delhi, India', 'Hyderabad, India', 'Chennai, India'].map((city) => (
                      <button
                        key={city}
                        type="button"
                        onClick={() => setFormData({ ...formData, location: city })}
                        className="text-xs px-3 py-1.5 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md font-medium"
                      >
                        {city.split(',')[0]}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Popular Areas */}
                <div className="mt-3">
                  <span className="text-xs font-medium text-gray-700">Popular Areas:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {[
                      'Koregaon Park, Pune',
                      'Baner, Pune', 
                      'Andheri, Mumbai',
                      'Bandra, Mumbai',
                      'Whitefield, Bangalore',
                      'Indiranagar, Bangalore',
                      'Connaught Place, Delhi',
                      'Saket, Delhi'
                    ].map((area) => (
                      <button
                        key={area}
                        type="button"
                        onClick={() => setFormData({ ...formData, location: area })}
                        className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded"
                      >
                        {area}
                      </button>
                    ))}
                  </div>
                </div>

                {/* More Cities */}
                <div className="mt-3">
                  <span className="text-xs font-medium text-gray-700">More Cities:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {[
                      'Ahmedabad, India',
                      'Kolkata, India',
                      'Surat, India',
                      'Jaipur, India',
                      'Lucknow, India',
                      'Nagpur, India',
                      'Indore, India',
                      'Chandigarh, India'
                    ].map((city) => (
                      <button
                        key={city}
                        type="button"
                        onClick={() => setFormData({ ...formData, location: city })}
                        className="text-xs px-2 py-1 bg-gray-50 hover:bg-gray-100 text-gray-600 rounded border border-gray-200"
                      >
                        {city.split(',')[0]}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Category Select */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Business Category
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  className="input-field"
                  required
                >
                  <option value="restaurant">Restaurant</option>
                  <option value="school">School</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="retail">Retail Store</option>
                </select>
                <p className="text-sm text-gray-500 mt-1">
                  Currently supported categories with best coverage
                </p>
              </div>

              {/* Limit Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Businesses
                </label>
                <input
                  type="number"
                  name="limit"
                  value={formData.limit}
                  onChange={handleInputChange}
                  className="input-field"
                  min="1"
                  max="60"
                  required
                />
                <p className="text-sm text-gray-500 mt-1">
                  Maximum 60 businesses per search (Google Places API limit)
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                  {error}
                </div>
              )}

              {/* Success Message */}
              {success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
                  <p className="font-semibold mb-2">{success}</p>
                  {success.includes('0 businesses') || success.includes('0 new leads') ? (
                    <div className="mt-3">
                      <p className="text-sm text-yellow-700 mb-2">
                        ⚠️ No businesses were found. This could mean:
                      </p>
                      <ul className="text-sm text-yellow-700 list-disc list-inside mb-3">
                        <li>The location might not have coverage in our database</li>
                        <li>Try using major cities (Pune, Mumbai, Bangalore, Delhi) for best results</li>
                        <li>Some categories work better than others (Restaurant, School, Healthcare)</li>
                        <li>Smaller cities may have limited data availability</li>
                      </ul>
                      <button
                        onClick={() => {
                          setSuccess(null)
                          setFormData({ location: 'Pune, India', category: 'restaurant', limit: 20 })
                        }}
                        className="btn-secondary text-sm"
                      >
                        Try with Pune Restaurants
                      </button>
                    </div>
                  ) : (
                    <div className="flex gap-2 mt-3">
                      <button
                        onClick={() => navigate('/leads', { state: { fromDiscover: true } })}
                        className="btn-primary text-sm"
                      >
                        View Leads
                      </button>
                      <button
                        onClick={() => navigate('/dashboard', { state: { refresh: true } })}
                        className="btn-secondary text-sm"
                      >
                        Go to Dashboard
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Submit Button */}
              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={discovering}
                  className="btn-primary flex-1"
                >
                  {discovering ? (
                    <>
                      <span className="animate-spin inline-block mr-2">⏳</span>
                      Discovering...
                    </>
                  ) : (
                    '🔍 Discover Leads'
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => navigate('/leads')}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>

          {/* Info Card */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">How it works:</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• We search Google Places API for businesses in your location</li>
              <li>• Each business is scored based on digital presence</li>
              <li>• Businesses without websites get higher priority</li>
              <li>• New leads are added to your available leads list</li>
              <li>• Duplicate businesses are automatically skipped</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DiscoverLeadsPage
