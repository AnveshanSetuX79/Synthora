import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { leadsAPI, demosAPI } from '../../services/api'
import DemoPreviewModal from '../../components/DemoPreviewModal'
import AICopilotPanel from '../../components/AICopilotPanel'

function LeadDetailPage() {
  const { leadId } = useParams()
  const navigate = useNavigate()
  
  const [lead, setLead] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [claiming, setClaiming] = useState(false)
  const [exclusivityTimer, setExclusivityTimer] = useState(null)
  const [generatingDemo, setGeneratingDemo] = useState(false)
  const [demoUrl, setDemoUrl] = useState(null)
  const [showDemoModal, setShowDemoModal] = useState(false)
  const [showCopilot, setShowCopilot] = useState(false)
  const [templateType, setTemplateType] = useState('auto')

  // Fetch lead details
  useEffect(() => {
    const fetchLeadDetails = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await leadsAPI.getLeadDetails(leadId)
        setLead(response.data.lead)  // Extract the lead object from the response
        
        // Calculate exclusivity timer if claimed
        if (response.data.lead.exclusivity_window_expires) {
          updateExclusivityTimer(response.data.lead.exclusivity_window_expires)
        }

        // Check if demo already exists
        if (response.data.lead.business?.id) {
          try {
            const demoResponse = await demosAPI.getDemo(response.data.lead.business.id)
            const publicUrl = demosAPI.getPublicDemoUrl(demoResponse.data.demo_id)
            setDemoUrl(publicUrl)
          } catch (err) {
            // Demo doesn't exist yet, that's okay
            setDemoUrl(null)
          }
        }
      } catch (err) {
        setError(err.response?.data?.detail?.message || 'Failed to fetch lead details')
      } finally {
        setLoading(false)
      }
    }

    fetchLeadDetails()
  }, [leadId])

  // Update exclusivity timer
  const updateExclusivityTimer = (expiresAt) => {
    const updateTimer = () => {
      const now = new Date()
      const expires = new Date(expiresAt)
      const diff = expires - now

      if (diff <= 0) {
        setExclusivityTimer('Expired')
        return
      }

      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diff % (1000 * 60)) / 1000)

      setExclusivityTimer(`${hours}h ${minutes}m ${seconds}s`)
    }

    updateTimer()
    const interval = setInterval(updateTimer, 1000)
    return () => clearInterval(interval)
  }

  // Handle claim lead
  const handleClaimLead = async () => {
    setClaiming(true)
    try {
      await leadsAPI.claimLead(leadId)
      // Refresh lead details
      const response = await leadsAPI.getLeadDetails(leadId)
      setLead(response.data.lead)  // Extract the lead object
      alert('Lead claimed successfully! You have 6 hours of exclusivity.')
    } catch (err) {
      alert(err.response?.data?.detail?.message || 'Failed to claim lead')
    } finally {
      setClaiming(false)
    }
  }

  // Handle demo generation
  const handleGenerateDemo = async () => {
    if (!lead?.business?.id) return

    setGeneratingDemo(true)
    try {
      const response = await demosAPI.generateDemo({
        business_id: lead.business.id,
        template_type: templateType
      })
      
      const publicUrl = demosAPI.getPublicDemoUrl(response.data.demo_id)
      setDemoUrl(publicUrl)
      setShowDemoModal(true)
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to generate demo')
    } finally {
      setGeneratingDemo(false)
    }
  }

  // Handle view demo
  const handleViewDemo = () => {
    if (demoUrl) {
      setShowDemoModal(true)
    }
  }

  // Get score breakdown
  const getScoreBreakdown = () => {
    if (!lead?.insights?.digital_score_breakdown) return []
    
    const breakdown = lead.insights.digital_score_breakdown
    return [
      { label: 'Rating', value: breakdown.rating || 0, max: 30 },
      { label: 'Reviews', value: breakdown.reviews || 0, max: 25 },
      { label: 'No Website', value: breakdown.no_website || 0, max: 30 },
      { label: 'Category Priority', value: breakdown.category_priority || 0, max: 15 },
    ]
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading lead details...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
          <button onClick={() => navigate('/leads')} className="btn-secondary mt-4">
            Back to Leads
          </button>
        </div>
      </div>
    )
  }

  if (!lead) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <p className="text-gray-600">Lead not found</p>
          <button onClick={() => navigate('/leads')} className="btn-secondary mt-4">
            Back to Leads
          </button>
        </div>
      </div>
    )
  }

  const business = lead.business || {}
  const insights = lead.insights || {}

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <button
              onClick={() => navigate('/leads')}
              className="text-primary-600 hover:text-primary-700 mb-2 flex items-center"
            >
              ← Back to Leads
            </button>
            <h1 className="text-3xl font-bold">{business.name}</h1>
            <p className="text-gray-600">{business.category} • {business.city}</p>
          </div>
          
          {/* Claim Button */}
          {lead.status === 'new' && (
            <button
              onClick={handleClaimLead}
              disabled={claiming}
              className="btn-primary"
            >
              {claiming ? 'Claiming...' : 'Claim This Lead'}
            </button>
          )}
        </div>

        {/* Exclusivity Timer */}
        {exclusivityTimer && exclusivityTimer !== 'Expired' && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-6">
            <strong>Exclusivity Window:</strong> {exclusivityTimer} remaining
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Business Details */}
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Business Details</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Address:</span>
                  <span className="font-medium text-right">{business.address}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Phone:</span>
                  <span className="font-medium">{business.phone || 'Not available'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Rating:</span>
                  <span className="font-medium">
                    {insights.rating ? `${insights.rating} ⭐` : 'No rating'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Reviews:</span>
                  <span className="font-medium">{insights.review_count || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Website:</span>
                  <span className="font-medium">
                    {insights.has_website ? (
                      <a href={insights.website_url} target="_blank" rel="noopener noreferrer" className="text-primary-600">
                        View Website
                      </a>
                    ) : (
                      <span className="text-green-600">No website ✓</span>
                    )}
                  </span>
                </div>
              </div>
            </div>

            {/* Score Breakdown */}
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Lead Score Breakdown</h2>
              <div className="space-y-4">
                {getScoreBreakdown().map((item) => (
                  <div key={item.label}>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-600">{item.label}</span>
                      <span className="text-sm font-medium">{item.value}/{item.max}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${(item.value / item.max) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
                <div className="pt-4 border-t">
                  <div className="flex justify-between">
                    <span className="font-bold">Total Score:</span>
                    <span className="font-bold text-primary-600">{lead.score}/100</span>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Business Intelligence */}
            {insights.ai_description && (
              <div className="card bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
                <div className="flex items-center mb-4">
                  <span className="text-2xl mr-2">🤖</span>
                  <h2 className="text-xl font-bold">AI Business Intelligence</h2>
                </div>
                
                {/* Business Description */}
                <div className="mb-4">
                  <h3 className="font-semibold text-gray-700 mb-2">About This Business</h3>
                  <p className="text-gray-600">{insights.ai_description}</p>
                </div>

                {/* Intelligence Scores */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {insights.ai_digital_maturity && (
                    <div className="bg-white rounded-lg p-3">
                      <div className="text-xs text-gray-500 mb-1">Digital Maturity</div>
                      <div className={`text-sm font-semibold capitalize ${
                        insights.ai_digital_maturity === 'high' ? 'text-green-600' :
                        insights.ai_digital_maturity === 'medium' ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {insights.ai_digital_maturity}
                      </div>
                    </div>
                  )}
                  
                  {insights.ai_growth_potential && (
                    <div className="bg-white rounded-lg p-3">
                      <div className="text-xs text-gray-500 mb-1">Growth Potential</div>
                      <div className={`text-sm font-semibold capitalize ${
                        insights.ai_growth_potential === 'high' ? 'text-green-600' :
                        insights.ai_growth_potential === 'medium' ? 'text-yellow-600' :
                        'text-gray-600'
                      }`}>
                        {insights.ai_growth_potential}
                      </div>
                    </div>
                  )}
                  
                  {insights.ai_online_presence_score !== null && (
                    <div className="bg-white rounded-lg p-3">
                      <div className="text-xs text-gray-500 mb-1">Online Presence</div>
                      <div className="text-sm font-semibold text-blue-600">
                        {insights.ai_online_presence_score}/100
                      </div>
                    </div>
                  )}
                  
                  {insights.ai_urgency_score !== null && (
                    <div className="bg-white rounded-lg p-3">
                      <div className="text-xs text-gray-500 mb-1">Urgency Score</div>
                      <div className="text-sm font-semibold text-orange-600">
                        {insights.ai_urgency_score}/100
                      </div>
                    </div>
                  )}
                </div>

                {/* Specialties */}
                {insights.ai_specialties && insights.ai_specialties.length > 0 && (
                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-700 mb-2">Specialties</h3>
                    <div className="flex flex-wrap gap-2">
                      {insights.ai_specialties.map((specialty, i) => (
                        <span key={i} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                          {specialty}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Target Customers */}
                {insights.ai_target_customers && insights.ai_target_customers.length > 0 && (
                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-700 mb-2">Target Customers</h3>
                    <div className="flex flex-wrap gap-2">
                      {insights.ai_target_customers.map((customer, i) => (
                        <span key={i} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                          👥 {customer}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Pain Points */}
                {insights.ai_pain_points && insights.ai_pain_points.length > 0 && (
                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-700 mb-2">Business Challenges</h3>
                    <ul className="space-y-2">
                      {insights.ai_pain_points.map((pain, i) => (
                        <li key={i} className="flex items-start">
                          <span className="text-yellow-500 mr-2">⚠️</span>
                          <span className="text-gray-600 text-sm">{pain}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommended Solutions */}
                {insights.ai_recommended_solutions && insights.ai_recommended_solutions.length > 0 && (
                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-700 mb-2">Recommended Solutions</h3>
                    <ul className="space-y-2">
                      {insights.ai_recommended_solutions.map((solution, i) => (
                        <li key={i} className="flex items-start">
                          <span className="text-green-500 mr-2">✅</span>
                          <span className="text-gray-600 text-sm">{solution}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Competitive Advantages */}
                {insights.ai_competitive_advantages && insights.ai_competitive_advantages.length > 0 && (
                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-700 mb-2">Competitive Advantages</h3>
                    <ul className="space-y-2">
                      {insights.ai_competitive_advantages.map((advantage, i) => (
                        <li key={i} className="flex items-start">
                          <span className="text-purple-500 mr-2">🏆</span>
                          <span className="text-gray-600 text-sm">{advantage}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Pitch Suggestions */}
                {insights.ai_pitch_suggestions && insights.ai_pitch_suggestions.length > 0 && (
                  <div className="bg-white rounded-lg p-4 border-2 border-purple-300">
                    <h3 className="font-semibold text-purple-700 mb-2 flex items-center">
                      <span className="mr-2">💡</span>
                      How to Pitch This Lead
                    </h3>
                    <ul className="space-y-2">
                      {insights.ai_pitch_suggestions.map((suggestion, i) => (
                        <li key={i} className="text-gray-700 text-sm">
                          <span className="font-medium text-purple-600">{i + 1}.</span> {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* AI Confidence */}
                {insights.ai_enrichment_confidence && (
                  <div className="mt-4 text-xs text-gray-500 text-center">
                    AI Confidence: {(insights.ai_enrichment_confidence * 100).toFixed(0)}%
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Quick Stats</h2>
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-gray-600">Lead Score</span>
                  <div className="text-2xl font-bold text-primary-600">{lead.score}</div>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Freshness</span>
                  <div className="text-lg font-medium capitalize">{insights.freshness}</div>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Status</span>
                  <div className="text-lg font-medium capitalize">{lead.status}</div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Actions</h2>
              
              {/* Demo Generation */}
              {!demoUrl ? (
                <div className="space-y-3 mb-4">
                  <label className="block text-sm font-medium text-gray-700">
                    Template Type
                  </label>
                  <select
                    value={templateType}
                    onChange={(e) => setTemplateType(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg"
                    disabled={lead.status === 'new'}
                  >
                    <option value="auto">Auto (Based on Category)</option>
                    <option value="restaurant">Restaurant</option>
                    <option value="school">School</option>
                  </select>
                  <button
                    type="button"
                    onClick={handleGenerateDemo}
                    disabled={lead.status === 'new' || generatingDemo}
                    className="btn-primary w-full"
                  >
                    {generatingDemo ? 'Generating...' : 'Generate Demo'}
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={handleViewDemo}
                  className="btn-primary w-full mb-2"
                >
                  View Demo
                </button>
              )}

              <div className="space-y-2">
                <button
                  type="button"
                  onClick={() => setShowCopilot(true)}
                  className="btn-primary w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  disabled={lead.status === 'new'}
                >
                  ✨ AI Business Copilot
                </button>
                <button
                  type="button"
                  onClick={() => navigate(`/outreach/${leadId}`)}
                  className="btn-secondary w-full"
                  disabled={lead.status === 'new'}
                >
                  Send Message
                </button>
                <button
                  type="button"
                  onClick={() => navigate(`/deals/create/${business.id}`)}
                  className="btn-secondary w-full"
                  disabled={lead.status === 'new'}
                >
                  Create Deal
                </button>
              </div>
              {lead.status === 'new' && (
                <p className="text-xs text-gray-500 mt-2">
                  Claim this lead to unlock actions
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Demo Preview Modal */}
        <DemoPreviewModal
          isOpen={showDemoModal}
          onClose={() => setShowDemoModal(false)}
          demoUrl={demoUrl}
          businessName={business.name}
          businessId={business.id}
        />

        {/* AI Copilot Panel */}
        {showCopilot && (
          <AICopilotPanel
            leadId={leadId}
            onClose={() => setShowCopilot(false)}
          />
        )}
      </div>
    </div>
  )
}

export default LeadDetailPage
