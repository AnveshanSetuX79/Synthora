import { useState, useEffect } from 'react';
import api from '../services/api';

const AIBusinessInsights = ({ leadId }) => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');

  useEffect(() => {
    fetchInsights();
  }, [leadId]);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/leads/${leadId}/ai-insights`);
      setInsights(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load AI insights');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
      </div>
    );
  }

  if (!insights) return null;

  const tabs = [
    { id: 'summary', label: '📊 Summary', icon: '📊' },
    { id: 'opportunity', label: '💰 Opportunity', icon: '💰' },
    { id: 'strategy', label: '🎯 Strategy', icon: '🎯' },
    { id: 'outreach', label: '💬 Outreach', icon: '💬' },
    { id: 'pricing', label: '💵 Pricing', icon: '💵' },
  ];

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-2xl font-bold text-gray-900">
            🤖 AI Business Intelligence
          </h2>
          <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
            {insights.generation_method === 'template' ? 'Template Mode' : 'AI Generated'}
          </span>
        </div>
        <p className="text-sm text-gray-600">
          Generated {new Date(insights.generated_at).toLocaleString()}
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 text-sm font-medium whitespace-nowrap transition ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Summary Tab */}
        {activeTab === 'summary' && (
          <div className="space-y-6">
            {/* Business Summary */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Business Overview</h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                <p className="text-gray-700">{insights.business_summary.summary}</p>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-gray-600">
                    Confidence: <strong>{insights.business_summary.confidence_level}</strong> ({insights.business_summary.confidence_score}%)
                  </span>
                  <span className="text-gray-600">
                    Source: <strong>{insights.business_summary.data_source}</strong>
                  </span>
                </div>
              </div>
            </div>

            {/* Digital Presence */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Digital Presence</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-3xl font-bold text-blue-600 mb-1">
                    {insights.digital_presence.overall_score}/100
                  </div>
                  <div className="text-sm text-gray-600">Digital Score</div>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="text-3xl font-bold text-purple-600 mb-1">
                    {insights.conversion_probability.percentage}%
                  </div>
                  <div className="text-sm text-gray-600">Conversion Probability</div>
                </div>
              </div>
              
              <div className="mt-4 space-y-2">
                {Object.entries(insights.digital_presence.breakdown).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Missing Elements */}
            {insights.digital_presence.missing_elements.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Missing Elements</h3>
                <div className="space-y-2">
                  {insights.digital_presence.missing_elements.map((element, index) => (
                    <div key={index} className="flex items-center gap-2 text-gray-700">
                      <span className="text-red-500">❌</span>
                      <span>{element}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Opportunity Tab */}
        {activeTab === 'opportunity' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
              <div className="text-4xl mb-2">{insights.opportunity_analysis.level}</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Opportunity Level</h3>
              <p className="text-gray-700">{insights.conversion_probability.reasoning}</p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Missed Revenue Estimate</h3>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-2xl font-bold text-yellow-900">
                  {insights.opportunity_analysis.missed_revenue_estimate}
                </p>
                <p className="text-sm text-yellow-700 mt-1">
                  Potential revenue being lost without proper digital presence
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Growth Potential</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                    {insights.opportunity_analysis.growth_potential.level}
                  </span>
                  <span className="text-gray-600">
                    Timeline: {insights.opportunity_analysis.growth_potential.timeline}
                  </span>
                </div>
                <ul className="space-y-2">
                  {insights.opportunity_analysis.growth_potential.factors.map((factor, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-green-500 mt-1">✓</span>
                      <span className="text-gray-700">{factor}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Market Position</h3>
              <p className="text-gray-700 bg-gray-50 rounded-lg p-4">
                {insights.opportunity_analysis.market_position}
              </p>
            </div>
          </div>
        )}

        {/* Strategy Tab */}
        {activeTab === 'strategy' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Opening Line</h3>
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
                <p className="text-gray-800">{insights.sales_strategy.opening_line}</p>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Value Pitch</h3>
              <div className="bg-green-50 border-l-4 border-green-500 p-4">
                <p className="text-gray-800">{insights.sales_strategy.value_pitch}</p>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Best Time to Contact</h3>
              <p className="text-gray-700 bg-yellow-50 rounded-lg p-4">
                ⏰ {insights.sales_strategy.best_time_to_contact}
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Approach Style</h3>
              <p className="text-gray-700 bg-purple-50 rounded-lg p-4">
                🎯 {insights.sales_strategy.approach_style}
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Objection Handling</h3>
              <div className="space-y-3">
                {Object.entries(insights.sales_strategy.objection_handling).map(([objection, response]) => (
                  <div key={objection} className="border border-gray-200 rounded-lg p-4">
                    <div className="font-medium text-gray-900 mb-2 capitalize">
                      "{objection.replace(/_/g, ' ')}"
                    </div>
                    <div className="text-gray-700 text-sm">{response}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Outreach Tab */}
        {activeTab === 'outreach' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">💬 WhatsApp Message</h3>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans">
                  {insights.outreach_messages.whatsapp_message}
                </pre>
                <button
                  onClick={() => navigator.clipboard.writeText(insights.outreach_messages.whatsapp_message)}
                  className="mt-3 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                >
                  📋 Copy Message
                </button>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">📞 Call Script</h3>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans">
                  {insights.outreach_messages.call_script}
                </pre>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">🔄 Follow-up Message</h3>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans">
                  {insights.outreach_messages.follow_up_message}
                </pre>
                <button
                  onClick={() => navigator.clipboard.writeText(insights.outreach_messages.follow_up_message)}
                  className="mt-3 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm"
                >
                  📋 Copy Message
                </button>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">📱 SMS Message</h3>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-gray-800">{insights.outreach_messages.sms_message}</p>
                <button
                  onClick={() => navigator.clipboard.writeText(insights.outreach_messages.sms_message)}
                  className="mt-3 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 text-sm"
                >
                  📋 Copy Message
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Pricing Tab */}
        {activeTab === 'pricing' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Recommended Services</h3>
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="text-xl font-bold text-gray-900">{insights.recommended_services.primary.service}</h4>
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mt-2 ${
                      insights.recommended_services.primary.priority === 'HIGH' ? 'bg-red-100 text-red-800' :
                      insights.recommended_services.primary.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {insights.recommended_services.primary.priority} Priority
                    </span>
                  </div>
                </div>
                <p className="text-gray-700 mb-2">{insights.recommended_services.primary.description}</p>
                <p className="text-sm text-gray-600">
                  <strong>Impact:</strong> {insights.recommended_services.primary.impact}
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Additional Services</h4>
                <ul className="space-y-2">
                  {insights.recommended_services.secondary.map((service, index) => (
                    <li key={index} className="flex items-center gap-2 text-gray-700">
                      <span className="text-blue-500">+</span>
                      <span>{service}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Pricing Recommendations</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">Basic Website</div>
                  <div className="text-2xl font-bold text-gray-900">{insights.recommended_services.pricing.basic_website}</div>
                </div>
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">With Booking System</div>
                  <div className="text-2xl font-bold text-gray-900">{insights.recommended_services.pricing.with_booking_system}</div>
                </div>
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">Full Package</div>
                  <div className="text-2xl font-bold text-gray-900">{insights.recommended_services.pricing.full_package}</div>
                </div>
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">Monthly Maintenance</div>
                  <div className="text-2xl font-bold text-gray-900">{insights.recommended_services.pricing.monthly_maintenance}</div>
                </div>
              </div>

              <div className="mt-4 bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Pricing Factors:</h4>
                <ul className="space-y-1">
                  {insights.recommended_services.pricing.pricing_factors.map((factor, index) => (
                    <li key={index} className="text-sm text-gray-700">• {factor}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Project Timeline</h3>
              <p className="text-gray-700 bg-blue-50 rounded-lg p-4">
                ⏱️ {insights.recommended_services.timeline}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Data Transparency Footer */}
      <div className="border-t border-gray-200 bg-gray-50 p-6">
        <details className="cursor-pointer">
          <summary className="font-semibold text-gray-900 mb-2">
            🔍 Data Transparency & Sources
          </summary>
          <div className="mt-4 space-y-4 text-sm">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Real Data (Verified):</h4>
              <ul className="space-y-1 text-gray-700">
                {Object.entries(insights.data_transparency.real_data).map(([key, value]) => (
                  <li key={key}>
                    <strong className="capitalize">{key.replace(/_/g, ' ')}:</strong> {value}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">AI Generated (Estimated):</h4>
              <ul className="space-y-1 text-gray-700">
                {Object.entries(insights.data_transparency.ai_generated).map(([key, value]) => (
                  <li key={key}>
                    <strong className="capitalize">{key.replace(/_/g, ' ')}:</strong> {value}
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
              <p className="text-yellow-800 text-xs">{insights.data_transparency.disclaimer}</p>
            </div>
          </div>
        </details>
      </div>
    </div>
  );
};

export default AIBusinessInsights;
