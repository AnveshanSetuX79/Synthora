import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Navbar from './components/Navbar'

// Loading component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>
)

// Eager load critical pages (public routes)
import HomePage from './pages/public/HomePage'
import LoginPage from './pages/public/LoginPage'
import RegisterPage from './pages/public/RegisterPage'

// Lazy load all other pages
const FAQPage = lazy(() => import('./pages/public/FAQPage'))
const DashboardPage = lazy(() => import('./pages/shared/DashboardPage'))
const DealsPage = lazy(() => import('./pages/shared/DealsPage'))
const DealDetailPage = lazy(() => import('./pages/shared/DealDetailPage'))
const CreateDealPage = lazy(() => import('./pages/shared/CreateDealPage'))
const PaymentPage = lazy(() => import('./pages/shared/PaymentPage'))
const ProfilePage = lazy(() => import('./pages/shared/ProfilePage'))
const MessagesPage = lazy(() => import('./pages/shared/MessagesPage'))
const NotificationsPage = lazy(() => import('./pages/shared/NotificationsPage'))
const FreelancerDashboard = lazy(() => import('./pages/freelancer/FreelancerDashboard'))
const LeadsPage = lazy(() => import('./pages/freelancer/LeadsPage'))
const LeadDetailPage = lazy(() => import('./pages/freelancer/LeadDetailPage'))
const MyLeadsPage = lazy(() => import('./pages/freelancer/MyLeadsPage'))
const DiscoverLeadsPage = lazy(() => import('./pages/freelancer/DiscoverLeadsPage'))
const OutreachPage = lazy(() => import('./pages/freelancer/OutreachPage'))
const AnalyticsPage = lazy(() => import('./pages/freelancer/AnalyticsPage'))
const KYCPage = lazy(() => import('./pages/freelancer/KYCPage'))
const OnboardingPage = lazy(() => import('./pages/freelancer/OnboardingPage'))
const BusinessOwnerDashboard = lazy(() => import('./pages/business-owner/BusinessOwnerDashboard'))
const BusinessOwnerOnboarding = lazy(() => import('./pages/business-owner/BusinessOwnerOnboarding'))
const BusinessOwnerDealDetailPage = lazy(() => import('./pages/business-owner/BusinessOwnerDealDetailPage'))
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'))
const AdminAnalyticsPage = lazy(() => import('./pages/admin/AdminAnalyticsPage'))
const AdminPanelPage = lazy(() => import('./pages/admin/AdminPanelPage'))
const FailureLogsPage = lazy(() => import('./pages/admin/FailureLogsPage'))
const FounderDashboard = lazy(() => import('./pages/admin/FounderDashboard'))
const AdminDisputesPage = lazy(() => import('./pages/admin/AdminDisputesPage'))
const DisputeList = lazy(() => import('./components/DisputeList'))

// Protected Route Component// Analytics wrapper to redirect based on role
function AnalyticsPageWrapper() {
  const { user } = useAuthStore()
  
  if (user?.role === 'admin' || user?.role === 'founder') {
    return <Navigate to="/admin/analytics" replace />
  }
  
  return <AnalyticsPage />
}

// Protected Route Component
function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}

function App() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
        {/* Public Routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/faq" element={<FAQPage />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leads"
          element={
            <ProtectedRoute allowedRoles={['freelancer', 'admin', 'founder']}>
              <LeadsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leads/discover"
          element={
            <ProtectedRoute allowedRoles={['freelancer', 'admin', 'founder']}>
              <DiscoverLeadsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leads/:leadId"
          element={
            <ProtectedRoute allowedRoles={['freelancer', 'admin', 'founder']}>
              <LeadDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/my-leads"
          element={
            <ProtectedRoute allowedRoles={['freelancer']}>
              <MyLeadsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/outreach/:leadId"
          element={
            <ProtectedRoute allowedRoles={['freelancer']}>
              <OutreachPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/messages/:freelancerId"
          element={
            <ProtectedRoute>
              <MessagesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/deals"
          element={
            <ProtectedRoute>
              <DealsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/deals/:dealId"
          element={
            <ProtectedRoute>
              <DealDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/deals/create/:businessId"
          element={
            <ProtectedRoute allowedRoles={['freelancer']}>
              <CreateDealPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/payment/:dealId"
          element={
            <ProtectedRoute>
              <PaymentPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AnalyticsPageWrapper />
            </ProtectedRoute>
          }
        />
        <Route
          path="/kyc"
          element={
            <ProtectedRoute allowedRoles={['freelancer']}>
              <KYCPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <NotificationsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/onboarding"
          element={
            <ProtectedRoute allowedRoles={['freelancer']}>
              <OnboardingPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/freelancer-dashboard"
          element={
            <ProtectedRoute allowedRoles={['freelancer']}>
              <FreelancerDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/business-dashboard"
          element={
            <ProtectedRoute allowedRoles={['businessowner']}>
              <BusinessOwnerDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/business-onboarding"
          element={
            <ProtectedRoute allowedRoles={['businessowner']}>
              <BusinessOwnerOnboarding />
            </ProtectedRoute>
          }
        />
        <Route
          path="/business-deals/:dealId"
          element={
            <ProtectedRoute allowedRoles={['businessowner']}>
              <BusinessOwnerDealDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/analytics"
          element={
            <ProtectedRoute allowedRoles={['admin', 'founder']}>
              <AdminAnalyticsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/panel"
          element={
            <ProtectedRoute allowedRoles={['admin', 'founder']}>
              <AdminPanelPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/failures"
          element={
            <ProtectedRoute allowedRoles={['admin', 'founder']}>
              <FailureLogsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={['admin', 'founder']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/founder/dashboard"
          element={
            <ProtectedRoute allowedRoles={['founder']}>
              <FounderDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/disputes"
          element={
            <ProtectedRoute allowedRoles={['admin', 'founder']}>
              <AdminDisputesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/disputes"
          element={
            <ProtectedRoute>
              <div className="max-w-7xl mx-auto px-4 py-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">My Disputes</h1>
                <DisputeList />
              </div>
            </ProtectedRoute>
          }
        />

        {/* 404 Route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      </Suspense>
    </div>
  )
}

export default App
