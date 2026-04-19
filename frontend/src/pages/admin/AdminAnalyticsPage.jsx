import { useState, useEffect } from 'react';
import { useAuthStore } from '../../store/authStore';

const AdminAnalyticsPage = () => {
  const { token } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let url = 'http://localhost:8000/api/admin/analytics/dashboard';
      const params = new URLSearchParams();
      if (dateRange.start) params.append('start_date', dateRange.start);
      if (dateRange.end) params.append('end_date', dateRange.end);
      if (params.toString()) url += `?${params.toString()}`;
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch dashboard data');
      }
      
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      console.error('Error fetching admin dashboard:', err);
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = async () => {
    try {
      let url = 'http://localhost:8000/api/admin/analytics/export';
      const params = new URLSearchParams();
      if (dateRange.start) params.append('start_date', dateRange.start);
      if (dateRange.end) params.append('end_date', dateRange.end);
      if (params.toString()) url += `?${params.toString()}`;
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error('Failed to export CSV');
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `admin-analytics-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      console.error('Error exporting CSV:', err);
      alert('Failed to export CSV');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 font-semibold">Error Loading Dashboard</p>
            <p className="text-red-700 mt-2">{error}</p>
            <button onClick={fetchDashboardData} className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Analytics Dashboard</h1>
              <p className="text-gray-600">Platform-wide metrics and insights</p>
            </div>
            <button onClick={exportToCSV} className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
              📊 Export CSV
            </button>
          </div>
          
          {/* Date Range Filter */}
          <div className="bg-white rounded-lg shadow p-4 flex gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <button onClick={fetchDashboardData} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Apply Filter
            </button>
            <button 
              onClick={() => {
                setDateRange({ start: '', end: '' });
                setTimeout(fetchDashboardData, 100);
              }} 
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Clear
            </button>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">User Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Users</div>
              <div className="text-3xl font-bold text-gray-900">{metrics?.users?.total || 0}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Freelancers</div>
              <div className="text-3xl font-bold text-blue-600">{metrics?.users?.freelancers || 0}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Business Owners</div>
              <div className="text-3xl font-bold text-green-600">{metrics?.users?.business_owners || 0}</div>
            </div>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Deal Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Deals</div>
              <div className="text-3xl font-bold text-gray-900">{metrics?.deals?.total || 0}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Active Deals</div>
              <div className="text-3xl font-bold text-yellow-600">{metrics?.deals?.active || 0}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Completed Deals</div>
              <div className="text-3xl font-bold text-green-600">{metrics?.deals?.completed || 0}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Avg Deal Value</div>
              <div className="text-3xl font-bold text-purple-600">₹{metrics?.deals?.average_value || 0}</div>
            </div>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Revenue Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Revenue</div>
              <div className="text-3xl font-bold text-green-600">₹{metrics?.revenue?.total || 0}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Today</div>
              <div className="text-2xl font-bold text-gray-900">₹{metrics?.revenue?.today || 0}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">This Week</div>
              <div className="text-2xl font-bold text-gray-900">₹{metrics?.revenue?.this_week || 0}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">This Month</div>
              <div className="text-2xl font-bold text-gray-900">₹{metrics?.revenue?.this_month || 0}</div>
            </div>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Commission Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Commission Rate</div>
              <div className="text-3xl font-bold text-purple-600">{((metrics?.commission?.rate || 0) * 100).toFixed(0)}%</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Commission</div>
              <div className="text-3xl font-bold text-green-600">₹{metrics?.commission?.total || 0}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Commission in Period</div>
              <div className="text-3xl font-bold text-blue-600">₹{metrics?.commission?.in_period || 0}</div>
            </div>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Conversion & Performance</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Overall Conversion Rate</div>
              <div className="text-3xl font-bold text-primary-600 mb-2">{metrics?.conversion?.overall_rate || 0}%</div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div className="bg-primary-600 h-3 rounded-full" style={{ width: `${metrics?.conversion?.overall_rate || 0}%` }} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Response Rate</div>
              <div className="text-3xl font-bold text-blue-600 mb-2">{metrics?.conversion?.response_rate || 0}%</div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div className="bg-blue-600 h-3 rounded-full" style={{ width: `${metrics?.conversion?.response_rate || 0}%` }} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Dispute Rate</div>
              <div className="text-3xl font-bold text-red-600 mb-2">{metrics?.conversion?.dispute_rate || 0}%</div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div className="bg-red-600 h-3 rounded-full" style={{ width: `${metrics?.conversion?.dispute_rate || 0}%` }} />
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Review Metrics</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Reviews</span>
                <span className="text-2xl font-bold text-gray-900">{metrics?.reviews?.total || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Average Rating</span>
                <span className="text-2xl font-bold text-yellow-600">⭐ {metrics?.reviews?.average_rating || 0}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Dispute Metrics</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Disputes</span>
                <span className="text-2xl font-bold text-gray-900">{metrics?.disputes?.total || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Open Disputes</span>
                <span className="text-2xl font-bold text-red-600">{metrics?.disputes?.open || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Resolved Disputes</span>
                <span className="text-2xl font-bold text-green-600">{metrics?.disputes?.resolved || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminAnalyticsPage;
