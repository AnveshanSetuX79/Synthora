import { useState, useEffect } from 'react'
import { useAuthStore } from '../../store/authStore'

function FailureLogsPage() {
  const { token } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [logs, setLogs] = useState([])
  const [stats, setStats] = useState(null)
  const [selectedLog, setSelectedLog] = useState(null)
  
  // Filters
  const [filters, setFilters] = useState({
    service: '',
    status: '',
    search: ''
  })
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 50,
    total: 0
  })

  useEffect(() => {
    fetchStats()
    fetchLogs()
  }, [filters, pagination.skip])

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/admin/failures/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) throw new Error('Failed to fetch stats')
      
      const data = await response.json()
      setStats(data)
    } catch (err) {
      console.error('Error fetching stats:', err)
    }
  }

  const fetchLogs = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const params = new URLSearchParams({
        skip: pagination.skip.toString(),
        limit: pagination.limit.toString()
      })
      
      if (filters.service) params.append('service', filters.service)
      if (filters.status) params.append('status', filters.status)
      if (filters.search) params.append('search', filters.search)
      
      const response = await fetch(
        `http://localhost:8000/api/admin/failures/logs?${params.toString()}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
      
      if (!response.ok) throw new Error('Failed to fetch logs')
      
      const data = await response.json()
      setLogs(data.logs || [])
      setPagination(prev => ({ ...prev, total: data.total }))
    } catch (err) {
      console.error('Error fetching logs:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = async (logId) => {
    if (!confirm('Retry this failed operation?')) return
    
    try {
      const response = await fetch('http://localhost:8000/api/admin/failures/retry', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ failure_log_id: logId })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to retry')
      }
      
      alert('Retry initiated successfully')
      await fetchLogs()
      await fetchStats()
    } catch (err) {
      console.error('Retry error:', err)
      alert(err.message || 'Failed to retry')
    }
  }

  const handleResolve = async (logId) => {
    if (!confirm('Mark this failure as resolved?')) return
    
    try {
      const response = await fetch('http://localhost:8000/api/admin/failures/resolve', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ failure_log_id: logId })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to resolve')
      }
      
      alert('Failure resolved successfully')
      await fetchLogs()
      await fetchStats()
    } catch (err) {
      console.error('Resolve error:', err)
      alert(err.message || 'Failed to resolve')
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'retrying': return 'bg-blue-100 text-blue-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'resolved': return 'bg-green-100 text-green-800'
      case 'fallback': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getServiceIcon = (service) => {
    switch (service) {
      case 'sms': return '📱'
      case 'email': return '📧'
      case 'payment': return '💳'
      default: return '❓'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🔧 Failure Logs & Retry Management</h1>
          <p className="text-gray-600">Monitor and manage failed operations with automatic retry</p>
        </div>

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Failures</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_failures}</div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Requiring Attention</div>
              <div className="text-3xl font-bold text-orange-600">{stats.requiring_attention}</div>
              <div className="text-xs text-gray-500 mt-1">Pending + Retrying</div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Failed (Max Attempts)</div>
              <div className="text-3xl font-bold text-red-600">{stats.by_status.failed}</div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Resolved</div>
              <div className="text-3xl font-bold text-green-600">{stats.by_status.resolved}</div>
            </div>
          </div>
        )}

        {/* Service Breakdown */}
        {stats && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Failures by Service</h2>
            <div className="grid grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-4xl mb-2">📱</div>
                <div className="text-2xl font-bold text-gray-900">{stats.by_service.sms}</div>
                <div className="text-sm text-gray-600">SMS Failures</div>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">📧</div>
                <div className="text-2xl font-bold text-gray-900">{stats.by_service.email}</div>
                <div className="text-sm text-gray-600">Email Failures</div>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">💳</div>
                <div className="text-2xl font-bold text-gray-900">{stats.by_service.payment}</div>
                <div className="text-sm text-gray-600">Payment Failures</div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Service</label>
              <select
                value={filters.service}
                onChange={(e) => setFilters(prev => ({ ...prev, service: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600"
              >
                <option value="">All Services</option>
                <option value="sms">SMS</option>
                <option value="email">Email</option>
                <option value="payment">Payment</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="retrying">Retrying</option>
                <option value="failed">Failed</option>
                <option value="resolved">Resolved</option>
                <option value="fallback">Fallback</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <input
                type="text"
                placeholder="Target or error message..."
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600"
              />
            </div>
            
            <div className="flex items-end">
              <button
                onClick={() => {
                  setFilters({ service: '', status: '', search: '' })
                  setPagination(prev => ({ ...prev, skip: 0 }))
                }}
                className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Failure Logs Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Failure Logs</h2>
            <p className="text-sm text-gray-600 mt-1">
              Showing {logs.length} of {pagination.total} failures
            </p>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading failure logs...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-600 mb-4">{error}</p>
              <button onClick={fetchLogs} className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                Retry
              </button>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600">No failure logs found</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Target</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Attempts</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Error</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {logs.map((log) => (
                      <tr key={log.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <span className="text-2xl mr-2">{getServiceIcon(log.service)}</span>
                            <span className="text-sm font-medium text-gray-900 capitalize">{log.service}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">{log.target}</div>
                          <div className="text-xs text-gray-500">{log.operation}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-semibold rounded ${getStatusColor(log.status)}`}>
                            {log.status}
                          </span>
                          {log.admin_notified && (
                            <span className="ml-2 text-xs text-orange-600">🔔 Notified</span>
                          )}
                          {log.fallback_attempted && (
                            <span className="ml-2 text-xs text-purple-600">↪️ Fallback</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.attempt_number} / {log.max_attempts}
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-red-600 max-w-xs truncate" title={log.error_message}>
                            {log.error_message || 'No error message'}
                          </div>
                          {log.error_code && (
                            <div className="text-xs text-gray-500">Code: {log.error_code}</div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(log.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="flex gap-2">
                            <button
                              onClick={() => setSelectedLog(log)}
                              className="text-blue-600 hover:text-blue-800"
                              title="View Details"
                            >
                              👁️
                            </button>
                            {log.status !== 'resolved' && (
                              <>
                                <button
                                  onClick={() => handleRetry(log.id)}
                                  className="text-green-600 hover:text-green-800"
                                  title="Retry Now"
                                >
                                  🔄
                                </button>
                                <button
                                  onClick={() => handleResolve(log.id)}
                                  className="text-purple-600 hover:text-purple-800"
                                  title="Mark Resolved"
                                >
                                  ✓
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
                <button
                  onClick={() => setPagination(prev => ({ ...prev, skip: Math.max(0, prev.skip - prev.limit) }))}
                  disabled={pagination.skip === 0}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600">
                  Page {Math.floor(pagination.skip / pagination.limit) + 1} of {Math.ceil(pagination.total / pagination.limit)}
                </span>
                <button
                  onClick={() => setPagination(prev => ({ ...prev, skip: prev.skip + prev.limit }))}
                  disabled={pagination.skip + pagination.limit >= pagination.total}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </>
          )}
        </div>

        {/* Detail Modal */}
        {selectedLog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-2xl font-bold text-gray-900">Failure Details</h2>
                  <button
                    onClick={() => setSelectedLog(null)}
                    className="text-gray-400 hover:text-gray-600 text-2xl"
                  >
                    ×
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Service</label>
                    <div className="mt-1 flex items-center">
                      <span className="text-2xl mr-2">{getServiceIcon(selectedLog.service)}</span>
                      <span className="text-lg capitalize">{selectedLog.service}</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Operation</label>
                    <p className="mt-1 text-gray-900">{selectedLog.operation}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Target</label>
                    <p className="mt-1 text-gray-900">{selectedLog.target}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Status</label>
                    <span className={`inline-block mt-1 px-3 py-1 text-sm font-semibold rounded ${getStatusColor(selectedLog.status)}`}>
                      {selectedLog.status}
                    </span>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Attempts</label>
                    <p className="mt-1 text-gray-900">{selectedLog.attempt_number} / {selectedLog.max_attempts}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Error Message</label>
                    <p className="mt-1 text-red-600 bg-red-50 p-3 rounded">{selectedLog.error_message || 'No error message'}</p>
                  </div>

                  {selectedLog.error_code && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Error Code</label>
                      <p className="mt-1 text-gray-900">{selectedLog.error_code}</p>
                    </div>
                  )}

                  {selectedLog.metadata && Object.keys(selectedLog.metadata).length > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Metadata</label>
                      <pre className="mt-1 text-sm bg-gray-50 p-3 rounded overflow-x-auto">
                        {JSON.stringify(selectedLog.metadata, null, 2)}
                      </pre>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Created At</label>
                      <p className="mt-1 text-gray-900">{new Date(selectedLog.created_at).toLocaleString()}</p>
                    </div>

                    {selectedLog.next_retry_at && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Next Retry</label>
                        <p className="mt-1 text-gray-900">{new Date(selectedLog.next_retry_at).toLocaleString()}</p>
                      </div>
                    )}
                  </div>

                  {selectedLog.resolved_at && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Resolved At</label>
                      <p className="mt-1 text-gray-900">{new Date(selectedLog.resolved_at).toLocaleString()}</p>
                    </div>
                  )}

                  <div className="flex gap-2 pt-4">
                    {selectedLog.status !== 'resolved' && (
                      <>
                        <button
                          onClick={() => {
                            handleRetry(selectedLog.id)
                            setSelectedLog(null)
                          }}
                          className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                        >
                          🔄 Retry Now
                        </button>
                        <button
                          onClick={() => {
                            handleResolve(selectedLog.id)
                            setSelectedLog(null)
                          }}
                          className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                        >
                          ✓ Mark Resolved
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => setSelectedLog(null)}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default FailureLogsPage
