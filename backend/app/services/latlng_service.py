"""LatLng.work API service for business discovery and geocoding."""
import requests
from typing import List, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LatLngError(Exception):
    """Base exception for LatLng API errors."""
    pass


class RateLimitError(LatLngError):
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


class LatLngService:
    """Service for interacting with LatLng.work API."""
    
    BASE_URL = "https://api.latlng.work"
    
    def __init__(self, api_key: str):
        """Initialize LatLng service.
        
        Args:
            api_key: LatLng API key (starts with latlng_)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-Api-Key": api_key})
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make HTTP request to LatLng API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            LatLngError: If request fails
            RateLimitError: If rate limit exceeded
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params or {}, timeout=10)
            
            if response.status_code == 429:
                raise RateLimitError("LatLng API rate limit exceeded (3,000 calls/day on free tier)")
            
            if response.status_code == 401:
                raise LatLngError("Invalid LatLng API key")
            
            if response.status_code == 403:
                raise LatLngError("Forbidden - check API key permissions")
            
            if response.status_code != 200:
                raise LatLngError(f"LatLng API error: {response.status_code} - {response.text}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LatLng API request failed: {e}")
            raise LatLngError(f"Request failed: {str(e)}")
    
    def geocode_location(self, location: str) -> tuple[float, float]:
        """Convert location name to coordinates using forward geocoding.
        
        Args:
            location: City name or address
            
        Returns:
            Tuple of (latitude, longitude)
            
        Raises:
            LatLngError: If geocoding fails
        """
        try:
            params = {"q": location, "limit": 1}
            result = self._make_request("api", params)
            
            if not result.get("features"):
                raise LatLngError(f"Location not found: {location}")
            
            # Get first result
            feature = result["features"][0]
            coords = feature["geometry"]["coordinates"]
            lon, lat = coords[0], coords[1]  # GeoJSON format is [lon, lat]
            
            logger.info(f"Geocoded '{location}' to ({lat}, {lon})")
            return lat, lon
            
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"Failed to parse geocoding response: {e}")
            raise LatLngError(f"Failed to geocode location: {location}")
    
    def search_nearby_places(
        self,
        latitude: float,
        longitude: float,
        category: str,
        radius: int = 1000,
        limit: int = 20
    ) -> List[Dict]:
        """Search for places near coordinates.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            category: Business category (restaurant, school, etc.)
            radius: Search radius in meters (max 5000)
            limit: Maximum results
            
        Returns:
            List of place dictionaries
        """
        try:
            # Map our categories to LatLng categories
            category_map = {
                "restaurant": "restaurant",
                "school": "school",
                "retail": "shop",
                "healthcare": "hospital",
                "salon": "beauty_salon",
                "gym": "fitness_centre",
            }
            
            latlng_category = category_map.get(category, "restaurant")
            
            params = {
                "lat": latitude,
                "lon": longitude,
                "radius": min(radius, 5000),  # Max 5000m
                "category": latlng_category,
                "limit": limit
            }
            
            result = self._make_request("places/nearby", params)
            places = result.get("places", [])
            
            logger.info(f"Found {len(places)} places near ({latitude}, {longitude})")
            return places
            
        except Exception as e:
            logger.error(f"Places nearby search failed: {e}")
            return []
    
    def search_businesses(
        self,
        location: str,
        category: str,
        limit: int = 20
    ) -> List[BusinessData]:
        """Search for businesses in a location.
        
        Args:
            location: City name, address, or coordinates (lat,lng)
            category: Business category
            limit: Maximum results
            
        Returns:
            List of BusinessData objects
        """
        try:
            # Step 1: Get coordinates (geocode if needed)
            logger.info(f"Processing location: '{location}'")
            if self._is_coordinates(location):
                # Location is already coordinates
                parts = location.split(',')
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                logger.info(f"✅ Detected coordinates: lat={lat}, lon={lon}")
            else:
                # Geocode the location name
                logger.info(f"Geocoding location name: '{location}'")
                lat, lon = self.geocode_location(location)
            
            # Step 2: Search nearby places
            places = self.search_nearby_places(lat, lon, category, radius=5000, limit=limit)
            
            # Step 3: Convert to BusinessData objects
            businesses = []
            for place in places:
                try:
                    business = self._parse_place(place, category, location)
                    if business:
                        businesses.append(business)
                except Exception as e:
                    logger.warning(f"Failed to parse place: {e}")
                    continue
            
            logger.info(f"Discovered {len(businesses)} businesses near {location}")
            return businesses
            
        except LatLngError as e:
            logger.error(f"Business search failed: {e}")
            raise
    
    def _is_coordinates(self, location: str) -> bool:
        """Check if location string is coordinates (lat,lng)."""
        try:
            parts = location.split(',')
            if len(parts) != 2:
                return False
            float(parts[0].strip())
            float(parts[1].strip())
            return True
        except (ValueError, AttributeError):
            return False
    
    def _parse_place(self, place: Dict, category: str, city: str) -> Optional[BusinessData]:
        """Parse LatLng place data into BusinessData.
        
        Args:
            place: LatLng place dictionary
            category: Business category
            city: City name
            
        Returns:
            BusinessData object or None if parsing fails
        """
        try:
            # Get name
            name = place.get("name")
            if not name:
                return None
            
            # Get coordinates
            lat = place.get("lat")
            lon = place.get("lon")
            if lat is None or lon is None:
                return None
            
            # Build address (LatLng doesn't provide full addresses in nearby search)
            address = f"{name}, {city}"
            
            # Create unique place ID
            place_id = f"latlng_{lat}_{lon}_{name.replace(' ', '_')}"
            
            # Note: LatLng doesn't provide phone, website, ratings in nearby search
            # These would need additional API calls or data enrichment
            return BusinessData(
                place_id=place_id,
                name=name,
                address=address,
                city=city,
                latitude=float(lat),
                longitude=float(lon),
                category=category,
                phone=None,  # Not available in nearby search
                website=None,  # Not available in nearby search
                rating=0.0,  # Not available in nearby search
                review_count=0  # Not available in nearby search
            )
            
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Failed to parse LatLng place: {e}")
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
            result = self._make_request("reverse", params)
            return result
            
        except LatLngError as e:
            logger.error(f"Reverse geocoding failed: {e}")
            raise
    
    def search_places(self, query: str, lat: Optional[float] = None, 
                     lon: Optional[float] = None, limit: int = 10) -> List[Dict]:
        """Search for places by name.
        
        Args:
            query: Search query
            lat: Optional latitude for location bias
            lon: Optional longitude for location bias
            limit: Maximum results
            
        Returns:
            List of place dictionaries
        """
        try:
            params = {
                "q": query,
                "limit": limit
            }
            
            if lat is not None and lon is not None:
                params["lat"] = lat
                params["lon"] = lon
            
            result = self._make_request("places/search", params)
            return result.get("places", [])
            
        except LatLngError as e:
            logger.error(f"Places search failed: {e}")
            return []
