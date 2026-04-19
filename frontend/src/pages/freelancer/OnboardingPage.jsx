import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const OnboardingPage = () => {
  const [step, setStep] = useState(1);
  const [profile, setProfile] = useState({
    portfolio: '',
    skills: [],
    experience: ''
  });
  const [city, setCity] = useState('');
  const [category, setCategory] = useState('');
  const [showTutorial, setShowTutorial] = useState(false);
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);

  const cities = ['Pune', 'Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad'];
  const categories = [
    { value: 'restaurant', label: 'Restaurants' },
    { value: 'school', label: 'Schools & Coaching' },
    { value: 'salon', label: 'Salons & Spas' },
    { value: 'gym', label: 'Gyms & Fitness' },
    { value: 'clinic', label: 'Clinics & Healthcare' },
    { value: 'retail', label: 'Retail Stores' }
  ];

  const skillOptions = [
    'HTML/CSS', 'JavaScript', 'React', 'WordPress', 
    'SEO', 'UI/UX Design', 'Mobile Responsive', 'E-commerce'
  ];

  const handleNext = () => {
    if (step < 5) {
      setStep(step + 1);
    } else {
      // Save preferences and complete onboarding
      localStorage.setItem('onboarding_completed', 'true');
      localStorage.setItem('preferred_city', city);
      localStorage.setItem('preferred_category', category);
      localStorage.setItem('profile_data', JSON.stringify(profile));
      navigate('/dashboard');
    }
  };

  const handleSkip = () => {
    localStorage.setItem('onboarding_completed', 'true');
    navigate('/dashboard');
  };

  const toggleSkill = (skill) => {
    setProfile(prev => ({
      ...prev,
      skills: prev.skills.includes(skill)
        ? prev.skills.filter(s => s !== skill)
        : [...prev.skills, skill]
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            {[1, 2, 3, 4, 5].map((s) => (
              <div
                key={s}
                className={`flex-1 h-2 rounded ${
                  s <= step ? 'bg-blue-600' : 'bg-gray-200'
                } ${s !== 1 ? 'ml-2' : ''}`}
              />
            ))}
          </div>
          <p className="text-sm text-gray-600 text-center">
            Step {step} of 5
          </p>
        </div>

        {/* Step 1: Welcome */}
        {step === 1 && (
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Welcome to LocalAI Leads! 👋
            </h1>
            <p className="text-lg text-gray-600 mb-6">
              Hi {user?.name || 'there'}! Let's get you set up in just 3 quick steps.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
              <h3 className="font-semibold text-blue-900 mb-3">What you'll get:</h3>
              <ul className="text-left space-y-2 text-blue-800">
                <li>✓ Access to high-quality local business leads</li>
                <li>✓ Auto-generated demo websites to impress clients</li>
                <li>✓ Built-in messaging and deal management</li>
                <li>✓ Earn money by helping businesses go digital</li>
              </ul>
            </div>
            <button
              onClick={handleNext}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition"
            >
              Let's Get Started
            </button>
          </div>
        )}

        {/* Step 2: Profile Completion */}
        {step === 2 && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Complete Your Profile
            </h2>
            <p className="text-gray-600 mb-6">
              Help businesses understand your expertise and experience.
            </p>
            
            {/* Portfolio URL */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Portfolio URL (Optional)
              </label>
              <input
                type="url"
                value={profile.portfolio}
                onChange={(e) => setProfile({...profile, portfolio: e.target.value})}
                placeholder="https://yourportfolio.com"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Skills */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Skills (Select all that apply)
              </label>
              <div className="grid grid-cols-2 gap-3">
                {skillOptions.map((skill) => (
                  <button
                    key={skill}
                    type="button"
                    onClick={() => toggleSkill(skill)}
                    className={`p-3 border-2 rounded-lg text-sm transition ${
                      profile.skills.includes(skill)
                        ? 'border-blue-600 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    {profile.skills.includes(skill) && '✓ '}
                    {skill}
                  </button>
                ))}
              </div>
            </div>

            {/* Experience */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Experience Level
              </label>
              <select
                value={profile.experience}
                onChange={(e) => setProfile({...profile, experience: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select your experience</option>
                <option value="beginner">Beginner (0-1 years)</option>
                <option value="intermediate">Intermediate (1-3 years)</option>
                <option value="advanced">Advanced (3-5 years)</option>
                <option value="expert">Expert (5+ years)</option>
              </select>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-blue-800 text-sm">
                💡 <strong>Tip:</strong> A complete profile helps you stand out! Businesses prefer freelancers with clear skills and experience.
              </p>
            </div>

            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-lg hover:bg-gray-50 transition"
              >
                Back
              </button>
              <button
                type="button"
                onClick={handleNext}
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition"
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Select City */}
        {step === 3 && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Which city do you want to work in?
            </h2>
            <p className="text-gray-600 mb-6">
              We'll show you leads from businesses in your selected city.
            </p>
            <div className="grid grid-cols-2 gap-4 mb-8">
              {cities.map((c) => (
                <button
                  key={c}
                  onClick={() => setCity(c)}
                  className={`p-4 border-2 rounded-lg text-left transition ${
                    city === c
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300'
                  }`}
                >
                  <div className="font-semibold text-gray-900">{c}</div>
                </button>
              ))}
            </div>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-lg hover:bg-gray-50 transition"
              >
                Back
              </button>
              <button
                type="button"
                onClick={handleNext}
                disabled={!city}
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Select Category */}
        {step === 4 && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              What type of businesses interest you?
            </h2>
            <p className="text-gray-600 mb-6">
              Choose a category to start with. You can explore others later!
            </p>
            <div className="grid grid-cols-1 gap-3 mb-8">
              {categories.map((cat) => (
                <button
                  key={cat.value}
                  onClick={() => setCategory(cat.value)}
                  className={`p-4 border-2 rounded-lg text-left transition ${
                    category === cat.value
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300'
                  }`}
                >
                  <div className="font-semibold text-gray-900">{cat.label}</div>
                </button>
              ))}
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <p className="text-green-800 text-sm">
                💡 <strong>Pro tip:</strong> Start with restaurants - they have high demand for websites and convert well!
              </p>
            </div>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setStep(3)}
                className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-lg hover:bg-gray-50 transition"
              >
                Back
              </button>
              <button
                type="button"
                onClick={handleNext}
                disabled={!category}
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {/* Step 5: First Lead Walkthrough */}
        {step === 5 && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              How to Work with Leads
            </h2>
            <p className="text-gray-600 mb-6">
              Quick tutorial on finding and contacting businesses
            </p>

            <div className="space-y-6 mb-8">
              {/* View Insights */}
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                    1
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      📊 View Lead Insights
                    </h3>
                    <p className="text-gray-700 mb-3">
                      Each lead shows business details, digital score, rating, and contact info. Higher scores mean better opportunities!
                    </p>
                    <div className="bg-white rounded p-3 text-sm">
                      <div className="flex justify-between mb-1">
                        <span className="text-gray-600">Digital Score:</span>
                        <span className="font-semibold text-blue-600">85/100</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Rating:</span>
                        <span className="font-semibold">⭐ 4.5 (120 reviews)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Generate Demo */}
              <div className="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-green-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                    2
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      🚀 Generate Demo Website
                    </h3>
                    <p className="text-gray-700 mb-3">
                      Click "Generate Demo" to create a professional website preview. This shows the business what you can build for them!
                    </p>
                    <div className="bg-white rounded p-3 text-sm text-gray-600">
                      Demo includes: Business info, photos, contact details, SEO optimization, and mobile-responsive design.
                    </div>
                  </div>
                </div>
              </div>

              {/* Initiate Contact */}
              <div className="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                    3
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      💬 Initiate Contact
                    </h3>
                    <p className="text-gray-700 mb-3">
                      Send a message via WhatsApp, SMS, or Email. Share your demo link and introduce yourself professionally.
                    </p>
                    <div className="bg-white rounded p-3 text-sm">
                      <p className="text-gray-600 mb-2"><strong>Limits:</strong></p>
                      <ul className="text-gray-600 space-y-1">
                        <li>• 10 messages per day</li>
                        <li>• 6-hour exclusivity per lead</li>
                        <li>• Max 2 follow-ups (48hr apart)</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <p className="text-yellow-800 text-sm">
                🎯 <strong>Your Goal:</strong> Generate demos, send professional messages, and convert leads into deals. Quality over quantity!
              </p>
            </div>

            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setStep(4)}
                className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-lg hover:bg-gray-50 transition"
              >
                Back
              </button>
              <button
                type="button"
                onClick={handleNext}
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition"
              >
                Start Finding Leads! 🚀
              </button>
            </div>
          </div>
        )}

        {/* Skip Button */}
        <button
          onClick={handleSkip}
          className="w-full mt-4 text-gray-500 hover:text-gray-700 text-sm"
        >
          Skip for now
        </button>
      </div>
    </div>
  );
};

export default OnboardingPage;
