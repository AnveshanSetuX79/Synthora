"""LocationIQ API service for business discovery and geocoding."""
import requests
from typing import List, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LocationIQError(Exception):
    """Base exception for LocationIQ API errors."""
    pass


class RateLimitError(LocationIQError):
    """Raised when API rate limit is exceeded."""
    pass


class BusinessData:
    """Data class for business information."""
    def __init__(
        self,
        place_id: str,
        name: str,
        address: str,
        city: str,
        latitude: float,
        longitude: float,
        category: str,
        phone: Optional[str] = None,
        website: Optional[str] = None,
        rating: float = 0.0,
        review_count: int = 0,
    ):
        self.place_id = place_id
        self.name = name
        self.address = address
        self.city = city
        self.latitude = latitude
        self.longitude = longitude
        self.category = category
        self.phone = phone
        self.website = website
        self.rating = rating
        self.review_count = review_count


class LocationIQService:
    """Service for interacting with LocationIQ API."""
    
    BASE_URL = "https://us1.locationiq.com/v1"
    
    def __init__(self, api_key: str):
        """Initialize LocationIQ service.
        
        Args:
            api_key: LocationIQ API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.params = {"key": api_key, "format": "json"}
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make HTTP request to LocationIQ API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            LocationIQError: If request fails
            RateLimitError: If rate limit exceeded
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 429:
                raise RateLimitError("LocationIQ API rate limit exceeded")
            
            if response.status_code == 401:
                raise LocationIQError("Invalid LocationIQ API key")
            
            if response.status_code != 200:
                raise LocationIQError(f"LocationIQ API error: {response.status_code} - {response.text}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LocationIQ API request failed: {e}")
            raise LocationIQError(f"Request failed: {str(e)}")
    
    def geocode_location(self, location: str) -> tuple[float, float]:
        """Convert location name to coordinates.
        
        Args:
            location: City name or address
            
        Returns:
            Tuple of (latitude, longitude)
            
        Raises:
            LocationIQError: If geocoding fails
        """
        try:
            params = {"q": location}
            results = self._make_request("search.php", params)
            
            if not results:
                raise LocationIQError(f"Location not found: {location}")
            
            # Get first result
            result = results[0]
            lat = float(result["lat"])
            lon = float(result["lon"])
            
            logger.info(f"Geocoded '{location}' to ({lat}, {lon})")
            return lat, lon
            
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"Failed to parse geocoding response: {e}")
            raise LocationIQError(f"Failed to geocode location: {location}")
    
    def search_nearby_places(
        self,
        latitude: float,
        longitude: float,
        category: str,
        radius: int = 5000,
        limit: int = 20
    ) -> List[Dict]:
        """Search for places near coordinates using Overpass API.
        
        LocationIQ doesn't have a direct POI search, so we use OpenStreetMap
        Overpass API which is free and doesn't require authentication.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            category: Business category (restaurant, school, etc.)
            radius: Search radius in meters
            limit: Maximum results
            
        Returns:
            List of place dictionaries
        """
        # Map categories to OSM tags
        category_map = {
            "restaurant": "amenity=restaurant",
            "school": "amenity=school",
            "retail": "shop",
            "healthcare": "amenity=clinic|amenity=hospital|amenity=doctors",
            "salon": "shop=hairdresser|shop=beauty",
            "gym": "leisure=fitness_centre",
        }
        
        osm_tag = category_map.get(category, "amenity=restaurant")
        
        # Build Overpass query
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Query for places within radius
        query = f"""
        [out:json][timeout:25];
        (
          node[{osm_tag}](around:{radius},{latitude},{longitude});
          way[{osm_tag}](around:{radius},{latitude},{longitude});
        );
        out body {limit};
        """
        
        try:
            response = requests.post(overpass_url, data={"data": query}, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Overpass API error: {response.status_code}")
                return []
            
            data = response.json()
            elements = data.get("elements", [])
            
            logger.info(f"Found {len(elements)} places near ({latitude}, {longitude})")
            return elements
            
        except Exception as e:
            logger.error(f"Overpass API request failed: {e}")
            return []
    
    def search_businesses(
        self,
        location: str,
        category: str,
        limit: int = 20
    ) -> List[BusinessData]:
        """Search for businesses in a location.
        
        Args:
            location: City name or address
            category: Business category
            limit: Maximum results
            
        Returns:
            List of BusinessData objects
        """
        try:
            # Step 1: Geocode the location
            lat, lon = self.geocode_location(location)
            
            # Step 2: Search nearby places using Overpass
            places = self.search_nearby_places(lat, lon, category, radius=5000, limit=limit)
            
            # Step 3: Convert to BusinessData objects
            businesses = []
            for place in places:
                try:
                    business = self._parse_osm_place(place, category)
                    if business:
                        businesses.append(business)
                except Exception as e:
                    logger.warning(f"Failed to parse place: {e}")
                    continue
            
            logger.info(f"Discovered {len(businesses)} businesses in {location}")
            return businesses
            
        except LocationIQError as e:
            logger.error(f"Business search failed: {e}")
            raise
    
    def _parse_osm_place(self, place: Dict, category: str) -> Optional[BusinessData]:
        """Parse OpenStreetMap place data into BusinessData.
        
        Args:
            place: OSM place dictionary
            category: Business category
            
        Returns:
            BusinessData object or None if parsing fails
        """
        try:
            tags = place.get("tags", {})
            
            # Get name
            name = tags.get("name")
            if not name:
                return None
            
            # Get coordinates
            if "lat" in place and "lon" in place:
                lat = float(place["lat"])
                lon = float(place["lon"])
            elif "center" in place:
                lat = float(place["center"]["lat"])
                lon = float(place["center"]["lon"])
            else:
                return None
            
            # Build address
            address_parts = []
            if "addr:housenumber" in tags:
                address_parts.append(tags["addr:housenumber"])
            if "addr:street" in tags:
                address_parts.append(tags["addr:street"])
            if "addr:city" in tags:
                address_parts.append(tags["addr:city"])
            
            address = ", ".join(address_parts) if address_parts else "Address not available"
            city = tags.get("addr:city", "Unknown")
            
            # Get contact info
            phone = tags.get("phone") or tags.get("contact:phone")
            website = tags.get("website") or tags.get("contact:website")
            
            # Create unique place ID
            place_id = f"osm_{place['type']}_{place['id']}"
            
            # Note: OSM doesn't have ratings/reviews, so we set defaults
            return BusinessData(
                place_id=place_id,
                name=name,
                address=address,
                city=city,
                latitude=lat,
                longitude=lon,
                category=category,
                phone=phone,
                website=website,
                rating=0.0,  # OSM doesn't have ratings
                review_count=0  # OSM doesn't have reviews
            )
            
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Failed to parse OSM place: {e}")
            return None
    
    def get_place_details(self, place_id: str) -> Optional[BusinessData]:
        """Get detailed information about a place.
        
        Note: This is a placeholder. OSM/LocationIQ doesn't have a direct
        equivalent to Google Places Details API.
        
        Args:
            place_id: Place identifier
            
        Returns:
            BusinessData object or None
        """
        logger.warning("get_place_details not fully implemented for LocationIQ")
        return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Dict:
        """Convert coordinates to address.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            Address dictionary
        """
        try:
            params = {
                "lat": latitude,
                "lon": longitude,
            }
            result = self._make_request("reverse.php", params)
            return result
            
        except LocationIQError as e:
            logger.error(f"Reverse geocoding failed: {e}")
            raise
