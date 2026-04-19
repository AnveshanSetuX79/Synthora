export default function TrustBadges({ variant = 'horizontal' }) {
  const badges = [
    {
      icon: '🔒',
      title: 'Secure Payment',
      description: 'Razorpay encrypted transactions'
    },
    {
      icon: '✓',
      title: 'Verified Freelancers',
      description: 'KYC verified professionals'
    },
    {
      icon: '🛡️',
      title: 'Escrow Protection',
      description: 'Your money is safe until delivery'
    },
    {
      icon: '📊',
      title: 'Milestone-Based',
      description: 'Pay as work progresses'
    }
  ];

  if (variant === 'vertical') {
    return (
      <div className="space-y-4">
        {badges.map((badge, index) => (
          <div key={index} className="flex items-start gap-3 p-4 bg-white rounded-lg border border-gray-200">
            <div className="text-3xl">{badge.icon}</div>
            <div>
              <h4 className="font-semibold text-gray-900">{badge.title}</h4>
              <p className="text-sm text-gray-600">{badge.description}</p>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {badges.map((badge, index) => (
        <div key={index} className="text-center p-6 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
          <div className="text-4xl mb-3">{badge.icon}</div>
          <h4 className="font-semibold text-gray-900 mb-2">{badge.title}</h4>
          <p className="text-sm text-gray-600">{badge.description}</p>
        </div>
      ))}
    </div>
  );
}
