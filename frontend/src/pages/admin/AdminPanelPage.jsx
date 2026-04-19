import { useState, useEffect } from 'react'
import { useAuthStore } from '../../store/authStore'
import { useSearchParams } from 'react-router-dom'

function AdminPanelPage() {
  const { token } = useAuthStore()
  const [searchParams] = useSearchParams()
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'businesses')
  const [loading, setLoading] = useState(false)
  
  // Businesses
  const [businesses, setBusinesses] = useState([])
  const [businessSearch, setBusinessSearch] = useState('')
  const [editingBusiness, setEditingBusiness] = useState(null)
  
  // Refresh status
  const [refreshStatus, setRefreshStatus] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  
  // Freelancers
  const [freelancers, setFreelancers] = useState([])
  const [selectedFreelancer, setSelectedFreelancer] = useState(null)
  
  // KYC
  const [pendingKYC, setPendingKYC] = useState([])
  const [selectedKYC, setSelectedKYC] = useState(null)
  
  // Disputes
  const [disputes, setDisputes] = useState([])
  const [selectedDispute, setSelectedDispute] = useState(null)

  useEffect(() => {
    if (activeTab === 'businesses') {
      fetchBusinesses()
      fetchRefreshStatus()
    }
    else if (activeTab === 'freelancers') fetchFreelancers()
    else if (activeTab === 'kyc') fetchPendingKYC()
    else if (activeTab === 'disputes') fetchDisputes()
  }, [activeTab])

  const fetchBusinesses = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8000/api/admin/businesses?search=${businessSearch}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
      
      if (!response.ok) {
        throw new Error('Failed to fetch businesses')
      }
      
      const data = await response.json()
      setBusinesses(data.businesses || [])
    } catch (err) {
      console.error('Error fetching businesses:', err)
      alert('Failed to load businesses. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const fetchRefreshStatus = async () => {
    try {
      const response = await fetch(
        'http://localhost:8000/api/admin/businesses/refresh/status',
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
      
      if (response.ok) {
        const data = await response.json()
        setRefreshStatus(data)
      }
    } catch (err) {
      console.error('Error fetching refresh status:', err)
    }
  }

  const triggerRefresh = async () => {
    if (!confirm('Trigger business data refresh? This will update businesses that haven\'t been refreshed in 7+ days.')) return
    
    setRefreshing(true)
    try {
      const response = await fetch(
        'http://localhost:8000/api/admin/businesses/refresh',
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to trigger refresh')
      }
      
      const result = await response.json()
      alert(`Refresh completed!\nProcessed: ${result.total_processed}\nSuccessful: ${result.successful}\nFailed: ${result.failed}`)
      
      // Refresh the status and business list
      await fetchRefreshStatus()
      await fetchBusinesses()
    } catch (err) {
      console.error('Refresh error:', err)
      alert(err.message || 'Failed to trigger refresh')
    } finally {
      setRefreshing(false)
    }
  }

  const updateBusiness = async (businessId, updates) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/admin/businesses/${businessId}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(updates)
        }
      )
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to update business')
      }
      
      // Update UI immediately
      setBusinesses(prev => prev.map(b => 
        b.id === businessId ? { ...b, ...updates } : b
      ))
      
      alert('Business updated successfully')
      setEditingBusiness(null)
      
      // Refresh to ensure consistency
      await fetchBusinesses()
    } catch (err) {
      console.error('Update error:', err)
      alert(err.message || 'Failed to update business')
    }
  }

  const deleteBusiness = async (businessId) => {
    if (!confirm('Are you sure you want to delete this business?')) return
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/admin/businesses/${businessId}`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to delete business')
      }
      
      // Immediately remove from UI for better UX
      setBusinesses(prev => prev.filter(b => b.id !== businessId))
      
      // Show success message
      alert('Business deleted successfully')
      
      // Refresh the list to ensure consistency
      await fetchBusinesses()
    } catch (err) {
      console.error('Delete error:', err)
      alert(err.message || 'Failed to delete business')
      // Refresh list even on error to show current state
      await fetchBusinesses()
    }
  }

  const fetchFreelancers = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        'http://localhost:8000/api/admin/freelancers',
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
      const data = await response.json()
      setFreelancers(data.freelancers || [])
    } catch (err) {
      console.error('Error fetching freelancers:', err)
    } finally {
      setLoading(false)
    }
  }

  const freelancerAction = async (freelancerId, action, reason) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/admin/freelancers/${freelancerId}/action`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action, reason })
        }
      )
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `Failed to ${action} freelancer`)
      }
      
      // Update UI immediately
      setFreelancers(prev => prev.map(f => {
        if (f.id === freelancerId) {
          return {
            ...f,
            is_active: action === 'activate'
          }
        }
        return f
      }))
      
      alert(`Freelancer ${action}ed successfully`)
      
      // Refresh to ensure consistency
      await fetchFreelancers()
    } catch (err) {
      console.error('Freelancer action error:', err)
      alert(err.message || `Failed to ${action} freelancer`)
    }
  }

  const fetchPendingKYC = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        'http://localhost:8000/api/admin/kyc/pending',
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
      const data = await response.json()
      setPendingKYC(data.submissions || [])
    } catch (err) {
      console.error('Error fetching KYC:', err)
    } finally {
      setLoading(false)
    }
  }

  const reviewKYC = async (kycId, approved, rejectionReason = null) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/admin/kyc/${kycId}/review`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ approved, rejection_reason: rejectionReason })
        }
      )
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to review KYC')
      }
      
      // Remove from pending list immediately
      setPendingKYC(prev => prev.filter(k => k.id !== kycId))
      
      alert(approved ? 'KYC approved' : 'KYC rejected')
      setSelectedKYC(null)
      
      // Refresh to ensure consistency
      await fetchPendingKYC()
    } catch (err) {
      console.error('KYC review error:', err)
      alert(err.message || 'Failed to review KYC')
    }
  }

  const fetchDisputes = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        'http://localhost:8000/api/admin/disputes',
        { headers: { 'Authorization': `Bearer ${token}` } }
      )
      const data = await response.json()
      setDisputes(data.disputes || [])
    } catch (err) {
      console.error('Error fetching disputes:', err)
    } finally {
      setLoading(false)
    }
  }

  const resolveDispute = async (dealId, resolution, amount = null, notes = null) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/admin/disputes/${dealId}/resolve`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ resolution, amount, notes })
        }
      )
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to resolve dispute')
      }
      
      // Remove from disputes list immediately
      setDisputes(prev => prev.filter(d => d.id !== dealId))
      
      alert('Dispute resolved successfully')
      setSelectedDispute(null)
      
      // Refresh to ensure consistency
      await fetchDisputes()
    } catch (err) {
      console.error('Dispute resolution error:', err)
      alert(err.message || 'Failed to resolve dispute')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Admin Panel</h1>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b">
          {['businesses', 'freelancers', 'kyc', 'disputes'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium capitalize ${
                activeTab === tab
                  ? 'border-b-2 border-primary-600 text-primary-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Businesses Tab */}
        {activeTab === 'businesses' && (
          <div className="space-y-4">
            {/* Refresh Status Card */}
            {refreshStatus && (
              <div className="card bg-blue-50 border-blue-200">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-lg mb-2">🔄 Data Refresh Status</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Total Businesses</p>
                        <p className="font-bold text-xl">{refreshStatus.statistics.total_active_businesses}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Need Refresh</p>
                        <p className="font-bold text-xl text-orange-600">
                          {refreshStatus.statistics.needing_refresh}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Refreshed (24h)</p>
                        <p className="font-bold text-xl text-green-600">
                          {refreshStatus.statistics.refreshed_last_24h}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Scheduler</p>
                        <p className="font-bold text-xl">
                          {refreshStatus.scheduler.running ? '✅ Running' : '❌ Stopped'}
                        </p>
                      </div>
                    </div>
                    {refreshStatus.scheduler.jobs && refreshStatus.scheduler.jobs.length > 0 && (
                      <div className="mt-2 text-xs text-gray-600">
                        Next scheduled run: {new Date(refreshStatus.scheduler.jobs[0].next_run).toLocaleString()}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={triggerRefresh}
                    disabled={refreshing}
                    className="btn-primary text-sm"
                  >
                    {refreshing ? 'Refreshing...' : '🔄 Refresh Now'}
                  </button>
                </div>
              </div>
            )}

            {/* Business List Card */}
            <div className="card">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Lead Management</h2>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Search businesses..."
                  value={businessSearch}
                  onChange={(e) => setBusinessSearch(e.target.value)}
                  className="input-field"
                />
                <button onClick={fetchBusinesses} className="btn-primary">
                  Search
                </button>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left">Name</th>
                      <th className="px-4 py-2 text-left">Category</th>
                      <th className="px-4 py-2 text-left">Address</th>
                      <th className="px-4 py-2 text-left">Phone</th>
                      <th className="px-4 py-2 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {businesses.map(business => (
                      <tr key={business.id} className="border-t">
                        <td className="px-4 py-2">{business.name}</td>
                        <td className="px-4 py-2">{business.category}</td>
                        <td className="px-4 py-2 text-sm">{business.address}</td>
                        <td className="px-4 py-2">{business.phone}</td>
                        <td className="px-4 py-2">
                          <button
                            onClick={() => setEditingBusiness(business)}
                            className="text-blue-600 hover:underline mr-2"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => deleteBusiness(business.id)}
                            className="text-red-600 hover:underline"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            </div>
          </div>
        )}

        {/* Freelancers Tab */}
        {activeTab === 'freelancers' && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Freelancer Monitoring</h2>
            
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : (
              <div className="space-y-4">
                {freelancers.map(freelancer => (
                  <div key={freelancer.id} className="border rounded p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-bold">{freelancer.name}</h3>
                        <p className="text-sm text-gray-600">{freelancer.email}</p>
                        <div className="flex gap-2 mt-2">
                          <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                            {freelancer.tier}
                          </span>
                          <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                            KYC: {freelancer.kyc_status}
                          </span>
                          <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">
                            {freelancer.completed_deals} / {freelancer.total_deals} deals
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {freelancer.is_active ? (
                          <button
                            onClick={() => freelancerAction(freelancer.id, 'suspend', 'Admin action')}
                            className="btn-secondary text-sm"
                          >
                            Suspend
                          </button>
                        ) : (
                          <button
                            onClick={() => freelancerAction(freelancer.id, 'activate', 'Admin action')}
                            className="btn-primary text-sm"
                          >
                            Activate
                          </button>
                        )}
                        <button
                          onClick={() => freelancerAction(freelancer.id, 'ban', 'Violation')}
                          className="bg-red-600 text-white px-3 py-1 rounded text-sm"
                        >
                          Ban
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* KYC Tab */}
        {activeTab === 'kyc' && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4">KYC Approval</h2>
            
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : pendingKYC.length === 0 ? (
              <div className="text-center py-8 text-gray-600">
                No pending KYC submissions
              </div>
            ) : (
              <div className="space-y-4">
                {pendingKYC.map(kyc => (
                  <div key={kyc.id} className="border rounded p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-bold">{kyc.freelancer_name}</h3>
                        <p className="text-sm text-gray-600">
                          Document: {kyc.document_type} - {kyc.document_number}
                        </p>
                        <p className="text-sm text-gray-600">
                          Bank: {kyc.bank_account_holder_name} ({kyc.bank_ifsc_code})
                        </p>
                        <p className="text-sm text-gray-600">
                          Submitted: {new Date(kyc.submitted_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => reviewKYC(kyc.id, true)}
                          className="btn-primary text-sm"
                        >
                          ✓ Approve
                        </button>
                        <button
                          onClick={() => {
                            const reason = prompt('Rejection reason:')
                            if (reason) reviewKYC(kyc.id, false, reason)
                          }}
                          className="bg-red-600 text-white px-3 py-1 rounded text-sm"
                        >
                          ✗ Reject
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Disputes Tab */}
        {activeTab === 'disputes' && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Dispute Resolution</h2>
            
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : disputes.length === 0 ? (
              <div className="text-center py-8 text-gray-600">
                No active disputes
              </div>
            ) : (
              <div className="space-y-4">
                {disputes.map(dispute => (
                  <div key={dispute.id} className="border rounded p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-bold">
                          {dispute.freelancer_name} vs {dispute.business_name}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Amount: ₹{(dispute.amount / 100).toFixed(2)}
                        </p>
                        <p className="text-sm text-gray-600">
                          Created: {new Date(dispute.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => resolveDispute(dispute.id, 'release', null, 'Approved by admin')}
                          className="btn-primary text-sm"
                        >
                          Release to Freelancer
                        </button>
                        <button
                          onClick={() => resolveDispute(dispute.id, 'refund', null, 'Refunded by admin')}
                          className="bg-red-600 text-white px-3 py-1 rounded text-sm"
                        >
                          Refund to Business
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Edit Business Modal */}
        {editingBusiness && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full">
              <h2 className="text-2xl font-bold mb-4">Edit Business</h2>
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  const formData = new FormData(e.target)
                  updateBusiness(editingBusiness.id, {
                    name: formData.get('name'),
                    category: formData.get('category'),
                    address: formData.get('address'),
                    phone: formData.get('phone')
                  })
                }}
              >
                <div className="space-y-4">
                  <input
                    name="name"
                    defaultValue={editingBusiness.name}
                    placeholder="Business Name"
                    className="input-field"
                    required
                  />
                  <input
                    name="category"
                    defaultValue={editingBusiness.category}
                    placeholder="Category"
                    className="input-field"
                  />
                  <input
                    name="address"
                    defaultValue={editingBusiness.address}
                    placeholder="Address"
                    className="input-field"
                  />
                  <input
                    name="phone"
                    defaultValue={editingBusiness.phone}
                    placeholder="Phone"
                    className="input-field"
                  />
                </div>
                <div className="flex gap-2 mt-6">
                  <button type="submit" className="btn-primary">
                    Save Changes
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingBusiness(null)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AdminPanelPage
