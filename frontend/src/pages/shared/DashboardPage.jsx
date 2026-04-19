import { Link, Navigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

function DashboardPage() {
  const { user } = useAuthStore()

  // Redirect based on role
  if (user?.role === 'freelancer') {
    return <Navigate to="/freelancer-dashboard" replace />
  }
  
  if (user?.role === 'businessowner') {
    return <Navigate to="/business-dashboard" replace />
  }
  
  if (user?.role === 'admin' || user?.role === 'founder') {
    return <Navigate to="/admin/dashboard" replace />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-600 mb-8">
          Welcome back, {user?.email || 'User'}!
        </p>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {user?.role === 'freelancer' && (
            <>
              <Link to="/leads" className="card hover:shadow-lg transition-shadow">
                <div className="text-4xl mb-3">🎯</div>
                <h3 className="text-xl font-semibold mb-2">Browse Leads</h3>
                <p className="text-gray-600">
                  Discover local businesses without websites and claim leads
                </p>
              </Link>

              <Link to="/my-leads" className="card hover:shadow-lg transition-shadow">
                <div className="text-4xl mb-3">📋</div>
                <h3 className="text-xl font-semibold mb-2">My Leads</h3>
                <p className="text-gray-600">
                  View and manage your claimed leads and track progress
                </p>
              </Link>
            </>
          )}

          <Link to="/deals" className="card hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-3">💼</div>
            <h3 className="text-xl font-semibold mb-2">Deals</h3>
            <p className="text-gray-600">
              Manage your deals and track milestone progress
            </p>
          </Link>

          <Link to="/analytics" className="card hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-3">📊</div>
            <h3 className="text-xl font-semibold mb-2">Analytics</h3>
            <p className="text-gray-600">
              View your performance metrics and ROI
            </p>
          </Link>

          <Link to="/profile" className="card hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-3">👤</div>
            <h3 className="text-xl font-semibold mb-2">Profile</h3>
            <p className="text-gray-600">
              Manage your account settings and preferences
            </p>
          </Link>
        </div>

        {/* Getting Started Guide for Freelancers */}
        {user?.role === 'freelancer' && (
          <div className="card bg-primary-50 border-primary-200">
            <h2 className="text-xl font-bold mb-4">🚀 Getting Started</h2>
            <ol className="space-y-3 text-gray-700">
              <li className="flex items-start">
                <span className="font-semibold mr-2">1.</span>
                <span>
                  <Link to="/leads" className="text-primary-600 hover:underline">
                    Browse available leads
                  </Link>{' '}
                  and find businesses without websites
                </span>
              </li>
              <li className="flex items-start">
                <span className="font-semibold mr-2">2.</span>
                <span>Claim a lead to get 6-hour exclusivity</span>
              </li>
              <li className="flex items-start">
                <span className="font-semibold mr-2">3.</span>
                <span>Generate a demo website to showcase value</span>
              </li>
              <li className="flex items-start">
                <span className="font-semibold mr-2">4.</span>
                <span>Send WhatsApp/SMS messages with the demo link</span>
              </li>
              <li className="flex items-start">
                <span className="font-semibold mr-2">5.</span>
                <span>Create a deal and get paid through milestone-based payments</span>
              </li>
            </ol>
          </div>
        )}

        {/* Stats Placeholder */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="card text-center">
            <div className="text-3xl font-bold text-primary-600 mb-1">-</div>
            <div className="text-gray-600">Active Leads</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-primary-600 mb-1">-</div>
            <div className="text-gray-600">Deals Closed</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-primary-600 mb-1">₹0</div>
            <div className="text-gray-600">Total Earnings</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
