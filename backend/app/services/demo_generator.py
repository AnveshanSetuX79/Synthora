"""Demo website generation service.

This service handles:
- Template-based demo website generation
- Business data injection into templates
- Demo caching for instant retrieval
- SEO metadata generation

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
"""
import logging
import json
from typing import Dict, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class DemoGeneratorError(Exception):
    """Base exception for demo generation errors."""
    pass


class TemplateNotFoundError(DemoGeneratorError):
    """Raised when template file is not found."""
    pass


class DemoGeneratorService:
    """Service for generating template-based demo websites."""
    
    # Template directory
    TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
    
    # Category to template mapping
    CATEGORY_TEMPLATES = {
        "restaurant": "restaurant.html",
        "cafe": "restaurant.html",  # Use restaurant template
        "school": "school.html",
        "gym": "school.html",  # Use school template for now
        "salon": "school.html",  # Use school template for now
    }
    
    def __init__(self):
        """Initialize demo generator with Jinja2 environment."""
        try:
            self.env = Environment(
                loader=FileSystemLoader(str(self.TEMPLATE_DIR)),
                autoescape=True
            )
            logger.info(f"Initialized demo generator with template dir: {self.TEMPLATE_DIR}")
        except Exception as e:
            logger.error(f"Failed to initialize demo generator: {str(e)}")
            raise DemoGeneratorError(f"Failed to initialize template engine: {str(e)}")
    
    def generate_demo(
        self,
        business_name: str,
        category: str,
        address: str,
        city: str,
        phone: Optional[str] = None,
        rating: Optional[float] = None,
        review_count: int = 0,
        description: Optional[str] = None
    ) -> str:
        """Generate demo website HTML for a business.
        
        Args:
            business_name: Name of the business
            category: Business category (restaurant, school, etc.)
            address: Full address
            city: City name
            phone: Phone number (optional)
            rating: Google rating (optional)
            review_count: Number of reviews
            description: Business description (optional)
            
        Returns:
            Generated HTML as string
            
        Raises:
            TemplateNotFoundError: If template for category not found
            DemoGeneratorError: For other generation errors
        """
        try:
            # Get template for category
            template_name = self._get_template_for_category(category)
            
            # Load template
            try:
                template = self.env.get_template(template_name)
            except TemplateNotFound:
                raise TemplateNotFoundError(
                    f"Template '{template_name}' not found for category '{category}'"
                )
            
            # Prepare template context
            context = self._prepare_context(
                business_name=business_name,
                category=category,
                address=address,
                city=city,
                phone=phone,
                rating=rating,
                review_count=review_count,
                description=description
            )
            
            # Render template
            html = template.render(**context)
            
            logger.info(f"Generated demo for {business_name} ({category})")
            return html
            
        except TemplateNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating demo for {business_name}: {str(e)}")
            raise DemoGeneratorError(f"Failed to generate demo: {str(e)}")
    
    def _get_template_for_category(self, category: str) -> str:
        """Get template filename for business category.
        
        Args:
            category: Business category
            
        Returns:
            Template filename
        """
        category_lower = category.lower().strip()
        return self.CATEGORY_TEMPLATES.get(category_lower, "restaurant.html")
    
    def _prepare_context(
        self,
        business_name: str,
        category: str,
        address: str,
        city: str,
        phone: Optional[str],
        rating: Optional[float],
        review_count: int,
        description: Optional[str]
    ) -> Dict:
        """Prepare template context with business data.
        
        Args:
            business_name: Name of the business
            category: Business category
            address: Full address
            city: City name
            phone: Phone number
            rating: Google rating
            review_count: Number of reviews
            description: Business description
            
        Returns:
            Dictionary of template variables
        """
        # Generate default description if not provided
        if not description:
            description = self._generate_default_description(business_name, category, city)
        
        # Format phone number
        formatted_phone = self._format_phone(phone) if phone else "Contact us for details"
        
        # Generate category-specific content
        category_content = self._generate_category_content(category, business_name)
        
        # Generate SEO meta tags
        meta_tags = self._generate_meta_tags(business_name, category, city, description)
        
        # Generate structured data
        structured_data = self._generate_structured_data(
            business_name, category, address, city, phone, rating, review_count
        )
        
        context = {
            "business_name": business_name,
            "category": category.title(),
            "address": address,
            "city": city,
            "phone": formatted_phone,
            "phone_raw": phone or "",
            "rating": rating or 0.0,
            "review_count": review_count,
            "description": description,
            "year": datetime.now().year,
            "meta_tags": meta_tags,
            "structured_data": structured_data,
            **category_content
        }
        
        return context
    
    def _generate_default_description(
        self,
        business_name: str,
        category: str,
        city: str
    ) -> str:
        """Generate default description for business.
        
        Args:
            business_name: Name of the business
            category: Business category
            city: City name
            
        Returns:
            Default description string
        """
        category_descriptions = {
            "restaurant": f"Welcome to {business_name}, your favorite {category} in {city}. "
                         f"Experience delicious food and great service.",
            "cafe": f"Welcome to {business_name}, a cozy cafe in {city}. "
                   f"Enjoy our coffee, snacks, and warm atmosphere.",
            "school": f"Welcome to {business_name}, a leading educational institution in {city}. "
                     f"Providing quality education and nurturing young minds.",
            "gym": f"Welcome to {business_name}, your fitness destination in {city}. "
                  f"Achieve your fitness goals with our expert trainers.",
            "salon": f"Welcome to {business_name}, a premium salon in {city}. "
                    f"Experience professional beauty and grooming services."
        }
        
        return category_descriptions.get(
            category.lower(),
            f"Welcome to {business_name} in {city}. We provide excellent service and quality."
        )
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number for display.
        
        Args:
            phone: Raw phone number
            
        Returns:
            Formatted phone number
        """
        # Remove non-numeric characters
        digits = ''.join(filter(str.isdigit, phone))
        
        # Format Indian phone numbers (10 digits)
        if len(digits) == 10:
            return f"+91 {digits[:5]} {digits[5:]}"
        elif len(digits) == 11 and digits[0] == '0':
            return f"+91 {digits[1:6]} {digits[6:]}"
        
        # Return original if format unknown
        return phone
    
    def _generate_category_content(self, category: str, business_name: str) -> Dict:
        """Generate category-specific content for templates.
        
        Args:
            category: Business category
            business_name: Name of the business
            
        Returns:
            Dictionary of category-specific variables
        """
        category_lower = category.lower()
        
        if category_lower in ["restaurant", "cafe"]:
            return {
                "menu_items": [
                    {"name": "Signature Dish", "description": "Our chef's special creation", "price": "₹299"},
                    {"name": "Popular Choice", "description": "Customer favorite", "price": "₹249"},
                    {"name": "Daily Special", "description": "Fresh and delicious", "price": "₹199"},
                    {"name": "Dessert", "description": "Sweet ending to your meal", "price": "₹149"},
                ],
                "features": [
                    "Fresh Ingredients",
                    "Expert Chefs",
                    "Cozy Ambiance",
                    "Quick Service"
                ]
            }
        elif category_lower == "school":
            return {
                "programs": [
                    {"name": "Primary Education", "description": "Foundation for lifelong learning", "age": "6-10 years"},
                    {"name": "Secondary Education", "description": "Building knowledge and skills", "age": "11-15 years"},
                    {"name": "Higher Secondary", "description": "Preparing for the future", "age": "16-18 years"},
                ],
                "features": [
                    "Experienced Faculty",
                    "Modern Facilities",
                    "Holistic Development",
                    "Safe Environment"
                ]
            }
        else:
            return {
                "services": [
                    {"name": "Service 1", "description": "Professional service"},
                    {"name": "Service 2", "description": "Quality service"},
                    {"name": "Service 3", "description": "Expert service"},
                ],
                "features": [
                    "Professional Staff",
                    "Quality Service",
                    "Customer Satisfaction",
                    "Affordable Pricing"
                ]
            }

    
    def _generate_meta_tags(
        self,
        business_name: str,
        category: str,
        city: str,
        description: str
    ) -> Dict:
        """Generate SEO meta tags.
        
        Args:
            business_name: Name of the business
            category: Business category
            city: City name
            description: Business description
            
        Returns:
            Dictionary of meta tag values
        """
        title = f"{business_name} - {category.title()} in {city}"
        og_title = f"{business_name} | Best {category.title()} in {city}"
        
        return {
            "title": title,
            "description": description[:160],  # Limit to 160 chars
            "keywords": f"{business_name}, {category}, {city}, {category} in {city}, best {category}",
            "og_title": og_title,
            "og_description": description[:200],
            "og_type": "business.business",
            "og_site_name": "LocalAI Leads",
            "twitter_card": "summary_large_image",
            "twitter_title": og_title,
            "twitter_description": description[:200]
        }
    
    def _generate_structured_data(
        self,
        business_name: str,
        category: str,
        address: str,
        city: str,
        phone: Optional[str],
        rating: Optional[float],
        review_count: int
    ) -> str:
        """Generate Schema.org structured data (JSON-LD).
        
        Args:
            business_name: Name of the business
            category: Business category
            address: Full address
            city: City name
            phone: Phone number
            rating: Google rating
            review_count: Number of reviews
            
        Returns:
            JSON-LD structured data as string
        """
        # Determine schema type based on category
        category_lower = category.lower()
        if category_lower in ["restaurant", "cafe"]:
            schema_type = "Restaurant"
        elif category_lower == "school":
            schema_type = "EducationalOrganization"
        else:
            schema_type = "LocalBusiness"
        
        schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": business_name,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": address,
                "addressLocality": city,
                "addressCountry": "IN"
            }
        }
        
        # Add phone if available
        if phone:
            schema["telephone"] = phone
        
        # Add rating if available
        if rating and rating > 0:
            schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(rating),
                "bestRating": "5",
                "reviewCount": str(review_count)
            }
        
        # Add category-specific fields
        if category_lower in ["restaurant", "cafe"]:
            schema["servesCuisine"] = "Multi-Cuisine"
            schema["priceRange"] = "$$"
        
        return json.dumps(schema, indent=2)
