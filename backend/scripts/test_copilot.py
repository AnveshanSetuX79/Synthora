"""Test AI Copilot functionality."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.ai_copilot import AICopilot

def test_copilot():
    """Test AI Copilot with sample data."""
    
    # Sample business data
    business_data = {
        'name': 'Vaijanath Amruttulya',
        'category': 'restaurant',
        'address': 'Pune, Maharashtra',
        'city': 'Pune',
        'phone': None,
        'latitude': 18.5204,
        'longitude': 73.8567
    }
    
    # Sample insights data (with AI enrichment)
    insights_data = {
        'digital_score': 30,
        'has_website': False,
        'website_url': None,
        'rating': None,
        'review_count': 0,
        'ai_description': 'A local restaurant serving customers in the area. Currently lacks online presence with potential for digital growth.',
        'ai_specialties': ['Traditional cuisine', 'Local flavors'],
        'ai_target_customers': ['Local residents', 'Food enthusiasts'],
        'ai_pain_points': ['No online ordering', 'Limited visibility', 'Missing digital menu'],
        'ai_recommended_solutions': ['Website with online ordering', 'Google My Business optimization', 'Social media presence'],
        'ai_competitive_advantages': ['Authentic recipes', 'Local reputation'],
        'ai_digital_maturity': 'low',
        'ai_growth_potential': 'high',
        'ai_estimated_size': 'small',
        'ai_online_presence_score': 20,
        'ai_urgency_score': 75,
        'ai_enrichment_confidence': 0.75,
        'ai_pitch_suggestions': ['Your competitors with websites are taking your customers', 'Online ordering can add ₹50,000/month']
    }
    
    # Generate intelligence
    copilot = AICopilot()
    intelligence = copilot.generate_sales_intelligence(
        business_data=business_data,
        insights_data=insights_data,
        remaining_uses=3
    )
    
    # Display results
    print("=" * 80)
    print("AI BUSINESS COPILOT - TEST RESULTS")
    print("=" * 80)
    print()
    
    print(f"Business: {intelligence['business_name']}")
    print(f"Remaining Uses: {intelligence['remaining_uses']}")
    print(f"Urgency: {intelligence['urgency_level']}")
    print()
    
    print("QUICK SUMMARY:")
    print(intelligence['quick_summary'])
    print()
    
    print("CONVERSION PROBABILITY:")
    print(f"  {intelligence['conversion_probability']['probability']} - {intelligence['conversion_probability']['category']}")
    print(f"  {intelligence['conversion_probability']['advice']}")
    print()
    
    print("STRENGTHS:")
    for strength in intelligence['strengths']:
        print(f"  • {strength}")
    print()
    
    print("DIGITAL GAPS:")
    for gap in intelligence['digital_gaps']:
        print(f"  • {gap['gap']} ({gap['impact']})")
        print(f"    → {gap['solution']}")
    print()
    
    print("SALES STRATEGY:")
    print(f"  Approach: {intelligence['sales_strategy']['approach']}")
    print(f"  Opening: \"{intelligence['sales_strategy']['opening_line']}\"")
    print(f"  Closing: {intelligence['sales_strategy']['closing_technique']}")
    print()
    
    print("DEAL VALUE:")
    print(f"  Initial: {intelligence['estimated_deal_value']['initial_project']}")
    print(f"  Monthly: {intelligence['estimated_deal_value']['monthly_retainer']}")
    print(f"  Lifetime: {intelligence['estimated_deal_value']['lifetime_value']}")
    print()
    
    print("NEXT ACTIONS:")
    for action in intelligence['next_actions']:
        print(f"  {action['priority']} {action['action']}")
    print()
    
    print("=" * 80)
    print("✅ AI Copilot test completed successfully!")
    print("=" * 80)

if __name__ == "__main__":
    test_copilot()
