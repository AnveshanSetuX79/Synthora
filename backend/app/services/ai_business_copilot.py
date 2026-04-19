"""AI Business Copilot for generating business intelligence reports.

This service uses AI to enhance real business data with actionable insights,
sales strategies, and personalized outreach recommendations.

IMPORTANT: This service ENHANCES real data, it does NOT generate fake data.
All AI-generated content is clearly marked as "AI Insight" or "Estimated".

Supports multiple AI backends:
- Template Mode (FREE, no AI needed)
- OpenAI/ChatGPT (Paid, ~$0.001/lead)
- Ollama (FREE, local AI)
"""
import logging
import json
from typing import Dict, Optional
from datetime import datetime
import os
import requests

logger = logging.getLogger(__name__)

# Try to import OpenAI (optional dependency)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not installed. Install with: pip install openai")


class AIBusinessCopilot:
    """AI-powered business intelligence and sales strategy generator."""
    
    def __init__(self, api_key: Optional[str] = None, use_ollama: bool = False, ollama_url: str = "http://localhost:11434"):
        """Initialize AI Business Copilot.
        
        Args:
            api_key: OpenAI API key (optional, for ChatGPT mode)
            use_ollama: Use Ollama for local AI (FREE)
            ollama_url: Ollama server URL (default: http://localhost:11434)
        """
        self.api_key = api_key
        self.use_ollama = use_ollama
        self.ollama_url = ollama_url
        self.client = None
        self.mode = "template"
        
        # Try Ollama first if enabled
        if use_ollama:
            if self._test_ollama_connection():
                self.mode = "ollama"
                logger.info("AI Business Copilot initialized in Ollama mode (FREE, local)")
            else:
                logger.warning("Ollama not available, falling back to template mode")
        
        # Try OpenAI if API key provided and Ollama not used
        elif api_key and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=api_key)
                self.mode = "chatgpt"
                logger.info("AI Business Copilot initialized in ChatGPT mode")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        
        if self.mode == "template":
            logger.info("AI Business Copilot initialized in Template mode (FREE)")
    
    def _test_ollama_connection(self) -> bool:
        """Test if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    logger.info(f"Ollama available with {len(models)} models")
                    return True
                else:
                    logger.warning("Ollama running but no models installed")
                    return False
            return False
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
    
    def generate_business_intelligence(
        self,
        name: str,
        category: str,
        city: str,
        digital_score: int,
        has_website: bool,
        rating: Optional[float] = None,
        review_count: Optional[int] = None,
        data_source: str = "Google Places",
        phone: Optional[str] = None,
        address: Optional[str] = None,
        place_id: Optional[str] = None
    ) -> Dict:
        """Generate complete business intelligence report.
        
        Args:
            name: Business name (REAL data)
            category: Business category (REAL data)
            city: City location (REAL data)
            digital_score: Digital presence score 0-100 (CALCULATED)
            has_website: Whether business has website (REAL data)
            rating: Google rating (REAL data)
            review_count: Number of reviews (REAL data)
            data_source: Where data came from (REAL data)
            phone: Phone number (REAL data)
            address: Address (REAL data)
            place_id: Google Place ID (REAL data)
            
        Returns:
            Complete business intelligence report
        """
        try:
            # If Ollama is enabled, use it
            if self.mode == "ollama":
                return self._generate_with_ollama(
                    name, category, city, digital_score, has_website,
                    rating, review_count, data_source, phone, address, place_id
                )
            # If AI is enabled, use OpenAI API
            elif self.mode == "chatgpt":
                return self._generate_with_ai(
                    name, category, city, digital_score, has_website,
                    rating, review_count, data_source, phone, address, place_id
                )
            else:
                # Use template-based generation (no API cost)
                return self._generate_with_template(
                    name, category, city, digital_score, has_website,
                    rating, review_count, data_source, phone, address, place_id
                )
                
        except Exception as e:
            logger.error(f"Error generating business intelligence: {str(e)}")
            return self._generate_fallback_report(name, category, city)
    
    def _generate_with_template(
        self,
        name: str,
        category: str,
        city: str,
        digital_score: int,
        has_website: bool,
        rating: Optional[float],
        review_count: Optional[int],
        data_source: str,
        phone: Optional[str],
        address: Optional[str],
        place_id: Optional[str]
    ) -> Dict:
        """Generate report using templates (no AI API cost).
        
        This provides good insights without requiring OpenAI API.
        """
        # Calculate confidence based on available data
        confidence = self._calculate_confidence(
            rating, review_count, phone, address, has_website
        )
        
        # Determine opportunity level
        opportunity_level = self._assess_opportunity(
            digital_score, has_website, rating, review_count
        )
        
        # Estimate pricing based on category and business size
        pricing = self._estimate_pricing(category, rating, review_count)
        
        # Generate personalized messages
        messages = self._generate_outreach_messages(
            name, category, city, has_website, digital_score
        )
        
        # Assess risks
        risks = self._assess_risks(
            digital_score, has_website, rating, review_count, phone
        )
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "generation_method": "template",
            
            # 1. Business Summary
            "business_summary": {
                "name": name,
                "category": category,
                "location": city,
                "data_source": data_source,
                "confidence_score": confidence,
                "confidence_level": self._get_confidence_level(confidence),
                "last_verified": datetime.utcnow().isoformat(),
                "summary": f"{name} is a {category} business in {city} with a digital presence score of {digital_score}/100."
            },
            
            # 2. Digital Presence Breakdown
            "digital_presence": {
                "overall_score": digital_score,
                "has_website": has_website,
                "rating": rating or "Not available",
                "review_count": review_count or "Not available",
                "breakdown": self._analyze_digital_presence(
                    digital_score, has_website, rating, review_count
                ),
                "missing_elements": self._identify_missing_elements(
                    has_website, digital_score
                )
            },
            
            # 3. Opportunity Analysis
            "opportunity_analysis": {
                "level": opportunity_level,
                "missed_revenue_estimate": self._estimate_missed_revenue(
                    category, has_website, rating
                ),
                "growth_potential": self._assess_growth_potential(
                    category, digital_score, rating, review_count
                ),
                "market_position": self._analyze_market_position(
                    rating, review_count, has_website
                )
            },
            
            # 4. Conversion Probability
            "conversion_probability": {
                "percentage": self._calculate_conversion_probability(
                    digital_score, has_website, rating, review_count
                ),
                "reasoning": self._explain_conversion_probability(
                    digital_score, has_website, rating, review_count
                ),
                "success_factors": self._identify_success_factors(
                    category, rating, review_count
                ),
                "red_flags": risks.get("red_flags", [])
            },
            
            # 5. Recommended Services
            "recommended_services": {
                "primary": self._recommend_primary_service(
                    has_website, digital_score, category
                ),
                "secondary": self._recommend_secondary_services(
                    category, digital_score
                ),
                "pricing": pricing,
                "timeline": self._estimate_timeline(category, has_website)
            },
            
            # 6. Sales Strategy
            "sales_strategy": {
                "opening_line": messages["opening_line"],
                "value_pitch": self._generate_value_pitch(
                    name, category, digital_score, has_website
                ),
                "objection_handling": self._generate_objection_responses(
                    category, has_website
                ),
                "best_time_to_contact": self._suggest_contact_time(category),
                "approach_style": self._suggest_approach_style(
                    category, rating, review_count
                )
            },
            
            # 7. Outreach Messages
            "outreach_messages": messages,
            
            # 8. Risks & Challenges
            "risks_challenges": risks,
            
            # 9. Data Transparency
            "data_transparency": {
                "real_data": {
                    "business_name": name,
                    "category": category,
                    "location": city,
                    "has_website": has_website,
                    "rating": rating if rating else "Not available",
                    "review_count": review_count if review_count else "Not available",
                    "phone": phone if phone else "Not available",
                    "address": address if address else "Not available",
                    "source": data_source
                },
                "calculated_data": {
                    "digital_score": f"{digital_score}/100 (calculated from available data)",
                    "confidence_score": f"{confidence}% (based on data completeness)"
                },
                "ai_generated": {
                    "opportunity_analysis": "Estimated based on category and digital presence",
                    "pricing_recommendations": "Estimated based on market rates and business size",
                    "outreach_messages": "Template-based with business-specific customization",
                    "conversion_probability": "Calculated using historical patterns"
                },
                "disclaimer": "All AI-generated insights are estimates based on available data and industry patterns. Actual results may vary."
            },
            
            # 10. Source Links
            "source_links": {
                "google_maps": f"https://www.google.com/maps/search/?api=1&query={name.replace(' ', '+')}+{city.replace(' ', '+')}" if name and city else None,
                "google_place": f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else None,
                "data_source": data_source
            }
        }
    
    def _calculate_confidence(
        self,
        rating: Optional[float],
        review_count: Optional[int],
        phone: Optional[str],
        address: Optional[str],
        has_website: bool
    ) -> int:
        """Calculate confidence score based on data completeness."""
        confidence = 0
        
        # Base confidence from having data
        if rating is not None:
            confidence += 20
        if review_count is not None and review_count > 0:
            confidence += 20
        if phone:
            confidence += 20
        if address:
            confidence += 20
        if has_website is not None:
            confidence += 20
        
        return min(confidence, 100)
    
    def _get_confidence_level(self, confidence: int) -> str:
        """Convert confidence score to level."""
        if confidence >= 80:
            return "High"
        elif confidence >= 60:
            return "Medium"
        else:
            return "Low"
    
    def _assess_opportunity(
        self,
        digital_score: int,
        has_website: bool,
        rating: Optional[float],
        review_count: Optional[int]
    ) -> str:
        """Assess opportunity level."""
        if not has_website and digital_score < 30:
            if rating and rating >= 4.0 and review_count and review_count > 50:
                return "🔥 HOT - High-rated business with no website"
            return "🎯 HIGH - Low digital presence, high potential"
        elif not has_website and digital_score < 50:
            return "✅ MEDIUM - Good opportunity"
        elif has_website and digital_score < 60:
            return "⚠️ LOW - Has website but needs improvement"
        else:
            return "❌ SKIP - Strong digital presence already"
    
    def _analyze_digital_presence(
        self,
        digital_score: int,
        has_website: bool,
        rating: Optional[float],
        review_count: Optional[int]
    ) -> Dict:
        """Analyze digital presence breakdown."""
        return {
            "website": "❌ No website" if not has_website else "✅ Has website",
            "online_reputation": f"⭐ {rating}/5.0 ({review_count} reviews)" if rating and review_count else "Not available",
            "social_media": "Unknown (not tracked)",
            "online_ordering": "Unknown (not tracked)",
            "google_my_business": "✅ Listed" if rating else "❌ Not found"
        }
    
    def _identify_missing_elements(
        self,
        has_website: bool,
        digital_score: int
    ) -> list:
        """Identify missing digital elements."""
        missing = []
        
        if not has_website:
            missing.append("Professional website")
        if digital_score < 40:
            missing.extend([
                "Online booking system",
                "Social media presence",
                "Customer reviews management",
                "SEO optimization"
            ])
        
        return missing
    
    def _estimate_missed_revenue(
        self,
        category: str,
        has_website: bool,
        rating: Optional[float]
    ) -> str:
        """Estimate missed revenue opportunity."""
        if not has_website:
            # Businesses without websites miss 30-50% of potential customers
            if category.lower() in ["restaurant", "cafe", "food"]:
                return "₹50,000 - ₹2,00,000/month (online orders + reservations)"
            elif category.lower() in ["salon", "spa", "gym"]:
                return "₹30,000 - ₹1,00,000/month (online bookings)"
            elif category.lower() in ["retail", "shop", "store"]:
                return "₹1,00,000 - ₹5,00,000/month (e-commerce sales)"
            else:
                return "₹20,000 - ₹1,00,000/month (online inquiries)"
        else:
            return "₹10,000 - ₹50,000/month (optimization opportunities)"
    
    def _assess_growth_potential(
        self,
        category: str,
        digital_score: int,
        rating: Optional[float],
        review_count: Optional[int]
    ) -> Dict:
        """Assess growth potential."""
        potential = "High" if digital_score < 40 else "Medium" if digital_score < 60 else "Low"
        
        factors = []
        if digital_score < 40:
            factors.append("Low digital presence = high improvement potential")
        if rating and rating >= 4.0:
            factors.append("Good reputation = easier to convert online visitors")
        if review_count and review_count > 50:
            factors.append("Many reviews = established business with loyal customers")
        
        return {
            "level": potential,
            "factors": factors,
            "timeline": "3-6 months to see significant growth" if potential == "High" else "6-12 months"
        }
    
    def _analyze_market_position(
        self,
        rating: Optional[float],
        review_count: Optional[int],
        has_website: bool
    ) -> str:
        """Analyze market position."""
        if rating and rating >= 4.5 and review_count and review_count > 100:
            return "Market Leader - High reputation, needs digital presence to match"
        elif rating and rating >= 4.0 and review_count and review_count > 50:
            return "Established Player - Good reputation, digital upgrade will boost growth"
        elif rating and rating >= 3.5:
            return "Average Performer - Digital presence can help differentiate"
        else:
            return "New/Unknown - Digital presence critical for visibility"
    
    def _calculate_conversion_probability(
        self,
        digital_score: int,
        has_website: bool,
        rating: Optional[float],
        review_count: Optional[int]
    ) -> int:
        """Calculate conversion probability percentage."""
        probability = 30  # Base probability
        
        # No website = higher need
        if not has_website:
            probability += 30
        
        # Good rating = more likely to invest
        if rating and rating >= 4.0:
            probability += 20
        
        # Many reviews = established business with budget
        if review_count and review_count > 50:
            probability += 10
        
        # Low digital score = clear need
        if digital_score < 30:
            probability += 10
        
        return min(probability, 95)  # Cap at 95%
    
    def _explain_conversion_probability(
        self,
        digital_score: int,
        has_website: bool,
        rating: Optional[float],
        review_count: Optional[int]
    ) -> str:
        """Explain conversion probability reasoning."""
        reasons = []
        
        if not has_website:
            reasons.append("No website = clear need")
        if rating and rating >= 4.0:
            reasons.append("Good rating = quality-focused business")
        if review_count and review_count > 50:
            reasons.append("Many reviews = established with budget")
        if digital_score < 30:
            reasons.append("Low digital score = high improvement potential")
        
        return " | ".join(reasons) if reasons else "Moderate opportunity"
    
    def _identify_success_factors(
        self,
        category: str,
        rating: Optional[float],
        review_count: Optional[int]
    ) -> list:
        """Identify success factors."""
        factors = []
        
        if rating and rating >= 4.0:
            factors.append("✅ Good reputation makes online presence more valuable")
        if review_count and review_count > 50:
            factors.append("✅ Established customer base to leverage")
        
        if category.lower() in ["restaurant", "cafe", "food"]:
            factors.append("✅ High demand for online ordering in food industry")
        elif category.lower() in ["salon", "spa", "gym"]:
            factors.append("✅ Online booking is standard in wellness industry")
        
        return factors
    
    def _recommend_primary_service(
        self,
        has_website: bool,
        digital_score: int,
        category: str
    ) -> Dict:
        """Recommend primary service."""
        if not has_website:
            return {
                "service": "Professional Website Development",
                "description": "Custom website with mobile-responsive design, contact forms, and SEO optimization",
                "priority": "HIGH",
                "impact": "Immediate online presence and credibility"
            }
        elif digital_score < 50:
            return {
                "service": "Website Redesign & Optimization",
                "description": "Modernize existing website with better UX, faster loading, and mobile optimization",
                "priority": "MEDIUM",
                "impact": "Improved user experience and conversion rates"
            }
        else:
            return {
                "service": "Digital Marketing & SEO",
                "description": "Improve search rankings and online visibility",
                "priority": "LOW",
                "impact": "Increased organic traffic"
            }
    
    def _recommend_secondary_services(
        self,
        category: str,
        digital_score: int
    ) -> list:
        """Recommend secondary services."""
        services = []
        
        if category.lower() in ["restaurant", "cafe", "food"]:
            services.extend([
                "Online ordering system integration",
                "Menu management system",
                "Table reservation system"
            ])
        elif category.lower() in ["salon", "spa", "gym"]:
            services.extend([
                "Online booking system",
                "Membership management",
                "Payment gateway integration"
            ])
        elif category.lower() in ["retail", "shop", "store"]:
            services.extend([
                "E-commerce platform",
                "Inventory management",
                "Payment gateway"
            ])
        else:
            services.extend([
                "Contact form with CRM integration",
                "Google My Business optimization",
                "Social media setup"
            ])
        
        return services
    
    def _estimate_pricing(
        self,
        category: str,
        rating: Optional[float],
        review_count: Optional[int]
    ) -> Dict:
        """Estimate pricing based on business size and category."""
        # Determine business size
        if review_count and review_count > 100:
            size = "large"
        elif review_count and review_count > 30:
            size = "medium"
        else:
            size = "small"
        
        # Base pricing by category
        if category.lower() in ["restaurant", "cafe", "food"]:
            base_prices = {
                "small": (15000, 25000),
                "medium": (25000, 40000),
                "large": (40000, 70000)
            }
        elif category.lower() in ["salon", "spa", "gym"]:
            base_prices = {
                "small": (12000, 20000),
                "medium": (20000, 35000),
                "large": (35000, 60000)
            }
        elif category.lower() in ["retail", "shop", "store"]:
            base_prices = {
                "small": (20000, 35000),
                "medium": (35000, 60000),
                "large": (60000, 100000)
            }
        else:
            base_prices = {
                "small": (10000, 18000),
                "medium": (18000, 30000),
                "large": (30000, 50000)
            }
        
        min_price, max_price = base_prices[size]
        
        return {
            "basic_website": f"₹{min_price:,} - ₹{max_price:,}",
            "with_booking_system": f"₹{min_price + 8000:,} - ₹{max_price + 15000:,}",
            "full_package": f"₹{min_price + 15000:,} - ₹{max_price + 30000:,}",
            "monthly_maintenance": "₹2,000 - ₹5,000/month",
            "business_size": size,
            "pricing_factors": [
                f"Business size: {size.capitalize()}",
                f"Category: {category}",
                "Includes: Design, development, hosting setup, basic SEO"
            ]
        }
    
    def _estimate_timeline(self, category: str, has_website: bool) -> str:
        """Estimate project timeline."""
        if not has_website:
            return "2-4 weeks for basic website, 4-8 weeks with advanced features"
        else:
            return "1-2 weeks for redesign, 2-4 weeks for major overhaul"
    
    def _generate_value_pitch(
        self,
        name: str,
        category: str,
        digital_score: int,
        has_website: bool
    ) -> str:
        """Generate value pitch."""
        if not has_website:
            return f"I noticed {name} has a great reputation but no website. In today's digital age, 70% of customers search online before visiting. A professional website could help you capture those customers and grow your business by 30-50%."
        else:
            return f"I noticed {name}'s website could be improved to better serve your customers. With a modern, mobile-friendly design and better SEO, you could increase online inquiries by 40-60%."
    
    def _generate_objection_responses(
        self,
        category: str,
        has_website: bool
    ) -> Dict:
        """Generate objection handling responses."""
        return {
            "too_expensive": "I understand budget is a concern. We can start with a basic package and add features as your business grows. Many clients see ROI within 3-6 months through increased customer inquiries.",
            "dont_need_website": "I respect that. However, 80% of customers now search online before visiting. Even a simple website with your menu/services, hours, and contact info can capture those customers who might otherwise go to competitors.",
            "too_busy": "That's exactly why we handle everything for you. We just need 2-3 hours of your time total - one meeting to understand your needs, and one to review the final website. We handle all the technical work.",
            "already_have_social_media": "Social media is great! A website complements it by giving you a professional home base that you own and control. Plus, it helps with Google search rankings so customers can find you more easily.",
            "not_tech_savvy": "No problem at all! We build everything for you and provide simple training. You'll be able to update basic info yourself, or we can handle updates for a small monthly fee."
        }
    
    def _suggest_contact_time(self, category: str) -> str:
        """Suggest best time to contact based on category."""
        if category.lower() in ["restaurant", "cafe", "food"]:
            return "Best time: 2:30 PM - 4:30 PM (between lunch and dinner rush)"
        elif category.lower() in ["salon", "spa"]:
            return "Best time: 10:00 AM - 12:00 PM or 3:00 PM - 5:00 PM (avoid peak hours)"
        elif category.lower() in ["gym", "fitness"]:
            return "Best time: 10:00 AM - 2:00 PM (between morning and evening rush)"
        elif category.lower() in ["retail", "shop", "store"]:
            return "Best time: 11:00 AM - 1:00 PM or 3:00 PM - 5:00 PM (avoid peak shopping hours)"
        else:
            return "Best time: 10:00 AM - 12:00 PM or 2:00 PM - 4:00 PM (standard business hours)"
    
    def _suggest_approach_style(
        self,
        category: str,
        rating: Optional[float],
        review_count: Optional[int]
    ) -> str:
        """Suggest approach style."""
        if rating and rating >= 4.5:
            return "Consultative - Acknowledge their success, position as growth partner"
        elif rating and rating >= 4.0:
            return "Solution-focused - Show how digital presence solves specific problems"
        else:
            return "Educational - Help them understand digital opportunities"
    
    def _generate_outreach_messages(
        self,
        name: str,
        category: str,
        city: str,
        has_website: bool,
        digital_score: int
    ) -> Dict:
        """Generate personalized outreach messages."""
        # Opening line
        if not has_website:
            opening = f"Hi! I came across {name} and was impressed by your {category} business in {city}. I noticed you don't have a website yet."
        else:
            opening = f"Hi! I'm a web developer specializing in {category} businesses in {city}. I noticed {name}'s online presence could be enhanced."
        
        # WhatsApp message
        whatsapp = f"""{opening}

I help local businesses like yours get more customers through professional websites. Would you be interested in a quick 10-minute call to discuss how a website could help grow your business?

I've worked with several {category} businesses in {city} and typically help them increase customer inquiries by 40-60%.

Let me know if you'd like to chat!"""
        
        # Call script
        call_script = f"""**Opening:**
"Hi, is this {name}? My name is [Your Name], and I'm a web developer who specializes in helping {category} businesses in {city}."

**Hook:**
"I came across your business and was really impressed by [mention specific thing - rating, reviews, location]. I noticed you {'don't have a website yet' if not has_website else 'have a website but it could be modernized'}, and I wanted to reach out because I've helped several {category} businesses increase their customer base by 40-60% with a professional online presence."

**Question:**
"Would you be open to a quick 10-minute conversation about how a website could help you attract more customers?"

**If interested:**
"Great! When would be a good time for you? I'm free [suggest 2-3 time slots]."

**If not interested:**
"I understand you're busy. Can I send you some information via WhatsApp that you can review when you have time?"

**If maybe later:**
"No problem! Can I follow up with you in a couple of weeks? What would be a better time?"
"""
        
        # Follow-up message
        followup = f"""Hi again! I wanted to follow up on my message about creating a website for {name}.

I understand you're busy running your business. I just wanted to share that I'm currently offering a special package for {category} businesses in {city}:

✅ Professional website design
✅ Mobile-friendly
✅ Google Maps integration
✅ Contact form
✅ 1 year free hosting

Starting from ₹15,000 only.

Would you like to see some examples of websites I've built for similar businesses?"""
        
        return {
            "opening_line": opening,
            "whatsapp_message": whatsapp,
            "call_script": call_script,
            "follow_up_message": followup,
            "sms_message": f"Hi! I'm [Name], a web developer. I noticed {name} doesn't have a website. I'd love to help you get more customers online. Can we chat? Reply YES for more info."
        }
    
    def _assess_risks(
        self,
        digital_score: int,
        has_website: bool,
        rating: Optional[float],
        review_count: Optional[int],
        phone: Optional[str]
    ) -> Dict:
        """Assess risks and challenges."""
        risks = []
        challenges = []
        red_flags = []
        
        # Risks
        if not phone:
            risks.append("⚠️ No phone number available - difficult to contact")
            red_flags.append("Missing contact information")
        
        if rating and rating < 3.5:
            risks.append("⚠️ Low rating - may have quality issues or unhappy customers")
            red_flags.append("Low customer satisfaction")
        
        if review_count and review_count < 5:
            risks.append("⚠️ Very few reviews - might be new or struggling business")
            red_flags.append("Limited social proof")
        
        if has_website and digital_score > 70:
            risks.append("⚠️ Already has strong digital presence - may not see value in upgrade")
            red_flags.append("Low perceived need")
        
        # Challenges
        if not has_website:
            challenges.append("May not understand value of website")
            challenges.append("Might have budget constraints")
        
        challenges.append("Need to demonstrate clear ROI")
        challenges.append("Competition from other web developers")
        
        return {
            "risks": risks if risks else ["✅ No major risks identified"],
            "challenges": challenges,
            "red_flags": red_flags if red_flags else ["✅ No red flags"],
            "mitigation_strategies": [
                "Start with free consultation to build trust",
                "Show portfolio of similar businesses",
                "Offer flexible payment plans",
                "Provide clear ROI projections"
            ]
        }
    
    def _generate_with_ai(
        self,
        name: str,
        category: str,
        city: str,
        digital_score: int,
        has_website: bool,
        rating: Optional[float],
        review_count: Optional[int],
        data_source: str,
        phone: Optional[str],
        address: Optional[str],
        place_id: Optional[str]
    ) -> Dict:
        """Generate report using OpenAI ChatGPT API.
        
        This provides higher quality, more personalized insights using GPT-4.
        Cost: ~$0.001 per lead (very affordable).
        """
        if not self.client:
            logger.warning("OpenAI client not available, falling back to template mode")
            return self._generate_with_template(
                name, category, city, digital_score, has_website,
                rating, review_count, data_source, phone, address, place_id
            )
        
        try:
            # Build the prompt for ChatGPT
            prompt = self._build_chatgpt_prompt(
                name, category, city, digital_score, has_website,
                rating, review_count, phone, address
            )
            
            # Call ChatGPT API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cheaper and faster than GPT-4
                messages=[
                    {
                        "role": "system",
                        "content": """You are an AI Business Copilot for freelancers selling digital services.
Your job is to generate COMPLETE, HONEST, and ACTIONABLE business intelligence reports.

CRITICAL RULES:
- DO NOT hallucinate unknown facts
- If data is missing, clearly say "Not available"
- Always separate REAL data vs AI insights
- Be practical, not generic
- Provide specific, actionable recommendations
- Use Indian Rupees (₹) for pricing
- Focus on local Indian market context"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            ai_insights = json.loads(response.choices[0].message.content)
            
            # Merge with template-based structure for consistency
            template_report = self._generate_with_template(
                name, category, city, digital_score, has_website,
                rating, review_count, data_source, phone, address, place_id
            )
            
            # Enhance template with AI insights
            enhanced_report = self._merge_ai_with_template(template_report, ai_insights)
            enhanced_report["generation_method"] = "chatgpt"
            
            logger.info(f"Generated AI report for {name} using ChatGPT")
            return enhanced_report
            
        except Exception as e:
            logger.error(f"Error generating AI report: {str(e)}")
            # Fallback to template mode
            return self._generate_with_template(
                name, category, city, digital_score, has_website,
                rating, review_count, data_source, phone, address, place_id
            )
    
    def _generate_with_ollama(
        self,
        name: str,
        category: str,
        city: str,
        digital_score: int,
        has_website: bool,
        rating: Optional[float],
        review_count: Optional[int],
        data_source: str,
        phone: Optional[str],
        address: Optional[str],
        place_id: Optional[str]
    ) -> Dict:
        """Generate report using Ollama (FREE local AI).
        
        This provides good quality insights using local AI models.
        Cost: $0 (completely free, runs on your machine).
        """
        try:
            # Build the prompt
            prompt = self._build_chatgpt_prompt(
                name, category, city, digital_score, has_website,
                rating, review_count, phone, address
            )
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "deepseek-v3.1:671b-cloud",  # Using your installed model
                    "prompt": f"""You are an AI Business Copilot for freelancers selling digital services.

{prompt}

Return ONLY valid JSON, no markdown formatting.""",
                    "stream": False,
                    "format": "json"
                },
                timeout=60  # Increased timeout for larger model
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "{}")
                
                try:
                    ai_insights = json.loads(ai_response)
                except json.JSONDecodeError:
                    logger.warning("Ollama returned invalid JSON, using template mode")
                    return self._generate_with_template(
                        name, category, city, digital_score, has_website,
                        rating, review_count, data_source, phone, address, place_id
                    )
                
                # Merge with template-based structure
                template_report = self._generate_with_template(
                    name, category, city, digital_score, has_website,
                    rating, review_count, data_source, phone, address, place_id
                )
                
                # Enhance template with AI insights
                enhanced_report = self._merge_ai_with_template(template_report, ai_insights)
                enhanced_report["generation_method"] = "ollama"
                
                logger.info(f"Generated AI report for {name} using Ollama")
                return enhanced_report
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._generate_with_template(
                    name, category, city, digital_score, has_website,
                    rating, review_count, data_source, phone, address, place_id
                )
                
        except Exception as e:
            logger.error(f"Error generating Ollama report: {str(e)}")
            # Fallback to template mode
            return self._generate_with_template(
                name, category, city, digital_score, has_website,
                rating, review_count, data_source, phone, address, place_id
            )
    
    def _build_chatgpt_prompt(
        self,
        name: str,
        category: str,
        city: str,
        digital_score: int,
        has_website: bool,
        rating: Optional[float],
        review_count: Optional[int],
        phone: Optional[str],
        address: Optional[str]
    ) -> str:
        """Build the prompt for ChatGPT."""
        return f"""Generate a business intelligence report for a freelancer targeting this business:

**REAL DATA (Verified from Google Places):**
- Business Name: {name}
- Category: {category}
- Location: {city}
- Digital Score: {digital_score}/100 (calculated)
- Website: {"Yes" if has_website else "No"}
- Rating: {rating if rating else "Not available"}
- Reviews: {review_count if review_count else "Not available"}
- Phone: {phone if phone else "Not available"}
- Address: {address if address else "Not available"}

**Your Task:**
Generate a JSON response with these sections:

1. **opportunity_insights**: 
   - Why this is a good/bad opportunity
   - Specific missed revenue estimate (in ₹)
   - Growth potential reasoning
   - Market position analysis

2. **sales_strategy**:
   - Personalized opening line (mention specific details about the business)
   - Value pitch (why they need a website/digital upgrade)
   - Best approach style for this type of business
   - Specific objection responses

3. **outreach_messages**:
   - WhatsApp message (conversational, friendly, 3-4 sentences)
   - Call script opening (natural, not salesy)
   - Follow-up message (if no response)
   - SMS message (under 160 characters)

4. **pricing_strategy**:
   - Recommended pricing range for basic website (₹X - ₹Y)
   - Justification for pricing based on business size
   - Upsell opportunities
   - Payment terms suggestion

5. **success_factors**:
   - Top 3 factors that will help close this deal
   - Top 3 risks or challenges
   - Mitigation strategies

6. **timeline_recommendation**:
   - Best time to contact (specific hours)
   - Project timeline estimate
   - Follow-up schedule

**IMPORTANT:**
- Be specific to {category} businesses in {city}
- Use Indian market context and pricing
- If data is missing, say "Not available" - don't make it up
- Be honest about challenges
- Provide actionable, practical advice

Return ONLY valid JSON, no markdown formatting."""
    
    def _merge_ai_with_template(self, template: Dict, ai_insights: Dict) -> Dict:
        """Merge AI-generated insights with template structure."""
        # Keep the template structure but enhance with AI insights
        enhanced = template.copy()
        
        # Enhance opportunity analysis
        if "opportunity_insights" in ai_insights:
            enhanced["opportunity_analysis"]["ai_insights"] = ai_insights["opportunity_insights"]
        
        # Enhance sales strategy
        if "sales_strategy" in ai_insights:
            if "opening_line" in ai_insights["sales_strategy"]:
                enhanced["sales_strategy"]["opening_line"] = ai_insights["sales_strategy"]["opening_line"]
            if "value_pitch" in ai_insights["sales_strategy"]:
                enhanced["sales_strategy"]["value_pitch"] = ai_insights["sales_strategy"]["value_pitch"]
        
        # Enhance outreach messages
        if "outreach_messages" in ai_insights:
            for key, value in ai_insights["outreach_messages"].items():
                if key in enhanced["outreach_messages"]:
                    enhanced["outreach_messages"][key] = value
        
        # Enhance pricing if provided
        if "pricing_strategy" in ai_insights:
            enhanced["recommended_services"]["ai_pricing_insights"] = ai_insights["pricing_strategy"]
        
        # Add AI-specific insights
        if "success_factors" in ai_insights:
            enhanced["ai_success_factors"] = ai_insights["success_factors"]
        
        if "timeline_recommendation" in ai_insights:
            enhanced["ai_timeline_recommendation"] = ai_insights["timeline_recommendation"]
        
        return enhanced
    
    def _generate_fallback_report(
        self,
        name: str,
        category: str,
        city: str
    ) -> Dict:
        """Generate minimal fallback report if everything fails."""
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "generation_method": "fallback",
            "error": "Failed to generate full report",
            "business_summary": {
                "name": name,
                "category": category,
                "location": city,
                "message": "Limited data available. Please try again later."
            }
        }
