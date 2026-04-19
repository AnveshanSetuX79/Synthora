import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import api from '../../services/api'

function BusinessOwnerOnboarding() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [demoUrl, setDemoUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const user = useAuthStore((state) => state.user)

  // Try to fetch demo if business exists
  useEffect(() => {
    const fetchDemo = async () => {
      if (user?.business_id) {
        try {
          const response = await api.get(`/demos/${user.business_id}`)
          if (response.data.demo_id) {
            const publicUrl = `${api.defaults.baseURL}/api/demos/public/${response.data.demo_id}`
            setDemoUrl(publicUrl)
          }
        } catch (err) {
          // No demo yet, that's okay
          console.log('No demo found yet')
        }
      }
    }
    fetchDemo()
  }, [user])

  const handleComplete = () => {
    // Mark onboarding as complete in localStorage
    localStorage.setItem('businessOwnerOnboardingComplete', 'true')
    navigate('/business-dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Step {step} of 4</span>
              <button
                type="button"
                onClick={handleComplete}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Skip Tutorial
              </button>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(step / 4) * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Step 1: Welcome */}
          {step === 1 && (
            <div className="card text-center">
              <div className="text-6xl mb-6">👋</div>
              <h1 className="text-4xl font-bold mb-4">Welcome to LocalAI Leads!</h1>
              <p className="text-xl text-gray-600 mb-8">
                We're excited to help you find the perfect freelancer to build your digital presence
              </p>
              <div className="grid md:grid-cols-3 gap-6 mb-8">
                <div className="p-6 bg-blue-50 rounded-lg">
                  <div className="text-3xl mb-3">🎯</div>
                  <h3 className="font-semibold mb-2">Quality Freelancers</h3>
                  <p className="text-sm text-gray-600">
                    Connect with verified web developers who specialize in local businesses
                  </p>
                </div>
                <div className="p-6 bg-green-50 rounded-lg">
                  <div className="text-3xl mb-3">💼</div>
                  <h3 className="font-semibold mb-2">Easy Management</h3>
                  <p className="text-sm text-gray-600">
                    Track projects, approve milestones, and communicate all in one place
                  </p>
                </div>
                <div className="p-6 bg-purple-50 rounded-lg">
                  <div className="text-3xl mb-3">🚀</div>
                  <h3 className="font-semibold mb-2">Fast Results</h3>
                  <p className="text-sm text-gray-600">
                    Get your website up and running quickly with our streamlined process
                  </p>
                </div>
              </div>
              <button onClick={() => setStep(2)} className="btn-primary text-lg px-8">
                Get Started →
              </button>
            </div>
          )}

          {/* Step 2: Demo Website Showcase */}
          {step === 2 && (
            <div className="card">
              <h2 className="text-3xl font-bold mb-6 text-center">Your Demo Website</h2>
              
              {demoUrl ? (
                <div className="mb-8">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="text-3xl">✨</div>
                      <h3 className="text-xl font-semibold text-green-900">
                        Great News! A freelancer created a demo for you
                      </h3>
                    </div>
                    <p className="text-green-800 mb-4">
                      Check out this professional website preview created specifically for your business. This is what your website could look like!
                    </p>
                    <a
                      href={demoUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                    >
                      View Your Demo Website →
                    </a>
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h4 className="font-semibold text-blue-900 mb-3">What's included in the demo:</h4>
                    <ul className="space-y-2 text-blue-800">
                      <li>✓ Your business information and contact details</li>
                      <li>✓ Professional design and layout</li>
                      <li>✓ Mobile-responsive (works on all devices)</li>
                      <li>✓ SEO-optimized for Google search</li>
                      <li>✓ Ready to share with customers</li>
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="mb-8">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="text-3xl">🎨</div>
                      <h3 className="text-xl font-semibold text-blue-900">
                        Demo Websites - Free Preview
                      </h3>
                    </div>
                    <p className="text-blue-800 mb-4">
                      Freelancers will create professional demo websites for your business at no cost. You can review them before making any commitment!
                    </p>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6 mb-6">
                    <div className="border border-gray-200 rounded-lg overflow-hidden">
                      <div className="bg-gradient-to-r from-orange-400 to-red-500 h-32 flex items-center justify-center text-white text-2xl font-bold">
                        Restaurant Demo
                      </div>
                      <div className="p-4">
                        <p className="text-sm text-gray-600">
                          Full menu, gallery, online ordering, contact form
                        </p>
                      </div>
                    </div>
                    <div className="border border-gray-200 rounded-lg overflow-hidden">
                      <div className="bg-gradient-to-r from-blue-400 to-purple-500 h-32 flex items-center justify-center text-white text-2xl font-bold">
                        Service Demo
                      </div>
                      <div className="p-4">
                        <p className="text-sm text-gray-600">
                          Services, pricing, testimonials, booking system
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-yellow-800 text-sm">
                      💡 <strong>No payment required:</strong> Review demos from multiple freelancers before choosing one. You only pay when you approve the work!
                    </p>
                  </div>
                </div>
              )}

              <div className="flex gap-4 justify-center">
                <button onClick={() => setStep(1)} className="btn-secondary">
                  ← Back
                </button>
                <button onClick={() => setStep(3)} className="btn-primary">
                  Continue →
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Platform Explanation */}
          {step === 3 && (
            <div className="card">
              <h2 className="text-3xl font-bold mb-6 text-center">How to Choose the Right Freelancer</h2>
              
              <div className="space-y-6 mb-8">
                {/* Compare Freelancers */}
                <div className="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-6">
                  <div className="flex items-start gap-4">
                    <div className="text-4xl">👥</div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-3">
                        Compare Freelancers
                      </h3>
                      <div className="space-y-3">
                        <div className="bg-white rounded-lg p-4">
                          <p className="font-medium text-gray-900 mb-2">Check Their Tier Level:</p>
                          <div className="flex gap-2 text-sm">
                            <span className="px-3 py-1 bg-gray-100 rounded">🆕 New (3 leads/day)</span>
                            <span className="px-3 py-1 bg-blue-100 rounded">✓ Verified (10 leads/day)</span>
                            <span className="px-3 py-1 bg-yellow-100 rounded">⭐ Top Rated (20 leads/day)</span>
                          </div>
                        </div>
                        <div className="bg-white rounded-lg p-4">
                          <p className="font-medium text-gray-900 mb-2">Review Their Profile:</p>
                          <ul className="text-sm text-gray-600 space-y-1">
                            <li>• Portfolio and past work</li>
                            <li>• Average rating and reviews</li>
                            <li>• Skills and experience level</li>
                            <li>• Response time and professionalism</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Milestone-Based Payment */}
                <div className="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-6">
                  <div className="flex items-start gap-4">
                    <div className="text-4xl">💰</div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-3">
                        Milestone-Based Payment (Safe & Secure)
                      </h3>
                      <div className="bg-white rounded-lg p-4 mb-3">
                        <p className="font-medium text-gray-900 mb-3">How it works:</p>
                        <div className="space-y-3">
                          <div className="flex items-start gap-3">
                            <div className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                            <div>
                              <p className="font-medium text-gray-900">Pay 50% Advance</p>
                              <p className="text-sm text-gray-600">Money held in escrow (not released yet)</p>
                            </div>
                          </div>
                          <div className="flex items-start gap-3">
                            <div className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                            <div>
                              <p className="font-medium text-gray-900">Freelancer Works</p>
                              <p className="text-sm text-gray-600">Track progress, communicate, request changes</p>
                            </div>
                          </div>
                          <div className="flex items-start gap-3">
                            <div className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                            <div>
                              <p className="font-medium text-gray-900">Approve & Pay 50%</p>
                              <p className="text-sm text-gray-600">Only when you're 100% satisfied</p>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="bg-green-600 text-white rounded-lg p-3 text-sm">
                        🛡️ <strong>Your money is protected:</strong> Funds are held in escrow. You approve each milestone before payment is released.
                      </div>
                    </div>
                  </div>
                </div>

                {/* Communication */}
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-6">
                  <div className="flex items-start gap-4">
                    <div className="text-4xl">💬</div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-3">
                        Stay in Touch
                      </h3>
                      <p className="text-gray-700 mb-3">
                        Use our built-in chat to discuss requirements, ask questions, and provide feedback. All communication is tracked for your protection.
                      </p>
                      <div className="bg-white rounded-lg p-3 text-sm text-gray-600">
                        <strong>Pro tip:</strong> Be clear about your requirements upfront. Share examples of websites you like and specific features you need.
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-4 justify-center">
                <button onClick={() => setStep(2)} className="btn-secondary">
                  ← Back
                </button>
                <button onClick={() => setStep(4)} className="btn-primary">
                  Continue →
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Dashboard Tour */}
          {step === 4 && (
            <div className="card">
              <h2 className="text-3xl font-bold mb-6 text-center">How It Works</h2>
              <div className="space-y-6 mb-8">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                    1
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Review Demo Websites</h3>
                    <p className="text-gray-600">
                      Freelancers create custom demo websites for your business. Review them on your dashboard
                      to see what your website could look like.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                    2
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Compare Freelancers</h3>
                    <p className="text-gray-600">
                      See all freelancers who contacted you, their experience levels, portfolios, and ratings.
                      Chat with them to discuss your needs.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                    3
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Create a Deal</h3>
                    <p className="text-gray-600">
                      Choose your freelancer and create a deal. Set milestones, agree on pricing, and track
                      progress as your website is built.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                    4
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Launch Your Website</h3>
                    <p className="text-gray-600">
                      Approve completed milestones, make payments securely through our platform, and launch
                      your new website to the world!
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex gap-4 justify-center">
                <button onClick={() => setStep(1)} className="btn-secondary">
                  ← Back
                </button>
                <button onClick={() => setStep(3)} className="btn-primary">
                  Continue →
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Dashboard Tour */}
          {step === 4 && (
            <div className="card">
              <h2 className="text-3xl font-bold mb-6 text-center">Your Dashboard</h2>
              <div className="mb-8">
                <div className="bg-gray-100 rounded-lg p-6 mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="text-3xl">📊</div>
                    <h3 className="text-xl font-semibold">Business Overview</h3>
                  </div>
                  <p className="text-gray-600">
                    See your business information, demo website, and key stats at a glance. Track active
                    deals, messages, and freelancer contacts.
                  </p>
                </div>

                <div className="bg-gradient-to-r from-orange-50 to-orange-100 border-2 border-orange-300 rounded-lg p-6 mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="text-3xl">🔔</div>
                    <h3 className="text-xl font-semibold text-orange-900">Pending Contact Requests</h3>
                  </div>
                  <p className="text-orange-800 mb-3">
                    <strong>Important:</strong> When freelancers contact you, they'll appear in your "Freelancer Contacts" section. You'll see:
                  </p>
                  <ul className="text-orange-800 space-y-2">
                    <li>• Who contacted you and when</li>
                    <li>• Their demo website (if they created one)</li>
                    <li>• Their profile, ratings, and experience</li>
                    <li>• Option to chat and create a deal</li>
                  </ul>
                </div>

                <div className="bg-gray-100 rounded-lg p-6 mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="text-3xl">💬</div>
                    <h3 className="text-xl font-semibold">Communication</h3>
                  </div>
                  <p className="text-gray-600">
                    Chat directly with freelancers to discuss your project requirements, ask questions, and
                    negotiate terms before creating a deal.
                  </p>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">💡</div>
                    <div>
                      <h3 className="font-semibold text-green-900 mb-2">Pro Tip</h3>
                      <p className="text-sm text-green-800">
                        Take your time to review multiple freelancers and their demos. Ask questions about
                        their process, timeline, and what's included. The right freelancer will be happy to
                        answer all your questions!
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-4 justify-center">
                <button onClick={() => setStep(3)} className="btn-secondary">
                  ← Back
                </button>
                <button onClick={handleComplete} className="btn-primary text-lg px-8">
                  Go to Dashboard 🚀
                </button>
              </div>
            </div>
          )}
            <div className="card">
              <h2 className="text-3xl font-bold mb-6 text-center">Your Dashboard</h2>
              <div className="mb-8">
                <div className="bg-gray-100 rounded-lg p-6 mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="text-3xl">📊</div>
                    <h3 className="text-xl font-semibold">Business Overview</h3>
                  </div>
                  <p className="text-gray-600">
                    See your business information, demo website, and key stats at a glance. Track active
                    deals, messages, and freelancer contacts.
                  </p>
                </div>

                <div className="bg-gray-100 rounded-lg p-6 mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="text-3xl">👥</div>
                    <h3 className="text-xl font-semibold">Freelancer List</h3>
                  </div>
                  <p className="text-gray-600">
                    View all freelancers who have contacted you. See their tier level (New, Verified, or Top
                    Rated), check if they sent you a demo, and access their portfolios.
                  </p>
                </div>

                <div className="bg-gray-100 rounded-lg p-6 mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="text-3xl">💬</div>
                    <h3 className="text-xl font-semibold">Communication</h3>
                  </div>
                  <p className="text-gray-600">
                    Chat directly with freelancers to discuss your project requirements, ask questions, and
                    negotiate terms before creating a deal.
                  </p>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">💡</div>
                    <div>
                      <h3 className="font-semibold text-green-900 mb-2">Pro Tip</h3>
                      <p className="text-sm text-green-800">
                        Take your time to review multiple freelancers and their demos. Ask questions about
                        their process, timeline, and what's included. The right freelancer will be happy to
                        answer all your questions!
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-4 justify-center">
                <button onClick={() => setStep(2)} className="btn-secondary">
                  ← Back
                </button>
                <button onClick={handleComplete} className="btn-primary text-lg px-8">
                  Go to Dashboard 🚀
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default BusinessOwnerOnboarding
