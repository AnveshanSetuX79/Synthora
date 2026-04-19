"""LatLng API service for geocoding and places search."""
import requests
from typing import List, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LatLngAPIError(Exception):
    """Base exception for LatLng API errors."""
    pass


class RateLimitError(LatLngAPIError):
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
        self.website_url = website  # Alias for compatibility
        self.rating = rating
        self.review_count = review_count
        self.has_website = bool(website)  # Computed property


class LatLngService:
    """Service for interacting with LatLng API."""
    
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
            LatLngAPIError: If request fails
            RateLimitError: If rate limit exceeded
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params or {}, timeout=10)
            
            if response.status_code == 429:
                raise RateLimitError("LatLng API rate limit exceeded")
            
            if response.status_code == 401:
                raise LatLngAPIError("Invalid LatLng API key")
            
            if response.status_code == 403:
                raise LatLngAPIError("Forbidden - check API key permissions")
            
            if response.status_code != 200:
                raise LatLngAPIError(f"LatLng API error: {response.status_code} - {response.text}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LatLng API request failed: {e}")
            raise LatLngAPIError(f"Request failed: {str(e)}")
    
    def _is_coordinates(self, location: str) -> Optional[tuple[float, float]]:
        """Check if location string is already coordinates.
        
        Args:
            location: Location string to check
            
        Returns:
            Tuple of (lat, lon) if valid coordinates, None otherwise
        """
        try:
            # Try to parse as "lat, lon" or "lat,lon"
            parts = location.replace(" ", "").split(",")
            if len(parts) == 2:
                lat = float(parts[0])
                lon = float(parts[1])
                
                # Validate coordinate ranges
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    logger.info(f"Detected coordinates: ({lat}, {lon})")
                    return lat, lon
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def geocode_location(self, location: str) -> tuple[float, float]:
        """Convert location name to coordinates using forward geocoding.
        
        Args:
            location: City name or address (or coordinates as "lat,lon")
            
        Returns:
            Tuple of (latitude, longitude)
            
        Raises:
            LatLngAPIError: If geocoding fails
        """
        # Check if location is already coordinates
        coords = self._is_coordinates(location)
        if coords:
            return coords
        
        try:
            params = {"q": location, "limit": 1}
            result = self._make_request("api", params)
            
            if not result.get("features"):
                raise LatLngAPIError(f"Location not found: {location}")
            
            # Get first result
            feature = result["features"][0]
            coords = feature["geometry"]["coordinates"]
            lon, lat = coords[0], coords[1]  # GeoJSON format is [lon, lat]
            
            logger.info(f"Geocoded '{location}' to ({lat}, {lon})")
            return lat, lon
            
        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"Failed to parse geocoding response: {e}")
            raise LatLngAPIError(f"Failed to geocode location: {location}")
    
    def search_nearby_places(
        self,
        latitude: float,
        longitude: float,
        category: str,
        radius: int = 2000,
        limit: int = 20
    ) -> List[Dict]:
        """Search for places near coordinates.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            category: Business category (restaurant, cafe, hotel, etc.)
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
            logger.error(f"Places search failed: {e}")
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
            # Step 1: Geocode the location to get coordinates and area details
            lat, lon = self.geocode_location(location)
            
            # Step 2: Get area details from the geocoding result
            area_info = self._extract_area_info(location, lat, lon)
            
            # Step 3: Search nearby places
            places = self.search_nearby_places(lat, lon, category, radius=5000, limit=limit)
            
            # Step 4: Convert to BusinessData objects
            businesses = []
            for place in places:
                try:
                    business = self._parse_place(place, category, area_info)
                    if business:
                        businesses.append(business)
                except Exception as e:
                    logger.warning(f"Failed to parse place: {e}")
                    continue
            
            logger.info(f"Discovered {len(businesses)} businesses in {location}")
            return businesses
            
        except LatLngAPIError as e:
            logger.error(f"Business search failed: {e}")
            raise
    
    def _extract_area_info(self, location: str, lat: float, lon: float) -> Dict:
        """Extract area information from location string and coordinates.
        
        Args:
            location: Original location string
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with area, city, and state information
        """
        try:
            # Try reverse geocoding to get detailed location info
            result = self.reverse_geocode(lat, lon)
            
            if result.get("features"):
                feature = result["features"][0]
                properties = feature.get("properties", {})
                
                # Extract components
                area = properties.get("neighbourhood") or properties.get("suburb")
                city = properties.get("city") or properties.get("town") or properties.get("village")
                state = properties.get("state")
                
                return {
                    "area": area,
                    "city": city or location.split(",")[0].strip(),
                    "state": state,
                    "full_location": location
                }
        except Exception as e:
            logger.warning(f"Could not extract area info: {e}")
        
        # Fallback: parse from location string
        parts = [p.strip() for p in location.split(",")]
        return {
            "area": parts[0] if len(parts) > 1 else None,
            "city": parts[0] if len(parts) == 1 else parts[1],
            "state": None,
            "full_location": location
        }
    
    def _parse_place(self, place: Dict, category: str, area_info: Dict) -> Optional[BusinessData]:
        """Parse LatLng place data into BusinessData.
        
        Args:
            place: LatLng place dictionary
            category: Business category
            area_info: Dictionary with area and city information
            
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
            
            # Build detailed address
            address_parts = [name]
            if area_info.get("area"):
                address_parts.append(area_info["area"])
            address_parts.append(area_info["city"])
            
            address = ", ".join(address_parts)
            
            # Create unique place ID
            place_id = f"latlng_{lat}_{lon}_{name.replace(' ', '_')}"
            
            # LatLng doesn't provide phone, website, ratings
            return BusinessData(
                place_id=place_id,
                name=name,
                address=address,
                city=area_info["city"],
                latitude=float(lat),
                longitude=float(lon),
                category=category,
                phone=None,
                website=None,
                rating=0.0,
                review_count=0
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
            
        except LatLngAPIError as e:
            logger.error(f"Reverse geocoding failed: {e}")
            raise
