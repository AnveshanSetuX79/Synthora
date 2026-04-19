"""AI Business Copilot - Actionable sales intelligence for freelancers."""
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AICopilot:
    """AI-powered business analysis and sales strategy generator."""
    
    MAX_USES_PER_LEAD = 3
    
    def __init__(self):
        """Initialize AI Copilot."""
        pass
    
    def generate_sales_intelligence(
        self,
        business_data: Dict,
        insights_data: Dict,
        remaining_uses: int
    ) -> Dict:
        """
        Generate actionable sales intelligence for a specific business.
        
        Args:
            business_data: Business information (name, category, address, etc.)
            insights_data: Business insights (scores, AI enrichment, etc.)
            remaining_uses: Number of remaining copilot uses for this lead
            
        Returns:
            Dict with structured sales intelligence
        """
        try:
            # Extract key data (with None safety)
            name = business_data.get('name', 'Unknown Business')
            category = business_data.get('category', 'business')
            has_website = insights_data.get('has_website', False)
            rating = insights_data.get('rating')
            review_count = insights_data.get('review_count') or 0  # Handle None
            digital_score = insights_data.get('digital_score') or 0  # Handle None
            
            # AI enrichment data (with None safety)
            ai_description = insights_data.get('ai_description')
            ai_pain_points = insights_data.get('ai_pain_points', [])
            ai_recommended_solutions = insights_data.get('ai_recommended_solutions', [])
            ai_digital_maturity = insights_data.get('ai_digital_maturity', 'low')
            ai_growth_potential = insights_data.get('ai_growth_potential', 'medium')
            ai_urgency_score = insights_data.get('ai_urgency_score') or 50  # Handle None
            ai_pitch_suggestions = insights_data.get('ai_pitch_suggestions', [])
            
            # Build intelligence report
            intelligence = {
                'business_name': name,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'remaining_uses': remaining_uses - 1,  # This use counts
                'urgency_level': self._calculate_urgency_level(ai_urgency_score),
                'quick_summary': self._generate_quick_summary(
                    name, category, has_website, digital_score, ai_digital_maturity
                ),
                'strengths': self._identify_strengths(
                    rating, review_count, category, insights_data
                ),
                'digital_gaps': self._identify_digital_gaps(
                    has_website, digital_score, ai_digital_maturity, insights_data
                ),
                'pain_points': ai_pain_points if ai_pain_points else self._infer_pain_points(
                    category, has_website, digital_score
                ),
                'recommended_solutions': self._generate_solutions(
                    category, has_website, digital_score, ai_recommended_solutions
                ),
                'sales_strategy': self._generate_sales_strategy(
                    name, category, has_website, ai_urgency_score, ai_growth_potential
                ),
                'pitch_angles': ai_pitch_suggestions if ai_pitch_suggestions else self._generate_pitch_angles(
                    category, has_website, digital_score
                ),
                'next_actions': self._generate_next_actions(
                    category, has_website, ai_urgency_score
                ),
                'estimated_deal_value': self._estimate_deal_value(
                    category, digital_score, ai_growth_potential
                ),
                'conversion_probability': self._estimate_conversion_probability(
                    digital_score, ai_urgency_score, ai_digital_maturity
                )
            }
            
            return intelligence
            
        except Exception as e:
            logger.error(f"Error generating sales intelligence: {e}")
            raise
    
    def _calculate_urgency_level(self, urgency_score: int) -> str:
        """Calculate urgency level from score."""
        if urgency_score >= 75:
            return "🔥 CRITICAL - Act within 24 hours"
        elif urgency_score >= 50:
            return "⚡ HIGH - Contact within 3 days"
        else:
            return "📊 MODERATE - Contact within 1 week"
    
    def _generate_quick_summary(
        self, name: str, category: str, has_website: bool, 
        digital_score: int, digital_maturity: str
    ) -> str:
        """Generate a quick business summary."""
        website_status = "no website" if not has_website else "basic website"
        maturity_desc = {
            'low': 'minimal digital presence',
            'medium': 'developing digital presence',
            'high': 'established digital presence'
        }.get(digital_maturity, 'unknown digital presence')
        
        return (
            f"{name} is a {category} with {website_status} and {maturity_desc}. "
            f"Digital score: {digital_score}/100. "
            f"{'High potential for digital transformation.' if digital_score < 50 else 'Opportunity for optimization.'}"
        )
    
    def _identify_strengths(
        self, rating: Optional[float], review_count: Optional[int], 
        category: str, insights: Dict
    ) -> List[str]:
        """Identify business strengths."""
        strengths = []
        
        if rating and rating >= 4.0:
            strengths.append(f"⭐ Strong reputation ({rating}/5.0 rating)")
        
        # Handle None review_count
        review_count = review_count or 0
        if review_count >= 50:
            strengths.append(f"💬 Active customer base ({review_count} reviews)")
        elif review_count >= 10:
            strengths.append(f"💬 Growing customer feedback ({review_count} reviews)")
        
        # Category-specific strengths
        if category in ['restaurant', 'cafe']:
            strengths.append("🍽️ Food service businesses have high online ordering potential")
        elif category in ['school', 'education']:
            strengths.append("🎓 Education sector values professional online presence")
        elif category in ['healthcare', 'clinic', 'hospital']:
            strengths.append("🏥 Healthcare needs online appointment systems")
        
        if not strengths:
            strengths.append("💼 Local business with growth potential")
        
        return strengths
    
    def _identify_digital_gaps(
        self, has_website: bool, digital_score: int, 
        digital_maturity: str, insights: Dict
    ) -> List[Dict[str, str]]:
        """Identify specific digital gaps with impact assessment."""
        gaps = []
        
        if not has_website:
            gaps.append({
                'gap': 'No Website',
                'impact': 'CRITICAL',
                'description': 'Missing 70% of potential customers who search online',
                'solution': 'Professional website with mobile optimization'
            })
        
        if digital_score < 30:
            gaps.append({
                'gap': 'Zero Online Presence',
                'impact': 'HIGH',
                'description': 'Invisible to customers searching online',
                'solution': 'Google My Business optimization + basic SEO'
            })
        
        if insights.get('review_count', 0) < 10:
            gaps.append({
                'gap': 'Low Social Proof',
                'impact': 'MEDIUM',
                'description': 'Customers trust businesses with reviews',
                'solution': 'Review generation campaign'
            })
        
        if digital_maturity == 'low':
            gaps.append({
                'gap': 'No Digital Marketing',
                'impact': 'HIGH',
                'description': 'Competitors are capturing their market share',
                'solution': 'Social media presence + local SEO'
            })
        
        return gaps
    
    def _infer_pain_points(
        self, category: str, has_website: bool, digital_score: int
    ) -> List[str]:
        """Infer business pain points based on data."""
        pain_points = []
        
        if not has_website:
            pain_points.append("Losing customers to competitors with websites")
            pain_points.append("Unable to showcase services 24/7")
        
        if digital_score < 40:
            pain_points.append("Low visibility in local search results")
            pain_points.append("Relying only on walk-in customers")
        
        # Category-specific pain points
        if category in ['restaurant', 'cafe']:
            pain_points.append("Missing online ordering revenue stream")
        elif category in ['school', 'education']:
            pain_points.append("Parents expect online information and enrollment")
        elif category in ['healthcare', 'clinic']:
            pain_points.append("Patients want online appointment booking")
        
        return pain_points
    
    def _generate_solutions(
        self, category: str, has_website: bool, digital_score: int,
        ai_solutions: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """Generate specific solution recommendations."""
        solutions = []
        
        if not has_website:
            solutions.append({
                'solution': 'Professional Website',
                'priority': 'CRITICAL',
                'timeline': '2-3 weeks',
                'roi': 'Increase inquiries by 200-300%'
            })
        
        if digital_score < 50:
            solutions.append({
                'solution': 'Local SEO Optimization',
                'priority': 'HIGH',
                'timeline': '1-2 weeks',
                'roi': 'Appear in top 3 local search results'
            })
        
        # Category-specific solutions
        if category in ['restaurant', 'cafe']:
            solutions.append({
                'solution': 'Online Ordering System',
                'priority': 'HIGH',
                'timeline': '1 week',
                'roi': '15-25% revenue increase'
            })
        elif category in ['school', 'education']:
            solutions.append({
                'solution': 'Online Admission Portal',
                'priority': 'MEDIUM',
                'timeline': '2-3 weeks',
                'roi': 'Streamline enrollment process'
            })
        
        # Add AI-suggested solutions if available
        if ai_solutions:
            for ai_solution in ai_solutions:
                # Check if not already added
                if not any(s['solution'].lower() in ai_solution.lower() for s in solutions):
                    solutions.append({
                        'solution': ai_solution,
                        'priority': 'MEDIUM',
                        'timeline': '2-4 weeks',
                        'roi': 'Improved digital presence'
                    })
        
        return solutions
    
    def _generate_sales_strategy(
        self, name: str, category: str, has_website: bool, 
        urgency_score: int, growth_potential: str
    ) -> Dict[str, any]:
        """Generate tailored sales strategy."""
        strategy = {
            'approach': '',
            'opening_line': '',
            'value_proposition': '',
            'objection_handling': {},
            'closing_technique': ''
        }
        
        # Determine approach based on urgency
        if urgency_score >= 70:
            strategy['approach'] = 'DIRECT - They need help NOW'
            strategy['opening_line'] = f"I noticed {name} doesn't have a website. Your competitors are capturing customers searching for {category} services online."
        else:
            strategy['approach'] = 'CONSULTATIVE - Build relationship first'
            strategy['opening_line'] = f"Hi! I help {category} businesses like {name} increase their customer reach through digital presence."
        
        # Value proposition
        if not has_website:
            strategy['value_proposition'] = (
                f"I can build you a professional website that brings in customers 24/7. "
                f"Most {category} businesses see 2-3x more inquiries within the first month."
            )
        else:
            strategy['value_proposition'] = (
                f"I can optimize your online presence to rank higher in local searches. "
                f"This means more customers finding you instead of competitors."
            )
        
        # Common objections
        strategy['objection_handling'] = {
            '"Too expensive"': 'Start with a basic package at ₹5,000. Pay only after you see results.',
            '"We\'re too busy"': 'I handle everything. You just approve the design. Takes 30 minutes of your time.',
            '"We get enough customers"': 'Great! Imagine getting 50% more with the same effort. That\'s what digital presence does.',
            '"Not sure it works"': 'I can show you a demo website for your business right now. See it before you decide.'
        }
        
        # Closing technique
        if urgency_score >= 70:
            strategy['closing_technique'] = 'URGENCY: "I can start this week. Let me show you a demo of what your website could look like."'
        else:
            strategy['closing_technique'] = 'SOFT CLOSE: "Would you like to see a free demo website I can create for you? No commitment needed."'
        
        return strategy
    
    def _generate_pitch_angles(
        self, category: str, has_website: bool, digital_score: int
    ) -> List[str]:
        """Generate specific pitch angles."""
        pitches = []
        
        if not has_website:
            pitches.append("🎯 'Your competitors with websites are taking your customers'")
            pitches.append("💰 'A website pays for itself in 2-3 new customers'")
        
        if digital_score < 40:
            pitches.append("📱 '80% of customers search online before visiting'")
            pitches.append("🔍 'You're invisible when people search for " + category + " near me'")
        
        # Category-specific pitches
        if category in ['restaurant', 'cafe']:
            pitches.append("🍽️ 'Online ordering can add ₹50,000-₹1,00,000/month in revenue'")
        elif category in ['school', 'education']:
            pitches.append("🎓 'Parents expect to find school information online'")
        elif category in ['healthcare', 'clinic']:
            pitches.append("🏥 'Patients want to book appointments online, not wait on phone'")
        
        return pitches
    
    def _generate_next_actions(
        self, category: str, has_website: bool, urgency_score: int
    ) -> List[Dict[str, str]]:
        """Generate specific next actions for the freelancer."""
        actions = []
        
        # Immediate actions
        if urgency_score >= 70:
            actions.append({
                'action': 'Call or WhatsApp TODAY',
                'priority': '🔥 URGENT',
                'script': 'Use the opening line from sales strategy above'
            })
        else:
            actions.append({
                'action': 'Send initial message within 48 hours',
                'priority': '⚡ HIGH',
                'script': 'Use consultative approach from sales strategy'
            })
        
        # Follow-up actions
        actions.append({
            'action': 'Generate demo website',
            'priority': '📊 MEDIUM',
            'script': 'Show them what their business could look like online'
        })
        
        actions.append({
            'action': 'Prepare case study',
            'priority': '📊 MEDIUM',
            'script': f'Find a similar {category} business you helped (or create example)'
        })
        
        actions.append({
            'action': 'Schedule follow-up',
            'priority': '📅 LOW',
            'script': 'If no response in 3 days, send reminder with demo link'
        })
        
        return actions
    
    def _estimate_deal_value(
        self, category: str, digital_score: int, growth_potential: str
    ) -> Dict[str, str]:
        """Estimate potential deal value."""
        # Base pricing by category
        base_prices = {
            'restaurant': {'min': 8000, 'max': 25000},
            'cafe': {'min': 6000, 'max': 18000},
            'school': {'min': 15000, 'max': 50000},
            'education': {'min': 10000, 'max': 35000},
            'healthcare': {'min': 12000, 'max': 40000},
            'clinic': {'min': 10000, 'max': 30000},
            'hospital': {'min': 25000, 'max': 100000},
            'default': {'min': 5000, 'max': 20000}
        }
        
        pricing = base_prices.get(category, base_prices['default'])
        
        # Adjust for growth potential
        if growth_potential == 'high':
            pricing['max'] = int(pricing['max'] * 1.5)
        
        return {
            'initial_project': f"₹{pricing['min']:,} - ₹{pricing['max']:,}",
            'monthly_retainer': f"₹{int(pricing['min'] * 0.3):,} - ₹{int(pricing['max'] * 0.3):,}",
            'lifetime_value': f"₹{int(pricing['max'] * 3):,}+ (over 12 months)"
        }
    
    def _estimate_conversion_probability(
        self, digital_score: int, urgency_score: int, digital_maturity: str
    ) -> Dict[str, any]:
        """Estimate probability of converting this lead."""
        # Calculate base probability
        score_factor = (100 - digital_score) / 100  # Lower score = higher need
        urgency_factor = urgency_score / 100
        maturity_factor = {'low': 0.8, 'medium': 0.6, 'high': 0.4}.get(digital_maturity, 0.5)
        
        probability = (score_factor * 0.4 + urgency_factor * 0.4 + maturity_factor * 0.2) * 100
        
        # Categorize
        if probability >= 70:
            category = "🟢 HIGH"
            advice = "Strong lead - prioritize this one"
        elif probability >= 50:
            category = "🟡 MEDIUM"
            advice = "Good potential - worth pursuing"
        else:
            category = "🔴 LOW"
            advice = "May need more nurturing"
        
        return {
            'probability': f"{int(probability)}%",
            'category': category,
            'advice': advice
        }
