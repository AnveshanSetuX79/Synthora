import { Link } from 'react-router-dom'
import TrustBadges from '../../components/TrustBadges'

function HomePage() {
  const testimonials = [
    {
      name: 'Rajesh Kumar',
      business: 'Kumar Restaurant, Mumbai',
      rating: 5,
      text: 'Got a beautiful website in just 7 days. The demo was so good, I approved immediately. Highly recommended!'
    },
    {
      name: 'Priya Sharma',
      business: 'Sharma Coaching Classes, Delhi',
      rating: 5,
      text: 'No payment until I approved the work - that gave me confidence. The freelancer was professional and delivered on time.'
    },
    {
      name: 'Amit Patel',
      business: 'Patel Electronics, Ahmedabad',
      rating: 5,
      text: 'The free demo website helped me see exactly what I was getting. Milestone payments made it risk-free.'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            LocalAI Leads
          </h1>
          <p className="text-xl text-gray-700 mb-4 max-w-2xl mx-auto">
            Connect freelance web developers with local businesses lacking digital presence.
          </p>
          
          {/* Trust Headlines */}
          <div className="mb-8 space-y-2">
            <p className="text-2xl font-semibold text-blue-600">
              ✨ We create free demo websites for your business
            </p>
            <p className="text-xl text-green-600 font-medium">
              💰 No payment until you approve the work
            </p>
          </div>

          <div className="flex gap-4 justify-center">
            <Link to="/register" className="btn-primary text-lg px-8 py-3">
              Get Started Free
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-3">
              Login
            </Link>
          </div>
        </div>

        {/* How It Works */}
        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <div className="card text-center">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold mb-2">Discover Leads</h3>
            <p className="text-gray-600">
              Find local businesses without websites using AI-powered lead scoring
            </p>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-4">🚀</div>
            <h3 className="text-xl font-semibold mb-2">Generate Free Demos</h3>
            <p className="text-gray-600">
              Create instant demo websites to showcase value - completely free for businesses
            </p>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-4">💰</div>
            <h3 className="text-xl font-semibold mb-2">Close Deals Safely</h3>
            <p className="text-gray-600">
              Milestone-based payments with escrow protection - pay only when you approve
            </p>
          </div>
        </div>
      </div>

      {/* Trust Badges */}
      <div className="bg-white py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Why Businesses Trust Us
          </h2>
          <TrustBadges />
        </div>
      </div>

      {/* Testimonials */}
      <div className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            What Our Clients Say
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex gap-1 mb-3">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <span key={i} className="text-yellow-400 text-xl">★</span>
                  ))}
                </div>
                <p className="text-gray-700 mb-4 italic">"{testimonial.text}"</p>
                <div className="border-t pt-4">
                  <p className="font-semibold text-gray-900">{testimonial.name}</p>
                  <p className="text-sm text-gray-600">{testimonial.business}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Example Demos */}
      <div className="bg-white py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">
            See Example Demo Websites
          </h2>
          <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
            These are real demo websites created by our freelancers. Businesses can view, share, and approve before making any payment.
          </p>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
              <div className="bg-gradient-to-r from-orange-400 to-red-500 h-32"></div>
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-2">Restaurant Demo</h3>
                <p className="text-gray-600 mb-4">
                  Full-featured restaurant website with menu, gallery, and online ordering
                </p>
                <span className="text-sm text-blue-600 font-medium">View Sample →</span>
              </div>
            </div>
            <div className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
              <div className="bg-gradient-to-r from-blue-400 to-purple-500 h-32"></div>
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-2">School/Coaching Demo</h3>
                <p className="text-gray-600 mb-4">
                  Professional education website with courses, faculty, and admissions
                </p>
                <span className="text-sm text-blue-600 font-medium">View Sample →</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* FAQ Link */}
      <div className="bg-blue-600 py-12">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Have Questions?
          </h2>
          <p className="text-blue-100 mb-6 text-lg">
            Check out our comprehensive FAQ section
          </p>
          <Link
            to="/faq"
            className="inline-block px-8 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
          >
            View FAQ
          </Link>
        </div>
      </div>
    </div>
  )
}

export default HomePage
