"""Google Places API integration service.

This service handles:
- Business search by category and location
- Business data extraction (name, address, phone, rating, reviews, website)
- API rate limiting and error handling
- Response parsing and validation

Requirements: 2.1, 2.2, 2.3
"""
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class BusinessData:
    """Structured business data from Google Places API."""
    place_id: str
    name: str
    address: str
    city: str
    phone: Optional[str]
    rating: Optional[float]
    review_count: int
    category: str
    has_website: bool
    website_url: Optional[str]
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class GooglePlacesAPIError(Exception):
    """Base exception for Google Places API errors."""
    pass


class RateLimitError(GooglePlacesAPIError):
    """Raised when API rate limit is exceeded."""
    pass


class GooglePlacesService:
    """Service class for Google Places API integration.
    
    Handles business discovery, data extraction, and error management.
    Implements exponential backoff for rate limiting and retries.
    """
    
    BASE_URL = "https://maps.googleapis.com/maps/api/place"
    
    # Rate limiting configuration
    MAX_REQUESTS_PER_DAY = 1000  # MVP limit
    RETRY_ATTEMPTS = 3
    RETRY_BACKOFF_FACTOR = 2  # Exponential: 1s, 2s, 4s
    
    def __init__(self, api_key: str):
        """Initialize Google Places service.
        
        Args:
            api_key: Google Places API key
        """
        if not api_key:
            raise ValueError("Google Places API key is required")
        
        self.api_key = api_key
        self._request_count = 0
        self._last_reset = time.time()
        
        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.RETRY_ATTEMPTS,
            backoff_factor=self.RETRY_BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def _check_rate_limit(self) -> None:
        """Check if rate limit is exceeded.
        
        Raises:
            RateLimitError: If daily request limit is exceeded
        """
        # Reset counter if 24 hours have passed
        current_time = time.time()
        if current_time - self._last_reset > 86400:  # 24 hours
            self._request_count = 0
            self._last_reset = current_time
        
        if self._request_count >= self.MAX_REQUESTS_PER_DAY:
            raise RateLimitError(
                f"Daily API request limit ({self.MAX_REQUESTS_PER_DAY}) exceeded. "
                "Limit will reset in 24 hours."
            )
    
    def _increment_request_count(self) -> None:
        """Increment the API request counter."""
        self._request_count += 1
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make API request with error handling.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            RateLimitError: If rate limit is exceeded
            GooglePlacesAPIError: For other API errors
        """
        self._check_rate_limit()
        
        url = f"{self.BASE_URL}/{endpoint}"
        params["key"] = self.api_key
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            self._increment_request_count()
            
            # Handle rate limiting
            if response.status_code == 429:
                raise RateLimitError("API rate limit exceeded")
            
            response.raise_for_status()
            data = response.json()
            
            # Check API-specific status
            status = data.get("status")
            if status == "OVER_QUERY_LIMIT":
                raise RateLimitError("Google Places API quota exceeded")
            elif status == "REQUEST_DENIED":
                raise GooglePlacesAPIError(f"API request denied: {data.get('error_message', 'Unknown error')}")
            elif status == "INVALID_REQUEST":
                raise GooglePlacesAPIError(f"Invalid request: {data.get('error_message', 'Unknown error')}")
            elif status not in ["OK", "ZERO_RESULTS"]:
                raise GooglePlacesAPIError(f"API error: {status}")
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {endpoint}")
            raise GooglePlacesAPIError("Request timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {endpoint}: {str(e)}")
            raise GooglePlacesAPIError(f"Request failed: {str(e)}")
    
    def search_businesses(
        self,
        location: str,
        category: str,
        radius: int = 5000
    ) -> List[BusinessData]:
        """Search for businesses by category and location.
        
        Args:
            location: City name or coordinates (e.g., "Pune" or "18.5204,73.8567")
            category: Business category (e.g., "restaurant", "school")
            radius: Search radius in meters (default: 5000m = 5km)
            
        Returns:
            List of BusinessData objects
            
        Raises:
            RateLimitError: If rate limit is exceeded
            GooglePlacesAPIError: For other API errors
        """
        logger.info(f"Searching businesses: location={location}, category={category}")
        
        # First, geocode the location if it's a city name
        if not self._is_coordinates(location):
            location = self._geocode_location(location)
        
        # Search for places
        params = {
            "location": location,
            "radius": radius,
            "type": self._map_category_to_type(category),
            "keyword": category
        }
        
        try:
            data = self._make_request("nearbysearch/json", params)
            results = data.get("results", [])
            
            businesses = []
            for result in results:
                try:
                    business = self._parse_place_result(result, category)
                    if business:
                        businesses.append(business)
                except Exception as e:
                    logger.warning(f"Failed to parse place {result.get('place_id')}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(businesses)} businesses")
            return businesses
            
        except GooglePlacesAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in search_businesses: {str(e)}")
            raise GooglePlacesAPIError(f"Search failed: {str(e)}")
    
    def get_business_details(self, place_id: str) -> Optional[BusinessData]:
        """Get detailed information for a specific business.
        
        Args:
            place_id: Google Places place_id
            
        Returns:
            BusinessData object or None if not found
            
        Raises:
            RateLimitError: If rate limit is exceeded
            GooglePlacesAPIError: For other API errors
        """
        logger.info(f"Fetching business details: place_id={place_id}")
        
        params = {
            "place_id": place_id,
            "fields": "place_id,name,formatted_address,formatted_phone_number,rating,user_ratings_total,website,types,address_components"
        }
        
        try:
            data = self._make_request("details/json", params)
            result = data.get("result")
            
            if not result:
                logger.warning(f"No details found for place_id={place_id}")
                return None
            
            # Extract category from types
            category = self._extract_category(result.get("types", []))
            
            return self._parse_place_details(result, category)
            
        except GooglePlacesAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_business_details: {str(e)}")
            raise GooglePlacesAPIError(f"Failed to get business details: {str(e)}")
    
    def refresh_business_data(self, place_id: str) -> Optional[BusinessData]:
        """Refresh business data from Google Places API.
        
        This is an alias for get_business_details, used for 7-day refresh cycle.
        
        Args:
            place_id: Google Places place_id
            
        Returns:
            Updated BusinessData object or None if not found
        """
        return self.get_business_details(place_id)
    
    def _is_coordinates(self, location: str) -> bool:
        """Check if location string is coordinates (lat,lng)."""
        parts = location.split(",")
        if len(parts) != 2:
            return False
        try:
            float(parts[0])
            float(parts[1])
            return True
        except ValueError:
            return False
    
    def _geocode_location(self, city: str) -> str:
        """Convert city name to coordinates using Geocoding API.
        
        Args:
            city: City name (e.g., "Pune")
            
        Returns:
            Coordinates as "lat,lng" string
            
        Raises:
            GooglePlacesAPIError: If geocoding fails
        """
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": city,
            "key": self.api_key
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            self._increment_request_count()
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") != "OK" or not data.get("results"):
                raise GooglePlacesAPIError(f"Failed to geocode location: {city}")
            
            location = data["results"][0]["geometry"]["location"]
            return f"{location['lat']},{location['lng']}"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Geocoding failed for {city}: {str(e)}")
            raise GooglePlacesAPIError(f"Geocoding failed: {str(e)}")
    
    def _map_category_to_type(self, category: str) -> str:
        """Map business category to Google Places type.
        
        Args:
            category: Business category (e.g., "Restaurant", "School")
            
        Returns:
            Google Places type string
        """
        category_mapping = {
            "restaurant": "restaurant",
            "school": "school",
            "cafe": "cafe",
            "bar": "bar",
            "gym": "gym",
            "salon": "beauty_salon",
            "spa": "spa"
        }
        return category_mapping.get(category.lower(), category.lower())
    
    def _extract_category(self, types: List[str]) -> str:
        """Extract primary business category from Google Places types.
        
        Args:
            types: List of Google Places types
            
        Returns:
            Primary category string
        """
        # Priority order for category extraction
        priority_types = [
            "restaurant", "school", "cafe", "bar", "gym", 
            "beauty_salon", "spa", "store", "shopping_mall"
        ]
        
        for ptype in priority_types:
            if ptype in types:
                return ptype.replace("_", " ").title()
        
        # Fallback to first non-generic type
        generic_types = {"establishment", "point_of_interest"}
        for t in types:
            if t not in generic_types:
                return t.replace("_", " ").title()
        
        return "Business"
    
    def _parse_place_result(self, result: Dict, category: str) -> Optional[BusinessData]:
        """Parse place search result into BusinessData.
        
        Args:
            result: Place result from API
            category: Business category
            
        Returns:
            BusinessData object or None if parsing fails
        """
        place_id = result.get("place_id")
        if not place_id:
            return None
        
        name = result.get("name", "")
        address = result.get("vicinity", "")
        
        # Extract city from address (simplified)
        city = self._extract_city_from_address(address)
        
        # Extract coordinates
        geometry = result.get("geometry", {})
        location = geometry.get("location", {})
        latitude = location.get("lat")
        longitude = location.get("lng")
        
        return BusinessData(
            place_id=place_id,
            name=name,
            address=address,
            city=city,
            phone=None,  # Not available in search results
            rating=result.get("rating"),
            review_count=result.get("user_ratings_total", 0),
            category=category,
            has_website=False,  # Need details API for this
            website_url=None,
            latitude=latitude,
            longitude=longitude
        )
    
    def _parse_place_details(self, result: Dict, category: str) -> BusinessData:
        """Parse place details result into BusinessData.
        
        Args:
            result: Place details result from API
            category: Business category
            
        Returns:
            BusinessData object
        """
        place_id = result.get("place_id", "")
        name = result.get("name", "")
        address = result.get("formatted_address", "")
        phone = result.get("formatted_phone_number")
        rating = result.get("rating")
        review_count = result.get("user_ratings_total", 0)
        website_url = result.get("website")
        has_website = bool(website_url)
        
        # Extract city from address components
        city = self._extract_city_from_components(result.get("address_components", []))
        if not city:
            city = self._extract_city_from_address(address)
        
        # Extract coordinates
        geometry = result.get("geometry", {})
        location = geometry.get("location", {})
        latitude = location.get("lat")
        longitude = location.get("lng")
        
        return BusinessData(
            place_id=place_id,
            name=name,
            address=address,
            city=city,
            phone=phone,
            rating=rating,
            review_count=review_count,
            category=category,
            has_website=has_website,
            website_url=website_url,
            latitude=latitude,
            longitude=longitude
        )
    
    def _extract_city_from_components(self, components: List[Dict]) -> str:
        """Extract city from address components.
        
        Args:
            components: Address components from Google Places
            
        Returns:
            City name or empty string
        """
        for component in components:
            types = component.get("types", [])
            if "locality" in types:
                return component.get("long_name", "")
            elif "administrative_area_level_2" in types:
                return component.get("long_name", "")
        return ""
    
    def _extract_city_from_address(self, address: str) -> str:
        """Extract city from formatted address string (fallback method).
        
        Args:
            address: Formatted address string
            
        Returns:
            City name or "Unknown"
        """
        # Simple heuristic: city is usually before the postal code
        # This is a fallback and may not be accurate
        parts = address.split(",")
        if len(parts) >= 2:
            # Try to find the part that looks like a city
            for part in parts:
                part = part.strip()
                # Skip parts that look like postal codes or states
                if part and not part[0].isdigit() and len(part) > 2:
                    return part
        return "Unknown"
