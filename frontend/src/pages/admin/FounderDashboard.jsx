import { useState, useEffect } from 'react'
import { analyticsAPI } from '../../services/api'

function FounderDashboard() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [timeRange, setTimeRange] = useState('30') // 7, 30, 90 days

  useEffect(() => {
    fetchFounderMetrics()
  }, [timeRange])

  const fetchFounderMetrics = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await analyticsAPI.getFounderDashboard(timeRange)
      setMetrics(response.data)
    } catch (err) {
      console.error('Error fetching founder dashboard:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (value, threshold, inverse = false) => {
    if (inverse) {
      return value <= threshold ? 'text-red-600' : 'text-green-600'
    }
    return value >= threshold ? 'text-green-600' : 'text-red-600'
  }

  const exportToCSV = () => {
    if (!metrics) return
    const csvData = [
      ['Metric', 'Value', 'Status'],
      ['Response Rate', `${metrics.viability?.response_rate || 0}%`, metrics.viability?.response_rate >= 15 ? 'Good' : 'Critical'],
      ['Demo to Signup', `${metrics.viability?.demo_to_signup || 0}%`, metrics.viability?.demo_to_signup >= 10 ? 'Good' : 'Critical'],
      ['Signup to Deal', `${metrics.viability?.signup_to_deal || 0}%`, metrics.viability?.signup_to_deal >= 20 ? 'Good' : 'Critical'],
      ['Average Deal Value', `₹${metrics.financial?.avg_deal_value || 0}`, ''],
      ['Revenue Per Day', `₹${metrics.financial?.revenue_per_day || 0}`, ''],
      ['Monthly Burn Rate', `₹${metrics.financial?.monthly_burn || 0}`, ''],
      ['Runway (months)', metrics.financial?.runway_months || 0, metrics.financial?.runway_months >= 6 ? 'Good' : 'Critical'],
    ]
    const csvContent = csvData.map(row => row.join(',')).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `founder-metrics-${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading founder metrics...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 font-semibold">Error Loading Dashboard</p>
            <p className="text-red-700 mt-2">{error}</p>
            <button onClick={fetchFounderMetrics} className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">🚀 Founder Business Viability Dashboard</h1>
            <p className="text-gray-600">Critical metrics for business decision-making</p>
          </div>
          <div className="flex gap-3">
            {/* Time Range Selector */}
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600"
            >
              <option value="7">Last 7 Days</option>
              <option value="30">Last 30 Days</option>
              <option value="90">Last 90 Days</option>
            </select>
            <button onClick={exportToCSV} className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
              Export CSV
            </button>
          </div>
        </div>

        {/* Critical Alerts */}
        {metrics?.alerts && metrics.alerts.length > 0 && (
          <div className="mb-8 bg-red-50 border-2 border-red-300 rounded-lg p-6">
            <h2 className="text-xl font-bold text-red-900 mb-4">⚠️ Critical Alerts</h2>
            <div className="space-y-2">
              {metrics.alerts.map((alert, idx) => (
                <div key={idx} className="flex items-start">
                  <span className="text-red-600 mr-2">•</span>
                  <span className="text-red-800">{alert}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Viability Metrics */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 Viability Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Response Rate</div>
              <div className={`text-3xl font-bold ${getStatusColor(metrics?.viability?.response_rate || 0, 15)}`}>
                {metrics?.viability?.response_rate || 0}%
              </div>
              <div className="text-xs text-gray-500 mt-2">Target: ≥15% (Viable)</div>
              <div className="text-xs text-gray-600 mt-1">
                {metrics?.viability?.total_contacted || 0} contacted, {metrics?.viability?.total_responded || 0} responded
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Demo → Signup Conversion</div>
              <div className={`text-3xl font-bold ${getStatusColor(metrics?.viability?.demo_to_signup || 0, 10)}`}>
                {metrics?.viability?.demo_to_signup || 0}%
              </div>
              <div className="text-xs text-gray-500 mt-2">Target: ≥10% (Viable)</div>
              <div className="text-xs text-gray-600 mt-1">
                {metrics?.viability?.demos_viewed || 0} demos, {metrics?.viability?.signups || 0} signups
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Signup → Deal Conversion</div>
              <div className={`text-3xl font-bold ${getStatusColor(metrics?.viability?.signup_to_deal || 0, 20)}`}>
                {metrics?.viability?.signup_to_deal || 0}%
              </div>
              <div className="text-xs text-gray-500 mt-2">Target: ≥20% (Viable)</div>
              <div className="text-xs text-gray-600 mt-1">
                {metrics?.viability?.signups || 0} signups, {metrics?.viability?.deals_created || 0} deals
              </div>
            </div>
          </div>
        </div>

        {/* Financial Metrics */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">💰 Financial Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Average Deal Value</div>
              <div className="text-3xl font-bold text-green-600">
                ₹{(metrics?.financial?.avg_deal_value || 0).toLocaleString()}
              </div>
              <div className="text-xs text-gray-500 mt-2">Per completed deal</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Revenue / Day</div>
              <div className="text-3xl font-bold text-blue-600">
                ₹{(metrics?.financial?.revenue_per_day || 0).toLocaleString()}
              </div>
              <div className="text-xs text-gray-500 mt-2">Average daily revenue</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Monthly Burn Rate</div>
              <div className="text-3xl font-bold text-orange-600">
                ₹{(metrics?.financial?.monthly_burn || 0).toLocaleString()}
              </div>
              <div className="text-xs text-gray-500 mt-2">Estimated monthly costs</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Runway</div>
              <div className={`text-3xl font-bold ${getStatusColor(metrics?.financial?.runway_months || 0, 6)}`}>
                {metrics?.financial?.runway_months || 0} mo
              </div>
              <div className="text-xs text-gray-500 mt-2">Target: ≥6 months</div>
            </div>
          </div>
        </div>

        {/* Cohort Analysis */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">👥 Cohort Analysis</h2>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tier</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Freelancers</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deals</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Completion Rate</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Deal Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Revenue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {metrics?.cohorts?.map((cohort, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${
                        cohort.tier === 'new' ? 'bg-gray-100 text-gray-800' :
                        cohort.tier === 'verified' ? 'bg-blue-100 text-blue-800' :
                        'bg-purple-100 text-purple-800'
                      }`}>
                        {cohort.tier}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{cohort.freelancer_count}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{cohort.total_deals}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{cohort.completion_rate}%</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{cohort.avg_deal_value.toLocaleString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">₹{cohort.total_revenue.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Geographic Performance */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">🌍 Geographic Performance</h2>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">City</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Businesses</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deals</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Conversion Rate</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Deal Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Revenue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {metrics?.geographic?.map((geo, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{geo.city}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{geo.total_businesses}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{geo.total_deals}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{geo.conversion_rate}%</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{geo.avg_deal_value.toLocaleString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">₹{geo.total_revenue.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Trend Graphs Placeholder */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📈 Trends Over Time</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Revenue Trend</h3>
              <div className="h-48 flex items-center justify-center bg-gray-50 rounded">
                <p className="text-gray-500">Chart visualization coming soon</p>
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Conversion Trend</h3>
              <div className="h-48 flex items-center justify-center bg-gray-50 rounded">
                <p className="text-gray-500">Chart visualization coming soon</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FounderDashboard
