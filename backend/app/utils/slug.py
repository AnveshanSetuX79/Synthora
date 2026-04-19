"""Slug generation utilities for SEO-friendly URLs."""
import re
from typing import Optional


def generate_slug(text: str, max_length: int = 100) -> str:
    """Generate SEO-friendly slug from text.
    
    Args:
        text: Input text to convert to slug
        max_length: Maximum length of slug
        
    Returns:
        URL-safe slug
        
    Example:
        >>> generate_slug("Bo Tai Restaurant")
        'bo-tai-restaurant'
        >>> generate_slug("Café & Bistro!")
        'cafe-bistro'
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Remove special characters and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Truncate to max length
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit('-', 1)[0]
    
    return slug or 'business'


def generate_demo_slug(business_name: str, city: str, category: str) -> str:
    """Generate complete demo URL slug.
    
    Args:
        business_name: Name of the business
        city: City name
        category: Business category
        
    Returns:
        Complete slug for demo URL
        
    Example:
        >>> generate_demo_slug("Bo Tai", "Bangalore", "Restaurant")
        'bangalore-restaurant-bo-tai'
    """
    city_slug = generate_slug(city, max_length=30)
    category_slug = generate_slug(category, max_length=30)
    name_slug = generate_slug(business_name, max_length=50)
    
    return f"{city_slug}-{category_slug}-{name_slug}"


def parse_demo_slug(slug: str) -> Optional[dict]:
    """Parse demo slug into components.
    
    Args:
        slug: Demo URL slug
        
    Returns:
        Dictionary with city, category, and name components or None
        
    Example:
        >>> parse_demo_slug("bangalore-restaurant-bo-tai")
        {'city': 'bangalore', 'category': 'restaurant', 'name': 'bo-tai'}
    """
    parts = slug.split('-', 2)
    if len(parts) >= 3:
        return {
            'city': parts[0],
            'category': parts[1],
            'name': parts[2]
        }
    return None
