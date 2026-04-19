import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

function AdminDashboard() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const isFounder = user?.role === 'founder'

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Admin Dashboard</h1>
        <p className="text-gray-600 mb-8">Choose your admin workspace</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl">
          {/* Founder Dashboard - Only for founders */}
          {isFounder && (
            <div
              onClick={() => navigate('/founder/dashboard')}
              className="card hover:shadow-lg transition cursor-pointer border-2 border-transparent hover:border-purple-600"
            >
              <div className="text-center">
                <div className="text-6xl mb-4">🚀</div>
                <h2 className="text-2xl font-bold mb-3">Founder Dashboard</h2>
                <p className="text-gray-600 mb-4">
                  Business viability metrics, runway calculation, and critical alerts
                </p>
                <ul className="text-sm text-gray-600 text-left space-y-2">
                  <li>• Response rate & conversion metrics</li>
                  <li>• Revenue/day & runway calculation</li>
                  <li>• Cohort analysis by tier</li>
                  <li>• Geographic performance</li>
                  <li>• Critical threshold alerts</li>
                </ul>
                <button className="btn-primary mt-6 w-full bg-purple-600 hover:bg-purple-700">
                  View Founder Metrics →
                </button>
              </div>
            </div>
          )}

          {/* Analytics Dashboard */}
          <div
            onClick={() => navigate('/admin/analytics')}
            className="card hover:shadow-lg transition cursor-pointer border-2 border-transparent hover:border-primary-600"
          >
            <div className="text-center">
              <div className="text-6xl mb-4">📊</div>
              <h2 className="text-2xl font-bold mb-3">Analytics & Reports</h2>
              <p className="text-gray-600 mb-4">
                View platform metrics, revenue reports, conversion rates, and export data
              </p>
              <ul className="text-sm text-gray-600 text-left space-y-2">
                <li>• User and deal metrics</li>
                <li>• Revenue tracking</li>
                <li>• Conversion funnels</li>
                <li>• Category performance</li>
                <li>• CSV export</li>
              </ul>
              <button className="btn-primary mt-6 w-full">
                View Analytics →
              </button>
            </div>
          </div>

          {/* Management Panel */}
          <div
            onClick={() => navigate('/admin/panel')}
            className="card hover:shadow-lg transition cursor-pointer border-2 border-transparent hover:border-primary-600"
          >
            <div className="text-center">
              <div className="text-6xl mb-4">⚙️</div>
              <h2 className="text-2xl font-bold mb-3">Management Panel</h2>
              <p className="text-gray-600 mb-4">
                Manage users, approve KYC, resolve disputes, and moderate content
              </p>
              <ul className="text-sm text-gray-600 text-left space-y-2">
                <li>• Manage businesses</li>
                <li>• Monitor freelancers</li>
                <li>• Approve KYC submissions</li>
                <li>• Resolve disputes</li>
                <li>• Suspend/ban users</li>
              </ul>
              <button className="btn-primary mt-6 w-full">
                Open Panel →
              </button>
            </div>
          </div>

          {/* Failure Logs & Retry Management */}
          <div
            onClick={() => navigate('/admin/failures')}
            className="card hover:shadow-lg transition cursor-pointer border-2 border-transparent hover:border-orange-600"
          >
            <div className="text-center">
              <div className="text-6xl mb-4">🔧</div>
              <h2 className="text-2xl font-bold mb-3">Failure Logs</h2>
              <p className="text-gray-600 mb-4">
                Monitor failed operations and manage automatic retry system
              </p>
              <ul className="text-sm text-gray-600 text-left space-y-2">
                <li>• SMS/Email/Payment failures</li>
                <li>• Automatic retry monitoring</li>
                <li>• Manual retry & resolution</li>
                <li>• Failure statistics</li>
                <li>• Admin notifications</li>
              </ul>
              <button className="btn-primary mt-6 w-full bg-orange-600 hover:bg-orange-700">
                View Failures →
              </button>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-12 max-w-4xl">
          <h3 className="text-xl font-bold mb-4">Quick Access</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button
              onClick={() => navigate('/admin/panel?tab=businesses')}
              className="card hover:bg-gray-50 transition text-center"
            >
              <div className="text-3xl mb-2">🏢</div>
              <div className="text-sm font-medium">Businesses</div>
            </button>
            <button
              onClick={() => navigate('/admin/panel?tab=freelancers')}
              className="card hover:bg-gray-50 transition text-center"
            >
              <div className="text-3xl mb-2">👥</div>
              <div className="text-sm font-medium">Freelancers</div>
            </button>
            <button
              onClick={() => navigate('/admin/panel?tab=kyc')}
              className="card hover:bg-gray-50 transition text-center"
            >
              <div className="text-3xl mb-2">✓</div>
              <div className="text-sm font-medium">KYC Approval</div>
            </button>
            <button
              onClick={() => navigate('/admin/panel?tab=disputes')}
              className="card hover:bg-gray-50 transition text-center"
            >
              <div className="text-3xl mb-2">⚖️</div>
              <div className="text-sm font-medium">Disputes</div>
            </button>
            <button
              onClick={() => navigate('/admin/failures')}
              className="card hover:bg-gray-50 transition text-center"
            >
              <div className="text-3xl mb-2">🔧</div>
              <div className="text-sm font-medium">Failure Logs</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard
