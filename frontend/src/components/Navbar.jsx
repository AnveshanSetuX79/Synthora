import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { useState } from 'react'
import NotificationBell from './NotificationBell'

function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/')
  }

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false)
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center" onClick={closeMobileMenu}>
            <span className="text-xl font-bold text-primary-600">LocalAI Leads</span>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            <Link
              to="/dashboard"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/dashboard')
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Dashboard
            </Link>

            {/* Freelancer-only links */}
            {user?.role === 'freelancer' && (
              <>
                <Link
                  to="/leads"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/leads')
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Browse Leads
                </Link>
                <Link
                  to="/my-leads"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/my-leads')
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  My Leads
                </Link>
              </>
            )}

            <Link
              to="/deals"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/deals')
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Deals
            </Link>

            <Link
              to="/analytics"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/analytics')
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Analytics
            </Link>

            {/* Admin-only links */}
            {(user?.role === 'admin' || user?.role === 'founder') && (
              <>
                <Link
                  to="/admin/dashboard"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/admin/dashboard')
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Admin
                </Link>
                {user?.role === 'founder' && (
                  <Link
                    to="/founder/dashboard"
                    className={`px-3 py-2 rounded-md text-sm font-medium ${
                      isActive('/founder/dashboard')
                        ? 'bg-purple-100 text-purple-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    🚀 Founder
                  </Link>
                )}
              </>
            )}
          </div>

          {/* User Menu - Desktop */}
          <div className="hidden md:flex items-center space-x-4">
            <NotificationBell />
            <span className="text-sm text-gray-700">
              {user?.email}
            </span>
            <Link
              to="/profile"
              className="text-sm text-gray-700 hover:text-primary-600"
            >
              Profile
            </Link>
            <button
              onClick={handleLogout}
              className="btn-secondary text-sm"
            >
              Logout
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-md text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? (
              // Close icon
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              // Hamburger icon
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {/* Mobile Navigation - Collapsible */}
        <div className={`md:hidden overflow-hidden transition-all duration-300 ease-in-out ${
          isMobileMenuOpen ? 'max-h-screen pb-3' : 'max-h-0'
        }`}>
          <div className="space-y-1 pt-2">
          <Link
            to="/dashboard"
            onClick={closeMobileMenu}
            className={`block px-3 py-2 rounded-md text-sm font-medium ${
              isActive('/dashboard')
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            Dashboard
          </Link>

          {user?.role === 'freelancer' && (
            <>
              <Link
                to="/leads"
                onClick={closeMobileMenu}
                className={`block px-3 py-2 rounded-md text-sm font-medium ${
                  isActive('/leads')
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Browse Leads
              </Link>
              <Link
                to="/my-leads"
                onClick={closeMobileMenu}
                className={`block px-3 py-2 rounded-md text-sm font-medium ${
                  isActive('/my-leads')
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                My Leads
              </Link>
            </>
          )}

          <Link
            to="/deals"
            onClick={closeMobileMenu}
            className={`block px-3 py-2 rounded-md text-sm font-medium ${
              isActive('/deals')
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            Deals
          </Link>

          <Link
            to="/analytics"
            onClick={closeMobileMenu}
            className={`block px-3 py-2 rounded-md text-sm font-medium ${
              isActive('/analytics')
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            Analytics
          </Link>

          {(user?.role === 'admin' || user?.role === 'founder') && (
            <>
              <Link
                to="/admin/dashboard"
                onClick={closeMobileMenu}
                className={`block px-3 py-2 rounded-md text-sm font-medium ${
                  isActive('/admin/dashboard')
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Admin Dashboard
              </Link>
              {user?.role === 'founder' && (
                <Link
                  to="/founder/dashboard"
                  onClick={closeMobileMenu}
                  className={`block px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/founder/dashboard')
                      ? 'bg-purple-100 text-purple-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  🚀 Founder Dashboard
                </Link>
              )}
            </>
          )}

          {/* Mobile User Menu */}
          <div className="border-t border-gray-200 mt-2 pt-2">
            <div className="px-3 py-2 text-sm text-gray-600">
              {user?.email}
            </div>
            <Link
              to="/profile"
              onClick={closeMobileMenu}
              className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              Profile
            </Link>
            <button
              onClick={() => {
                closeMobileMenu()
                handleLogout()
              }}
              className="w-full text-left px-3 py-2 rounded-md text-sm font-medium text-red-600 hover:bg-red-50"
            >
              Logout
            </button>
          </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
