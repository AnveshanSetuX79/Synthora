import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function InsightPanel({ lead, onClose, onClaim, onViewDetails, claiming, canClaim }) {
  const navigate = useNavigate()
  
  if (!lead) return null
  
  // Handle both flat structure (AvailableLeadItem) and nested structure (LeadResponse)
  const businessName = lead.business_name || lead.business?.name || 'Unknown Business'
  const category = lead.category || lead.business?.category || 'Business'
  const address = lead.address || lead.business?.address || ''
  const city = lead.city || lead.business?.city || ''
  const phone = lead.phone || lead.business?.phone
  const leadId = lead.lead_id || lead.id
  
  // Insights can be flat or nested
  const digitalScore = lead.digital_score || lead.insights?.digital_score || 0
  const opportunityTag = lead.opportunity_tag || lead.insights?.opportunity_tag || 'Low'
  const freshness = lead.freshness || lead.insights?.freshness || 'low'
  const rating = lead.rating || lead.insights?.rating
  const reviewCount = lead.review_count || lead.insights?.review_count || 0
  const hasWebsite = lead.has_website !== undefined ? lead.has_website : lead.insights?.has_website
  const websiteUrl = lead.website_url || lead.insights?.website_url
  const scoreBreakdown = lead.digital_score_breakdown || lead.insights?.digital_score_breakdown
  const lastVerified = lead.last_verified || lead.insights?.last_verified
  
  const handleClaimClick = async () => {
    if (onClaim) {
      await onClaim(leadId)
    }
  }
  
  const handleViewDetailsClick = () => {
    if (onViewDetails) {
      onViewDetails()
    } else {
      navigate(`/leads/${leadId}`)
    }
    if (onClose) {
      onClose()
    }
  }
  
  const getOpportunityColor = (tag) => {
    switch (tag) {
      case 'High': return 'bg-red-100 text-red-800 border-red-300'
      case 'Medium': return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'Low': return 'bg-green-100 text-green-800 border-green-300'
      default: return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }
  
  const getFreshnessColor = (freshness) => {
    switch (freshness) {
      case 'high': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }
  
  return (
    <>
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-[1001]"
        onClick={onClose}
      />
      
      {/* Panel */}
      <div className="fixed right-0 top-0 h-full w-full md:w-96 bg-white shadow-2xl z-[1002] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-2xl font-bold text-gray-900">{businessName}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
            >
              ×
            </button>
          </div>
          
          {/* Category */}
          <div className="mb-4">
            <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              {category}
            </span>
          </div>
          
          {/* Address */}
          <div className="mb-4">
            <p className="text-sm text-gray-600">
              <span className="font-medium">📍</span> {address}
            </p>
            <p className="text-sm text-gray-500 mt-1">{city}</p>
          </div>
          
          {/* Phone */}
          {phone && (
            <div className="mb-4">
              <p className="text-sm text-gray-600">
                <span className="font-medium">📞</span> {phone}
              </p>
            </div>
          )}
          
          {/* Tags */}
          <div className="flex gap-2 mb-6">
            <span className={`px-3 py-1 text-sm font-semibold rounded border ${getOpportunityColor(opportunityTag)}`}>
              {opportunityTag} Opportunity
            </span>
            <span className={`px-3 py-1 text-sm font-semibold rounded ${getFreshnessColor(freshness)}`}>
              {freshness} freshness
            </span>
          </div>
          
          {/* Digital Score */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Digital Score</span>
              <span className="text-2xl font-bold text-blue-600">{digitalScore}/100</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${digitalScore}%` }}
              />
            </div>
          </div>
          
          {/* Score Breakdown */}
          {scoreBreakdown && (
            <div className="mb-6">
              <h3 className="text-sm font-bold text-gray-900 mb-3">Score Breakdown</h3>
              <div className="space-y-2">
                {Object.entries(scoreBreakdown).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="font-medium">{value} pts</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Business Insights */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-bold text-gray-900 mb-3">Business Insights</h3>
            <div className="space-y-2 text-sm">
              {rating && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Rating</span>
                  <span className="font-medium">⭐ {rating}/5</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-600">Reviews</span>
                <span className="font-medium">{reviewCount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Website</span>
                <span className={`font-medium ${hasWebsite ? 'text-green-600' : 'text-red-600'}`}>
                  {hasWebsite ? '✓ Yes' : '✗ No'}
                </span>
              </div>
              {websiteUrl && (
                <div className="flex justify-between">
                  <span className="text-gray-600">URL</span>
                  <a 
                    href={websiteUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-xs truncate max-w-[150px]"
                  >
                    {websiteUrl}
                  </a>
                </div>
              )}
              {lastVerified && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Verified</span>
                  <span className="font-medium text-xs">
                    {new Date(lastVerified).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>
          
          {/* Growth Opportunities */}
          <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="text-sm font-bold text-green-900 mb-2">🚀 Growth Opportunities</h3>
            <ul className="text-sm text-green-800 space-y-1">
              {!hasWebsite && (
                <li>• Build professional website to increase online visibility</li>
              )}
              {reviewCount < 20 && (
                <li>• Implement review collection strategy to build trust</li>
              )}
              {category === 'restaurant' && (
                <>
                  <li>• Add online ordering system for convenience</li>
                  <li>• Create digital menu with photos</li>
                  <li>• Set up table reservation system</li>
                </>
              )}
              {category === 'school' && (
                <>
                  <li>• Develop online admission portal</li>
                  <li>• Create virtual tour of facilities</li>
                  <li>• Build parent communication app</li>
                </>
              )}
              {category === 'retail' && (
                <>
                  <li>• Launch e-commerce platform</li>
                  <li>• Implement inventory management system</li>
                  <li>• Create loyalty program</li>
                </>
              )}
            </ul>
          </div>
          
          {/* Digital Weaknesses */}
          <div className="mb-6 p-4 bg-orange-50 rounded-lg border border-orange-200">
            <h3 className="text-sm font-bold text-orange-900 mb-2">⚠️ Digital Weaknesses</h3>
            <ul className="text-sm text-orange-800 space-y-1">
              {!hasWebsite && (
                <li>• Missing website - losing potential customers</li>
              )}
              {reviewCount < 10 && (
                <li>• Low review count - limited social proof</li>
              )}
              {rating < 4 && rating > 0 && (
                <li>• Rating below 4.0 - reputation management needed</li>
              )}
              {digitalScore < 40 && (
                <li>• Very low digital presence - high improvement potential</li>
              )}
              <li>• No social media integration detected</li>
              <li>• Missing online booking/ordering system</li>
            </ul>
          </div>
          
          {/* Why This Lead? */}
          <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="text-sm font-bold text-blue-900 mb-2">💡 Why This Lead?</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              {!hasWebsite && (
                <li>• No website - high conversion potential</li>
              )}
              {rating >= 4 && (
                <li>• High rating ({rating}⭐) - quality business</li>
              )}
              {reviewCount > 50 && (
                <li>• {reviewCount} reviews - established presence</li>
              )}
              {opportunityTag === 'High' && (
                <li>• High opportunity score - act fast!</li>
              )}
              {freshness === 'high' && (
                <li>• Fresh lead - recently verified</li>
              )}
            </ul>
          </div>
          
          {/* Available Slots */}
          <div className="mb-6 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-yellow-900">Available Slots</span>
              <span className="text-lg font-bold text-yellow-900">
                {lead.available_slots !== undefined ? lead.available_slots : '5'}/5
              </span>
            </div>
            <p className="text-xs text-yellow-700 mt-1">
              {lead.available_slots === 0 ? 'No slots available' : 'Freelancers can still contact this business'}
            </p>
          </div>
          
          {/* Actions */}
          <div className="space-y-3">
            {lead.demo_url && (
              <button
                type="button"
                onClick={() => window.open(lead.demo_url, '_blank')}
                className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
              >
                <span>🌐</span>
                <span>View Demo Website</span>
              </button>
            )}
            
            {onClaim && (
              <button
                type="button"
                onClick={handleClaimClick}
                disabled={claiming || !canClaim}
                className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {claiming ? 'Claiming...' : !canClaim ? 'No Slots Available' : '🎯 Claim This Lead'}
              </button>
            )}
            
            <button
              type="button"
              onClick={handleViewDetailsClick}
              className="w-full bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold border-2 border-blue-600 hover:bg-blue-50 transition-colors"
            >
              View Full Details
            </button>
            
            <button
              type="button"
              onClick={onClose}
              className="w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

export default InsightPanel
