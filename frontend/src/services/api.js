import axios from 'axios'
import { useAuthStore } from '../store/authStore'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000, // Increased to 30 seconds temporarily for development
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      // Handle specific error codes
      if (error.response.status === 401) {
        // Unauthorized - clear auth and redirect to login
        useAuthStore.getState().logout()
        window.location.href = '/login'
      } else if (error.response.status === 403) {
        // Forbidden
        console.error('Access forbidden:', error.response.data)
      } else if (error.response.status === 404) {
        // Not found
        console.error('Resource not found:', error.response.data)
      } else if (error.response.status >= 500) {
        // Server error
        console.error('Server error:', error.response.data)
      }
    } else if (error.request) {
      // Network error
      console.error('Network error:', error.message)
    }
    
    return Promise.reject(error)
  }
)

// API service functions
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  verifyOTP: (data) => api.post('/api/auth/verify-otp', data),
  login: (data) => api.post('/api/auth/login', data),
  refreshToken: (refreshToken) => api.post('/api/auth/refresh', { refreshToken }),
}

export const leadsAPI = {
  discoverLeads: (data) => api.post('/api/leads/discover', data, { timeout: 120000 }), // 2 minute timeout for discovery
  discover: (data) => api.post('/api/leads/discover', data, { timeout: 120000 }), // Alias for backward compatibility
  getLeads: (params) => api.get('/api/leads', { params }),
  getLeadDetails: (leadId) => api.get(`/api/leads/${leadId}`),
  claimLead: (leadId) => api.post(`/api/leads/${leadId}/claim`),
  getAvailableLeads: (params) => api.get('/api/leads/available', { params }),
  getMyLeads: (params) => api.get('/api/leads/my-leads', { params }),
}

export const dealsAPI = {
  createDeal: (data) => api.post('/api/deals', data),
  getDealDetails: (dealId) => api.get(`/api/deals/${dealId}`),
  updateDealStatus: (dealId, data) => api.put(`/api/deals/${dealId}/status`, data),
  getMyDeals: (params) => api.get('/api/deals/my-deals', { params }),
  updateMilestone: (dealId, milestoneId, data) => 
    api.put(`/api/deals/${dealId}/milestones/${milestoneId}`, data),
}

export const outreachAPI = {
  sendMessage: (data) => api.post('/api/outreach/send', data),
  getMessageHistory: (leadContactId) => api.get(`/api/outreach/history/${leadContactId}`),
  handleOptOut: (data) => api.post('/api/outreach/opt-out', data),
  getStats: (params) => api.get('/api/outreach/stats', { params }),
}

export const paymentsAPI = {
  createOrder: (data) => api.post('/api/payments/create-order', data),
  verifyPayment: (data) => api.post('/api/payments/verify', data),
  getPaymentStatus: (dealId) => api.get(`/api/payments/${dealId}`),
  processRefund: (data) => api.post('/api/payments/refund', data),
}

export const demosAPI = {
  generateDemo: (data) => api.post('/api/demos/generate', data),
  getDemo: (businessId) => api.get(`/api/demos/${businessId}`),
  getDemoAnalytics: (businessId) => api.get(`/api/demos/${businessId}/analytics`),
  getPublicDemoUrl: (demoId) => {
    const baseURL = api.defaults.baseURL || 'http://localhost:8000'
    return `${baseURL}/api/demos/public/${demoId}`
  },
}

export const analyticsAPI = {
  trackEvent: (data) => api.post('/api/analytics/track', data),
  getConversionFunnel: (params) => api.get('/api/analytics/funnel', { params, timeout: 30000 }), // 30 second timeout
  getFreelancerROI: (params) => api.get('/api/analytics/freelancer-roi', { params, timeout: 30000 }), // 30 second timeout
  getEventHistory: (params) => api.get('/api/analytics/events', { params }),
  getCategoryInsights: (category) => api.get(`/api/analytics/category-insights/${category}`),
  getAdminDashboard: () => api.get('/api/analytics/admin/dashboard', { timeout: 30000 }), // 30 second timeout for admin
  getFounderDashboard: (days) => api.get('/api/analytics/founder/dashboard', { params: { days }, timeout: 30000 }),
}

export const kycAPI = {
  submitKYC: (data) => api.post('/api/payments/kyc/submit', data),
  getKYCStatus: () => api.get('/api/payments/kyc/status'),
}

export const payoutAPI = {
  processPayout: (data) => api.post('/api/payments/payout', data),
  checkEligibility: () => api.get('/api/payments/payout/eligibility'),
  createLinkedAccount: () => api.post('/api/payments/linked-account/create'),
}

export const followUpAPI = {
  scheduleFollowUps: () => api.post('/api/outreach/schedule-followups'),
  getLeadsNeedingFollowUp: () => api.get('/api/outreach/leads-needing-followup'),
}

export const disputesAPI = {
  createDispute: (data) => api.post('/api/disputes', data),
  getDispute: (disputeId) => api.get(`/api/disputes/${disputeId}`),
  listDisputes: (params) => api.get('/api/disputes', { params }),
  addMessage: (disputeId, data) => api.post(`/api/disputes/${disputeId}/messages`, data),
  escalate: (disputeId) => api.post(`/api/disputes/${disputeId}/escalate`),
  resolve: (disputeId, data) => api.post(`/api/disputes/${disputeId}/resolve`, data),
  close: (disputeId) => api.post(`/api/disputes/${disputeId}/close`),
}

export const reviewsAPI = {
  createReview: (data) => api.post('/api/reviews', data),
  getFreelancerReviews: (freelancerId, params) => api.get(`/api/reviews/freelancer/${freelancerId}`, { params }),
  respondToReview: (reviewId, data) => api.post(`/api/reviews/${reviewId}/respond`, data),
  checkEligibility: (dealId) => api.get(`/api/reviews/deal/${dealId}/eligibility`),
  getPendingReviews: () => api.get('/api/reviews/pending'),
}

export default api
