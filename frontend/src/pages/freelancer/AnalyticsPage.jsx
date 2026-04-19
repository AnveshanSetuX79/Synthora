import { useState, useEffect } from 'react'
import { analyticsAPI } from '../../services/api'

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState('Month')
  const [roiMetrics, setRoiMetrics] = useState(null)
  const [funnel, setFunnel] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAnalytics()
  }, [period])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch ROI metrics
      const roiResponse = await analyticsAPI.getFreelancerROI({ period })
      setRoiMetrics(roiResponse.data.roi_metrics)

      // Fetch conversion funnel
      const funnelResponse = await analyticsAPI.getConversionFunnel()
      setFunnel(funnelResponse.data.funnel)

      setLoading(false)
    } catch (err) {
      console.error('Error fetching analytics:', err)
      setError(err.response?.data?.detail?.message || 'Failed to load analytics')
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
        <p className="mt-2 text-gray-600">Track your performance and ROI</p>
      </div>

      {/* Period Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Time Period</label>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="Week">Last 7 Days</option>
          <option value="Month">Last 30 Days</option>
          <option value="Quarter">Last 90 Days</option>
          <option value="AllTime">All Time</option>
        </select>
      </div>

      {/* ROI Metrics */}
      {roiMetrics && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">ROI Metrics</h2>
          
          {/* Earnings Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Total Earnings</p>
              <p className="text-3xl font-bold text-green-600">₹{roiMetrics.earnings.total.toLocaleString()}</p>
              <p className="text-sm text-gray-500 mt-2">Avg per deal: ₹{roiMetrics.earnings.average_per_deal.toLocaleString()}</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Win Rate</p>
              <p className="text-3xl font-bold text-blue-600">{roiMetrics.deals.win_rate}%</p>
              <p className="text-sm text-gray-500 mt-2">{roiMetrics.deals.closed} of {roiMetrics.leads.used} leads</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 mb-1">Avg Time to Close</p>
              <p className="text-3xl font-bold text-purple-600">{roiMetrics.efficiency.avg_time_to_close_days} days</p>
              <p className="text-sm text-gray-500 mt-2">Expected close: {roiMetrics.efficiency.expected_close_probability}%</p>
            </div>
          </div>

          {/* Efficiency Metrics */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Efficiency Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600 mb-2">Cost Per Acquisition</p>
                <p className="text-2xl font-bold text-gray-900">{roiMetrics.efficiency.cost_per_acquisition.toFixed(1)} messages/deal</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-2">Leads Used</p>
                <p className="text-2xl font-bold text-gray-900">{roiMetrics.leads.used} leads</p>
                <p className="text-sm text-gray-500">{roiMetrics.leads.contacted} contacted</p>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-600">Conversion Rate</span>
                  <span className="text-sm font-semibold text-gray-900">{roiMetrics.performance.conversion_rate}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${roiMetrics.performance.conversion_rate}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-600">Response Rate</span>
                  <span className="text-sm font-semibold text-gray-900">{roiMetrics.performance.response_rate}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${roiMetrics.performance.response_rate}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-600">Average Rating</span>
                  <span className="text-sm font-semibold text-gray-900">{roiMetrics.performance.average_rating}/5.0</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-yellow-500 h-2 rounded-full" 
                    style={{ width: `${(roiMetrics.performance.average_rating / 5) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Conversion Funnel */}
      {funnel && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Conversion Funnel</h2>
          <p className="text-sm text-gray-600 mb-6">
            Overall conversion rate: <span className="font-semibold text-blue-600">{funnel.overall_conversion_rate}%</span>
          </p>

          <div className="space-y-4">
            {Object.entries(funnel.funnel).map(([stage, data], index) => (
              <div key={stage}>
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <p className="text-sm font-medium text-gray-900 capitalize">
                      {stage.replace(/_/g, ' ')}
                    </p>
                    <p className="text-xs text-gray-500">
                      {data.count} ({data.percentage}%)
                      {index > 0 && ` • ${data.conversion_from_previous}% from previous`}
                    </p>
                  </div>
                  <span className="text-lg font-bold text-gray-900">{data.count}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className={`h-3 rounded-full ${
                      index === 0 ? 'bg-blue-600' :
                      index === 1 ? 'bg-green-600' :
                      index === 2 ? 'bg-yellow-500' :
                      index === 3 ? 'bg-orange-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${data.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
