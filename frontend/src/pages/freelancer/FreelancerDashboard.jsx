import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import api from '../../services/api';
import { useAuthStore } from '../../store/authStore';

const FreelancerDashboard = () => {
  const location = useLocation();
  const [analytics, setAnalytics] = useState(null);
  const [funnel, setFunnel] = useState(null);
  const [period, setPeriod] = useState('month');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    fetchData();
  }, [period]);

  // Refresh data when component mounts or becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        fetchData();
      }
    };

    // Refresh on mount
    fetchData();

    // Refresh when tab becomes visible
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  // Refresh when navigating from other pages
  useEffect(() => {
    if (location.state?.refresh) {
      fetchData();
      // Clear the state
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Add timeout wrapper
      const timeout = (ms) => new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), ms)
      );
      
      const fetchWithTimeout = async () => {
        const [analyticsRes, funnelRes] = await Promise.all([
          api.get(`/api/analytics/freelancer-roi?period=${period}`),
          api.get('/api/analytics/funnel')
        ]);
        return { analyticsRes, funnelRes };
      };
      
      const { analyticsRes, funnelRes } = await Promise.race([
        fetchWithTimeout(),
        timeout(30000) // 30 second timeout
      ]);
      
      setAnalytics(analyticsRes.data);
      setFunnel(funnelRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      if (error.message === 'Request timeout') {
        setError('Dashboard is taking longer than expected. This might be due to slow database queries. Please try again later.');
      } else {
        setError(error.response?.data?.detail?.message || 'Failed to load dashboard data');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Dashboard</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={fetchData}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name}! 👋
          </h1>
          <p className="text-gray-600">Here's your performance overview</p>
        </div>

        {/* Period Selector */}
        <div className="mb-6 flex gap-2">
          {['week', 'month', 'quarter', 'alltime'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg capitalize transition ${
                period === p
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              {p === 'alltime' ? 'All Time' : p}
            </button>
          ))}
        </div>

        {/* Earnings Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Total Earnings</div>
            <div className="text-3xl font-bold text-gray-900">
              ₹{analytics?.earnings?.total?.toLocaleString() || 0}
            </div>
            <div className="text-sm text-green-600 mt-2">
              Avg: ₹{analytics?.earnings?.average_per_deal?.toLocaleString() || 0}/deal
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Win Rate</div>
            <div className="text-3xl font-bold text-gray-900">
              {analytics?.deals?.win_rate || 0}%
            </div>
            <div className="text-sm text-gray-600 mt-2">
              {analytics?.deals?.closed || 0} of {analytics?.leads?.used || 0} leads
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Deals Closed</div>
            <div className="text-3xl font-bold text-gray-900">
              {analytics?.deals?.closed || 0}
            </div>
            <div className="text-sm text-gray-600 mt-2">
              {analytics?.deals?.created || 0} created
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Current Tier</div>
            <div className="text-3xl font-bold text-gray-900 capitalize">
              {user?.tier || 'New'}
            </div>
            <div className="text-sm text-blue-600 mt-2 cursor-pointer hover:underline" onClick={() => window.location.href = '/profile'}>
              View progress →
            </div>
          </div>
        </div>

        {/* Efficiency Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Efficiency</h3>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-600">Cost per Acquisition</div>
                <div className="text-xl font-bold text-gray-900">
                  {analytics?.efficiency?.cost_per_acquisition?.toFixed(1) || 0} messages
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Expected Close Probability</div>
                <div className="text-xl font-bold text-gray-900">
                  {analytics?.efficiency?.expected_close_probability || 0}%
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance</h3>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-600">Conversion Rate</div>
                <div className="text-xl font-bold text-gray-900">
                  {analytics?.performance?.conversion_rate || 0}%
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Response Rate</div>
                <div className="text-xl font-bold text-gray-900">
                  {analytics?.performance?.response_rate || 0}%
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity</h3>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-600">Leads Used</div>
                <div className="text-xl font-bold text-gray-900">
                  {analytics?.leads?.used || 0}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Messages Sent</div>
                <div className="text-xl font-bold text-gray-900">
                  {analytics?.leads?.contacted || 0}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Conversion Funnel */}
        {funnel && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Conversion Funnel</h3>
            <div className="space-y-4">
              {Object.entries(funnel.funnel || {}).map(([stage, data], index) => {
                const stageNames = {
                  leads_discovered: 'Leads Discovered',
                  leads_contacted: 'Leads Contacted',
                  demos_viewed: 'Demos Viewed',
                  deals_created: 'Deals Created',
                  payments_completed: 'Payments Completed'
                };
                
                return (
                  <div key={stage}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-semibold">
                          {index + 1}
                        </div>
                        <span className="font-medium text-gray-900">
                          {stageNames[stage] || stage}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-gray-900">{data.count}</div>
                        <div className="text-sm text-gray-600">{data.percentage}%</div>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-blue-600 h-3 rounded-full transition-all"
                        style={{ width: `${data.percentage}%` }}
                      />
                    </div>
                    {data.conversion_from_previous !== undefined && (
                      <div className="text-sm text-gray-600 mt-1 ml-11">
                        {data.conversion_from_previous}% conversion from previous stage
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <div className="text-sm text-blue-900">
                <strong>Overall Conversion Rate:</strong> {funnel.overall_conversion_rate}%
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <a
            href="/leads"
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition text-center"
          >
            <div className="text-4xl mb-2">🎯</div>
            <h4 className="font-semibold text-gray-900 mb-1">Browse Leads</h4>
            <p className="text-sm text-gray-600">Find new opportunities</p>
          </a>
          <a
            href="/deals"
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition text-center"
          >
            <div className="text-4xl mb-2">💼</div>
            <h4 className="font-semibold text-gray-900 mb-1">My Deals</h4>
            <p className="text-sm text-gray-600">Manage active projects</p>
          </a>
          <a
            href="/analytics"
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition text-center"
          >
            <div className="text-4xl mb-2">📊</div>
            <h4 className="font-semibold text-gray-900 mb-1">Full Analytics</h4>
            <p className="text-sm text-gray-600">Detailed insights</p>
          </a>
        </div>
      </div>
    </div>
  );
};

export default FreelancerDashboard;
