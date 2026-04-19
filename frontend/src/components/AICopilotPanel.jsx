import { useState } from 'react';
import api from '../services/api';

export default function AICopilotPanel({ leadId, onClose }) {
  const [intelligence, setIntelligence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchIntelligence = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post(`/api/leads/copilot/${leadId}`);
      setIntelligence(response.data.intelligence);
    } catch (err) {
      if (err.response?.data?.detail?.error === 'LIMIT_EXCEEDED') {
        setError('AI Copilot limit reached (3 uses per lead)');
      } else if (err.response?.data?.detail?.error === 'NOT_CLAIMED') {
        setError('You must claim this lead first');
      } else {
        setError(err.response?.data?.detail?.message || 'Failed to generate intelligence');
      }
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (urgency) => {
    if (urgency.includes('CRITICAL')) return 'text-red-600';
    if (urgency.includes('HIGH')) return 'text-orange-600';
    return 'text-blue-600';
  };

  const getImpactBadge = (impact) => {
    const colors = {
      'CRITICAL': 'bg-red-100 text-red-800',
      'HIGH': 'bg-orange-100 text-orange-800',
      'MEDIUM': 'bg-yellow-100 text-yellow-800',
      'LOW': 'bg-blue-100 text-blue-800'
    };
    return colors[impact] || colors['MEDIUM'];
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-t-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-4xl">✨</span>
              <div>
                <h2 className="text-2xl font-bold">AI Business Copilot</h2>
                <p className="text-purple-100 text-sm">Actionable sales intelligence powered by AI</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {!intelligence && !loading && !error && (
            <div className="text-center py-12">
              <span className="text-6xl mb-4 block">✨</span>
              <h3 className="text-xl font-semibold mb-2">Get AI-Powered Sales Strategy</h3>
              <p className="text-gray-600 mb-6">
                Analyze this business and get actionable insights to close the deal
              </p>
              <button
                onClick={fetchIntelligence}
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition"
              >
                Generate Intelligence
              </button>
              <p className="text-sm text-gray-500 mt-4">
                Limited to 3 uses per lead
              </p>
            </div>
          )}

          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Analyzing business data...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
              <span className="text-4xl block mb-2">⚠️</span>
              <p className="text-red-800 font-semibold">{error}</p>
            </div>
          )}

          {intelligence && (
            <div className="space-y-6">
              {/* Remaining Uses */}
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xl">⏰</span>
                  <span className="font-semibold text-purple-900">Remaining Uses:</span>
                </div>
                <span className="text-2xl font-bold text-purple-600">{intelligence.remaining_uses}</span>
              </div>

              {/* Urgency Level */}
              <div className={`border-l-4 border-current p-4 rounded ${getUrgencyColor(intelligence.urgency_level)}`}>
                <div className="flex items-center gap-2 font-bold text-lg mb-1">
                  <span className="text-xl">⚡</span>
                  {intelligence.urgency_level}
                </div>
              </div>

              {/* Quick Summary */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                  <span className="text-xl">🎯</span>
                  Quick Summary
                </h3>
                <p className="text-blue-800">{intelligence.quick_summary}</p>
              </div>

              {/* Conversion Probability */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-bold text-green-900 mb-3 flex items-center gap-2">
                  <span className="text-xl">📈</span>
                  Conversion Probability
                </h3>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-3xl font-bold text-green-600">{intelligence.conversion_probability.probability}</div>
                    <div className="text-lg font-semibold">{intelligence.conversion_probability.category}</div>
                  </div>
                  <div className="text-green-700">{intelligence.conversion_probability.advice}</div>
                </div>
              </div>

              {/* Strengths */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <span className="text-xl">✅</span>
                  Business Strengths
                </h3>
                <ul className="space-y-2">
                  {intelligence.strengths.map((strength, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-green-600 mt-1">✓</span>
                      <span>{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Digital Gaps */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <span className="text-xl">⚠️</span>
                  Digital Gaps (Your Opportunity)
                </h3>
                <div className="space-y-3">
                  {intelligence.digital_gaps.map((gap, idx) => (
                    <div key={idx} className="border-l-4 border-orange-400 pl-4 py-2">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold">{gap.gap}</span>
                        <span className={`text-xs px-2 py-1 rounded ${getImpactBadge(gap.impact)}`}>
                          {gap.impact}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-1">{gap.description}</p>
                      <p className="text-sm text-blue-600 font-semibold">→ {gap.solution}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Pain Points */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-bold text-gray-900 mb-3">Their Pain Points</h3>
                <ul className="space-y-2">
                  {intelligence.pain_points.map((pain, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-red-500 mt-1">•</span>
                      <span>{pain}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Recommended Solutions */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-bold text-gray-900 mb-3">Recommended Solutions</h3>
                <div className="space-y-3">
                  {intelligence.recommended_solutions.map((solution, idx) => (
                    <div key={idx} className="bg-gray-50 p-3 rounded">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold">{solution.solution}</span>
                        <span className={`text-xs px-2 py-1 rounded ${getImpactBadge(solution.priority)}`}>
                          {solution.priority}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>⏱️ Timeline: {solution.timeline}</div>
                        <div>💰 ROI: {solution.roi}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sales Strategy */}
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
                <h3 className="font-bold text-purple-900 mb-3 text-lg">🎯 Your Sales Strategy</h3>
                
                <div className="space-y-4">
                  <div>
                    <div className="font-semibold text-purple-800 mb-1">Approach:</div>
                    <div className="bg-white p-2 rounded">{intelligence.sales_strategy.approach}</div>
                  </div>
                  
                  <div>
                    <div className="font-semibold text-purple-800 mb-1">Opening Line:</div>
                    <div className="bg-white p-2 rounded italic">"{intelligence.sales_strategy.opening_line}"</div>
                  </div>
                  
                  <div>
                    <div className="font-semibold text-purple-800 mb-1">Value Proposition:</div>
                    <div className="bg-white p-2 rounded">{intelligence.sales_strategy.value_proposition}</div>
                  </div>
                  
                  <div>
                    <div className="font-semibold text-purple-800 mb-2">Handle Objections:</div>
                    <div className="space-y-2">
                      {Object.entries(intelligence.sales_strategy.objection_handling).map(([objection, response], idx) => (
                        <div key={idx} className="bg-white p-2 rounded">
                          <div className="text-sm font-semibold text-red-600">{objection}</div>
                          <div className="text-sm text-green-600">→ {response}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <div className="font-semibold text-purple-800 mb-1">Closing Technique:</div>
                    <div className="bg-white p-2 rounded font-semibold">{intelligence.sales_strategy.closing_technique}</div>
                  </div>
                </div>
              </div>

              {/* Pitch Angles */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-bold text-gray-900 mb-3">💡 Pitch Angles to Use</h3>
                <ul className="space-y-2">
                  {intelligence.pitch_angles.map((pitch, idx) => (
                    <li key={idx} className="bg-yellow-50 p-2 rounded">{pitch}</li>
                  ))}
                </ul>
              </div>

              {/* Next Actions */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-bold text-gray-900 mb-3">📋 Your Next Actions</h3>
                <div className="space-y-3">
                  {intelligence.next_actions.map((action, idx) => (
                    <div key={idx} className="border-l-4 border-blue-400 pl-4 py-2">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold">{action.action}</span>
                        <span className="text-xs">{action.priority}</span>
                      </div>
                      <p className="text-sm text-gray-600">{action.script}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Deal Value */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-bold text-green-900 mb-3 flex items-center gap-2">
                  <span className="text-xl">💰</span>
                  Estimated Deal Value
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <div className="text-sm text-green-700">Initial Project</div>
                    <div className="text-xl font-bold text-green-600">{intelligence.estimated_deal_value.initial_project}</div>
                  </div>
                  <div>
                    <div className="text-sm text-green-700">Monthly Retainer</div>
                    <div className="text-xl font-bold text-green-600">{intelligence.estimated_deal_value.monthly_retainer}</div>
                  </div>
                  <div>
                    <div className="text-sm text-green-700">Lifetime Value</div>
                    <div className="text-xl font-bold text-green-600">{intelligence.estimated_deal_value.lifetime_value}</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
