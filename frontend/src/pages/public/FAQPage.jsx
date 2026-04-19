import { useState } from 'react';

export default function FAQPage() {
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      category: 'For Business Owners',
      questions: [
        {
          q: 'How does LocalAI Leads work?',
          a: 'We connect local businesses with verified web developers. You get a free demo website first, then only pay if you approve the work. Payment is held in escrow and released in milestones.'
        },
        {
          q: 'Is the demo website really free?',
          a: 'Yes! Freelancers create a demo website for your business at no cost. You can view it, share it, and decide if you want to proceed. There\'s no obligation to pay unless you approve the work.'
        },
        {
          q: 'How does payment work?',
          a: 'Payment is milestone-based and held in escrow. For your first project, you pay 50% upfront and 50% on delivery. After 20 projects, it becomes 30% design, 40% development, 30% final delivery. You approve each milestone before payment is released.'
        },
        {
          q: 'What if I\'m not satisfied with the work?',
          a: 'You can reject milestones and request revisions. If there\'s a dispute, our admin team mediates within 48 hours. You\'re protected by our escrow system - money is only released when you approve.'
        },
        {
          q: 'How long does it take to get a website?',
          a: 'Timeline varies by package. Typically: Starter (5-7 days), Standard (10-14 days), Premium (15-21 days). You\'ll see progress at each milestone.'
        }
      ]
    },
    {
      category: 'For Freelancers',
      questions: [
        {
          q: 'How do I get started as a freelancer?',
          a: 'Register, complete KYC verification, and start claiming leads. New freelancers get 3 leads per day. As you build your reputation, you can upgrade to Verified (10 leads/day) or Top Rated (20 leads/day).'
        },
        {
          q: 'How do tier upgrades work?',
          a: 'Tiers upgrade automatically based on performance: Verified requires 70% response rate, 4.0+ rating, 20% conversion, and 5+ deals. Top Rated requires 85% response, 4.5+ rating, 30% conversion, and 10+ deals.'
        },
        {
          q: 'When do I get paid?',
          a: 'Payment is released when the business owner approves each milestone. For disputes, admin resolves within 24 hours. Funds are held in escrow for your protection.'
        },
        {
          q: 'What are the platform fees?',
          a: 'We charge 10% commission on your earnings. The business owner pays an additional 5%. This covers payment processing, escrow, and platform maintenance.'
        },
        {
          q: 'Can I contact leads directly?',
          a: 'You have a 6-hour exclusivity window when you claim a lead. You can send up to 10 outreach messages per day via WhatsApp, SMS, or email. Follow-ups are limited to 2 attempts with 48-hour intervals.'
        }
      ]
    },
    {
      category: 'Payment & Security',
      questions: [
        {
          q: 'Is my payment information secure?',
          a: 'Yes! We use Razorpay for payment processing, which is PCI-DSS compliant. We never store your card details. All transactions are encrypted.'
        },
        {
          q: 'What payment methods do you accept?',
          a: 'We accept credit cards, debit cards, and UPI through Razorpay. All major Indian payment methods are supported.'
        },
        {
          q: 'How does escrow protection work?',
          a: 'When you make a payment, funds are held in escrow (not released to the freelancer). Money is only released when you approve each milestone. This protects both parties.'
        },
        {
          q: 'Can I get a refund?',
          a: 'Refunds are based on approved milestones. If no work has started, you get a full refund (minus processing fees). Partial refunds are based on unapproved milestones. All milestones approved means no refund.'
        }
      ]
    },
    {
      category: 'Platform Features',
      questions: [
        {
          q: 'What is a demo website?',
          a: 'A demo website is a fully functional preview of your business website created by a freelancer. It includes your business information, photos, contact details, and is SEO-optimized. You can view and share it before deciding to proceed.'
        },
        {
          q: 'How do disputes work?',
          a: 'If there\'s a disagreement, you have 48 hours to resolve it directly with the freelancer through our dispute chat. If unresolved, it escalates to admin mediation. Admin reviews the case and makes a decision within 24 hours.'
        },
        {
          q: 'Can I leave reviews?',
          a: 'Yes! After project completion, you have 30 days to leave a review (5-star rating and written feedback). Reviews help other businesses make informed decisions and help freelancers build their reputation.'
        },
        {
          q: 'How are leads generated?',
          a: 'We use Google Places API to find local businesses that need websites. Leads are scored based on digital presence, reviews, and category. Higher-scored leads are prioritized.'
        }
      ]
    }
  ];

  const toggleQuestion = (categoryIndex, questionIndex) => {
    const index = `${categoryIndex}-${questionIndex}`;
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h1>
          <p className="text-lg text-gray-600">
            Everything you need to know about LocalAI Leads
          </p>
        </div>

        {/* FAQ Categories */}
        <div className="space-y-8">
          {faqs.map((category, categoryIndex) => (
            <div key={categoryIndex} className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                {category.category}
              </h2>
              <div className="space-y-4">
                {category.questions.map((faq, questionIndex) => {
                  const index = `${categoryIndex}-${questionIndex}`;
                  const isOpen = openIndex === index;
                  
                  return (
                    <div key={questionIndex} className="border-b border-gray-200 last:border-0 pb-4 last:pb-0">
                      <button
                        type="button"
                        onClick={() => toggleQuestion(categoryIndex, questionIndex)}
                        className="w-full flex justify-between items-start text-left py-2"
                      >
                        <span className="font-semibold text-gray-900 pr-4">
                          {faq.q}
                        </span>
                        <span className="text-2xl text-gray-400 flex-shrink-0">
                          {isOpen ? '−' : '+'}
                        </span>
                      </button>
                      {isOpen && (
                        <div className="mt-2 text-gray-600 leading-relaxed">
                          {faq.a}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Contact Section */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            Still have questions?
          </h3>
          <p className="text-gray-600 mb-4">
            Can't find the answer you're looking for? Please reach out to our support team.
          </p>
          <a
            href="mailto:support@localai.com"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Contact Support
          </a>
        </div>
      </div>
    </div>
  );
}
