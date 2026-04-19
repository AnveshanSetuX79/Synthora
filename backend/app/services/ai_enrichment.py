"""AI-powered business enrichment service.

This service uses AI to gather additional business intelligence beyond
what's available from Google Places API, including:
- Business description and specialties
- Target customer demographics
- Competitive analysis
- Digital presence assessment
- Growth potential indicators
- Recommended services/solutions
"""
import logging
import json
from typing import Dict, Optional, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class AIEnrichmentService:
    """Service for AI-powered business data enrichment."""
    
    def __init__(self):
        """Initialize AI enrichment service."""
        self.enabled = os.getenv("AI_ENRICHMENT_ENABLED", "false").lower() == "true"
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        
    def enrich_business_data(
        self,
        business_name: str,
        category: str,
        address: str,
        city: str,
        rating: Optional[float] = None,
        review_count: Optional[int] = None,
        has_website: bool = False,
        website_url: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict:
        """Enrich business data with AI-generated insights.
        
        Args:
            business_name: Name of the business
            category: Business category (restaurant, school, etc.)
            address: Full address
            city: City name
            rating: Google rating (0-5)
            review_count: Number of reviews
            has_website: Whether business has a website
            website_url: Website URL if available
            phone: Phone number if available
            
        Returns:
            Dictionary with enriched data:
            {
                "business_description": str,
                "specialties": List[str],
                "target_customers": List[str],
                "digital_maturity": str,  # "low", "medium", "high"
                "growth_potential": str,  # "low", "medium", "high"
                "pain_points": List[str],
                "recommended_solutions": List[str],
                "competitive_advantages": List[str],
                "estimated_size": str,  # "small", "medium", "large"
                "online_presence_score": int,  # 0-100
                "urgency_score": int,  # 0-100 (how urgently they need help)
                "enrichment_confidence": float  # 0-1
            }
        """
        if not self.enabled:
            return self._get_fallback_enrichment(
                business_name, category, has_website, rating, review_count
            )
        
        try:
            # Build context for AI
            context = self._build_context(
                business_name, category, address, city,
                rating, review_count, has_website, website_url, phone
            )
            
            # Generate AI insights
            insights = self._generate_ai_insights(context)
            
            return insights
            
        except Exception as e:
            logger.error(f"AI enrichment failed: {str(e)}")
            return self._get_fallback_enrichment(
                business_name, category, has_website, rating, review_count
            )
    
    def _build_context(
        self,
        business_name: str,
        category: str,
        address: str,
        city: str,
        rating: Optional[float],
        review_count: Optional[int],
        has_website: bool,
        website_url: Optional[str],
        phone: Optional[str]
    ) -> str:
        """Build context string for AI analysis."""
        context_parts = [
            f"Business Name: {business_name}",
            f"Category: {category}",
            f"Location: {address}, {city}",
        ]
        
        if rating is not None:
            context_parts.append(f"Google Rating: {rating}/5")
        if review_count is not None:
            context_parts.append(f"Review Count: {review_count}")
        
        context_parts.append(f"Has Website: {'Yes' if has_website else 'No'}")
        if website_url:
            context_parts.append(f"Website: {website_url}")
        if phone:
            context_parts.append(f"Phone: {phone}")
        
        return "\n".join(context_parts)
    
    def _generate_ai_insights(self, context: str) -> Dict:
        """Generate AI insights using OpenAI API.
        
        Note: This is a placeholder. In production, you would:
        1. Call OpenAI API with the context
        2. Use a structured prompt to get consistent JSON output
        3. Parse and validate the response
        """
        # TODO: Implement actual OpenAI API call
        # For now, return intelligent fallback based on context analysis
        
        # Parse context to extract key info
        has_website = "Has Website: Yes" in context
        rating_line = [l for l in context.split("\n") if "Google Rating:" in l]
        rating = float(rating_line[0].split(": ")[1].split("/")[0]) if rating_line else 0
        
        category_line = [l for l in context.split("\n") if "Category:" in l]
        category = category_line[0].split(": ")[1].lower() if category_line else "business"
        
        return self._generate_rule_based_insights(category, has_website, rating)
    
    def _generate_rule_based_insights(
        self,
        category: str,
        has_website: bool,
        rating: float
    ) -> Dict:
        """Generate insights using rule-based logic (fallback for AI)."""
        
        # Category-specific insights
        category_insights = {
            "restaurant": {
                "specialties": ["Menu digitization", "Online ordering", "Table reservations"],
                "target_customers": ["Local diners", "Food delivery users", "Event organizers"],
                "pain_points": ["Limited online visibility", "Manual order management", "No online menu"],
                "recommended_solutions": [
                    "Professional website with online menu",
                    "Online ordering system integration",
                    "Google My Business optimization",
                    "Social media marketing setup"
                ]
            },
            "school": {
                "specialties": ["Student enrollment", "Parent communication", "Online learning"],
                "target_customers": ["Parents", "Students", "Educational institutions"],
                "pain_points": ["Manual admission process", "Limited parent engagement", "No online presence"],
                "recommended_solutions": [
                    "School website with admission portal",
                    "Parent-teacher communication app",
                    "Online fee payment system",
                    "Virtual tour and gallery"
                ]
            },
            "healthcare": {
                "specialties": ["Patient appointments", "Medical records", "Telemedicine"],
                "target_customers": ["Patients", "Healthcare seekers", "Insurance providers"],
                "pain_points": ["Manual appointment booking", "No online consultation", "Limited reach"],
                "recommended_solutions": [
                    "Online appointment booking system",
                    "Patient portal for records",
                    "Telemedicine integration",
                    "Health blog and resources"
                ]
            },
            "retail": {
                "specialties": ["E-commerce", "Inventory management", "Customer loyalty"],
                "target_customers": ["Local shoppers", "Online buyers", "Wholesale clients"],
                "pain_points": ["No online store", "Limited customer reach", "Manual inventory"],
                "recommended_solutions": [
                    "E-commerce website",
                    "Online catalog and ordering",
                    "Customer loyalty program",
                    "Social media shop integration"
                ]
            }
        }
        
        # Get category-specific data or use default
        cat_data = category_insights.get(
            category,
            {
                "specialties": ["Digital presence", "Online marketing", "Customer engagement"],
                "target_customers": ["Local customers", "Online users", "Business clients"],
                "pain_points": ["Limited online visibility", "No digital presence", "Manual processes"],
                "recommended_solutions": [
                    "Professional business website",
                    "Google My Business optimization",
                    "Social media presence",
                    "Online customer engagement"
                ]
            }
        )
        
        # Assess digital maturity
        if has_website and rating >= 4.0:
            digital_maturity = "medium"
            online_presence_score = 60
        elif has_website:
            digital_maturity = "low"
            online_presence_score = 40
        else:
            digital_maturity = "low"
            online_presence_score = 20
        
        # Assess growth potential
        if not has_website and rating >= 3.5:
            growth_potential = "high"
            urgency_score = 85
        elif not has_website:
            growth_potential = "medium"
            urgency_score = 70
        else:
            growth_potential = "medium"
            urgency_score = 50
        
        # Estimate business size based on rating and reviews
        if rating >= 4.0:
            estimated_size = "medium"
        elif rating >= 3.0:
            estimated_size = "small"
        else:
            estimated_size = "small"
        
        # Competitive advantages
        competitive_advantages = []
        if rating >= 4.0:
            competitive_advantages.append("Strong customer satisfaction")
        if not has_website:
            competitive_advantages.append("Untapped online market potential")
        competitive_advantages.append(f"Established {category} business")
        
        # Business description
        business_description = self._generate_description(category, has_website, rating)
        
        return {
            "business_description": business_description,
            "specialties": cat_data["specialties"],
            "target_customers": cat_data["target_customers"],
            "digital_maturity": digital_maturity,
            "growth_potential": growth_potential,
            "pain_points": cat_data["pain_points"],
            "recommended_solutions": cat_data["recommended_solutions"],
            "competitive_advantages": competitive_advantages,
            "estimated_size": estimated_size,
            "online_presence_score": online_presence_score,
            "urgency_score": urgency_score,
            "enrichment_confidence": 0.75,  # Rule-based has medium confidence
            "enriched_at": datetime.utcnow().isoformat()
        }
    
    def _generate_description(self, category: str, has_website: bool, rating: float) -> str:
        """Generate business description."""
        descriptions = {
            "restaurant": f"A {'well-rated' if rating >= 4.0 else 'local'} restaurant serving customers in the area. "
                         f"{'Currently lacks online presence' if not has_website else 'Has basic online presence'} "
                         f"with potential for digital growth through online ordering and menu digitization.",
            
            "school": f"An educational institution providing quality education. "
                     f"{'Needs digital transformation' if not has_website else 'Has basic web presence'} "
                     f"to improve parent engagement and streamline admissions.",
            
            "healthcare": f"A healthcare provider serving the local community. "
                         f"{'Could benefit from online appointment system' if not has_website else 'Has online presence'} "
                         f"and telemedicine capabilities.",
            
            "retail": f"A retail business serving local customers. "
                     f"{'Missing e-commerce opportunity' if not has_website else 'Has online presence'} "
                     f"with potential for online sales growth."
        }
        
        return descriptions.get(
            category,
            f"A local {category} business with {'strong' if rating >= 4.0 else 'growing'} customer base. "
            f"{'Needs digital presence' if not has_website else 'Has basic online presence'} "
            f"to expand reach and improve customer engagement."
        )
    
    def _get_fallback_enrichment(
        self,
        business_name: str,
        category: str,
        has_website: bool,
        rating: Optional[float],
        review_count: Optional[int]
    ) -> Dict:
        """Get fallback enrichment when AI is disabled."""
        rating = rating or 0
        return self._generate_rule_based_insights(category, has_website, rating)
    
    def get_pitch_suggestions(self, enrichment_data: Dict) -> List[str]:
        """Generate pitch suggestions based on enrichment data.
        
        Args:
            enrichment_data: Enriched business data
            
        Returns:
            List of pitch suggestions for freelancers
        """
        suggestions = []
        
        # Based on digital maturity
        if enrichment_data.get("digital_maturity") == "low":
            suggestions.append(
                "Highlight how a professional website can increase their customer reach by 300%"
            )
        
        # Based on urgency
        if enrichment_data.get("urgency_score", 0) > 70:
            suggestions.append(
                "Emphasize the competitive advantage of going online before competitors"
            )
        
        # Based on pain points
        pain_points = enrichment_data.get("pain_points", [])
        if pain_points:
            suggestions.append(
                f"Address their key challenge: {pain_points[0].lower()}"
            )
        
        # Based on growth potential
        if enrichment_data.get("growth_potential") == "high":
            suggestions.append(
                "Show case studies of similar businesses that grew 5x after digital transformation"
            )
        
        return suggestions


# Singleton instance
ai_enrichment_service = AIEnrichmentService()
